import logging
import queue
import wave
import requests
import sounddevice as sd
from vosk import Model, KaldiRecognizer, SetLogLevel
from tqdm import tqdm
from urllib.request import urlretrieve
from zipfile import ZipFile

import json
from pathlib import Path
import os
import time


MODEL_PRE_URL = "https://alphacephei.com/vosk/models/"
MODEL_LIST_URL = MODEL_PRE_URL + "model-list.json"
MODEL_BASE_PATH = "/opt/vosk_models"

class Vosk():

    DEFAULT_LANGUAGE = "en-us"
    def __init__(self, language=None, samplerate=None, device=None, log=None):

        if not Path(MODEL_BASE_PATH).exists():
            Path(MODEL_BASE_PATH).mkdir(parents=True)

        self.log = log or logging.getLogger(__name__)
        self.update_model_list()
        SetLogLevel(-1)
        self.downloading = False

        self._device = device or sd.default.device
        if samplerate is None:
            device_info = sd.query_devices(self._device, "input")
            samplerate = int(device_info["default_samplerate"])
        self._samplerate = samplerate
        self.recognizer = None
        if language is not None:
            self.set_language(language, init=False)
            self.init()

    def is_ready(self):
        return self.recognizer is not None

    def init(self):
        model_path = self.get_model_path(self._language)
        if not model_path.exists():
            self.download_model(self._language)
        model_path = str(model_path)
        model = Model(model_path)
        self.recognizer = KaldiRecognizer(model, self._samplerate)

    def update_model_list(self):
        response = requests.get(MODEL_LIST_URL, timeout=10)
        self.available_models = [model for model in response.json() if
                model["type"] == "small" and model["obsolete"] == "false"]
        self.available_languages = [model["lang"] for model in self.available_models]
        self.available_model_names = [model["name"] for model in self.available_models]

    def stt(self, filename, stream=False):
        with wave.open(filename, "rb") as wf:
            if wf.getnchannels() != 1 or wf.getsampwidth() != 2 or wf.getcomptype() != "NONE":
                print("Audio file must be WAV format mono PCM.")
                sys.exit(1)
            self.recognizer.SetWords(True)
            if stream:
                self.recognizer.SetPartialWords(True)
                return self.get_stream_result(wf, self.recognizer)
            else:
                self.recognizer.SetPartialWords(False)
                return self.recognizer.Result()

    def get_stream_result(self, wf, recognizer):
        while True:
            data = wf.readframes(4000)
            if len(data) == 0:
                break
            if self.recognizer.AcceptWaveform(data):
                yield self.recognizer.Result()
            else:
                yield self.recognizer.PartialResult()

    def listen(self, stream=False, device=None, samplerate=None):
        """ Listen from microphone """
        q = queue.Queue()

        def callback(indata, frames, time, status):
            if status:
                self.log.warning(status)
            q.put(bytes(indata))

        if stream:
            return self._listen_streaming(q, device, samplerate, callback)
        else:
            return self._listen_non_streaming(q, device, samplerate, callback)

    def _listen_streaming(self, q, device=None, samplerate=None, callback=None):

        """ Listen from microphone and return the result.   
        Args:
            device (int, optional): The device ID to use. Defaults to None.
            samplerate (int, optional): The samplerate to use. Defaults to None.
        Returns:
            str: The recognized text.
        """
        with sd.RawInputStream(samplerate=samplerate, blocksize=8000, device=device,
                                dtype="int16", channels=1, callback=callback):

            while True:
                data = q.get()
                result = {
                    "done": False,
                    "partial": "",
                    "final": ""
                }
                if self.recognizer.AcceptWaveform(data):
                    text = self.recognizer.Result()
                    text = json.loads(text)["text"]
                    if text == "":
                        continue
                    result["done"] = True
                    result["final"] = text
                else:
                    partial = self.recognizer.PartialResult()
                    partial = json.loads(partial)["partial"]
                    if partial == "":
                        continue
                    result["partial"] = partial
                yield result

    def _listen_non_streaming(self, q, device=None, samplerate=None, callback=None):

        """ Listen from microphone and return the result.   
        Args:
            device (int, optional): The device ID to use. Defaults to None.
            samplerate (int, optional): The samplerate to use. Defaults to None.
        Returns:
            str: The recognized text.
        """

        with sd.RawInputStream(samplerate=samplerate, blocksize=8000, device=device,
                                dtype="int16", channels=1, callback=callback):

            while True:
                data = q.get()
                if self.recognizer.AcceptWaveform(data):
                    text = self.recognizer.Result()
                    text = json.loads(text)["text"]
                    if text == "":
                        continue
                    return text

    def set_language(self, language, init=True):
        if language not in self.available_languages:
            raise ValueError(f"Vosk does not support language: {language}. Available languages: {self.available_languages}")
        self._language = language
        if init:
            self.init()

    def get_model_name(self, lang):
        return self.available_model_names[self.available_languages.index(lang)]

    def get_model_path(self, lang):
        model_name = self.get_model_name(lang)
        return Path(MODEL_BASE_PATH, model_name)

    def is_model_downloaded(self, lang):
        model_path = self.get_model_path(lang)
        return model_path.exists()

    def download_model2(self, lang, progress_callback=None):
        model_path = self.get_model_path(lang)
        if self.is_model_downloaded(lang):
            return
        
        if self.downloading:
            return

        self.downloading = True
        try:
            # 根据是否有回调函数选择不同的进度报告方式
            if progress_callback:
                # 使用回调函数
                reporthook = self.download_progress_hook(progress_callback=progress_callback)
                urlretrieve(
                    MODEL_PRE_URL + str(model_path.name) + ".zip",
                    str(model_path) + ".zip",
                    reporthook=reporthook,
                    data=None
                )
            else:
                # 使用tqdm显示进度
                with tqdm(
                    unit="B", unit_scale=True, unit_divisor=1024, miniters=1,
                    desc=(MODEL_PRE_URL + str(model_path.name) + ".zip").rsplit("/", maxsplit=1)[-1]
                ) as t:
                    reporthook = self.download_progress_hook(tqdm_bar=t)
                    urlretrieve(
                        MODEL_PRE_URL + str(model_path.name) + ".zip",
                        str(model_path) + ".zip",
                        reporthook=reporthook,
                        data=None
                    )
                    t.total = t.n
            
            # 解压和清理文件
            with ZipFile(str(model_path) + ".zip", "r") as model_ref:
                model_ref.extractall(model_path.parent)
            Path(str(model_path) + ".zip").unlink()
        finally:
            self.downloading = False
            try:
                os.remove(str(model_path) + ".zip")
            except:
                pass

    def download_model(self, lang, progress_callback=None, max_retries=5):
        model_path = self.get_model_path(lang)
        if self.is_model_downloaded(lang):
            return
        
        if self.downloading:
            return

        self.downloading = True
        zip_url = MODEL_PRE_URL + f"{model_path.name}.zip"
        zip_path = f"{model_path}.zip"
        retries = 0
        
        try:
            while retries < max_retries:
                try:
                    # Check for partially downloaded file
                    resume_byte_pos = 0
                    if os.path.exists(zip_path):
                        resume_byte_pos = os.path.getsize(zip_path)
                        self.log.info(f"Resuming download from byte position {resume_byte_pos}")

                    headers = {}
                    if resume_byte_pos > 0:
                        headers['Range'] = f'bytes={resume_byte_pos}-'

                    # Send request
                    response = requests.get(zip_url, headers=headers, stream=True, timeout=30)
                    
                    # Check response status
                    if response.status_code not in [200, 206]:  # 200: full response, 206: partial content
                        response.raise_for_status()
                    
                    # Get total file size
                    content_length = response.headers.get('content-length')
                    if content_length is None:
                        total_size = None
                    else:
                        total_size = int(content_length) + resume_byte_pos
                    
                    # Prepare progress display
                    if progress_callback:
                        progress_callback(resume_byte_pos, total_size)
                    else:
                        t = tqdm(
                            total=total_size, initial=resume_byte_pos,
                            unit="B", unit_scale=True, unit_divisor=1024,
                            desc=zip_url.rsplit("/", maxsplit=1)[-1]
                        )

                    # Write to file
                    mode = 'ab' if resume_byte_pos > 0 else 'wb'
                    with open(zip_path, mode) as f:
                        downloaded_this_attempt = 0
                        for chunk in response.iter_content(chunk_size=8192):
                            if chunk:  # Filter out keep-alive empty chunks
                                f.write(chunk)
                                chunk_size = len(chunk)
                                downloaded_this_attempt += chunk_size
                                resume_byte_pos += chunk_size
                                
                                if progress_callback:
                                    progress_callback(resume_byte_pos, total_size)
                                else:
                                    t.update(chunk_size)

                    if not progress_callback:
                        t.close()

                    # Verify file size if possible
                    if total_size is not None:
                        downloaded_size = os.path.getsize(zip_path)
                        if downloaded_size != total_size:
                            raise Exception(f"Download incomplete: received {downloaded_size} bytes, expected {total_size} bytes")
                    else:
                        self.log.warning("Cannot verify file integrity - server did not provide content length")

                    # Unzip and clean up
                    with ZipFile(zip_path, "r") as model_ref:
                        model_ref.extractall(model_path.parent)
                    os.remove(zip_path)
                    
                    # Download successful, exit loop
                    break
                    
                except Exception as e:
                    retries += 1
                    self.log.error(f"Download attempt {retries}/{max_retries} failed: {str(e)}")
                    
                    # If max retries reached, raise exception
                    if retries >= max_retries:
                        self.log.error(f"Reached maximum retry count ({max_retries}), download failed")
                        raise
                    
                    # Wait before retrying (exponential backoff)
                    wait_time = 2 **retries
                    self.log.info(f"Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                    
        except Exception as e:
            self.log.error(f"Final download failure: {str(e)}")
            # Keep partially downloaded file for possible resume
            raise
        finally:
            self.downloading = False

    def download_progress_hook(self, tqdm_bar=None, progress_callback=None):
        last_b = [0]
        
        def update_to(b=1, bsize=1, tsize=None):
            if tsize not in (None, -1):
                if tqdm_bar:
                    tqdm_bar.total = tsize
                # elif progress_callback:
                #     # 第一次调用时，传递总大小
                #     progress_callback(0, tsize)
            
            # 计算已下载的字节数
            downloaded = (b - last_b[0]) * bsize
            last_b[0] = b
            
            if tqdm_bar:
                # 更新tqdm进度条
                return tqdm_bar.update(downloaded)
            elif progress_callback:
                # 调用进度回调函数
                current = min(b * bsize, tsize) if tsize else b * bsize
                progress_callback(current, tsize)
            
            return downloaded
        
        return update_to

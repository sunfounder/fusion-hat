import requests
import os
import logging
import pyaudio
from ..utils import enable_speaker

def volume_gain(input_file, output_file, gain):
    """ Apply volume gain to audio file.

    Args:
        input_file (str): Input audio file path.
        output_file (str): Output audio file path.
        gain (float): Gain factor.

    Returns:
        bool: True if success, False otherwise.
    """
    import sox

    try:
        transform = sox.Transformer()
        transform.vol(gain)

        transform.build(input_file, output_file)

        return True
    except Exception as e:
        print(f"[ERROR] volume_gain err: {e}")
        return False

class OpenAI_TTS():
    """ OpenAI TTS engine. """
    WHISPER = 'whisper'

    MODLES = [
        "tts-1",
        "tts-1-hd",
        "gpt-4o-mini-tts",
        "accent",
        "emotional-range",
        "intonation",
        "impressions",
        "speed-of-speech",
        "tone",
        "whispering",
    ]

    VOICES = [
        "alloy",
        "ash",
        "ballad",
        "coral",
        "echo",
        "fable",
        "nova",
        "onyx",
        "sage",
        "shimmer"
    ]

    DEFAULT_MODEL = 'tts-1'
    DEFAULT_VOICE = 'alloy'
    DEFAULT_INSTRUCTIONS = "Speak in a cheerful and positive tone."

    URL = "https://api.openai.com/v1/audio/speech"

    def __init__(self, *args,
        voice: str=DEFAULT_VOICE,
        model: str=DEFAULT_MODEL,
        api_key: str=None,
        gain: float=3,
        log: logging.Logger=None) -> None:
        """ Initialize OpenAI TTS engine.

        Args:
            voice (str, optional): Voice, default is 'alloy'.
            model (str, optional): Model, default is 'tts-1'.
            api_key (str, optional): API key.
            gain (float, optional): Volume gain, default is 3.
            log (logging.Logger, optional): Logger, default is None.
        """
        self.log = log or logging.getLogger(__name__)
        enable_speaker()

        self._model = model or self.DEFAULT_MODEL
        self._voice = voice or self.DEFAULT_VOICE
        self._gain = gain
        self.is_ready = False

        self.set_api_key(api_key)

    def tts(self, words: str, output_file: str="/tmp/openai_tts.wav", instructions: str=DEFAULT_INSTRUCTIONS, stream: bool=False) -> bool:
        """ Request OpenAI TTS API.

        Args:
            words (str): Words to say.
            output_file (str, optional): Output file, default is '/tmp/openai_tts.wav'.
            instructions (str, optional): Instructions, default is DEFAULT_INSTRUCTIONS.
            stream (bool, optional): Whether to stream the audio, default is False.

        Returns:
            bool: True if success, False otherwise.
        """
        
        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": self._model,
            "input": words,
            "voice": self._voice,
            "response_format": "wav",
            "instructions": instructions,
        }
        
        try:
            response = requests.post(self.URL, json=data, headers=headers, stream=True)
            
            response.raise_for_status()
            
            if stream:
                self._stream_audio(response)
            else:
                with open(output_file, "wb") as f:
                    for chunk in response.iter_content(chunk_size=1024):
                        if chunk:
                            f.write(chunk)
                
                if self._gain > 1:
                    old_output_file = output_file.replace('.wav', f'_old.wav')
                    os.rename(output_file, old_output_file)
                    volume_gain(old_output_file, output_file, self._gain)
                    os.remove(old_output_file)

            return True
        
        except requests.exceptions.RequestException as e:
            self.log.error(f"OpenAI TTS API request error: {e}")
            return False
        except IOError as e:
            self.log.error(f"OpenAI TTS API file operation error: {e}")
            return False

    def _stream_audio(self, response: requests.Response) -> None:
        """ Stream audio from response.

        Args:
            response (requests.Response): Response from OpenAI TTS API.
        """
        p = pyaudio.PyAudio()
        
        stream = p.open(format=p.get_format_from_width(2),
                        channels=1,
                        rate=22050,
                        output=True)
        
        for chunk in response.iter_content(chunk_size=1024):
            if chunk:
                stream.write(chunk)
        
        stream.stop_stream()
        stream.close()
        p.terminate()

    def say(self, words: str, instructions: str=DEFAULT_INSTRUCTIONS, stream: bool=True) -> None:
        """ Say words.

        Args:
            words (str): Words to say.
            instructions (str, optional): Instructions, default is DEFAULT_INSTRUCTIONS.
            stream (bool, optional): Whether to stream the audio, default is True.
        """
        if stream:
            self.tts(words, instructions=instructions, stream=True)
        else:
            file_name = "/tmp/openai_tts.wav"
            self.tts(words, instructions=instructions, output_file=file_name, stream=False)
            os.system(f'aplay {file_name}')
            os.remove(file_name)

    def set_voice(self, voice: str) -> None:
        """ Set voice.

        Args:
            voice (str): Voice.
        """
        if voice not in self.VOICES:
            raise ValueError(f'Voice {voice} is not supported')
        self._voice = voice

    def set_model(self, model: str) -> None:
        """ Set model.

        Args:
            model (str): Model.
        """
        if model not in self.MODLES:
            raise ValueError(f'Model {model} is not supported')
        self._model = model

    def set_api_key(self, api_key: str) -> None:
        """ Set api key.

        Args:
            api_key (str): API key.
        """
        self._api_key = api_key

    def set_gain(self, gain: int) -> None:
        """ Set gain.

        Args:
            gain (int): Gain.
        """
        self._gain = gain

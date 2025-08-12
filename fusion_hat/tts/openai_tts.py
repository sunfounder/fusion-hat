from openai import AsyncOpenAI
from openai.helpers import LocalAudioPlayer
import asyncio
import os

from .tts_engine import TTSEngine

class OpenAI_TTS(TTSEngine):
    """
    OpenAI TTS engine.
    """
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

    def __init__(self, *args, voice=DEFAULT_VOICE, model=DEFAULT_MODEL, api_key=None, **kwargs):

        super().__init__(*args, **kwargs)

        self._model = model or self.DEFAULT_MODEL
        self._voice = voice or self.DEFAULT_VOICE
        self.is_ready = False

        if api_key:
            self.set_api_key(api_key)
        else:
            if os.environ.get("OPENAI_API_KEY"):
                self.client = AsyncOpenAI()
                self.is_ready = True

    async def async_say(self, words, instructions=DEFAULT_INSTRUCTIONS):
        async with self.client.audio.speech.with_streaming_response.create(
            model=self._model,
            voice=self._voice,
            input=words,
            instructions=instructions,
            response_format="pcm",
        ) as response:
            await LocalAudioPlayer().play(response)

    def say(self, words, instructions=DEFAULT_INSTRUCTIONS):

        '''
        Say words.

        :param words: words to say.
        :type words: str
        :param instructions: instructions.
        :type instructions: str

        '''
        asyncio.run(self.async_say(words, instructions))

    def set_voice(self, voice):
        """
        Set voice.

        :param voice: voice.
        :type voice: str
        """
        if voice not in self.VOICES:
            raise ValueError(f'Voice {voice} is not supported')
        self._voice = voice

    def set_model(self, model):
        """
        Set model.

        :param model: model.
        :type model: str
        """
        if model not in self.MODLES:
            raise ValueError(f'Model {model} is not supported')
        self._model = model

    def set_api_key(self, api_key):
        """
        Set api key.

        :param api_key: api key.
        :type api_key: str
        """
        self._api_key = api_key
        self.client = AsyncOpenAI(api_key=self._api_key)
        self.is_ready = True

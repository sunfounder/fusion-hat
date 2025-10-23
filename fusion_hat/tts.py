""" Text-to-Speech (TTS) module.

This module provides a Text-to-Speech (TTS) class that can be used to convert text to speech using different TTS engines.

Available TTS engines:

- ``Piper``: A fast and local neural text-to-speech engine that embeds espeak-ng for phonemization.
- ``Pico2Wave``: SVOX Pico TTS engine used to convert text into a WAV audio file.
- ``Espeak``: A compact open source software speech synthesizer for English and other languages.
- ``OpenAI_TTS`` Online TTS service from OpenAI.

Example:

    ``Piper``

    Initialize Piper TTS engine.

    >>> from fusion_hat.tts import Piper
    >>> tts = Piper()

    Checkout available countries.

    >>> tts.available_countrys()
    ['ar_JO', 'ca_ES', 'cs_CZ', 'cy_GB', 'da_DK', 'de_DE', 'el_GR', 'en_GB', 'en_US', 'es_ES', 'es_MX', 'fa_IR', 'fi_FI', 'fr_FR', 'hu_HU', 'is_IS', 'it_IT', 'ka_GE', 'kk_KZ', 'lb_LU', 'lv_LV', 'ml_IN', 'ne_NP', 'nl_BE', 'nl_NL', 'no_NO', 'pl_PL', 'pt_BR', 'pt_PT', 'ro_RO', 'ru_RU', 'sk_SK', 'sl_SI', 'sr_RS', 'sv_SE', 'sw_CD', 'tr_TR', 'uk_UA', 'vi_VN', 'zh_CN']
    
    List all models for country en_US.

    >>> tts.available_models('en_US')
    {'amy': ['en_US-amy-low', 'en_US-amy-medium'], 'arctic': ['en_US-arctic-medium'], 'bryce': ['en_US-bryce-medium'], 'danny': ['en_US-danny-low'], 'hfc_female': ['en_US-hfc_female-medium'], 'hfc_male': ['en_US-hfc_male-medium'], 'joe': ['en_US-joe-medium'], 'john': ['en_US-john-medium'], 'kathleen': ['en_US-kathleen-low'], 'kristin': ['en_US-kristin-medium'], 'kusal': ['en_US-kusal-medium'], 'l2arctic': ['en_US-l2arctic-medium'], 'lessac': ['en_US-lessac-low', 'en_US-lessac-medium', 'en_US-lessac-high'], 'libritts': ['en_US-libritts-high'], 'libritts_r': ['en_US-libritts_r-medium'], 'ljspeech': ['en_US-ljspeech-medium', 'en_US-ljspeech-high'], 'norman': ['en_US-norman-medium'], 'reza_ibrahim': ['en_US-reza_ibrahim-medium'], 'ryan': ['en_US-ryan-low', 'en_US-ryan-medium', 'en_US-ryan-high'], 'sam': ['en_US-sam-medium']}
    
    Set model

    >>> tts.set_model('en_US-amy-low')
    
    Say message.

    >>> tts.say("Hi, I'm piper TTS. A fast and local neural text-to-speech engine that embeds espeak-ng for phonemization.")

    ``Espeak``

    Import and initialize Espeak TTS engine.

    >>> from fusion_hat.tts import Espeak
    >>> tts = Espeak()

    Set amplitude 0-200, default 100

    >>> tts.set_amp(200)
    
    Set speed 80-260, default 150

    >>> tts.set_speed(150)
    
    Set gap 0-200, default 1

    >>> tts.set_gap(1)
    
    Set pitch 0-99, default 80

    >>> tts.set_pitch(80)

    Say message.

    >>> tts.say("Hello world!")

    ``Pico2Wave``

    Import and initialize Pico2Wave TTS engine.

    >>> from fusion_hat.tts import Pico2Wave
    >>> tts = Pico2Wave()

    List available languages.

    >>> tts.SUPPORTED_LANGUAUE
    ['en-US', 'en-GB', 'de-DE', 'es-ES', 'fr-FR', 'it-IT']

    Set language.

    >>> tts.set_lang('en-US')
    
    Say message.

    >>> tts.say("Hello world!")

    ``OpenAI TTS``

    Import and initialize OpenAI TTS engine.

    >>> from fusion_hat.tts import OpenAI_TTS
    >>> API_KEY = "sk-..."
    >>> tts = OpenAI_TTS(api_key=API_KEY)

    Set voice.

    >>> tts.set_voice(tts.Voice.ALLOY)
    
    Say message.

    >>> tts.say("Hello world!")

    Say message with instructions.
    
    >>> tts.say("I'm so sad right now.", instructions="say it sadly")
"""

__all__ = [
    "Piper",
    "Pico2Wave",
    "Espeak",
    "OpenAI_TTS",
]

from sunfounder_voice_assistant.tts import Piper, Pico2Wave, Espeak, OpenAI_TTS
from .device import enable_speaker

# Save original __init__ methods
_original_piper_init = Piper.__init__
_original_pico2wave_init = Pico2Wave.__init__
_original_espeak_init = Espeak.__init__
_original_openai_tts_init = OpenAI_TTS.__init__

# Override __init__ methods to enable speaker
def _piper_init_with_speaker(self, *args, **kwargs):
    _original_piper_init(self, *args, **kwargs)
    enable_speaker()

def _pico2wave_init_with_speaker(self, *args, **kwargs):
    _original_pico2wave_init(self, *args, **kwargs)
    enable_speaker()

def _espeak_init_with_speaker(self, *args, **kwargs):
    _original_espeak_init(self, *args, **kwargs)
    enable_speaker()

def _openai_tts_init_with_speaker(self, *args, **kwargs):
    _original_openai_tts_init(self, *args, **kwargs)
    enable_speaker()

# Apply modified __init__ methods
Piper.__init__ = _piper_init_with_speaker
Pico2Wave.__init__ = _pico2wave_init_with_speaker
Espeak.__init__ = _espeak_init_with_speaker
OpenAI_TTS.__init__ = _openai_tts_init_with_speaker

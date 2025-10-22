TTS Class
================

This module provides a text-to-speech (TTS) interface using ``espeak`` or ``pico2wave`` engines.

The ``TTS`` class offers support for converting text to speech using either the ``espeak`` or ``pico2wave`` engine. It allows for language configuration and voice parameter tuning (for ``espeak``), with runtime checks for executable availability.

**Supported Languages (pico2wave)**


- en-US
- en-GB
- de-DE
- es-ES
- fr-FR
- it-IT



**Class: TTS**


.. class:: TTS(engine=TTS.PICO2WAVE, lang=None)

    Initializes the TTS engine.

    :param engine: Choose ``TTS.ESPEAK`` or ``TTS.PICO2WAVE`` as the TTS engine.
    :type engine: str
    :param lang: Language for ``pico2wave`` engine (e.g., 'en-US').
    :type lang: str
    :raises Exception: If the specified engine is not installed.

**Attributes**


.. data:: TTS.ESPEAK

    Constant for using the ``espeak`` engine.

.. data:: TTS.PICO2WAVE

    Constant for using the ``pico2wave`` engine.

.. data:: TTS.SUPPORTED_LANGUAUE

    List of supported languages for ``pico2wave``.

**Methods**


.. method:: say(words)

    Say the given words using the configured TTS engine.

    :param words: Text to speak.
    :type words: str

.. method:: espeak(words)

    Say the given words using the ``espeak`` engine.

    :param words: Text to speak.
    :type words: str

    :raises RuntimeError: If ``espeak`` is not available.

.. method:: pico2wave(words)

    Say the given words using the ``pico2wave`` engine.

    :param words: Text to speak.
    :type words: str

    :raises RuntimeError: If ``pico2wave`` is not available.

.. method:: lang(*value)

    Get or set the current language for ``pico2wave``.

    :param value: Optional language string (e.g., 'en-US').
    :type value: str
    :return: Current language setting.
    :rtype: str

    :raises ValueError: If the provided language is not supported.

.. method:: supported_lang()

    Return a list of supported languages for ``pico2wave``.

    :return: List of language codes.
    :rtype: list[str]

.. method:: espeak_params(amp=None, speed=None, gap=None, pitch=None)

    Configure voice parameters for ``espeak``.

    :param amp: Amplitude (0–200)
    :type amp: int
    :param speed: Speed of speech (80–260)
    :type speed: int
    :param gap: Gap between words (in milliseconds)
    :type gap: int
    :param pitch: Voice pitch (0–99)
    :type pitch: int

    :raises ValueError: If any parameter is out of its valid range.

**Dependencies**


- ``espeak`` (optional)
- ``pico2wave`` (optional)
- ``aplay`` for audio playback
- ``fusion_hat`` 


**Example Usage**


.. code-block:: python

   from fusion_hat import TTS

   # Initialize TTS class
   tts = TTS(lang='en-US')
   # Speak text
   tts.say("Hello World")
   # show all supported languages
   print(tts.supported_lang())

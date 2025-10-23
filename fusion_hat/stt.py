""" Speech to Text module

Convert speech to text.

Example:
    import STT and instantiate it

    >>> from fusion_hat.stt import STT
    >>> stt = STT(language="en-us")

    Listen for speech input

    >>> result = stt.listen(stream=False)
    >>> print(result)
    Hello

    Use Stream to get partial results

    >>> for result in stt.listen(stream=True):
    >>>     if result["done"]:
    >>>         print(f"\\r\\x1b[Kfinal: {result['final']}")
    >>>     else:
    >>>         print(f"\\r\\x1b[Kpartial: {result['partial']}", end="", flush=True)

    Wait for wake words

    >>> WAKE_WORDS = ["hey robot", "hello robot"]
    >>> stt = STT(language="en-us")
    >>> stt.set_wake_words(WAKE_WORDS)
    >>> print(f'Wake me with: {WAKE_WORDS}')
    Wake me with: ['hey robot', 'hello robot']
    >>> result = stt.wait_until_heard()
    >>> print("Wake word detected")
    Wake word detected

    Wake word in thread

    >>> while True:
    >>>     stt.start_listening_wake_words()
    >>>     while not stt.is_waked():
    >>>         print("Waiting for wake word...")
    >>>         time.sleep(3)
    >>>     print("Wake word detected")

"""

from sunfounder_voice_assistant.stt import STT, Vosk

__all__ = [
    "STT",
    "Vosk",
]
""" Large Language Model (LLM) module

This module provides a base class for large language models (LLMs) and preset LLM classes.

Example:
    import a preset LLM class

    >>> from fusion_hat.llm import Deepseek as LLM
    >>> from fusion_hat.llm import Grok as LLM
    >>> from fusion_hat.llm import Doubao as LLM
    >>> from fusion_hat.llm import Qwen as LLM
    >>> from fusion_hat.llm import OpenAI as LLM

    initialize the LLM instance

    >>> API_KEY = "your_api_key"
    >>> MODEL = "your_model"
    >>> llm = LLM(api_key=API_KEY, model=MODEL)
    
    For Ollama, you don't need api_key, but you might need to set ip.

    >>> from fusion_hat.llm import Ollama as LLM
    >>> llm = LLM(ip="localhost", model="deepseek-r1:1.5b")

    You can also import a basic LLM class.

    >>> from fusion_hat.llm import LLM as LLM

    You will need to set the base url which compatible with OpenAI completion API.

    >>> llm = LLM(
            base_url="https://api.deepseek.com",
            model=MODEL,
            api_key=API_KEY,
        )

    Or set the whole url if it's not ends with "/v1/chat/completions"

    >>> llm = LLM(
            url="https://api.deepseek.com/v1/chat/completions",
            model=MODEL,
            api_key=API_KEY,
        )

    Set instructions

    >>> llm.set_instructions("You are a helpful assistant.")

    Set welcome message

    >>> llm.set_welcome("Hello, I am a helpful assistant. How can I help you?")

    Prompt the LLM with input text

    >>> input_text = "Hello"
    >>> response = llm.prompt(input_text, stream=True)
    >>> for next_word in response:
    >>>     if next_word:
    >>>         print(next_word, end="", flush=True)
    >>> print("")

    Prompt with image

    >>> input_text = "Hello"
    >>> image = "image.jpg"
    >>> response = llm.prompt(input_text, image=image, stream=True)
    >>> for next_word in response:
    >>>     if next_word:
    >>>         print(next_word, end="", flush=True)
    >>> print("")
"""

from sunfounder_voice_assistant.llm import *

__all__ = [
    "LLM",
    "Deepseek",
    "Grok",
    "Doubao",
    "Qwen",
    "OpenAI",
    "Ollama",
    "Gemini",
]

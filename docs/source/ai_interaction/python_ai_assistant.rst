.. note::

    Hello, welcome to the SunFounder Raspberry Pi & Arduino & ESP32 Enthusiasts Community on Facebook! Dive deeper into Raspberry Pi, Arduino, and ESP32 with fellow enthusiasts.

    **Why Join?**

    - **Expert Support**: Solve post-sale issues and technical challenges with help from our community and team.
    - **Learn & Share**: Exchange tips and tutorials to enhance your skills.
    - **Exclusive Previews**: Get early access to new product announcements and sneak peeks.
    - **Special Discounts**: Enjoy exclusive discounts on our newest products.
    - **Festive Promotions and Giveaways**: Take part in giveaways and holiday promotions.

    👉 Ready to explore and create with us? Click [|link_sf_facebook|] and join today!

.. _ai_voice_assistant_car:

7. AI Voice Assistant
===========================

This lesson turns your Fusion HAT+ into a **voice-first AI assistant**.  
With the provided code, the robot will: **wait for a wake word**, **transcribe your speech** with Vosk, send it to an **OpenAI LLM**, and **speak back** using Piper TTS.

----

Before You Start
----------------

Make sure you have:

* :ref:`test_piper` — Piper voice works (e.g., you can play “Hello”).  
* :ref:`test_vosk` — Vosk STT works for your language (e.g., ``en-us``).  
* :ref:`py_online_llm` — Your **OpenAI API key** saved in ``secret.py`` as ``OPENAI_API_KEY``.  
* A working **microphone** and **speaker** on Fusion HAT.  
* A stable network connection (LLM is online).

----

Run the Example
---------------

.. code-block:: bash

   cd ~/fusion-hat/examples/
   sudo python3 voice_assistant.py

**Configuration used by the code:**

* LLM: **OpenAI** (``gpt-4o-mini``)  
* TTS: **Piper** (``en_US-ryan-low``)  
* STT: **Vosk** (``en-us``)  
* Wake word: ``"hey buddy"``  
* Keyboard input: **enabled** (optional manual input)  
* Image mode: **enabled** (``WITH_IMAGE=True``) — requires a multimodal-capable LLM if you decide to use images later

**What happens:**

1. The assistant shows a welcome message with the wake phrase.  
2. It listens for **“hey buddy”**.  
3. After wake, your speech is transcribed (Vosk → text).  
4. The text is sent to **OpenAI (gpt-4o-mini)** for a response.  
5. The answer is spoken with **Piper** (``en_US-ryan-low``).

**Example interaction**

.. code-block:: text

   You: Hey Buddy
   Robot: Hi there!

   You: What’s the capital of Italy?
   Robot: The capital of Italy is Rome.

Code
-----------------

.. code-block:: python

  from fusion_hat.voice_assistant import VoiceAssistant
  from fusion_hat.llm import OpenAI as LLM
  from secret import OPENAI_API_KEY as API_KEY

  llm = LLM(
      api_key=API_KEY,
      model="gpt-4o-mini",
  )

  # Robot name
  NAME = "Buddy"

  # Enable image, need to set up a multimodal language model
  WITH_IMAGE = True

  # Set models and languages
  LLM_MODEL = "gpt-4o-mini"
  TTS_MODEL = "en_US-ryan-low"
  STT_LANGUAGE = "en-us"

  # Enable keyboard input
  KEYBOARD_ENABLE = True

  # Enable wake word
  WAKE_ENABLE = True
  WAKE_WORD = [f"hey {NAME.lower()}"]
  # Set wake word answer, set empty to disable
  ANSWER_ON_WAKE = "Hi there"

  # Welcome message
  WELCOME = f"Hi, I'm {NAME}. Wake me up with: " + ", ".join(WAKE_WORD)

  # Set instructions
  INSTRUCTIONS = f"""
  You are a helpful assistant, named {NAME}.
  """

  va = VoiceAssistant(
      llm,
      name=NAME,
      with_image=WITH_IMAGE,
      tts_model=TTS_MODEL,
      stt_language=STT_LANGUAGE,
      keyboard_enable=KEYBOARD_ENABLE,
      wake_enable=WAKE_ENABLE,
      wake_word=WAKE_WORD,
      answer_on_wake=ANSWER_ON_WAKE,
      welcome=WELCOME,
      instructions=INSTRUCTIONS,
  )

  if __name__ == "__main__":
      va.run()

**Code explanation:**

* ``OpenAI(..., model="gpt-4o-mini")`` — Uses **OpenAI** as the only LLM in this lesson.  
* ``NAME`` / ``WAKE_WORD`` — Personalize the assistant (“Buddy”, “hey buddy”).  
* ``WITH_IMAGE=True`` — Enables image mode in the assistant (no image I/O logic included here).  
* ``TTS_MODEL="en_US-ryan-low"`` — Piper voice used for replies.  
* ``STT_LANGUAGE="en-us"`` — Vosk language for recognition.  
* ``KEYBOARD_ENABLE=True`` — Allows optional manual text input during debugging.  
* ``WELCOME`` / ``INSTRUCTIONS`` — Startup message and assistant persona/system prompt.  
* ``va.run()`` — Starts the loop: **wake → listen → LLM → speak**.


Switching to Other LLMs or TTS
------------------------------

You can easily switch to other LLMs, TTS, or STT languages with just a few edits:

* Supported LLMs:

  * OpenAI
  * Doubao
  * Deepseek
  * Gemini
  * Qwen
  * Grok

* :ref:`test_piper` — Check the supported languages of **Piper TTS**.  
* :ref:`test_vosk` — Check the supported languages of **Vosk STT**.  

To switch, simply modify the initialization part in the code:

.. code-block:: python

   from fusion_hat.llm import Gemini as LLM
   llm = LLM(api_key="YOUR_KEY", model="gemini-pro")

   # Set models and languages
   TTS_MODEL = "en_US-ryan-low"
   STT_LANGUAGE = "en-us"



----

Troubleshooting
-----------------------------

* **Robot doesn’t respond to wake word**

  - Check if the microphone works.  
  - Make sure ``WAKE_ENABLE = True``.  
  - Adjust the wake word to match your pronunciation.  
  - Reduce background noise and speak clearly.

* **No sound from the speaker**

  - Check the TTS model name (e.g., ``en_US-ryan-low``).  
  - Test Piper or Espeak manually.  
  - Verify speaker connection and volume.

* **API key error or timeout**

  - Check your key in ``secret.py``.  
  - Make sure your network connection is stable.  
  - Confirm the LLM model is supported (e.g., ``gpt-4o-mini``).

* **Wake word works but no response**

  - Check if the STT language matches your accent.  
  - Make sure the model downloaded correctly.  
  - Try printing debug logs to confirm STT is running.

* **TTS works but no LLM reply**

  - Check if the API key is valid.  
  - Verify model name and LLM settings.  
  - Ensure internet connectivity. 




.. note::

    Hello, welcome to the SunFounder Raspberry Pi & Arduino & ESP32 Enthusiasts Community on Facebook! Dive deeper into Raspberry Pi, Arduino, and ESP32 with fellow enthusiasts.

    **Why Join?**

    - **Expert Support**: Solve post-sale issues and technical challenges with help from our community and team.
    - **Learn & Share**: Exchange tips and tutorials to enhance your skills.
    - **Exclusive Previews**: Get early access to new product announcements and sneak peeks.
    - **Special Discounts**: Enjoy exclusive discounts on our newest products.
    - **Festive Promotions and Giveaways**: Take part in giveaways and holiday promotions.

    👉 Ready to explore and create with us? Click [|link_sf_facebook|] and join today!

3. STT with Vosk (Offline)
==============================================

Vosk is a lightweight speech-to-text (STT) engine that supports many languages and runs fully **offline** on Raspberry Pi.  
You only need internet access once to download a language model. After that, everything works without a network connection.  

In this lesson, we will:  

* Check the microphone on Raspberry Pi.  
* Install and test Vosk with a chosen language model.  

1. Check Your Microphone
--------------------------

Before using speech recognition, make sure your USB microphone works correctly.

#. List available recording devices:

   .. code-block:: bash

      arecord -l

   Look for a line like ``card 1: ... device 0``.  

#. Record a short sample (replace ``1,0`` with the numbers you found):

   .. code-block:: bash

      arecord -D plughw:1,0 -f S16_LE -r 16000 -d 3 test.wav

   * Example: if your device is ``card 2, device 0``, use:

   .. code-block:: bash

      arecord -D plughw:2,0 -f S16_LE -r 16000 -d 3 test.wav

#. Play it back to confirm the recording:

   .. code-block:: bash

      aplay test.wav

#. Adjust microphone volume if needed:

   .. code-block:: bash

      alsamixer

   * Press **F6** to select your USB microphone.  
   * Find the **Mic** or **Capture** channel.  
   * Make sure it is not muted (**[MM]** means mute, press ``M`` to unmute → should show **[OO]**).  
   * Use ↑ / ↓ arrow keys to change the recording volume.


.. _test_vosk:

2. Test Vosk
--------------------------

**Run the program**

   .. code-block:: bash

      cd ~/fusion-hat/examples
      sudo python3 stt_vosk_stream.py

The first time you run this code with a new language, Vosk will:

* **Automatically download the language model** (by default, the small version).
* **Print out the list of supported languages**.
* Start **listening** for audio input through the microphone.

You’ll see something like this in the terminal:

.. code-block:: text

         vosk-model-small-en-us-0.15.zip: 100%|███████████████████| 39.3M/39.3M [00:05<00:00, 7.85MB/s]
         ['ar', 'ar-tn', 'ca', 'cn', 'cs', 'de', 'en-gb', 'en-in', 'en-us', 'eo', 'es', 'fa', 'fr', 'gu', 'hi', 'it', 'ja', 'ko', 'kz', 'nl', 'pl', 'pt', 'ru', 'sv', 'te', 'tg', 'tr', 'ua', 'uz', 'vn']
         Say something

This means:

   * The model file (``vosk-model-small-en-us-0.15``) has been downloaded.  
   * The list of supported languages has been printed.  
   * The system is now listening — say something into the Fusion HAT+ microphone, and the recognized text will appear in the terminal.

**Tips:**

* Keep the microphone about **15–30 cm** away for better accuracy.  
* Choose a **model that matches your language and accent**.  
* Use a quiet environment to improve recognition.

**Code**

.. code-block:: python

   from fusion_hat.stt import Vosk as STT

   stt = STT(language="en-us")

   while True:
      print("Say something")
      for result in stt.listen(stream=True):
         if result["done"]:
               print(f"final:   {result['final']}")
         else:
               print(f"partial: {result['partial']}", end="\r", flush=True)


**Code explanation:**

* ``stt.listen(stream=True)`` — Starts streaming speech recognition and yields intermediate results as you speak.  
* ``result["partial"]`` — Displays the **real-time recognized text** (updated continuously).  
* ``result["final"]`` — Displays the **final recognized sentence** when you stop speaking.  
* The loop runs continuously, allowing **hands-free real-time transcription**.

Tip: This streaming mode is perfect for **voice assistants**, **command control**, or **live transcription**.

Troubleshooting
-----------------

* **No such file or directory (when running `arecord`)**

  You may have used the wrong card/device number.  
  Run:

  .. code-block:: bash

     arecord -l

  and replace ``1,0`` with the numbers shown for your USB microphone.

* **Recorded file has no sound**

  Open the mixer and check the microphone volume:

  .. code-block:: bash

     alsamixer

  * Press **F6** to select your USB mic.  
  * Make sure **Mic/Capture** is not muted (**[OO]** instead of **[MM]**).  
  * Increase the level with ↑.

* **Vosk does not recognize speech**

  * Make sure the **language code** matches your model (e.g. ``en-us`` for English, ``zh-cn`` for Chinese).  
  * Keep the microphone 15–30 cm away and avoid background noise.  
  * Speak clearly and slowly.

* **High latency / slow recognition**

  * The default auto-download is a **small model** (faster, but less accurate).  
  * If it’s still slow, close other programs to free CPU.  

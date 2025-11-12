.. note::

    Hello, welcome to the SunFounder Raspberry Pi & Arduino & ESP32 Enthusiasts Community on Facebook! Dive deeper into Raspberry Pi, Arduino, and ESP32 with fellow enthusiasts.

    **Why Join?**

    - **Expert Support**: Solve post-sale issues and technical challenges with help from our community and team.
    - **Learn & Share**: Exchange tips and tutorials to enhance your skills.
    - **Exclusive Previews**: Get early access to new product announcements and sneak peeks.
    - **Special Discounts**: Enjoy exclusive discounts on our newest products.
    - **Festive Promotions and Giveaways**: Take part in giveaways and holiday promotions.

    👉 Ready to explore and create with us? Click [|link_sf_facebook|] and join today!

1. TTS with Espeak and Pico2Wave
=================================================

In this lesson, we'll use two built-in text-to-speech (TTS) engines on Raspberry Pi — **Espeak** and **Pico2Wave** — to make the Fusion HAT+ talk.  

These two engines are both simple and run offline, but they sound quite different:

* **Espeak**: very lightweight and fast, but the voice is robotic. You can adjust speed, pitch, and volume.  
* **Pico2Wave**: produces a smoother and more natural voice than Espeak, but has fewer options to configure.  

You'll hear the difference in **voice quality** and **features**.  

----

1. Testing Espeak
--------------------

Espeak is a lightweight TTS engine included in Raspberry Pi OS.  
Its voice sounds robotic, but it is highly configurable: you can adjust volume, pitch, speed, and more.  

**Run the program**

  .. code-block:: bash
  
      cd ~/fusion-hat/examples
      sudo python3 tts_espeak.py

  * You should hear the Fusion HAT+ say: “Hello! I'm Espeak TTS.”
  * Try changing the tuning parameters in the code to experiment with how ``amp``, ``speed``, ``gap``, and ``pitch`` affect the sound.

**Code**

.. code-block:: python
  
  from fusion_hat.tts import Espeak

  # Create Espeak TTS instance
  tts = Espeak()
  # Set amplitude 0-200, default 100
  tts.set_amp(200)
  # Set speed 80-260, default 150
  tts.set_speed(150)
  # Set gap 0-200, default 1
  tts.set_gap(1)
  # Set pitch 0-99, default 80
  tts.set_pitch(80)

  tts.say("Hello! I’m Espeak TTS.")

**Code explanation:**

* ``tts.set_amp()`` — Controls the volume (0–200).  
* ``tts.set_speed()`` — Adjusts the speaking speed (80–260).  
* ``tts.set_gap()`` — Sets the word gap (0–200).  
* ``tts.set_pitch()`` — Sets the pitch (0–99).  
* ``tts.say()`` — Converts text to speech and plays it.

💡 **Tip:** Try increasing the pitch and speed to make the robot sound cheerful, or lowering them to make it sound serious.

----


2. Testing Pico2Wave
---------------------

Pico2Wave produces a **more natural and human-like voice** compared to Espeak.  
It’s very easy to use, but less flexible — you can only **change the language**, not the pitch, speed, or volume.  
This makes Pico2Wave a great choice when you want clear and smooth speech without too much configuration.

**Run the program**

  .. code-block:: bash
  
      cd ~/fusion-hat/examples
      sudo python3 tts_pico2wave.py

* You should hear the Fusion HAT+ say: “Hello! I'm Pico2Wave TTS.”  
* Try changing the language (for example, ``es-ES`` for Spanish) and listen to how the voice changes.  

**Code**

.. code-block:: python

  from fusion_hat.tts import Pico2Wave

  # Create Pico2Wave TTS instance
  tts = Pico2Wave()

  # Set the language
  tts.set_lang('en-US')  # en-US, en-GB, de-DE, es-ES, fr-FR, it-IT
  
  # Quick hello (sanity check)
  tts.say("Hello! I'm Pico2Wave TTS.")

**Code explanation:**

* ``tts.set_lang()`` — Sets the output language for speech synthesis.

  - ``en-US`` (default)
  - ``en-GB``
  - ``de-DE``
  - ``es-ES``
  - ``fr-FR``
  - ``it-IT``

* ``tts.say()`` — Converts the text to speech and plays it immediately.  


----

Troubleshooting
-------------------

* **No sound when running Espeak or Pico2Wave**

  * Check that your speakers/headphones are connected and volume is not muted.  
  * Run a quick test in terminal:

    .. code-block:: bash

       espeak "Hello world"
       pico2wave -w test.wav "Hello world" && aplay test.wav

  If you hear nothing, the issue is with audio output, not your Python code.

* **Espeak voice sounds too fast or too robotic**

  * Try adjusting the parameters in your code:

    .. code-block:: python

       tts.set_speed(120)   # slower
       tts.set_pitch(60)    # different pitch

* **Permission denied when running code**

  * Try running with ``sudo``:

    .. code-block:: bash

       sudo python3 test_tts_espeak.py

Comparison: Espeak vs Pico2Wave
-------------------------------------

.. list-table::
   :widths: 20 40 40
   :header-rows: 1

   * - Feature
     - Espeak
     - Pico2Wave
   * - Voice quality
     - Robotic, synthetic
     - More natural, human-like
   * - Languages
     - Default English
     - Fewer, but common ones
   * - Adjustable
     - Yes (speed, pitch, etc.)
     - No (only language)
   * - Performance
     - Very fast, lightweight
     - Slightly slower, heavier


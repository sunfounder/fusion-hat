.. _class_music:


Music Class
==================

The ``Music`` class provides methods for playing tones, music, and sound effects, managing musical attributes like tempo and key, and generating notes programmatically.


The ``Music`` class offers high-level musical control for playback and tone generation. It supports playing WAV files, generating tones by frequency and duration, configuring key signatures, tempo, and time signatures.


**Class: Music**


.. class:: Music()

    Initializes the music system, sets defaults for tempo, key, and time signature, and enables the speaker.

**Constants**


.. data:: FORMAT

    Audio format (16-bit PCM).

.. data:: CHANNELS

    Number of audio channels (1 = mono).

.. data:: RATE

    Audio sample rate (44100 Hz).

.. data:: NOTE_BASE_FREQ

    Base frequency of A4 = 440Hz.

.. data:: NOTE_BASE_INDEX

    MIDI note index of A4 = 69.

.. data:: NOTES

    List of note names in MIDI order (C0 to C8).

.. data:: WHOLE_NOTE, HALF_NOTE, QUARTER_NOTE, EIGHTH_NOTE, SIXTEENTH_NOTE

    Predefined note duration values.

.. data:: KEY_*_MAJOR

    Key signature constants.

**Methods**


.. method:: time_signature(top=None, bottom=None)

    Set or get the time signature.

    :param top: Top number (e.g., 4 in 4/4).
    :param bottom: Bottom number (e.g., 4 in 4/4).
    :return: Time signature tuple.
    :rtype: tuple

.. method:: key_signature(key=None)

    Set or get the musical key signature.

    :param key: Integer or string (e.g., "###" or Music.KEY_D_MAJOR).
    :return: Key signature as integer.
    :rtype: int

.. method:: tempo(tempo=None, note_value=QUARTER_NOTE)

    Set or get the tempo (BPM).

    :param tempo: Beats per minute.
    :param note_value: Note value as base (e.g., QUARTER_NOTE).
    :return: Tuple of tempo and note value.
    :rtype: tuple

.. method:: beat(beat)

    Get duration in seconds for a beat.

    :param beat: Beat count (e.g., 1, 0.5).
    :return: Time in seconds.
    :rtype: float

.. method:: note(note, natural=False)

    Convert a note name or MIDI index into frequency.

    :param note: Note name (e.g., "C4") or MIDI index.
    :param natural: Ignore key signature if True.
    :return: Frequency in Hz.
    :rtype: float

.. method:: sound_play(filename, volume=None)

    Play a sound file (blocking).

    :param filename: Path to a sound file.
    :param volume: Volume (0–100).
    :rtype: None

.. method:: sound_play_threading(filename, volume=None)

    Play a sound file in a background thread.

    :param filename: Path to a sound file.
    :param volume: Volume (0–100).
    :rtype: None

.. method:: music_play(filename, loops=1, start=0.0, volume=None)

    Play a music file using pygame.mixer.music.

    :param filename: Path to a music file.
    :param loops: Number of loops (0 = loop forever).
    :param start: Start position in seconds.
    :param volume: Volume (0–100).
    :rtype: None

.. method:: music_set_volume(value)

    Set volume for music playback.

    :param value: Volume (0–100).
    :rtype: None

.. method:: music_stop()

    Stop music playback.

.. method:: music_pause()

    Pause music playback.

.. method:: music_resume()

    Resume paused music.

.. method:: music_unpause()

    Unpause music (alias for ``music_resume()``).

.. method:: sound_length(filename)

    Get duration of a sound file.

    :param filename: Path to a sound file.
    :return: Duration in seconds.
    :rtype: float

.. method:: get_tone_data(freq, duration)

    Generate tone waveform data.

    :param freq: Frequency in Hz.
    :param duration: Duration in seconds.
    :return: Raw PCM data as bytes.
    :rtype: bytes

.. method:: play_tone_for(freq, duration)

    Play a tone at specified frequency and duration.

    :param freq: Frequency in Hz.
    :param duration: Time in seconds.
    :rtype: None

**Dependencies**


- pygame
- pyaudio
- fusion_hat

**Example Usage**


.. code-block:: python

   from fusion_hat import Music

   music = Music()

   # You can directly play a frequency for specific duration in seconds
   music.play_tone_for(400, 1)

   # Or use note to get the frequency
   music.play_tone_for(music.note("Middle C"), 0.5)
   # and set tempo and use beat to get the duration in seconds
   # Which make's it easy to code a song according to a sheet!
   music.tempo(120)
   music.play_tone_for(music.note("Middle C"), music.beat(1))

   # Here's an example playing Greensleeves
   set_volume(80)
   music.tempo(60, 1/4)

   print("Measure 1")
   music.play_tone_for(music.note("G4"), music.beat(1/8))
   print("Measure 2")
   music.play_tone_for(music.note("A#4"), music.beat(1/4))
   music.play_tone_for(music.note("C5"), music.beat(1/8))
   music.play_tone_for(music.note("D5"), music.beat(1/8 + 1/16))
   music.play_tone_for(music.note("D#5"), music.beat(1/16))
   music.play_tone_for(music.note("D5"), music.beat(1/8))


   # Play a sound
   music.sound_play("file.wav", volume=50)
   # Play a sound in the background
   music.sound_play_threading("file.wav", volume=80)
   # Get sound length
   music.sound_length("file.wav")


   # Play music
   music.music_play("file.mp3")
   # Play music in loop
   music.music_play("file.mp3", loop=0)
   # Play music in 3 times
   music.music_play("file.mp3", loop=3)
   # Play music in starts from 2 second
   music.music_play("file.mp3", start=2)
   # Set music volume
   music.music_set_volume(50)
   # Stop music
   music.music_stop()
   # Pause music
   music.music_pause()
   # Resume music
   music.music_resume()
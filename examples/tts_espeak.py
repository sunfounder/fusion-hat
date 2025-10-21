from fusion_hat.tts import Espeak

# Create Espeak TTS instance
tts = Espeak()

# Optional voice tuning
tts.set_amp(100)    # 0 to 200
tts.set_speed(150)  # 80 to 260
tts.set_gap(1)      # 0 to 200
tts.set_pitch(80)   # 0 to 99

tts.say("Hello! I’m Espeak TTS.")
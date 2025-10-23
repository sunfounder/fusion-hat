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
from fusion_hat.tts import Piper

tts = Piper()

tts.set_model('en_US-amy-low')
msg = "Hi, I'm piper TTS. A fast and local neural text-to-speech engine that embeds espeak-ng for phonemization."
tts.say(msg, stream=False)

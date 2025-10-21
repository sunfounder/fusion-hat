from fusion_hat.tts import Piper

tts = Piper()

# List supported languages
print(tts.available_countrys())

# List models for English (en_us)
print(tts.available_models('en_us'))

# Set a voice model (auto-download if not already present)
tts.set_model("en_US-amy-low")

# Say something
tts.say("Hello! I'm Piper TTS.")
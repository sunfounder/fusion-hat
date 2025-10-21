from fusion_hat.tts import Pico2Wave

# Create Pico2Wave TTS instance
tts = Pico2Wave()

# Set the language
tts.set_lang('en-US')  # en-US, en-GB, de-DE, es-ES, fr-FR, it-IT

# Quick hello (sanity check)
tts.say("Hello! I'm Pico2Wave TTS.")

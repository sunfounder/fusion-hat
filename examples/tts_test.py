# Import TTS class
from  fusion_hat import TTS

# Initialize TTS class
tts = TTS(lang='en-US')
# Speak text
tts.say("Hello World")
# show all supported languages
print(tts.supported_lang())
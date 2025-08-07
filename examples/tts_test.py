# Import TTS class
from fusion_hat.tts import Espeak
from fusion_hat.tts import Pico2Wave
from fusion_hat.tts import Piper
import time

# Initialize TTS class
espeak = Espeak()
pico2wave = Pico2Wave()
piper = Piper()

# Speak text
text = "Hello, I am Espeak, a text-to-speech engine."
print(f"Espeak: {text}")
espeak.say(text)
time.sleep(1)
text = "Hello, I am Pico2Wave, a text-to-speech engine."
print(f"Pico2Wave: {text}")
pico2wave.say(text)
time.sleep(1)
text = "Hello, I am Piper, a model-based text-to-speech engine."
print(f"Piper: {text}")
piper.say(text)
time.sleep(1)

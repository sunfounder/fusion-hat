from fusion_hat.tts import Piper
import time

piper = Piper()
piper.set_model("en_US-amy-medium")

start = time.time()

text = "Hello, I am Piper, a model-based text-to-speech engine."
print(f"Piper: {text}")
piper.say(text, stream=True)
end = time.time()
print(f"Time elapsed: {end - start}")

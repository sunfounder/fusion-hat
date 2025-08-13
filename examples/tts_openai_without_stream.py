# Import TTS class
from fusion_hat.tts import OpenAI_TTS
from secret import OPENAI_API_KEY

openai_tts = OpenAI_TTS(
    api_key=OPENAI_API_KEY,
    gain=3,
    model="tts-1",
    voice="alloy",
    stream=False,
)

text = "Hello, I am OpenAI, a online model-based text-to-speech engine."
openai_tts.say(text)

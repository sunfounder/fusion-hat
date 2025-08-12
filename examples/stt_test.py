from fusion_hat.stt import OpenAI_STT
from fusion_hat.stt import Vosk

# create a audio file for test
import os
words = "Hello, I am Pico2Wave, a text-to-speech engine."
cmd = f"pico2wave -l en-US -w test.wav \"{words}\""
os.system(cmd)

# ================ VOSK ===================
# Set Language here will init the model
# vosk = Vosk(language="en-us")
# vosk = Vosk(language="cn")

# You can also manually manage the models
vosk = Vosk()
language = "en-us"

def progress_callback(current, total):
    percent = current / total * 100
    print(f"\rDownloaded: {current} / {total} ({percent:.2f}%)", end="")

if not vosk.is_model_downloaded(language):
    print(f"Model {language} not downloaded, download it")
    vosk.download_model(language, progress_callback=progress_callback)
    print()
    print(f"Model {language} downloaded")

# vosk.set_language(language)

# ================ OPENAI ===================
# openai = OpenAI_STT()

print("Say something")

# Not Stream
# result = openai.stt("test.wav")
# print(result)

# Stream
# whisper-1 do not support stream
openai.set_model("gpt-4o-mini-transcribe")
result = openai.stt("test.wav", stream=True)
for next_word in result:
    print(next_word, end="", flush=True)

# Listen stream (only for vosk)
# With stream, you can see the result right away!
# for result in vosk.listen(stream=True):
#     if result["done"]:
#         print(result['final'])
#     else:
#         print(result["partial"], end="\r", flush=True)


# Listen without stream (only for vosk)
# Withou stream, you can get the final result at the end
# while True:
#     result = vosk.listen(stream=False)
#     print(result)

from fusion_hat.stt import Vosk

vosk = Vosk(language="en-us")
vosk = Vosk(language="cn")

print("Say something")

while True:
    result = vosk.listen(stream=False)
    print(result)
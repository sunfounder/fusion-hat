from fusion_hat.stt import Vosk

vosk = Vosk(language="en-us")
vosk = Vosk(language="cn")

print("Say something")

for result in vosk.listen(stream=True):
    if result["done"]:
        print(result['final'])
    else:
        print(result["partial"], end="\r", flush=True)

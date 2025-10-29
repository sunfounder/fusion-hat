from fusion_hat.stt import Vosk as STT

stt = STT(language="en-us")

while True:
    print("Say something")
    for result in stt.listen(stream=True):
        if result["done"]:
            print(f"\r\x1b[Kfinal: {result['final']}")
        else:
            print(f"\r\x1b[Kpartial: {result['partial']}", end="", flush=True)

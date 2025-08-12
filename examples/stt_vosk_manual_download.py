from fusion_hat.stt import Vosk

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

vosk.set_language(language)
print("Say something")

for result in vosk.listen(stream=True):
    if result["done"]:
        print(result['final'])
    else:
        print(result["partial"], end="\r", flush=True)

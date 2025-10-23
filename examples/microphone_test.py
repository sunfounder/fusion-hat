from fusion_hat.microphone import Microphone
from fusion_hat.device import enable_speaker
import os


mic = Microphone()
enable_speaker()

print("Echo test start")

while True:
    print("Say something")

    mic.listen("temp.wav")
    print("Playback")

    os.system("aplay temp.wav")

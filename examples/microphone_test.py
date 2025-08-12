from fusion_hat.microphone import Microphone
import os


mic = Microphone()

print("Echo test start")

while True:
    print("Say something")

    mic.listen("temp.wav")
    print("Playback")

    os.system("aplay temp.wav")

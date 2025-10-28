from fusion_hat.user_button import UserButton
import time

usr = UserButton()

def on_press():
    print("On Press!")


def on_release():
    print("On Release!")

usr.set_on_press(on_press)
usr.set_on_release(on_release)

while True:
    if usr.pressed:
        print("User button pressed")
    else:
        print("User button released")
    time.sleep(1)

from fusion_hat.pin import Pin
import time

btn = Pin(17, mode=Pin.IN, pull=Pin.PULL_UP, bounce_time=0.05)

def on_press():
    print(f"Button pressed")

def on_release():
    print(f"Button released")

btn.when_activated = on_press
btn.when_deactivated = on_release

while True:
    print(f'btn value: {btn.value()}')
    time.sleep(.1)

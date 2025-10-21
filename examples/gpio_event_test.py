from fusion_hat.pin import Pin
import time

btn = Pin(17, mode=Pin.IN, pull=Pin.PULL_UP, bounce_time=0.05)

btn.when_activated = lambda: print(f"Button pressed - {time.time()}")
btn.when_deactivated = lambda: print(f"Button released - {time.time()}")

while True:
    print(f'btn value: {btn.value()}')
    time.sleep(.1)

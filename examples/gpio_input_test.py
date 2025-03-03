from fusion_hat import Pin
from time import sleep

print("GPIO Input Test")

io17 = Pin(17, Pin.IN, Pin.PULL_UP)
io4 = Pin(4, Pin.IN, Pin.PULL_DOWN)
io27 = Pin(27, Pin.IN, Pin.PULL_NONE, active_state=True)
io22 = Pin(22, Pin.IN, Pin.PULL_NONE, active_state=False)


while True:
    # Read the value of the GPIO pin
    print(f'GPIO 17: {io17.value()}, GPIO 4: {io4.value()}, GPIO 27: {io27.value()}, GPIO 22: {io22.value()}')

    sleep(.5)


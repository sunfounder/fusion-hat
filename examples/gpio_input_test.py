from fusion_hat.pin import Pin, Mode, Pull, Active
from time import sleep

print("GPIO Input Test")

io17 = Pin(17, mode=Mode.IN, pull=Pull.UP)
io4 = Pin(4, mode=Mode.IN, pull=Pull.DOWN)
io27 = Pin(27, mode=Mode.IN, pull=Pull.NONE, active_state=Active.HIGH)
io22 = Pin(22, mode=Mode.IN, pull=Pull.NONE, active_state=Active.LOW)


while True:
    # Read the value of the GPIO pin
    print(f'GPIO 17: {io17.value()}, GPIO 4: {io4.value()}, GPIO 27: {io27.value()}, GPIO 22: {io22.value()}')

    sleep(.5)


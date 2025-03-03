from fusion_hat import Pin
from time import sleep

io17 = Pin(17, Pin.OUT)

while True:
    io17.value(1)
    sleep(0.5)
    io17.value(0)
    sleep(0.5)

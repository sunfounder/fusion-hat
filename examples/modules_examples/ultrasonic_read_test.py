# Import Ultrasonic and Pin class
from fusion_hat.modules import Ultrasonic
from fusion_hat.pin import Pin
from time import sleep


# Create Ultrasonic object
us = Ultrasonic(Pin(17), Pin(4))

while True:
    # Read distance
    distance = us.read()
    print(f"Distance: {distance}cm")
    sleep(0.2)
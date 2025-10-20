# Import Ultrasonic and Pin class
from fusion_hat import Ultrasonic, Pin
from time import sleep

# Create Ultrasonic object
us = Ultrasonic(Pin(27), Pin(22))

while True:
    # Read distance
    distance = us.read()
    print(f"Distance: {distance}cm")
    sleep(0.2)
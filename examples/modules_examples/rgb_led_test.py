#!/usr/bin/env python3
from fusion_hat.modules import RGB_LED
from fusion_hat.pwm import PWM
from time import sleep

# Initialize an RGB LED. Connect the red component to P0, green to P1, and blue to P2.
rgb_led = RGB_LED(PWM(0), PWM(1), PWM(2), common=RGB_LED.CATHODE)

try:
    # Set the RGB LED to red.
    rgb_led.color((255, 0, 0))
    sleep(1)

    # Set the RGB LED to green.
    rgb_led.color("#00FF22") 
    sleep(1)

    # Set the RGB LED to purple.
    rgb_led.color(0xFF00FF)  
    sleep(1)

    # Set the RGB LED to black.
    rgb_led.color(0x000000)  

except KeyboardInterrupt:
    # Handle a KeyboardInterrupt (Ctrl+C) to exit.
    rgb_led.color(0x000000)  
    pass

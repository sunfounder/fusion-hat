#!/usr/bin/env python3
from fusion_hat.pin import Pin, Mode
from time import sleep

# Initialize an LED connected to GPIO pin 17 as an output pin.
led = Pin(17,mode=Mode.OUT)

try:
    # Start an infinite loop to toggle the LED state.
    while True:
        # Turn on the LED and print a message to the console.
        led.high()
        print('...LED ON')

        # Wait for 0.5 seconds with the LED on.
        sleep(0.5)

        # Turn off the LED and print a message to the console.
        led.low()
        print('LED OFF...')

        # Wait for 0.5 seconds with the LED off.
        sleep(1)

except KeyboardInterrupt:
    # Gracefully handle a keyboard interrupt (Ctrl+C) by breaking the loop.
    pass

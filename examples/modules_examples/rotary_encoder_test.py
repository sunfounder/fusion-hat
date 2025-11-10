#!/usr/bin/env python3
from fusion_hat.modules import Rotary_Encoder
from fusion_hat.pin import Pin, Mode, Pull
from signal import pause  # Import pause function from signal module


# Initialize the rotary encoder and button (sw)
encoder = Rotary_Encoder(clk=17, dt=4)  # Rotary Encoder connected to GPIO pins 17 (CLK) and 4 (DT)
sw = Pin(27, mode=Mode.IN, pull=Pull.UP)  # Button (sw) connected to GPIO pin 27


def rotary_change():
    """ Update the counter based on the rotary encoder's rotation. """
    print('Counter =', encoder.steps())  # Display current counter value

def reset_counter():
    """ Reset the counter to zero when the button (sw) is pressed. """
    encoder.reset()  # Reset the counter
    print('Counter reset')  # Indicate counter reset

# Set up event handlers for the rotary encoder and button (sw)
encoder.when_rotated = rotary_change
sw.when_activated = reset_counter


# Run an event loop that waits for button (sw) events and keeps the script running
print("CTRL + C to exit")
pause()

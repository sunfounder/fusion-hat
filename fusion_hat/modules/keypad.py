#!/usr/bin/env python3
from gpiozero import DigitalOutputDevice, Button

class Keypad:
    def __init__(self, rows_pins, cols_pins, keys):
        """
        Initialize the Keypad with specified row and column pins and keypad layout.
        :param rows_pins: List of GPIO pins for the rows.
        :param cols_pins: List of GPIO pins for the columns.
        :param keys: List of keys in the keypad layout.
        """
        # Initialize row pins as DigitalOutputDevice
        self.rows = [DigitalOutputDevice(pin) for pin in rows_pins]
        # Initialize column pins as Buttons
        self.cols = [Button(pin, pull_up=False) for pin in cols_pins]
        self.keys = keys  # Set the keypad layout

    def read(self):
        """
        Read the currently pressed keys on the keypad.
        :return: A list of pressed keys.
        """
        pressed_keys = []
        # Scan each row and column to identify pressed keys
        for i, row in enumerate(self.rows):
            row.on()  # Enable the current row
            for j, col in enumerate(self.cols):
                if col.is_pressed:  # Check if the column button is pressed
                    # Calculate the key index based on row and column
                    index = i * len(self.cols) + j
                    pressed_keys.append(self.keys[index])
            row.off()  # Disable the current row
        return pressed_keys


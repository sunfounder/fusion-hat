from fusion_hat.modules import Keypad
from time import sleep

try:
    # Configure rows, columns, and keypad layout
    # pin from left to right - 4 17 27 22 23 24 25 12
    rows_pins = [4, 17, 27, 22]
    cols_pins = [23, 24, 25, 12]
    keys = ["1", "2", "3", "A",
            "4", "5", "6", "B",
            "7", "8", "9", "C",
            "*", "0", "#", "D"]

    # Create an instance of the Keypad class
    keypad = Keypad(rows_pins, cols_pins, keys)
    last_key_pressed = []


    # Continuously read the keypad and print newly pressed keys
    while True:
        pressed_keys = keypad.read()
        if pressed_keys and pressed_keys != last_key_pressed:
            print(pressed_keys)  # Print the list of pressed keys
            last_key_pressed = pressed_keys
        sleep(0.1)  # Short delay to reduce CPU load

except KeyboardInterrupt:
    # Handle a keyboard interrupt (Ctrl+C) for a clean exit
    pass

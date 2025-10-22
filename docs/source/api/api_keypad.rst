Keypad Class
============

The ``Keypad`` class provides an interface for matrix-style keypads (e.g., 3x4 or 4x4) using GPIO pins on a Raspberry Pi via the ``gpiozero`` library. It enables detection of pressed keys based on row and column scanning.

**Initialization**

.. method:: __init__(rows_pins, cols_pins, keys)

   Initialize the keypad with row and column GPIO pin lists and a layout of keys.

   :param rows_pins: List of GPIO pins connected to the rows of the keypad.
   :type rows_pins: list[int]
   :param cols_pins: List of GPIO pins connected to the columns of the keypad.
   :type cols_pins: list[int]
   :param keys: Flat list of keypad keys in row-major order.
   :type keys: list[str]


Example: 

.. code-block:: python

   rows_pins = [4, 17, 27, 22]
   cols_pins = [23, 24, 25, 12]
   keys = ["1", "2", "3", "A",
            "4", "5", "6", "B",
            "7", "8", "9", "C",
            "*", "0", "#", "D"]

   # Create an instance of the Keypad class
   keypad = Keypad(rows_pins, cols_pins, keys)

**Reading Keypad**


.. method:: read()

   Read the keys currently being pressed on the keypad.

   :return: A list of keys currently pressed.
   :rtype: list[str]

   The scanning method enables each row sequentially and checks which column lines register a press.

**Usage Example**


.. code-block:: python

   from fusion_hat import Keypad
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

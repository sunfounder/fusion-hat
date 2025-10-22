LCD1602 Class
=============

The ``LCD1602`` class provides an interface for controlling a 1602 LCD display module (16 characters x 2 lines) via I2C. It supports basic operations such as writing text, clearing the display, and toggling the backlight.


**Initialization**



.. method:: __init__(address=None, backlight=True, bus=1)

   Initialize the LCD1602 display module via I2C. Automatically scans for known I2C addresses.

   :param address: I2C address of the LCD module. If None, the class tries default addresses (0x27, 0x3F).
   :type address: int or None
   :param backlight: Whether the backlight should be enabled on startup.
   :type backlight: bool
   :param bus: I2C bus number.
   :type bus: int
   :raises OSError: If no compatible LCD1602 module is found on the I2C bus.

**Backlight Control**



.. method:: open_back_light()

   Turn on the LCD backlight.

.. method:: close_back_light()

   Turn off the LCD backlight.

**Display Control**



.. method:: clear()

   Clear the display and reset cursor position to the top-left.

.. method:: send_command(cmd)

   Send a command byte directly to the LCD controller.

   :param cmd: Command byte.
   :type cmd: int

.. method:: send_data(data)

   Send a data byte to the LCD (used for character display).

   :param data: ASCII character code to display.
   :type data: int

**Writing Text**



.. method:: write(x, y, str)

   Write a string to a specific (x, y) position on the LCD.

   :param x: Horizontal position (column), 0–15.
   :type x: int
   :param y: Vertical position (row), 0 or 1.
   :type y: int
   :param str: Text string to display.
   :type str: str

.. method:: message(text)

   Write a multiline message to the LCD. Newline characters (`\n`) automatically move to the second line.

   :param text: Message string with optional newline.
   :type text: str

**Low-Level Communication**



.. method:: write_byte(data)

   Write a raw byte to the LCD module with optional backlight control.

   :param data: Raw byte value.
   :type data: int

**Constants**



.. data:: DEFAULT_ADDRESS_1
   :value: 0x27

   Default I2C address used by many LCD modules.

.. data:: DEFAULT_ADDRESS_2
   :value: 0x3F

   Alternative default I2C address used by some LCD modules.

**Usage Example**



.. code-block:: python

   from fusion_hat import LCD1602
   from time import sleep

   lcd = LCD1602(address=0x27, backlight=1)

   while True:
      lcd.clear()
      lcd.write(0, 0, 'Greetings!')
      lcd.write(1, 1, 'From SunFounder')
      sleep(1)
      lcd.clear()
      lcd.message('Hello\n   World!')
      sleep(1)
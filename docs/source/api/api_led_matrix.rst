LedMatrix Class
===============

The ``LedMatrix`` class provides an interface to control an 8x8 LED matrix display via SPI using the ``luma.led_matrix`` library. It supports displaying custom binary patterns to the matrix.

**Initialization**

.. method:: __init__(rotate=0)

   Initializes the SPI interface and LED matrix device.

   :param rotate: Rotation of the display in degrees (0, 90, 180, 270).
   :type rotate: int

   This sets up the SPI communication using the ``luma.core.interface.serial.spi`` and initializes a ``max7219`` 8x8 LED matrix device. The optional ``rotate`` parameter controls display orientation.

**Pattern Display**

.. method:: display_pattern(pattern)

   Display a pattern on the 8x8 LED matrix.

   :param pattern: List of 8 integers (each between 0-255), representing rows of binary data. Each bit in an integer corresponds to one pixel (LED).
   :type pattern: list[int]

   The matrix will light up pixels according to the bits set in each row value. The most significant bit is on the left (column 0), and the least significant bit is on the right (column 7).

   **Example Pattern:**

   .. code-block:: python

      from fusion_hat import LedMatrix

      pattern = [
         0b00011000,
         0b00111100,
         0b01111110,
         0b11111111,
         0b11111111,
         0b01111110,
         0b00111100,
         0b00011000
      ]

      led = LedMatrix()
      led.display_pattern(pattern)

   This will display a symmetrical diamond/star shape on the 8x8 matrix.

**Dependencies**

- ``luma.led_matrix`` 
- ``luma.core`` 
- ``PIL`` (Python Imaging Library)


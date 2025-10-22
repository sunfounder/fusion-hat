RGB_LED Class
====================


The ``RGB_LED`` class allows you to set the color of a 3-pin RGB LED using ``PWM`` objects for each of the red, green, and blue channels. Colors can be set using hex strings (e.g., "#FF0000"), 24-bit integers, or RGB tuples/lists.



**Class: RGB_LED**

.. class:: RGB_LED(r_pin, g_pin, b_pin, common=1)

    Initializes a 3-pin RGB LED object.

    :param r_pin: PWM object controlling the red channel.
    :type r_pin: robot_hat.PWM
    :param g_pin: PWM object controlling the green channel.
    :type g_pin: robot_hat.PWM
    :param b_pin: PWM object controlling the blue channel.
    :type b_pin: robot_hat.PWM
    :param common: LED type, either ``RGB_LED.ANODE`` or ``RGB_LED.CATHODE``. Default is ``RGB_LED.ANODE``.
    :type common: int

    :raises TypeError: If any pin is not a ``PWM`` object.
    :raises ValueError: If ``common`` is not ``RGB_LED.ANODE`` or ``RGB_LED.CATHODE``.

**Constants**

.. data:: RGB_LED.ANODE

    Common anode RGB LED configuration.

.. data:: RGB_LED.CATHODE

    Common cathode RGB LED configuration.

**Methods**

.. method:: color(color)

    Sets the LED to a specific color.

    :param color: The color to display. Can be a hex string (e.g., "#RRGGBB"), a 24-bit integer, or a tuple/list of 3 integers (0–255).
    :type color: str or int or tuple or list

    :raises TypeError: If color is not a string, int, tuple, or list.
    :raises ValueError: If tuple/list does not contain exactly 3 elements.


**Example Usage**

.. code-block:: python

   # Import RGB_LED and PWM class
   from fusion_hat import RGB_LED, PWM

   # Create RGB_LED object for common anode RGB LED
   rgb = RGB_LED(PWM(0), PWM(1), PWM(2), common=RGB_LED.ANODE)
   # or for common cathode RGB LED
   rgb = RGB_LED(PWM(0), PWM(1), PWM(2), common=RGB_LED.CATHODE)

   # Set color with 24 bit int
   rgb.color(0xFF0000) # Red
   # Set color with RGB tuple
   rgb.color((0, 255, 0)) # Green
   # Set color with RGB List
   rgb.color([0, 0, 255]) # Blue
   # Set color with RGB hex string starts with “#”
   rgb.color("#FFFF00") # Yellow
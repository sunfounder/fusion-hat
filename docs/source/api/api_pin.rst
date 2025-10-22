.. _class_pin:


Pin Class
=========

The ``Pin`` class provides an abstraction layer for GPIO pin control using the ``gpiozero`` library on Raspberry Pi.
It supports both input and output modes, internal pull-up/down resistors, interrupts, and pin state management.


**Constants**


.. data:: OUT
   :value: 0x01

   Pin mode: output.

.. data:: IN
   :value: 0x02

   Pin mode: input.

.. data:: PULL_UP
   :value: 0x11

   Use internal pull-up resistor.

.. data:: PULL_DOWN
   :value: 0x12

   Use internal pull-down resistor.

.. data:: PULL_NONE
   :value: None

   No internal pull resistor.

.. data:: IRQ_FALLING
   :value: 0x21

   Trigger interrupt on falling edge.

.. data:: IRQ_RISING
   :value: 0x22

   Trigger interrupt on rising edge.

.. data:: IRQ_RISING_FALLING
   :value: 0x23

   Trigger interrupt on both edges.

**Initialization**


.. method:: __init__(pin, mode=None, pull=None, active_state=None, bounce_time=None)

   Initialize a ``Pin`` instance.

   :param pin: Board pin name (e.g., 'D0') or GPIO pin number.
   :type pin: str or int
   :param mode: Pin mode (IN or OUT).
   :type mode: int
   :param pull: Internal pull resistor (PULL_UP, PULL_DOWN, PULL_NONE).
   :type pull: int
   :param active_state: Pin polarity (True for active-high, False for active-low).
   :type active_state: bool or None
   :param bounce_time: Debounce time for input pins (in milliseconds).
   :type bounce_time: int or None

**Methods**


.. method:: setup(mode, pull=None, active_state=None, bounce_time=None)

   Configure the pin.

   :param mode: Pin mode (IN or OUT).
   :param pull: Pull resistor type.
   :param active_state: Active state polarity.
   :param bounce_time: Debounce time in milliseconds.

.. method:: value(value=None)

   Get or set the pin value.

   :param value: Set value (1 or 0), or leave ``None`` to read.
   :type value: int or None
   :returns: Pin value (1 or 0).
   :rtype: int


.. method:: on()

   Set the pin high.

   :returns: 1

.. method:: off()

   Set the pin low.

   :returns: 0

.. method:: high()

   Alias for :meth:`on`.

.. method:: low()

   Alias for :meth:`off`.

.. method:: irq(handler, trigger, bouncetime=200, pull=None)

   Attach an interrupt handler to the pin.

   :param handler: Function to call on interrupt.
   :type handler: function
   :param trigger: Trigger type (IRQ_FALLING, IRQ_RISING, IRQ_RISING_FALLING).
   :param bouncetime: Debounce time in milliseconds.
   :type bouncetime: int
   :param pull: Pull resistor setting (optional).

.. method:: close()

   Release the GPIO resource.

.. method:: deinit()

   Fully deinitialize the pin and its GPIO factory.

.. method:: dict(_dict=None)

   Get or override the board-to-GPIO pin mapping.

   :param _dict: Optional new pin mapping dictionary.
   :type _dict: dict or None
   :returns: Current pin dictionary.
   :rtype: dict

.. method:: name()

   Get the GPIO name of the pin (e.g., "GPIO17").

   :returns: GPIO name.
   :rtype: str

**Properties**


.. attribute:: when_activated

   Handler function called when the pin becomes active (e.g., button press).

.. attribute:: when_deactivated

   Handler function called when the pin becomes inactive (e.g., button release).

**Usage Example 1**


.. code-block:: python

   from fusion_hat import Pin
   from time import sleep

   print("GPIO Input Test")

   io17 = Pin(17, Pin.IN, Pin.PULL_UP)
   io4 = Pin(4, Pin.IN, Pin.PULL_DOWN)
   io27 = Pin(27, Pin.IN, Pin.PULL_NONE, active_state=True)
   io22 = Pin(22, Pin.IN, Pin.PULL_NONE, active_state=False)


   while True:
      # Read the value of the GPIO pin
      print(f'GPIO 17: {io17.value()}, GPIO 4: {io4.value()}, GPIO 27: {io27.value()}, GPIO 22: {io22.value()}')

      sleep(.5)

**Usage Example 2**

.. code-block:: python

   from fusion_hat import Pin
   from time import sleep

   io17 = Pin(17, Pin.OUT)

   while True:
      io17.value(1)
      sleep(0.5)
      io17.value(0)
      sleep(0.5)


**Usage Example 3**

.. code-block:: python

   from fusion_hat import Pin
   import time

   btn = Pin(17, mode=Pin.IN, pull=Pin.PULL_UP, bounce_time=0.05)

   btn.when_activated = lambda: print(f"Button pressed - {time.time()}")
   btn.when_deactivated = lambda: print(f"Button released - {time.time()}")

   while True:
      print(f'btn value: {btn.value()}')
      time.sleep(.1)
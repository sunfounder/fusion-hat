Ultrasonic Class
=======================

This module provides an interface to an ultrasonic distance sensor using GPIO pins.

The ``Ultrasonic`` class allows measuring distance using an ultrasonic sensor by triggering a sound pulse and listening for its echo. The time delay between transmission and reception is used to calculate the distance.


**Class: Ultrasonic**



.. class:: Ultrasonic(trig, echo, timeout=0.02)

    Initializes the ultrasonic sensor with a trigger and echo pin.

    :param trig: GPIO pin used to send the ultrasonic pulse.
    :type trig: robot_hat.Pin
    :param echo: GPIO pin used to receive the reflected signal.
    :type echo: robot_hat.Pin
    :param timeout: Timeout in seconds for waiting on echo (default 0.02s).
    :type timeout: float

    :raises TypeError: If ``trig`` or ``echo`` is not a ``robot_hat.Pin`` instance.

**Methods**



.. method:: read(times=10)

    Measures the distance to the nearest object.

    It attempts to read the distance up to ``times`` times, ignoring failures up to that limit.

    :param times: Number of attempts to get a valid reading.
    :type times: int
    :return: Distance in centimeters, or -1 if all attempts fail.
    :rtype: float

**Private Methods**



.. method:: _read()

    Internal method that performs a single distance measurement attempt.

    :return: Distance in centimeters, -1 on timeout, or -2 if an invalid pulse is captured.
    :rtype: float

**Constants**



.. data:: SOUND_SPEED

    Speed of sound in air, used to calculate distance.

    :value: 343.3 (in m/s)
    :type: float


**Example Usage**



.. code-block:: python

   # Import Ultrasonic and Pin class
   from fusion_hat import Ultrasonic, Pin
   from time import sleep

   # Create Ultrasonic object
   us = Ultrasonic(trig=Pin(27), echo=Pin(22))

   while True:
      # Read distance
      distance = us.read()
      print(f"Distance: {distance}cm")
      sleep(0.2)
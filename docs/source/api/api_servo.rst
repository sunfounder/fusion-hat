Servo Class
===========

The ``Servo`` class provides an interface to control standard RC servo motors using PWM signals. It is derived from the ``PWM`` class and allows control over servo angle and pulse width.



**Initialization**

.. method:: __init__(channel, address=None, *args, **kwargs)

   Initialize a servo motor on a specific PWM channel.

   :param channel: PWM channel number (0–14) or string identifier (e.g., "P0").
   :type channel: int or str
   :param address: Optional I2C address of the PWM controller.
   :type address: int or None

**Servo Configuration**

.. attribute:: MAX_PW
   :value: 2500

   Maximum pulse width in microseconds.

.. attribute:: MIN_PW
   :value: 500

   Minimum pulse width in microseconds.

.. attribute:: FREQ
   :value: 50

   Default PWM frequency in Hz.

.. attribute:: PERIOD
   :value: 4095

   PWM period (resolution) value.

**Servo Control Methods**

.. method:: angle(angle)

   Set the servo motor to a specified angle.

   :param angle: Servo angle from -90 to 90 degrees.
   :type angle: float or int
   :raises ValueError: If the angle is not a number.

   The input angle is mapped to a pulse width in the range 500–2500µs.

.. method:: pulse_width_time(pulse_width_time)

   Set the servo's pulse width directly (typically in microseconds).

   :param pulse_width_time: Pulse width (500–2500µs).
   :type pulse_width_time: float

   Internally converts the pulse width to a PWM value relative to a 20ms cycle (50Hz).

**Usage Example**

.. code-block:: python

   from fusion_hat import Servo

   servo = Servo(channel="P0")
   servo.angle(0)        # Set to center
   servo.angle(90)       # Set to max rotation
   servo.angle(-90)      # Set to min rotation
   servo.pulse_width_time(1500)  # Set pulse width directly

**Notes**

- The angle range -90 to 90 is a common standard, but may vary based on servo model.
- Using ``pulse_width_time()`` allows for more precise tuning or non-standard control.

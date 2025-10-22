Buzzer Class
============

The ``Buzzer`` class provides control for both active and passive buzzers using either a PWM or digital GPIO pin. It supports simple on/off operations for active buzzers and frequency/duration control for passive buzzers.


**Initialization**


.. method:: __init__(buzzer)

   Initialize a ``Buzzer`` instance with a ``PWM`` or ``Pin`` object.

   :param buzzer: Either a PWM object (for passive buzzer) or a GPIO Pin object (for active buzzer).
   :type buzzer: PWM or Pin
   :raises TypeError: If an unsupported object is passed.

**Control Methods**


.. method:: on()

   Turn on the buzzer. For passive buzzers, sets 50% duty cycle. For active buzzers, sets pin high.

.. method:: off()

   Turn off the buzzer. For passive buzzers, sets duty cycle to 0. For active buzzers, sets pin low.

.. method:: freq(freq)

   Set frequency for passive buzzer.

   :param freq: Frequency in Hz.
   :type freq: float or int
   :raises TypeError: If the buzzer is active (uses a Pin).

.. method:: play(freq, duration=None)

   Play a note on the passive buzzer at a specific frequency for a specified duration.

   :param freq: Frequency in Hz, or musical note string (e.g., ``'A4'``, ``'C5'``).
   :type freq: float or str
   :param duration: Duration of the note in seconds. If ``None``, plays continuously.
   :type duration: float or None
   :raises TypeError: If the buzzer is active (uses a Pin).

**Constants**


.. data:: NOTE

   A dictionary mapping musical note names (e.g., ``"C4"``, ``"A4"``, ``"G#3"``) to their corresponding frequencies in Hz.

   :type: dict[str, float]

**Usage Examples**


.. code-block:: python

   from ezblock import Buzzer, PWM, Pin

   # For passive buzzer using PWM
   pwm_buzzer = Buzzer(PWM("P0"))
   pwm_buzzer.play('C4', 0.5)
   pwm_buzzer.play(440, 1.0)
   pwm_buzzer.off()

   # For active buzzer using GPIO
   pin_buzzer = Buzzer(Pin("D3"))
   pin_buzzer.on()
   time.sleep(1)
   pin_buzzer.off()

**Notes**


- Active buzzers only support on/off operation.
- Passive buzzers support musical notes and tone generation using frequency.
- Musical notes can be accessed from ``Buzzer.NOTE``.


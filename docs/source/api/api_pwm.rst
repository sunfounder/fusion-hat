.. _class_pwm:


PWM Class
=========

The ``PWM`` class provides an interface to hardware Pulse Width Modulation (PWM) via I2C. It allows setting PWM frequency, duty cycle, and period for up to 12 channels.

**Constants**


.. data:: ADDR
   :value: [0x17]

   Default I2C address for the PWM device.

.. data:: CLOCK
   :value: 72000000.0

   Clock frequency in Hz (72 MHz).

.. data:: REG_PSC_START
   :value: 0x40

   Start register for prescaler settings.

.. data:: REG_PSC_END
   :value: 0x49

   End register for prescaler settings.

.. data:: REG_ARR_START
   :value: 0x50

   Start register for auto-reload (period) settings.

.. data:: REG_ARR_END
   :value: 0x59

   End register for auto-reload (period) settings.

.. data:: REG_CCP_START
   :value: 0x60

   Start register for capture/compare values.

.. data:: REG_CCP_END
   :value: 0x77

   End register for capture/compare values.

.. data:: CHANNEL_NUM
   :value: 12

   Number of available PWM channels.

**Initialization**


.. method:: __init__(channel, freq=50, addr=None, *args, **kwargs)

   Initialize the PWM instance for a specified channel.

   :param channel: PWM channel number (0–11) or string "P0"–"P11".
   :type channel: int or str
   :param freq: PWM frequency in Hz (default is 50 Hz).
   :type freq: float
   :param addr: Optional I2C address override.
   :type addr: int or None

   :raises ValueError: If channel is out of range or improperly formatted.

**Methods**


.. method:: freq(freq=None)

   Set or get the PWM frequency.

   :param freq: Frequency in Hz (optional).
   :type freq: float or None
   :return: Current frequency.
   :rtype: float

.. method:: prescaler(psc=None)

   Set or get the prescaler value.

   :param psc: Prescaler value (0–65535).
   :type psc: int or None
   :return: Current prescaler.
   :rtype: int

.. method:: period(arr=None)

   Set or get the auto-reload register (ARR), which defines the PWM period.

   :param arr: Period value (0–65535).
   :type arr: int or None
   :return: Current period.
   :rtype: int

.. method:: pulse_width(ccp=None)

   Set or get the pulse width (CCP value).

   :param ccp: Pulse width (0–65535).
   :type ccp: int or None
   :return: Current pulse width.
   :rtype: int

.. method:: pulse_width_percent(duty_cycle=None)

   Set or get the duty cycle percentage.

   :param duty_cycle: Duty cycle in percent (0.0–100.0).
   :type duty_cycle: float or None
   :return: Current duty cycle.
   :rtype: float

**Attributes**


.. attribute:: channel

   PWM channel number assigned to the instance.

.. attribute:: duty_cycle

   Current duty cycle (as a percentage).

**Usage Example**


.. code-block:: python

   from fusion_hat import PWM
   from time import sleep

   p0 = PWM(0)
   p0.freq(50)
   p0.pulse_width_percent(50)

   p4 = PWM("P4")
   p4.freq(100)
   p4.pulse_width_percent(0)

   while True:
      for i in range(0, 101, 10):
         p4.pulse_width_percent(i)
         sleep(0.2)
      sleep(1)
      
      for i in range(100, -1, -10):
         p4.pulse_width_percent(i)
         sleep(0.2)
      sleep(1)
      
PWM_GROUP Class
===============

The ``PWM_GROUP`` class provides a high-level interface for controlling multiple PWM channels simultaneously via I2C on a Robot HAT. It allows setting frequency, duty cycle, pulse width, and supports batch updates to all channels.

**PWM Channel Mapping**

+-----------+--------+---------------+
| Channel   | Pin    | Timer Channel |
+===========+========+===============+
| 0         | A8     | TIM0_CH0      |
| 1         | A9     | TIM0_CH1      |
| 2         | A10    | TIM0_CH2      |
| 3         | A11    | TIM0_CH3      |
| 4         | B4     | TIM2_CH0      |
| 5         | B5     | TIM2_CH1      |
| 6         | B0     | TIM2_CH2      |
| 7         | B1     | TIM2_CH3      |
| 8         | B14    | TIM14_CH0     |
| 9         | B15    | TIM14_CH1     |
| 10        | B8     | TIM15_CH0     |
| 11        | B9     | TIM16_CH1     |
+-----------+--------+---------------+


**Initialization**

.. method:: __init__(channels, freq=50, addr=0x17, auto_write=False)

   Initialize a ``PWM_GROUP`` object for managing multiple PWM channels.

   :param channels: List of channel indices (0–11).
   :type channels: list of int
   :param freq: PWM frequency in Hz (default: 50).
   :type freq: int
   :param addr: I2C address (default: 0x17).
   :type addr: int
   :param auto_write: Automatically apply changes on assignment.
   :type auto_write: bool

**Frequency and Timer Configuration**

.. method:: freq(freq=None)

   Set or get the PWM frequency.

   :param freq: Frequency in Hz (optional).
   :type freq: int or None
   :return: Current frequency.
   :rtype: int

.. method:: prescaler(psc=None)

   Set or get the prescaler value.

   :param psc: Prescaler value (0–65535).
   :type psc: int or None
   :return: Current prescaler.
   :rtype: int

.. method:: period(arr=None)

   Set or get the period (auto-reload) value.

   :param arr: Period value (0–65535).
   :type arr: int or None
   :return: Current period.
   :rtype: int

**Pulse Width and Duty Cycle**

.. method:: pulse_width(index, pulse_width=None)

   Set or get the pulse width for a specific channel.

   :param index: Channel index.
   :type index: int
   :param pulse_width: Pulse width value (0–65535).
   :type pulse_width: int or None
   :return: Current pulse width.
   :rtype: int

.. method:: pulse_width_all(pulse_widths=None)

   Set or get pulse widths for all channels.

   :param pulse_widths: List of pulse widths (optional).
   :type pulse_widths: list of int or None
   :return: List of current pulse widths.
   :rtype: list of int

.. method:: pulse_width_perecent(index, percent=None)

   Set or get the duty cycle (percentage) for a channel.

   :param index: Channel index.
   :type index: int
   :param percent: Duty cycle percentage (0–100).
   :type percent: float or None
   :return: Current duty cycle.
   :rtype: float

.. method:: pulse_width_perecent_all(percents=None)

   Set or get duty cycle percentages for all channels.

   :param percents: List of duty cycle percentages (0–100).
   :type percents: list of float or None
   :return: List of current duty cycles.
   :rtype: list of float

**Utility Methods**

.. method:: write()

   Apply stored pulse width values to all configured channels.

**Item Access**

.. method:: __getitem__(index)

   Get the stored CCP value for a channel.

   :param index: Channel index.
   :type index: int
   :return: CCP value.
   :rtype: int

.. method:: __setitem__(index, value)

   Set the stored CCP value for a channel. If ``auto_write=True``, it is immediately written.

   :param index: Channel index.
   :type index: int
   :param value: CCP value.
   :type value: int

**Example Usage**

.. code-block:: python

   from fusion_hat import PWM_GROUP
   import time

   st = time.time()
   pwm_group = PWM_GROUP([0, 1, 2, 3, 8, 9, 10, 11,4, 5, 6, 7], freq=50)
   print(f'init PWM_GROUP {time.time()-st}')

   print(f'freq: {pwm_group.freq()}Hz, period: {pwm_group.period()}, prescaler: {pwm_group.prescaler()}')
   _step = (pwm_group.period()+1) / 12
   for i in range(12):
      pwm_group[i] = _step*(i+1)
   print(f'pwm_group: {pwm_group.pulse_width_all()}')
   pwm_group.write()

   try:
      while True:
         time.sleep(3)
         pwm_group.freq(50)
         time.sleep(3)
         pwm_group.freq(100)
   finally:
      print('reset pwm_group to 0')
      for i in range(12):
         pwm_group[i] = 0
      pwm_group.write()
      print(f'pwm_group: {pwm_group.pulse_width_all()}')





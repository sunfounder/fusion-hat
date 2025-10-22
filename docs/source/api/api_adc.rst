.. _class_adc:


ADC Class
=========

The ``ADC`` class provides an interface to an analog-to-digital converter over I2C. It supports reading raw values and converted voltage values from specified analog channels.


**Constants**


.. data:: ADDR
   :value: [0x17]

   Default I2C address of the ADC device.

.. data:: REG_ADC_START
   :value: 0x10

   Starting register address for ADC readings.

.. data:: REG_ADC_END
   :value: 0x19

   Ending register address for ADC readings.

.. data:: CHANNEL_NUM
   :value: 5

   Number of available ADC channels (A0–A4).

**Initialization**


.. method:: __init__(chn, address=None, *args, **kwargs)

   Initialize the ADC interface.

   :param chn: Channel identifier (integer 0–4 or string "A0"–"A4").
   :type chn: int or str
   :param address: Optional I2C address (default: 0x17).
   :type address: int

   :raises ValueError: If the channel is out of range or improperly formatted.

**Methods**


.. method:: read()

   Read the raw ADC value from the specified channel.

   :returns: ADC raw value (0–4095).
   :rtype: int

.. method:: read_voltage()

   Read and convert the ADC value into a voltage.

   :returns: Voltage reading (0.0–3.3V).
   :rtype: float

**Usage Example**


.. code-block:: python

   from fusion_hat import ADC
   import time

   a0 = ADC(0)
   a1 = ADC(1)
   a2 = ADC(2)
   a3 = ADC(3)
   bat_lv = ADC(4)


   while True:
      v0 = a0.read_voltage()
      v1 = a1.read_voltage()
      v2 = a2.read_voltage()
      v3 = a3.read_voltage()
      vbat = bat_lv.read_voltage() * 3
      print(f'A0: {v0:.2f}V, A1: {v1:.2f}V, A2: {v2:.2f}V, A3: {v3:.2f}V, Bat: {vbat:.2f}V')
      time.sleep(0.5)
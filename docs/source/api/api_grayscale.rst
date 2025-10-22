Grayscale_Module Class
======================

The ``Grayscale_Module`` class provides an interface for interacting with a 3-channel grayscale sensor module. It uses ADC channels to detect surface reflectivity and determine black or white line presence for each sensor (left, middle, right).



**Constants**

.. data:: LEFT
   :value: 0

   Index of the left channel.

.. data:: MIDDLE
   :value: 1

   Index of the middle channel.

.. data:: RIGHT
   :value: 2

   Index of the right channel.

.. data:: REFERENCE_DEFAULT
   :value: [1000, 1000, 1000]

   Default reference values for black/white detection threshold.

**Initialization**

.. method:: __init__(pin0, pin1, pin2, reference=None)

   Initialize the grayscale module with 3 ADC channels.

   :param pin0: ADC channel for the left sensor.
   :type pin0: ADC
   :param pin1: ADC channel for the middle sensor.
   :type pin1: ADC
   :param pin2: ADC channel for the right sensor.
   :type pin2: ADC
   :param reference: Optional initial reference values for each channel (list of 3 integers).
   :type reference: list[int] or None
   :raises TypeError: If any pin is not an instance of ``ADC``.

**Reference Management**

.. method:: reference(ref=None)

   Get or set the threshold reference values.

   :param ref: Reference threshold values, or None to read current values.
   :type ref: list[int] or None
   :return: Current reference values.
   :rtype: list[int]
   :raises TypeError: If ``ref`` is not a 3-element list.

**Sensor Reading**

.. method:: read(channel=None)

   Read grayscale value(s) from the sensor.

   :param channel: Channel index to read (0, 1, 2) or None to read all channels.
   :type channel: int or None
   :return: Single grayscale value or list of 3 grayscale values.
   :rtype: int or list[int]

.. method:: read_status(datas=None)

   Read sensor status as binary values (0 = white, 1 = black).

   :param datas: Optional list of grayscale readings to evaluate. If None, reads from the sensor.
   :type datas: list[int] or None
   :return: List of binary status values for left, middle, and right sensors.
   :rtype: list[int]
   :raises ValueError: If reference values have not been set.

**Usage Example**

.. code-block:: python

   from fusion_hat import Grayscale_Module, ADC

   gs = Grayscale_Module(ADC("A0"), ADC("A1"), ADC("A2"))
   gs.reference([800, 850, 820])

   raw_data = gs.read()           # Get analog grayscale readings
   status = gs.read_status()      # Get binary status: 0 = white, 1 = black

   left = gs.read(Grayscale_Module.LEFT)

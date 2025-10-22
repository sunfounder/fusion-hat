ADXL345 Class
=============

The ``ADXL345`` class provides an interface for the ADXL345 3-axis digital accelerometer using the I2C protocol. It allows reading acceleration data from the X, Y, and Z axes.

**Constants**


.. data:: X
   :value: 0

   Constant representing the X-axis.

.. data:: Y
   :value: 1

   Constant representing the Y-axis.

.. data:: Z
   :value: 2

   Constant representing the Z-axis.

.. data:: ADDR
   :value: 0x53

   Default I2C address of the ADXL345.

**Initialization**


.. method:: __init__(address=0x53, bus=1, *args, **kwargs)

   Initialize the ADXL345 accelerometer.

   :param address: I2C address of the device.
   :type address: int
   :param bus: I2C bus number.
   :type bus: int

**Methods**


.. method:: read(axis=None)

   Read acceleration data from a specified axis or all axes.

   :param axis: Axis to read (``ADXL345.X``, ``ADXL345.Y``, or ``ADXL345.Z``). If ``None``, reads all axes.
   :type axis: int or None
   :return: Acceleration in g-force from one axis or a list of all three axes.
   :rtype: float or list of float

Example:

.. code-block:: python

   from fusion_hat import ADXL345

   acc = ADXL345()
   x = acc.read(ADXL345.X)     # Read X-axis
   y = acc.read(ADXL345.Y)     # Read Y-axis
   z = acc.read(ADXL345.Z)     # Read Z-axis
   xyz = acc.read()            # Read all axes as a list

**Internal Method**


.. method:: _read(axis)

   Internal method to read raw acceleration data from a single axis.

   :param axis: Axis index (0 for X, 1 for Y, 2 for Z)
   :type axis: int
   :return: Acceleration value for the specified axis in g-force.
   :rtype: float

**Usage Notes**


- Values are returned in units of g-force.
- The first read may return inaccurate data; the implementation performs an extra read to mitigate this.
- The class writes control values to power and format registers before reading data.


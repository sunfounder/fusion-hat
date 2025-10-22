.. _class_i2c:


I2C Class
=========

The ``I2C`` class provides a high-level abstraction for interacting with I2C devices using the ``smbus2`` library. It supports common I2C read/write operations, memory register access, bus scanning, and device availability checks.



**Initialization**

.. method:: __init__(address=None, bus=1, *args, **kwargs)

   Initialize the I2C interface.

   :param address: I2C device address or list of candidate addresses.
   :type address: int or list of int
   :param bus: I2C bus number (default is 1).
   :type bus: int

**Core Methods**

.. method:: write(data)

   Write data to the I2C device. Automatically determines the appropriate command (byte, word, or block).

   :param data: Data to write (int, list, or bytearray).
   :type data: int or list or bytearray
   :raises ValueError: If ``data`` is of an unsupported type.

.. method:: read(length=1)

   Read raw bytes from the I2C device.

   :param length: Number of bytes to read.
   :type length: int
   :return: List of read bytes.
   :rtype: list of int

.. method:: mem_write(data, memaddr)

   Write data to a specific register on the device.

   :param data: Data to write.
   :type data: int, list, or bytearray
   :param memaddr: Register address.
   :type memaddr: int

.. method:: mem_read(length, memaddr)

   Read data from a specific register on the device.

   :param length: Number of bytes to read.
   :type length: int
   :param memaddr: Register address.
   :type memaddr: int
   :return: List of bytes or False on failure.
   :rtype: list or bool

**Device Status**

.. method:: is_ready()

   Check whether the device is responding on the I2C bus.

   :return: True if device is found, False otherwise.
   :rtype: bool

.. method:: is_avaliable()

   Alias for :meth:`is_ready`. Returns ``True`` if the device is on the bus.

   :return: True if device is available.
   :rtype: bool

**Bus Scanning**

.. staticmethod:: scan(bus=None)

   Scan the I2C bus for connected devices.

   :param bus: I2C bus number (defaults to class bus).
   :type bus: int or None
   :return: List of detected I2C addresses.
   :rtype: list of int

**Internal Low-Level Read/Write**

These methods include retry logic and detailed debug output:

- ``_write_byte(data)``
- ``_write_byte_data(reg, data)``
- ``_write_word_data(reg, data)``
- ``_write_i2c_block_data(reg, data)``
- ``_read_byte()``
- ``_read_byte_data(reg)``
- ``_read_word_data(reg)``
- ``_read_i2c_block_data(reg, num)``

Each of these is decorated with a retry mechanism to handle transient ``OSError`` conditions gracefully.

**Usage Example**

.. code-block:: python

   from fusion_hat import I2C

   i2c = I2C(address=[0x17, 0x15])
   if i2c.is_ready():
       i2c.write([0x01, 0x02])
       data = i2c.read(2)
       print("Read:", data)

**Notes**

- Default I2C bus is ``1``, which is standard for Raspberry Pi.
- The ``RETRY`` mechanism attempts failed I2C operations up to 5 times before returning ``False``.


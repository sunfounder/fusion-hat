DHT11 Class
===========

The ``DHT11`` class provides an interface for reading temperature and humidity data from a DHT11 sensor using the Raspberry Pi's GPIO pins.



**Initialization**



.. method:: __init__(pin)

   Initialize the DHT11 sensor.

   :param pin: The BCM GPIO pin number to which the DHT11 sensor is connected.
   :type pin: int

**Methods**



.. method:: read()

   Read data from the DHT11 sensor.

   This function performs the signal protocol required by the DHT11 to fetch 40 bits of data (5 bytes). It then verifies the checksum and extracts the humidity and temperature values.

   :return: Tuple of (humidity, temperature) on success, or ``False`` on failure.
   :rtype: tuple[int, int] or bool

   Example::

       sensor = DHT11(pin=4)
       result = sensor.read()
       if result:
           humidity, temperature = result
           print(f"Humidity: {humidity}%, Temperature: {temperature}°C")
       else:
           print("Sensor read failed.")

.. method:: destroy()

   Clean up GPIO settings. This should be called when the sensor is no longer in use.

.. method:: __del__()

   Destructor that automatically cleans up GPIO resources.

**Constants**



.. data:: STATE_INIT_PULL_DOWN

   Internal state constant used in the read signal decoding state machine.

.. data:: STATE_INIT_PULL_UP

   Internal state constant.

.. data:: STATE_DATA_FIRST_PULL_DOWN

   Internal state constant.

.. data:: STATE_DATA_PULL_UP

   Internal state constant.

.. data:: STATE_DATA_PULL_DOWN

   Internal state constant.

.. data:: MAX_UNCHANGE_COUNT

   Maximum number of unchanged signal reads before timing out.

**Usage Example**



.. code-block:: python

   from fusion_hat import DHT11
   from time import sleep

   dht11 = DHT11(pin=17)

   while True:
      result = dht11.read()
      if result:
         humidity, temperature = result
         print ("humidity: %s %%,  Temperature: %s C`" % (humidity, temperature))
      else:
         print("time out")
      sleep(1)

**Notes**



- Requires root or GPIO access on the Raspberry Pi.
- Uses ``RPi.GPIO`` internally.
- Results may be unstable if not given enough delay between reads (1–2 seconds recommended).

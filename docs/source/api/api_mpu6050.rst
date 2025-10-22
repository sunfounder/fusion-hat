MPU6050 Class
======================


The ``MPU6050`` class communicates with the MPU-6050 sensor over I2C using the ``smbus2`` library. It provides methods for reading acceleration, gyroscope, and temperature data, as well as setting configuration parameters such as filter and sensor ranges.



**Class: MPU6050**


.. class:: MPU6050(address=0x68, bus=1)

    Initializes the MPU-6050 sensor and wakes it from sleep mode.

    :param address: I2C address of the sensor (default is 0x68).
    :param bus: I2C bus number (default is 1).

**Methods**


.. method:: get_temp()

    Reads and returns the onboard temperature.

    :returns: Temperature in degrees Celsius.
    :rtype: float

.. method:: set_accel_range(accel_range)

    Sets the accelerometer range.

    :param accel_range: One of ACCEL_RANGE_2G, ACCEL_RANGE_4G, ACCEL_RANGE_8G, ACCEL_RANGE_16G.

.. method:: read_accel_range(raw=False)

    Reads the current accelerometer range.

    :param raw: If True, returns the raw register value. If False, returns the range in G.
    :returns: Accelerometer range (2, 4, 8, 16) or -1 on error.
    :rtype: int

.. method:: get_accel_data(g=False)

    Reads accelerometer data.

    :param g: If True, returns values in G. If False, returns values in m/s².
    :returns: List of [x, y, z] acceleration values.
    :rtype: list[float]

.. method:: set_gyro_range(gyro_range)

    Sets the gyroscope range.

    :param gyro_range: One of GYRO_RANGE_250DEG, GYRO_RANGE_500DEG, GYRO_RANGE_1000DEG, GYRO_RANGE_2000DEG.

.. method:: read_gyro_range(raw=False)

    Reads the current gyroscope range.

    :param raw: If True, returns the raw register value. If False, returns the range in degrees/sec.
    :returns: Gyroscope range (250, 500, 1000, 2000) or -1 on error.
    :rtype: int

.. method:: get_gyro_data()

    Reads gyroscope data.

    :returns: List of [x, y, z] rotation values in degrees/sec.
    :rtype: list[float]

.. method:: set_filter_range(filter_range=FILTER_BW_256)

    Sets the low-pass filter bandwidth.

    :param filter_range: One of the FILTER_BW_* constants.

.. method:: get_all_data()

    Reads and returns all sensor data.

    :returns: A list containing accelerometer data, gyroscope data, and temperature.
    :rtype: list

**Constants**


Predefined constants for sensor configuration:

- Accelerometer Ranges:
    - ACCEL_RANGE_2G
    - ACCEL_RANGE_4G
    - ACCEL_RANGE_8G
    - ACCEL_RANGE_16G

- Gyroscope Ranges:
    - GYRO_RANGE_250DEG
    - GYRO_RANGE_500DEG
    - GYRO_RANGE_1000DEG
    - GYRO_RANGE_2000DEG

- Filter Bandwidth:
    - FILTER_BW_256
    - FILTER_BW_188
    - FILTER_BW_98
    - FILTER_BW_42
    - FILTER_BW_20
    - FILTER_BW_10
    - FILTER_BW_5



**Usage Example**


.. code-block:: python

   from fusion_hat import MPU6050
   from time import sleep

   mpu = MPU6050()

   # mpu.set_accel_range(MPU6050.ACCEL_RANGE_2G)
   # mpu.set_gyro_range(MPU6050.GYRO_RANGE_250DEG)


   while True:
      temp = mpu.get_temp()
      acc_x, acc_y, acc_z  = mpu.get_accel_data()
      gyro_x, gyro_y, gyro_z = mpu.get_gyro_data()
      print(
         f"Temp: {temp:0.2f} 'C"
         f"  |  ACC: {acc_x:8.5f}g {acc_y:8.5f}g {acc_z:8.5f}g"
         f"  |  GYRO: {gyro_x:8.5f}deg/s {gyro_y:8.5f}deg/s {gyro_z:8.5f}deg/s"
      )
      sleep(0.2)
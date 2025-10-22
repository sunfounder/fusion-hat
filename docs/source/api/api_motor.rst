.. _class_motor:

Motor Class
===========

The ``Motor`` class controls a single DC motor using PWM and direction pins. It supports two operation modes:

- **Mode 1**: One PWM pin and one GPIO pin (TC1508S)
- **Mode 2**: Two PWM pins (TC618S)


**Initialization**


.. method:: __init__(*args, **kwargs)

   Initialize a motor driver.

   Supported parameter combinations:

      - ``motor='M0'`` to ``M3`` (predefined pins)
      - ``pwm``, ``dir`` (PWM + GPIO for mode 1)
      - ``pwm_a``, ``pwm_b`` (PWM + PWM for mode 2)

   :keyword str motor: Motor label ('M0'–'M3')
   :keyword PWM pwm: PWM object (mode 1)
   :keyword Pin dir: Direction GPIO pin (mode 1)
   :keyword PWM pwm_a: First PWM (mode 2)
   :keyword PWM pwm_b: Second PWM (mode 2)
   :keyword int mode: Motor mode (1 or 2)
   :keyword int freq: Frequency of PWM (default: 100)
   :keyword bool is_reversed: Whether the motor direction is reversed

**Motor Control**


.. method:: speed(speed=None)

   Set or get the motor speed.

   :param speed: Motor speed from -100.0 to 100.0
   :type speed: float
   :return: Current speed if no parameter given.
   :rtype: float

.. method:: set_is_reverse(is_reverse)

   Configure whether the motor direction is reversed.

   :param is_reverse: Reversed state
   :type is_reverse: bool

.. method:: stop()

   Stop the motor.

   :rtype: None


**Usage Examples**

.. code-block:: python

   from fusion_hat import Motor, PWM, Pin
   from time import sleep

   m0 = Motor("M0", is_reversed=True)
   m1 = Motor("M1", is_reversed=True)
   m2 = Motor("M2", is_reversed=False)
   m3 = Motor("M3", is_reversed=False)

   try:
      while True:
         m0.speed(-50)
         m1.speed(-50)
         m2.speed(-50)
         m3.speed(-50)
         sleep(1)
         m0.speed(50)
         m1.speed(50)
         m2.speed(50)
         m3.speed(50)
         sleep(1)
         m0.stop()
         m1.stop()
         m2.stop()
         m3.stop()
   finally:
      m0.stop()
      m1.stop()
      m2.stop()
      m3.stop()
      sleep(.1)


Motors Class
============

The ``Motors`` class manages a pair of DC motors (left and right), typically used for differential drive robots. It supports persistent configuration via a file.

**Initialization**


.. method:: __init__(db=config_file, *args, **kwargs)

   Initialize left and right motors using saved configuration.

   :param db: Path to the configuration file
   :type db: str

**Motor Access**



.. method:: __getitem__(key)

   Access motors by index (1 or 2).

   :param key: Motor ID (1 or 2)
   :type key: int
   :return: Motor instance
   :rtype: Motor



.. property:: left

   The left motor (based on saved config)

.. property:: right

   The right motor (based on saved config)





**Motor Configuration**

.. method:: set_left_id(id)

   Set and persist the motor to be used as left.

   :param id: Motor ID (1 or 2)
   :type id: int

.. method:: set_right_id(id)

   Set and persist the motor to be used as right.

   :param id: Motor ID (1 or 2)
   :type id: int

.. method:: set_left_reverse()

   Toggle and persist the reverse setting for the left motor.

   :return: New reverse state
   :rtype: bool

.. method:: set_right_reverse()

   Toggle and persist the reverse setting for the right motor.

   :return: New reverse state
   :rtype: bool

**Motion Control**


.. method:: speed(left_speed, right_speed)

   Set speed for both motors.

   :param left_speed: Left motor speed (-100.0 ~ 100.0)
   :param right_speed: Right motor speed (-100.0 ~ 100.0)
   :type left_speed: float
   :type right_speed: float

.. method:: forward(speed)

   Drive both motors forward.

   :param speed: Speed (-100.0 ~ 100.0)
   :type speed: float

.. method:: backward(speed)

   Drive both motors backward.

   :param speed: Speed (-100.0 ~ 100.0)
   :type speed: float

.. method:: turn_left(speed)

   Turn left in place.

   :param speed: Speed (-100.0 ~ 100.0)
   :type speed: float

.. method:: turn_right(speed)

   Turn right in place.

   :param speed: Speed (-100.0 ~ 100.0)
   :type speed: float

.. method:: stop()

   Stop both motors.

   :rtype: None

**Configuration File Format**


A sample configuration file (e.g. ``/opt/robot_hat/default_motors.config``) stores persistent settings:

.. code-block:: ini

   left = 1
   right = 2
   left_reverse = False
   right_reverse = True

**Usage Example**


.. code-block:: python

   from fusion_hat import Motors

   motors = Motors()
   motors.set_left_id(1)
   motors.set_right_id(2)
   motors.forward(80)
   time.sleep(2)
   motors.stop()


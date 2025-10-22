 .. note::

    Hello, welcome to the SunFounder Raspberry Pi & Arduino & ESP32 Enthusiasts Community on Facebook! Dive deeper into Raspberry Pi, Arduino, and ESP32 with fellow enthusiasts.

    **Why Join?**

    - **Expert Support**: Solve post-sale issues and technical challenges with help from our community and team.
    - **Learn & Share**: Exchange tips and tutorials to enhance your skills.
    - **Exclusive Previews**: Get early access to new product announcements and sneak peeks.
    - **Special Discounts**: Enjoy exclusive discounts on our newest products.
    - **Festive Promotions and Giveaways**: Take part in giveaways and holiday promotions.

    👉 Ready to explore and create with us? Click [|link_sf_facebook|] and join today!

.. _on_board_mcu:

On-Board MCU
=======================

The Fusion HAT+ comes with an GD32E203C8T6 microcontroller. 
It is an ARM Cortex-M23 processor with a maximum clock frequency of 72MHz. 
The microcontroller has 64KB of Flash memory and 8KB of SRAM.

The onboard PWM and ADC are driven by the microcontroller. 
Communication between the Raspberry Pi and the microcontroller is established via the I2C interface. 
**The I2C address used for communication is 0x17.**



ADC
-----------------------

Register addresses is 1 byte, 0x10 to 0x19 are ADC channels 0 to 3.
The ADC precision is 12 bit, and the value is 0 to 4095.
See more details in :py:class:`fusion_hat.ADC`.


.. table::

    +-------------------+-------------------------------+
    |     Address       | Description                   |
    +===================+===============================+
    |     ``0x10``      | ADC channel 0 H               |
    +-------------------+-------------------------------+
    |     ``0x11``      | ADC channel 0 L               |
    +-------------------+-------------------------------+
    |     ``0x12``      | ADC channel 1 H               |
    +-------------------+-------------------------------+
    |     ``0x13``      | ADC channel 1 L               |
    +-------------------+-------------------------------+
    |     ``0x14``      | ADC channel 2 H               |
    +-------------------+-------------------------------+
    |     ``0x15``      | ADC channel 2 L               |
    +-------------------+-------------------------------+
    |     ``0x16``      | ADC channel 3 H               |
    +-------------------+-------------------------------+
    |     ``0x17``      | ADC channel 3 L               |
    +-------------------+-------------------------------+
    |     ``0x18``      | ADC 4 H  (Battery Level)      |
    +-------------------+-------------------------------+
    |     ``0x19``      | ADC channel 4 L               |
    +-------------------+-------------------------------+

**Example:**

Read Channel 0 ADC value:

.. code-block:: python

    from smbus import SMBus
    bus = SMBus(1)

    # read 16 bits (2 bytes) data from register 0x10 and 0x11 
    val = bus.read_i2c_block_data(0x17, 0x10, 2)
    msb = val[0]
    lsb = val[1]
    value = (msb << 8) | lsb


PWM
-----------------------


Changing PWM Frequency
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Frequency is defined with prescaler and period.

To set frequency first you need to define the period you want.
Like on Arduino, normaly is 255, or like PCA9685 is 4095.

CPU clock is 72MHz, Then you can calculate the prescaler from your desire frequency

    prescaler = 72MHz / (Period + 1) / Frequency - 1

Or if you don't care about the period, there's a way to calculate both period and prescaler from
frequency. See :py:func:`fusion_hat.PWM.freq`.


Pulse width
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To control the channel pulse width is rather simple, just write the value to the register.

**But** what is the value? If you want to set the PWM to 50% pulse width, you need to know
exactly what the period is. Base on the above calculation, if you set the period to 4095,
then set pulse value to 2048 is about 50% pulse width.

.. table::

    +-------------------+--------------------+-------------------+--------------------+
    | Address           | Description        | Address           | Description        |
    +===================+====================+===================+====================+
    | ``0x60``          | PWM0_CCR_H         | ``0x6C``          | PWM6_CCR_H         |
    +-------------------+--------------------+-------------------+--------------------+
    | ``0x61``          | PWM0_CCR_L         | ``0x6D``          | PWM6_CCR_L         |
    +-------------------+--------------------+-------------------+--------------------+
    | ``0x62``          | PWM1_CCR_H         | ``0x6E``          | PWM7_CCR_H         |
    +-------------------+--------------------+-------------------+--------------------+
    | ``0x63``          | PWM1_CCR_L         | ``0x6F``          | PWM7_CCR_L         |
    +-------------------+--------------------+-------------------+--------------------+
    | ``0x64``          | PWM2_CCR_H         | ``0x70``          | PWM8_CCR_H         |
    +-------------------+--------------------+-------------------+--------------------+
    | ``0x65``          | PWM2_CCR_L         | ``0x71``          | PWM8_CCR_L         |
    +-------------------+--------------------+-------------------+--------------------+
    | ``0x66``          | PWM3_CCR_H         | ``0x72``          | PWM9_CCR_H         |
    +-------------------+--------------------+-------------------+--------------------+
    | ``0x67``          | PWM3_CCR_L         | ``0x73``          | PWM9_CCR_L         |
    +-------------------+--------------------+-------------------+--------------------+
    | ``0x68``          | PWM4_CCR_H         | ``0x74``          | PWM10_CCR_H        |
    +-------------------+--------------------+-------------------+--------------------+
    | ``0x69``          | PWM4_CCR_L         | ``0x75``          | PWM10_CCR_L        |
    +-------------------+--------------------+-------------------+--------------------+
    | ``0x6A``          | PWM5_CCR_H         | ``0x76``          | PWM11_CCR_H        |
    +-------------------+--------------------+-------------------+--------------------+
    | ``0x6B``          | PWM5_CCR_L         | ``0x77``          | PWM11_CCR_L        |
    +-------------------+--------------------+-------------------+--------------------+



Prescaler
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Register from 0x40 is to set the PWM prescaler. ranges from 0~65535.
There are 7 timers for all channels. See :ref:`pwm_timer`

.. table::

    +-------------------+---------------------+
    | Address           | Description         |
    +===================+=====================+
    | ``0x40``          | PWM_TIM0_PSC_H      |
    +-------------------+---------------------+
    | ``0x41``          | PWM_TIM0_PSC_L      |
    +-------------------+---------------------+
    | ``0x42``          | PWM_TIM1_PSC_H      |
    +-------------------+---------------------+
    | ``0x43``          | PWM_TIM1_PSC_L      |
    +-------------------+---------------------+
    | ``0x44``          | PWM_TIM2_PSC_H      |
    +-------------------+---------------------+
    | ``0x45``          | PWM_TIM2_PSC_L      |
    +-------------------+---------------------+



Period
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Register from 0x44 is to set the PWM period. ranges from 0~65535.
There are only 7 timers for all channels. See :ref:`pwm_timer`

.. table::

    +-------------------+---------------------+
    | Address           | Description         |
    +===================+=====================+
    | ``0x50``          | PWM_TIM0_ARR_H      |
    +-------------------+---------------------+
    | ``0x51``          | PWM_TIM0_ARR_L      |
    +-------------------+---------------------+
    | ``0x52``          | PWM_TIM1_ARR_H      |
    +-------------------+---------------------+
    | ``0x53``          | PWM_TIM1_ARR_L      |
    +-------------------+---------------------+
    | ``0x54``          | PWM_TIM2_ARR_H      |
    +-------------------+---------------------+
    | ``0x55``          | PWM_TIM2_ARR_L      |
    +-------------------+---------------------+


.. _pwm_timer:

PWM Timer
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

What is PWM Timer? PWM Timer is a tool to turn on and off the PWM channel for you.

The MCU only have 3 timers for PWM: **which means you cannot set frequency on different channels at with the same timer**.

Example: if you set frequency on channel 0, channel 1, 2, 3 will be affected.
If you change channel 2 frequency, channel 0, 1, 3 will be override.

This happens like if you want to control both a passive buzzer (who changes frequency all the time) and servo (who needs a fix frequency of 50Hz). Then you should seperate them into two different timer.

.. table::

    +---------------+-------------------+
    | Timer         | PWM Channel       |
    +===============+===================+
    | Timer 0       | 0, 1, 2, 3        |
    +---------------+-------------------+
    | Timer 1       | 4, 5, 6, 7        |
    +---------------+-------------------+
    | Timer 2       | 8, 9, 10, 11      |
    +---------------+-------------------+



Set PWM Timer
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


.. code-block:: python

    from smbus import SMBus
    bus = SMBus(1)

    # Set timer 0 period to 4095
    bus.write_word_data(0x17, 0x50, 4095)
    # Set frequency to 50Hz,
    freq = 50
    # Calculate prescaler
    prescaler = int(72000000 / (4095 + 1) / freq) - 1
    # Set prescaler
    bus.write_word_data(0x17, 0x40, prescaler)
    
    # Set channel 0 to 50% pulse width
    bus.write_word_data(0x17, 0x60, 2048)



Charging Status
--------------------------


.. table::

    +-------------------+-------------------------------+
    |     Address       | Value                         |
    +===================+===============================+
    |     ``0x25``      | 0: Not Change                 |
    +-------------------+-------------------------------+
    |                   | 1: Changing                   |
    +-------------------+-------------------------------+



.. _safe_shutdown:

Safe Shutdown
--------------------------

The Fusion HAT+ includes a built-in safe shutdown mechanism. It performs a software-based shutdown by reading the microcontroller’s register status via I2C.

.. table::

    +-------------------+---------------------------------------+
    |     Address       | Value                                 |
    +===================+=======================================+
    |     ``0x26``      | 0: No request                         |
    +-------------------+---------------------------------------+
    |                   | 1: Low battery, shutdown requested.   |
    +-------------------+---------------------------------------+
    |                   | 2: Shutdown requested by power button.|
    +-------------------+---------------------------------------+

This feature is automatically enabled during installation of the ``fusion-hat`` library. 
The necessary code is set up to run at startup, so no additional configuration is required.


**Configuring Raspberry Pi Shutdown Signal**

Once configured, when the Raspberry Pi shuts down, a specific pin changes its voltage level. Fusion HAT+ detects this and cuts power to the Pi safely.


For Raspberry Pi 4B / 5:

    * Use a jumper to connect ``RPI_STATE`` on the HAT to 3V3.

    * Configure the Raspberry Pi EEPROM to disable IO power on shutdown. When the Pi shuts down, its 3.3V pin goes LOW, triggering the power cut.

    Run the following command to edit EEPROM settings:

    .. code-block:: bash

        sudo rpi-eeprom-config -e

    Set the ``POWER_OFF_ON_HALT`` value to 1:

    .. code-block:: bash

        POWER_OFF_ON_HALT=1


For other Raspberry Pi models:

    * Use a jumper to connect ``RPI_STATE`` on the HAT to GPIO26.

    * Edit the Raspberry Pi's ``/boot/firmware/config.txt`` file:

    .. code-block:: bash

        sudo nano /boot/firmware/config.txt
    
    Add the following line at the end of the file to set GPIO26 HIGH on boot and LOW on shutdown:

    .. code-block:: bash
        
        dtoverlay=gpio-poweroff,gpio_pin=26, active_low=1



ISP Programming Interface
---------------------------

A row of six unpopulated pads used for flashing the MCU firmware, providing power, communication, boot mode selection, and reset functionality.

* VCC/GND: Supplies power to the programmer.
* RX/TX: Reserved for future functionality.
* BOOT0: Pull high to enter bootloader mode; pull low for normal operation.
* Reset (RST): Short to GND to manually reset the MCU.
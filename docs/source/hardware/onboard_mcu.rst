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
See more details in :py:class:`fusion_hat.adc.ADC`.


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

.. **Example:**

.. Read Channel 0 ADC value:

.. .. code-block:: python

..     from smbus import SMBus
..     bus = SMBus(1)

..     # read 16 bits (2 bytes) data from register 0x10 and 0x11 
..     val = bus.read_i2c_block_data(0x17, 0x10, 2)
..     msb = val[0]
..     lsb = val[1]
..     value = (msb << 8) | lsb


PWM
-----------------------

Frequency and Period Settings
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The PWM frequency is determined by the period value (ARR) and the prescaler (PSC). The principle is that the microcontroller’s internal clock runs at 72 MHz. Through prescaling, the clock is divided to obtain a frequency Fp, which is then further divided by the period count to get the PWM output frequency F. Therefore,  

.. code-block::

    F = 72,000,000 / (PSC + 1) / (ARR + 1)

In general, by specifying the desired frequency and period, you can calculate the required prescaler.  
For example, to drive a servo motor, you need a 50 Hz frequency and a desired resolution of 12 bits (i.e., a period of 2¹² = 4096). The prescaler PSC can be calculated as:  

.. code-block::

    PSC = 72,000,000 / F / (ARR + 1) - 1  
    = 72,000,000 / 50 / (4095 + 1) - 1  
    = 350.5625  
    ≈ 351  

Since PSC must be an integer, it is approximated to 351. Therefore, by setting PSC = 351 and ARR = 4096, you get an actual PWM frequency of:  

.. code-block::

    72,000,000 / 352 / 4096 = 49.937 Hz ≈ 50 Hz.  

By default, the PWM prescaler (PSC) and period (ARR) are set to 351 and 4095, respectively, resulting in a default frequency of approximately 50 Hz.

The pulse width corresponds to the duty cycle value within the period.  
For example, with the configuration above where the period (ARR) is 4096, setting the pulse width (CCR) to 2048 yields a 50% PWM output.  

.. code-block::

    Duty Cycle = CCR / (ARR + 1)

Pulse width
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To control the channel pulse width is rather simple, just write the value to the register.

**But** what is the value? If you want to set the PWM to 50% pulse width, you need to know
exactly what the period is. Base on the above calculation, if you set the period to 4095,
then set pulse value to 2048 is about 50% pulse width.

.. list-table::
   :header-rows: 1
   :widths: 20 30 20 30

   * - Address
     - Description
     - Address
     - Description
   * - ``0x60``
     - PWM0_CCR_H
     - ``0x6C``
     - PWM6_CCR_H
   * - ``0x61``
     - PWM0_CCR_L
     - ``0x6D``
     - PWM6_CCR_L
   * - ``0x62``
     - PWM1_CCR_H
     - ``0x6E``
     - PWM7_CCR_H
   * - ``0x63``
     - PWM1_CCR_L
     - ``0x6F``
     - PWM7_CCR_L
   * - ``0x64``
     - PWM2_CCR_H
     - ``0x70``
     - PWM8_CCR_H
   * - ``0x65``
     - PWM2_CCR_L
     - ``0x71``
     - PWM8_CCR_L
   * - ``0x66``
     - PWM3_CCR_H
     - ``0x72``
     - PWM9_CCR_H
   * - ``0x67``
     - PWM3_CCR_L
     - ``0x73``
     - PWM9_CCR_L
   * - ``0x68``
     - PWM4_CCR_H
     - ``0x74``
     - PWM10_CCR_H
   * - ``0x69``
     - PWM4_CCR_L
     - ``0x75``
     - PWM10_CCR_L
   * - ``0x6A``
     - PWM5_CCR_H
     - ``0x76``
     - PWM11_CCR_H
   * - ``0x6B``
     - PWM5_CCR_L
     - ``0x77``
     - PWM11_CCR_L


Prescaler
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Registers from 0x40 are used to set the PWM prescaler (range: 0–65535).

.. list-table::
   :header-rows: 1
   :widths: 20 40

   * - Address
     - Description
   * - ``0x40``
     - PWM_TIM0_PSC_H
   * - ``0x41``
     - PWM_TIM0_PSC_L
   * - ``0x42``
     - PWM_TIM1_PSC_H
   * - ``0x43``
     - PWM_TIM1_PSC_L
   * - ``0x44``
     - PWM_TIM2_PSC_H
   * - ``0x45``
     - PWM_TIM2_PSC_L


Period
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Registers from 0x50 are used to set the PWM period (range: 0–65535).

.. list-table::
   :header-rows: 1
   :widths: 20 40

   * - Address
     - Description
   * - ``0x50``
     - PWM_TIM0_ARR_H
   * - ``0x51``
     - PWM_TIM0_ARR_L
   * - ``0x52``
     - PWM_TIM1_ARR_H
   * - ``0x53``
     - PWM_TIM1_ARR_L
   * - ``0x54``
     - PWM_TIM2_ARR_H
   * - ``0x55``
     - PWM_TIM2_ARR_L


Button and LED Control
---------------------------

.. list-table::
   :header-rows: 1
   :widths: 20 10 70

   * - Item
     - Address
     - Description
   * - **USR Button (r/-)**
     - 0x24
     - Read the level state of the USR button:

       0: Low level 

       1: High level
   * - **LED (r/w)**
     - 0x30
     - Read or control the LED:

       0: off

       1: on

       2: toggle

Buzzer Switch Control
-----------------------------

.. list-table::
   :header-rows: 1
   :widths: 20 10 70

   * - Item
     - Address
     - Description
   * - **Buzzer Switch (r/w)**
     - 0x31
     - Read or control the buzzer switch:

       0: off

       1: on


Servo Zeroing
-----------------------

* When you press the button twice, all the PWM signals will be set to 1500us pulse, 20000us period. That is, the servo will be in the middle position. You should secure the servo arm to the servo in this state.
* Press the button twice again, all the PWM signals will be set to 0 pulse.

.. _charging_status:

Charging Status
----------------------

.. list-table::
   :header-rows: 1
   :widths: 20 60

   * - Address
     - Value
   * - ``0x25``
     - 0: Not Charging 

       1: Charging


.. _safe_shutdown:

Safe Shutdown
-----------------------

The Fusion HAT+ includes a built-in safe shutdown mechanism. It performs a software-based shutdown by reading the microcontroller’s register status via I2C.

.. list-table::
   :header-rows: 1
   :widths: 20 60

   * - Address
     - Value
   * - ``0x26``
     - 0: No request 

       1: Low battery, shutdown requested 

       2: Shutdown requested by power button

To configure the Raspberry Pi shutdown signal, please refer to :ref:`shutdown_behavior` for detailed instructions.


.. ISP Programming Interface
.. ---------------------------

.. A row of six unpopulated pads used for flashing the MCU firmware, providing power, communication, boot mode selection, and reset functionality.

.. * VCC/GND: Supplies power to the programmer.
.. * RX/TX: Reserved for future functionality.
.. * BOOT0: Pull high to enter bootloader mode; pull low for normal operation.
.. * Reset (RST): Short to GND to manually reset the MCU.
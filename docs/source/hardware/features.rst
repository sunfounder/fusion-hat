 .. note::

    Hello, welcome to the SunFounder Raspberry Pi & Arduino & ESP32 Enthusiasts Community on Facebook! Dive deeper into Raspberry Pi, Arduino, and ESP32 with fellow enthusiasts.

    **Why Join?**

    - **Expert Support**: Solve post-sale issues and technical challenges with help from our community and team.
    - **Learn & Share**: Exchange tips and tutorials to enhance your skills.
    - **Exclusive Previews**: Get early access to new product announcements and sneak peeks.
    - **Special Discounts**: Enjoy exclusive discounts on our newest products.
    - **Festive Promotions and Giveaways**: Take part in giveaways and holiday promotions.

    👉 Ready to explore and create with us? Click [|link_sf_facebook|] and join today!

Features
==============

    * Shutdown Current: 40mA
    * Power Input: USB Type-C, 5V/3A
    * Charging Power: 7.4V/1.5A 15W
    * Output Power: 5V/5A, 3.3V/1A
    * Included Batteries: 2 x 3.7V 18650 Lithium-ion Batteries, XH2.54 3P Interface
    * Battery Protection: Reverse polarity protection
    * Charging Protection: Input undervoltage protection, input overvoltage protection, charging balance, overheat protection
    * Onboard Power Indicator Light: PWR
    * Onboard 2 Battery Level Indicator LEDs
    * Onboard User LED, 2 tactile switches
    * Motor Driver: 5V/1.8A x 4
    * 4-channel 12-bit ADC
    * 12-channel PWM (8-channel shared with motor)
    * 4-channel digital signals
    * Onboard SPI interface, UART interface, I2C interface, WS2812 interface
    * Mono Speaker: 4Ω2.5W
    * Power Button: Safe shutdown
    * Microphone: Onboard I2S microphone


Compatibility and Power Notes
------------------------------------------------------------

The **Fusion HAT+** supports a wide range of commonly used servos and DC motors, including:

* **Micro servos:** SG90, MG90S
* **Standard servos:** MG996R, DS3218
* **SunFounder custom servos**
* **Low-current DC motors:** 130 series, N20 series
* **SunFounder custom DC motors** with **XH2.54 2-pin connectors**

**Servo Power (PWM Interface)**

The PWM interface provides up to **5V/5A** maximum output, which is shared with the Raspberry Pi.

* When connecting multiple servos, carefully account for their current draw.
* If the total servo current exceeds 5A, use an **external power supply (BEC)** to avoid overload and ensure stable operation.

**DC Motor Power**

DC motors are powered **directly from the onboard batteries (6–8.4V)**.

* Each motor channel supports up to **1.8A maximum current**.
* Do **not** connect motors with higher current requirements, as this may damage the motor driver chip.

Electrical Characteristics
-----------------------------------

.. list-table:: Electrical Characteristics
   :widths: 50 25 25 25 25
   :header-rows: 1

   * - Parameters:
     - Minimum Value:
     - Typical Value:
     - Maximum Value:
     - Unit:
   * - Input Voltage:
     - 4.25
     - 5
     - 8.4
     - V
   * - Battery Input Voltage:
     - 6.0
     - 7.4
     - 8.4
     - V
   * - Overcharge Protection (Battery):
     -
     - 8.4
     -
     - V
   * - Input Undervoltage Protection:
     - 4.15
     - 4.25
     - 4.35
     - V
   * - Input Overvoltage Protection:
     - 8.3
     - 8.4
     - 8.5
     - V
   * - Charging Current (5V):
     -
     -
     - 1.5
     - A
   * - Output Current (5V):
     -
     -
     - 5.0
     - A
   * - Output Voltage:
     - 5.197
     - 5.285
     - 5.376
     - V
   * - Charging Overheat Protection:
     - 125
     - 135
     - 145
     - °C
   * - DC-DC Overheat Protection:
     - 
     - 
     - 150
     - °C
   * - Motor Output Current:  
     -
     -
     - 1.8
     - A  
   * - Overdischarge Protectiont:  
     -
     - 6
     - 
     - V   
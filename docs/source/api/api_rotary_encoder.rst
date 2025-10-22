Rotary_Encoder Class
===========================


The ``Rotary_Encoder`` class enables interaction with a rotary encoder using two GPIO pins: one for the A (CLK) signal and one for the B (DT) signal. It keeps track of the rotation steps and allows registering a callback function for real-time response to changes.


**Class: Rotary_Encoder**


.. class:: Rotary_Encoder(clk, dt)

    Initializes a rotary encoder.

    :param clk: Pin identifier for the A signal (CLK).
    :type clk: str or int (depending on platform)
    :param dt: Pin identifier for the B signal (DT).
    :type dt: str or int (depending on platform)

    :ivar position: The current step count of the encoder.
    :vartype position: int
    :ivar when_rotated: A user-defined callback function that is executed when the encoder is rotated.
    :vartype when_rotated: Callable or None

**Methods**

.. method:: update()

    Callback function triggered by changes on the A signal (usually the rising edge).
    Determines the direction of rotation and updates the position counter.
    Automatically called via interrupt.

.. method:: steps()

    Returns the current position of the rotary encoder.

    :return: The current step count.
    :rtype: int

.. method:: reset()

    Resets the step counter to zero.

    :rtype: None

**Attributes**



.. attribute:: when_rotated

    Optional user-supplied callback function called every time the encoder is rotated.

    :type: Callable or None



**Example Usage**



.. code-block:: python

    from fusion_hat import Rotary_Encoder
    from signal import pause  # Import pause function from signal module

    encoder = Rotary_Encoder(clk=17, dt=4)  # Rotary Encoder connected to GPIO pins 17 (CLK) and 4 (DT)

    def rotary_change():
        """ Update the counter based on the rotary encoder's rotation. """
        print('Counter =', encoder.steps())  # Display current counter value

    encoder.when_rotated = rotary_change  # Call the function when the rotary encoder is rotated

    print("CTRL + C to exit")
    pause()
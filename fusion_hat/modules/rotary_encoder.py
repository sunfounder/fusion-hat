from ..pin import Pin

class Rotary_Encoder:
    def __init__(self, clk, dt):
        """
        Initialize the rotary encoder.
        :param clk: GPIO pin for A signal (CLK)
        :param dt: GPIO pin for B signal (DT)
        """
        self.pin_a = Pin(clk, Pin.IN, Pin.PULL_UP)  # Set A pin as input
        self.pin_b = Pin(dt, Pin.IN, Pin.PULL_UP)  # Set B pin as input

        self.position = 0  # Store the current position
        self.last_state = self.pin_a.value()  # Store the last state of A pin

        self.when_rotated = None  # External callback function for rotation events

        # Set up an interrupt on the rising edge of A signal
        self.pin_a.when_activated = self.update

    def update(self):
        """
        Callback function triggered when A signal changes (rising edge).
        Determines the rotation direction and updates the position.
        """
        if self.pin_b.value() == 0:
            self.position += 1  # Clockwise rotation
        else:
            self.position -= 1  # Counterclockwise rotation

        # print(f"Rotary_Encoder Position: {self.position}")

        # If an external callback function is set, execute it
        if self.when_rotated:
            self.when_rotated()

    def steps(self):
        """
        Get the current position value.
        :return: The current step count.
        """
        return self.position

    def reset(self):
        """ Reset the encoder position to zero. """
        self.position = 0

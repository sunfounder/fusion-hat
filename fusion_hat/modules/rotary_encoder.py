from ..pin import Pin

class Rotary_Encoder:
    def __init__(self, clk, dt, *, bounce_time=0.002, reverse=False):
        """
        Initialize a rotary encoder using fusion_hat.Pin

        :param clk: GPIO pin number for channel A (CLK)
        :param dt:  GPIO pin number for channel B (DT)
        :param bounce_time: Debounce time (seconds) for internal interrupt filtering
        :param reverse: True to reverse the counting direction
        """
        # Must use keyword arguments for mode and pull, otherwise setup() won't be called
        self.pin_a = Pin(clk, mode=Pin.IN, pull=Pin.PULL_UP, bounce_time=bounce_time)
        self.pin_b = Pin(dt,  mode=Pin.IN, pull=Pin.PULL_UP, bounce_time=bounce_time)

        self.position = 0
        self.reverse = -1 if reverse else 1

        # External callback: triggered whenever a valid rotation occurs
        # Compatible with two signatures:
        #   when_rotated()
        #   when_rotated(direction, position)
        self.when_rotated = None

        # Bind both rising and falling edges on channel A
        self.pin_a.when_activated = self._a_rising
        self.pin_a.when_deactivated = self._a_falling

    # --- Edge handlers ---

    def _a_rising(self):
        """
        Called on rising edge of channel A.
        Read channel B to determine rotation direction.
        Typical rule:
            A↑ with B=0 -> CW (+1)
            A↑ with B=1 -> CCW (-1)
        """
        direction = +1 if self.pin_b.value() == 0 else -1
        self._apply(direction)

    def _a_falling(self):
        """
        Called on falling edge of channel A.
        Read channel B to determine rotation direction.
        Typical rule:
            A↓ with B=1 -> CW (+1)
            A↓ with B=0 -> CCW (-1)
        """
        direction = +1 if self.pin_b.value() == 1 else -1
        self._apply(direction)

    def _apply(self, direction: int):
        """
        Apply one step of rotation, considering direction and reverse flag.
        Then invoke the external callback if set.
        """
        direction *= self.reverse
        self.position += direction

        if self.when_rotated:
            try:
                # New-style callback: when_rotated(direction, position)
                self.when_rotated(direction, self.position)
            except TypeError:
                # Backward-compatible: when_rotated()
                self.when_rotated()

    # --- Public API ---

    def steps(self):
        """
        Return the current step count.
        """
        return self.position

    def reset(self):
        """
        Reset the encoder position to zero.
        """
        self.position = 0

    def close(self):
        """
        Release interrupts and clean up GPIO resources.
        """
        try:
            self.pin_a.when_activated = None
            self.pin_a.when_deactivated = None
        except Exception:
            pass
        try:
            self.pin_a.close()
        except Exception:
            pass
        try:
            self.pin_b.close()
        except Exception:
            pass

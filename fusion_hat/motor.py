""" Motor

This module provides a class for controlling motors on the Fusion Hat.

Example:

    Simple usage

    >>> from fusion_hat.motor import Motor
    >>> motor = Motor('M0', is_reversed=False)
    >>> motor.set_power(50)

    Change the direction of the motor.

    >>> motor.set_is_reverse(True)
    >>> motor.set_power(50)

    Spin the motor in the other direction.

    >>> motor.set_power(-50)

    Stop the motor

    >>> motor.stop()
"""

from .pwm import PWM
from ._utils import mapping
from ._base import _Base
from .device import raise_if_fusion_hat_not_ready

class Motor(_Base):
    """ Motor class

    There are two ways to initialize a motor:

    Method 1: Pass a motor name as a string.

    Args:
        motor (str): Motor name
    
    Method 2: Pass two pwm pins as PWM objects.

    Args:
        pwm_a (fusion_hat.pwm.PWM): Motor speed control pwm pin a
        pwm_b (fusion_hat.pwm.PWM): Motor speed control pwm pin b
    """

    DEFAULT_FREQ = 100 # Hz
    """Default PWM frequency"""
    DEFAULT_MAX = 100 # %
    """Default maximum motor power"""
    DEFAULT_MIN = 0 # %
    """Default minimum motor power"""

    MOTOR_PINS = {
        'M0': ['P11', 'P10'],
        'M1': ['P9', 'P8'],
        'M2': ['P6', 'P7'],
        'M3': ['P4', 'P5']
    }
    """Motor pins"""

    def __init__(self, *args, **kwargs) -> None:
        raise_if_fusion_hat_not_ready()

        self.motor = None
        self.pwm_a = None
        self.pwm_b = None

        args = list(args)
        if len(args) == 1:
            self.motor = args.pop()

        elif len(args) == 2:
            self.pwm_a = args.pop(0)
            self.pwm_b = args.pop(1)
        
        super().__init__(*args, **kwargs)

        self.freq = kwargs.get('freq', self.DEFAULT_FREQ)
        self.max = kwargs.get('max', self.DEFAULT_MAX)
        self.min = kwargs.get('min', self.DEFAULT_MIN)
        self.is_reversed = kwargs.get('is_reversed', False)

        if self.motor != None:
            if self.motor not in ['M0', 'M1', 'M2', 'M3']:
                raise ValueError("motor must be 'M0', 'M1', 'M2', 'M3'")
            self.pwm_a = PWM(self.MOTOR_PINS[self.motor][0], *args, **kwargs)
            self.pwm_b = PWM(self.MOTOR_PINS[self.motor][1], *args, **kwargs)

        if not isinstance(self.pwm_a, PWM):
            raise TypeError("pin_a must be a class PWM")
        if not isinstance(self.pwm_b, PWM):
            raise TypeError("pin_b must be a class PWM")

        self.pwm_a.freq(self.freq)
        self.pwm_a.pulse_width_percent(0)
        self.pwm_b.freq(self.freq)
        self.pwm_b.pulse_width_percent(0)

        self._power = 0

    # Deprecated
    def speed(self, power: float = None) -> None:
        """ [DEPRECATED] Get or set motor power

        Args:
            power (float, optional): Motor power(-100.0~100.0). Defaults to None.
        """
        print(f"WARNING: Motor.speed() is deprecated, please use Motor.power() instead")
        self.power(power)

    def power(self, power: float = None) -> None:
        """ Get or set motor power

        Args:
            power (float, optional): Motor power(-100.0~100.0). Defaults to None.
        """
        if power is None:
            return self._power

        dir = 1 if power > 0 else 0
        if self.is_reversed:
            dir = dir ^ 1 # XOR
        power = abs(power)
        self._power = power
        if power > 0:
            power = mapping(power, 0, 100, self.min, self.max)
            power = int(power)

        if dir == 1:
            self.pwm_a.pulse_width_percent(power)
            self.pwm_b.pulse_width_percent(0)
        else:
            self.pwm_a.pulse_width_percent(0)
            self.pwm_b.pulse_width_percent(power)

    def set_is_reverse(self, is_reverse: bool) -> None:
        """ Set motor is reversed or not

        Args:
            is_reverse (bool): True or False
        """
        self.is_reversed = is_reverse

    def stop(self) -> None:
        """Stop motor"""
        self.power(0)

#!/usr/bin/env python3
from .basic import _Basic_class
from .pwm import PWM
from .utils import mapping

class Motor(_Basic_class):
    """Motor"""
    PERIOD = 4095
    PRESCALER = 10
    DEFAULT_FREQ = 100 # Hz
    DEFAULT_MAX = 100 # %
    DEFAULT_MIN = 0 # %

    DEFAULT_MOTOR_PINS = {
        'M0': ['P11', 'P10'],
        'M1': ['P9', 'P8'],
        'M2': ['P6', 'P7'],
        'M3': ['P4', 'P5']
    }

    def __init__(self, *args, **kwargs):
        """
        Initialize a motor

        :param pwm: Motor speed control pwm pin
        :type pwm: fusion_hat.pwm.PWM
        :param dir: Motor direction control pin
        :type dir: fusion_hat.pin.Pin
        """

        self.motor = None
        self.pwm_a = None
        self.pwm_b = None

        if len(args) == 1:
            self.motor = args[0]
        elif len(args) == 2:
            self.pwm_a = args[0]
            self.pwm_b = args[1]

        self.freq = kwargs.get('freq', self.DEFAULT_FREQ)
        self.max = kwargs.get('max', self.DEFAULT_MAX)
        self.min = kwargs.get('min', self.DEFAULT_MIN)
        self.is_reversed = kwargs.get('is_reversed', False)

        if self.motor != None:
            if self.motor not in ['M0', 'M1', 'M2', 'M3']:
                raise ValueError("motor must be 'M0', 'M1', 'M2', 'M3'")
            self.pwm_a = PWM(self.DEFAULT_MOTOR_PINS[self.motor][0])
            self.pwm_b = PWM(self.DEFAULT_MOTOR_PINS[self.motor][1])

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
    def speed(self, power=None):
        print(f'[WARNING] Motor.speed is deprecated, use Motor.power instead')
        self.power(power)

    def power(self, power=None):
        """
        Get or set motor power

        :param power: Motor power(-100.0~100.0)
        :type power: float
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

    def set_is_reverse(self, is_reverse):
        """
        Set motor is reversed or not

        :param is_reverse: True or False
        :type is_reverse: bool
        """
        self.is_reversed = is_reverse

    def stop(self):
        """Stop motor"""
        self.power(0)

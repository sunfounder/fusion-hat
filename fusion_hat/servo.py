#!/usr/bin/env python3
from .pwm import PWM
from ._utils import mapping, constrain
from typing import Optional

class Servo(PWM):
    """ Servo motor class """
    MAX_PW = 2500
    MIN_PW = 500
    FREQ = 50
    PERIOD = 4095

    def __init__(self, channel: int, address: Optional[str]=None, offset: Optional[float]=0.0, min: Optional[float]=-90, max: Optional[float]=90, *args, **kwargs):
        """ Initialize the servo motor class

        Args:
            channel (int/str): PWM channel number(0-14/P0-P14)
            address (str, optional): I2C address(0x17), leave it None to use default address, defaults to None
            offset (float, optional): offset value(-20.0~20.0), leave it None to use default offset, defaults to 0.0
        """
        super().__init__(channel, address, *args, **kwargs)
        self.period(self.PERIOD)
        self._offset = offset
        prescaler = self.CLOCK / self.FREQ / self.PERIOD
        self.prescaler(prescaler)
        self._angle = 0
        self._min = min
        self._max = max

    def offset(self, offset: Optional[float]=None) -> float:
        """ Set the offset of the servo motor

        Args:
            offset (float, optional): offset value(-20.0~20.0), leave it None to get the offset value, defaults to None

        Returns:
            float: offset value(-20.0~20.0) if offset is None, else None
        """
        if offset is None:
            return self._offset
        offset = constrain(offset, -20.0, 20.0)
        self._offset = offset
        return self._offset

    def angle(self, angle: Optional[float]=None) -> float:
        """ Get or set the angle of the servo motor

        Args:
            angle (float, optional): angle(-90~90), leave it None to get the angle value, defaults to None

        Returns:
            float: angle(-90~90) if angle is None, else None
        """
        if angle is None:
            return self._angle
        angle = constrain(angle, self._min, self._max)
        self._angle = angle
        calibrated_angle = angle + self._offset
        return self.set_raw_angle(calibrated_angle)

    def set_raw_angle(self, angle: float) -> None:
        """ Set the angle of the servo motor

        Args:
            angle (float): angle(-90~90)

        Raises:
            ValueError: angle value should be int or float value
        """
        if not (isinstance(angle, int) or isinstance(angle, float)):
            raise ValueError(
                "Angle value should be int or float value, not %s" % type(angle))
        angle = constrain(angle, -90, 90)
        pulse_width_time = mapping(angle, -90, 90, self.MIN_PW, self.MAX_PW)
        self.pulse_width_time(pulse_width_time)

    def pulse_width_time(self, pulse_width_time: float) -> None:
        """ Set the pulse width of the servo motor

        Args:
            pulse_width_time (float): pulse width time(500~2500)

        Raises:
            ValueError: pulse width time value should be int or float value
        """
        if not (isinstance(pulse_width_time, int) or isinstance(pulse_width_time, float)):
            raise ValueError(
                "Pulse width time value should be int or float value, not %s" % type(pulse_width_time))
        if pulse_width_time > self.MAX_PW:
            pulse_width_time = self.MAX_PW
        if pulse_width_time < self.MIN_PW:
            pulse_width_time = self.MIN_PW

        pwr = pulse_width_time / 20000
        value = int(pwr * self.PERIOD)
        self.pulse_width(value)

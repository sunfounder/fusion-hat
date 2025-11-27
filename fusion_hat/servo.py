""" Servo motor class

Example:

    Simple usage:

    >>> from fusion_hat.servo import Servo
    >>> servo = Servo(0)
    >>> servo.angle(-90)
    >>> servo.angle(0)
    >>> servo.angle(90)

    Change the angle range:

    >>> servo = Servo(0, min=0, max=180)
    >>> servo.angle(0)
    >>> servo.angle(180)

    Add offset:

    >>> servo = Servo(0, offset=10.0)
    >>> servo.angle(0)
    >>> servo.angle(90)
"""

from .pwm import PWM
from ._utils import mapping, constrain
from .device import raise_if_fusion_hat_not_ready

from typing import Optional

class Servo(PWM):
    """ Servo motor class

    Args:
        channel (int/str): PWM channel number(0-14/P0-P14)
        offset (float, optional): offset value(-20.0~20.0), leave it None to use default offset, defaults to 0.0
        min (float, optional): minimum angle(-90~90), leave it None to use default min angle, defaults to -90
        max (float, optional): maximum angle(-90~90), leave it None to use default max angle, defaults to 90
        *args: Pass to :class:`fusion_hat.pwm.PWM`
        **kwargs: Pass to :class:`fusion_hat.pwm.PWM`
    """
    MAX_PW = 2500
    MIN_PW = 500
    FREQ = 50

    def __init__(self, channel: int, offset: Optional[float]=0.0, min: Optional[float]=-90, max: Optional[float]=90, *args, **kwargs):
        super().__init__(channel, *args, **kwargs)
        raise_if_fusion_hat_not_ready()

        self.freq(self.FREQ)
        self._offset = offset
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

        """
        angle = constrain(angle, -90, 90)
        pulse_width = mapping(angle, -90, 90, self.MIN_PW, self.MAX_PW)
        pulse_width = int(pulse_width)
        self.log.debug(f"Servo channel {self.channel} angle: {angle}, pulse_width: {pulse_width}")
        self.pulse_width(pulse_width)

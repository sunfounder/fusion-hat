""" PWM class to control a single PWM channel

Example:

    Simple example to control PWM channel 0 at 50Hz with 50% duty cycle.

    >>> from fusion_hat.pwm import PWM
    >>> pwm = PWM(0)
    >>> pwm.freq(50)
    >>> pwm.pulse_width_percent(50)

    Advanced example to control PWM channel with 50 Hz frequency, 20000us and pulse width 500-2500us for servos.

    >>> from fusion_hat.pwm import PWM
    >>> pwm = PWM(0)
    >>> pwm.freq(50)
    >>> pwm.pulse_width(1500) # servo center position
    >>> pwm.pulse_width(2500) # servo max position
    >>> pwm.pulse_width(500) # servo min position

"""
from ._base import _Base
from .device import raise_if_fusion_hat_not_ready

from typing import Optional

class PWM(_Base):
    """ PWM class to control a single PWM channel

    Args:
        channel (int/str): PWM channel number(0-11/P0-P11)
        freq (int, optional): PWM frequency, default is 50Hz
        addr (int, optional): I2C address, default is 0x17
        *args: Additional arguments for :class:`fusion_hat._i2c.I2C`
        **kwargs: Additional keyword arguments for :class:`fusion_hat._i2c.I2C`
    
    Raises:
        ValueError: Invalid channel number
    """

    CHANNEL_NUM = 12

    PATH = "/sys/class/fusion_hat/fusion_hat/pwm"

    def __init__(self, channel: int, freq: int=50, *args, **kwargs):
        super().__init__(*args, **kwargs)
        raise_if_fusion_hat_not_ready()

        if isinstance(channel, str):
            if channel.startswith("P"):
                channel = int(channel[1:])
            else:
                raise ValueError(
                    f'PWM channel should be between [P0, P11], not "{channel}"')
        if isinstance(channel, int):
            if channel < 0 or channel > self.CHANNEL_NUM - 1:
                raise ValueError(
                    f'channel must be in range of 0-11, not "{channel}"')
        self.channel = channel

        self.log.debug(f"PWM channel {self.channel} initilizing")
        self.timer_index = channel // 4
        self.enable()
        self._period = self.read_period()
        self.log.debug(f"PWM channel {self.channel} period: {self._period}")
        self._freq = 1000000 / self._period
        self.log.debug(f"PWM channel {self.channel} frequency: {self._freq}")
        self.duty_cycle(0)

        self.log.debug(f"PWM channel {self.channel} initilized")

    def enable(self, enable: bool=True) -> None:
        """ Enable/disable PWM channel

        Args:
            enable (bool, optional): enable or disable, default is True
        """
        with open(f"{self.PATH}/pwm{self.channel}/enable", "w") as f:
            f.write("1" if enable else "0")
        self.log.debug(f"PWM channel {self.channel} enabled: {enable}")

    def read_period(self) -> int:
        """ Get period in ms

        Returns:
            int: period in ms
        """
        with open(f"{self.PATH}/pwm{self.channel}/period", "r") as f:
            value = f.read().strip()
            return int(value)

    def write_period(self, period: int) -> int:
        """ Set period in ms

        Args:
            period (int): period in ms
        """
        with open(f"{self.PATH}/pwm{self.channel}/period", "w") as f:
            f.write(str(period))

    def read_duty_cycle(self) -> int:
        """ Get duty cycle in ms

        Returns:
            int: duty cycle in ms
        """
        with open(f"{self.PATH}/pwm{self.channel}/duty_cycle", "r") as f:
            value = f.read().strip()
            return int(value)

    def write_duty_cycle(self, duty_cycle: int) -> int:
        """ Set duty cycle in ms

        Args:
            duty_cycle (int): duty cycle in ms
        """
        self.log.debug(f"PWM channel {self.channel} duty cycle: {duty_cycle}")
        with open(f"{self.PATH}/pwm{self.channel}/duty_cycle", "w") as f:
            f.write(str(duty_cycle))

    def freq(self, freq: Optional[float]=None) -> float:
        """ Set/get frequency, leave blank to get frequency

        Args:
            freq (float, optional): frequency(0-65535)(Hz), default is 50Hz

        Returns:
            float: frequency
        """
        if freq == None:
            return self._freq
        
        self._freq = int(freq)
        # Calculate period in ms
        period = int(1000000/self._freq)
        self.period(period)
        return self._freq

    def prescaler(self, prescaler: Optional[int]=None, raw: bool=False) -> int:
        """ [Deprecated] Set/get prescaler, leave blank to get prescaler"""
        self.log.warning("prescaler is deprecated, please use freq instead.")

    def period(self, period: Optional[int]=None) -> int:
        """ Set/get period, leave blank to get period

        Args:
            period (int, optional): period(0-65535), default is 0
            raw (bool, optional): Whether to write period directly, default is False

        Returns:
            int: period
        """
        if period == None:
            return self._period
        self.log.debug(f"PWM channel {self.channel} period: {period}")
        self.write_period(period)
        return self._period

    def duty_cycle(self, duty_cycle: Optional[int]=None) -> int:
        """ Set/get duty cycle, in ms

        Args:
            duty_cycle (int, optional): duty cycle
        Returns:
            int: duty cycle
        """
        if duty_cycle == None:
            return self._duty_cycle
        self.log.debug(f"PWM channel {self.channel} duty cycle: {duty_cycle}")
        self.write_duty_cycle(duty_cycle)
        self._duty_cycle = duty_cycle
        self._pulse_width_percent = round(self._duty_cycle / self._period * 100, 2)
        return self._duty_cycle

    def pulse_width(self, pulse_width: Optional[int]=None) -> int:
        """ Set/get pulse width, in ms

        Args:
            pulse_width (int, optional): pulse width in ms

        Returns:
            int: pulse width
        """
        return self.duty_cycle(pulse_width)

    def pulse_width_percent(self, pulse_width_percent: Optional[float]=None) -> float:   
        """ Set/get pulse width percentage, leave blank to get pulse width percentage

        Args:
            pulse_width_percent (float, optional): pulse width percentage(0-100), default is 0

        Returns:
            float: pulse width percentage
        """
        if pulse_width_percent == None:
            return self._pulse_width_percent
        self.log.debug(f"PWM channel {self.channel} pulse width percent: {pulse_width_percent}")
        duty_cycle = int(pulse_width_percent * self._period / 100)
        self.duty_cycle(duty_cycle)
        return self._pulse_width_percent

    def close(self) -> None:
        """ Close PWM channel """
        self.enable(False)

    def __del__(self) -> None:
        """ Close PWM channel when object is deleted """
        try:
            if hasattr(self, 'close'):
                self.close()
        except Exception:
            pass
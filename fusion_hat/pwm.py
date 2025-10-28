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
import math
from ._base import _base
from typing import Optional

timer = [{"arr": 1} for _ in range(7)]

class PWM(_base):
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

    CLOCK = 72000000.0

    CHANNEL_NUM = 12
    DEFAULT_PRESCALER = 22
    PERIOD = 65535

    PATH = "/sys/class/fusion_hat/fusion_hat/pwm"

    def __init__(self, channel: int, freq: int=50, *args, **kwargs):
        super().__init__(*args, **kwargs)
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

        self.timer_index = channel // 4

        self._duty_cycle = self.read_duty_cycle()
        self._period = self.read_period()
        self._freq = 1000000000 / self._period
        self._pulse_width_percent = round(self._duty_cycle / self._period * 100, 2)
        self.pulse_width(0)

    def read_period(self) -> int:
        """ Get period in nanoseconds

        Returns:
            int: period in nanoseconds
        """
        with open(f"{self.PATH}/pwm{self.channel}/period", "r") as f:
            value = f.read().strip()
            return int(value)

    def write_period(self, period: int) -> int:
        """ Set period in nanoseconds

        Args:
            period (int): period in nanoseconds
        """
        with open(f"{self.PATH}/pwm{self.channel}/period", "w") as f:
            f.write(str(period))

    def read_duty_cycle(self) -> int:
        """ Get duty cycle in nanoseconds

        Returns:
            int: duty cycle in nanoseconds
        """
        with open(f"{self.PATH}/pwm{self.channel}/duty_cycle", "r") as f:
            value = f.read().strip()
            return int(value)

    def write_duty_cycle(self, duty_cycle: int) -> int:
        """ Set duty cycle in nanoseconds

        Args:
            duty_cycle (int): duty cycle in nanoseconds
        """
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
        # Calculate period in nanoseconds
        period = int(1000000000/self._freq) - 1
        # --- calculate the prescaler and period ---
        # frequency = CLOCK / (arr + 1) / (psc + 1)
        assumed_psc = int(math.sqrt(self.CLOCK/self._freq)) # assumed prescaler, start from square root
        assumed_psc -= 5
        if assumed_psc < 0:
            assumed_psc = 0
        # Calculate arr and frequency errors
        for psc in range(assumed_psc, assumed_psc+10):
            arr = int(self.CLOCK/self._freq/psc)
            psc_arr.append((psc, arr))
            freq_errors.append(abs(self._freq - self.CLOCK/psc/arr))
        # Find the best match
        best_match = freq_errors.index(min(freq_errors))
        psc, arr = psc_arr[best_match]
        self._prescaler = int(psc) - 1
        self._period = int(arr) - 1
        self.prescaler(self._prescaler, raw=True)
        self.period(self._period, raw=True)
        return self._freq

    def prescaler(self, prescaler: Optional[int]=None, raw: bool=False) -> int:
        """ [Deprecated] Set/get prescaler, leave blank to get prescaler"""
        print("[Warning] prescaler is deprecated, please use freq instead.")

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
        self.write_period(period)
        return self._period

    def duty_cycle(self, duty_cycle: Optional[int]=None) -> int:
        """ Set/get duty cycle, in nanoseconds

        Args:
            duty_cycle (int, optional): duty cycle
        Returns:
            int: duty cycle
        """
        if duty_cycle == None:
            return self._duty_cycle
        self.write_duty_cycle(duty_cycle)
        self._duty_cycle = duty_cycle
        self._pulse_width_percent = round(self._duty_cycle / self._period * 100, 2)
        return self._duty_cycle

    def pulse_width(self, pulse_width: Optional[int]=None) -> int:
        """ Set/get pulse width, in nanoseconds

        Args:
            pulse_width (int, optional): pulse width in nanoseconds

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
        duty_cycle = int(pulse_width_percent * self._period / 100)
        self.write_duty_cycle(duty_cycle)
        return self._pulse_width_percent

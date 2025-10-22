#!/usr/bin/env python3
import math
from ._i2c import I2C
from .device import I2C_ADDRESS
from typing import Optional


timer = [{"arr": 1} for _ in range(7)]

class PWM(I2C):
    """ PWM class to control a single PWM channel """

    CLOCK = 72000000.0

    # 3 timer2 for 12 channels
    REG_PSC_START = 0x40
    REG_PSC_END = 0x49

    REG_ARR_START = 0x50
    REG_ARR_END = 0x59

    REG_CCP_START = 0x60
    REG_CCP_END = 0x77

    CHANNEL_NUM = 12

    def __init__(self, channel: int, freq: int=50, addr: int=I2C_ADDRESS, *args, **kwargs):
        """ Initialize PWM

        Args:
            channel (int/str): PWM channel number(0-11/P0-P11)
            freq (int, optional): PWM frequency, default is 50Hz
            addr (int, optional): I2C address, default is 0x17
        
        Raises:
            ValueError: Invalid channel number
        """
        super().__init__(addr, *args, **kwargs)
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

        if channel < 4:
            self.timer_index = 0
        elif channel < 8:
            self.timer_index = 1
        else:
            self.timer_index = 2

        self._prescaler_register = self.REG_PSC_START + self.timer_index
        self._period_register = self.REG_ARR_START + self.timer_index
        self._pulse_width_register = self.REG_CCP_START + self.channel
        self._prescaler = 0
        self._period = 0
        self._pulse_width = 0
        self._pulse_width_percent = 0.0
        self._freq = freq
        self.freq(freq)
        self.pulse_width(0)

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
        # Calculate arr and frequency errors
        psc_arr = []
        freq_errors = []
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
        self.prescaler(self._prescaler)
        self.period(self._period)
        return self._freq

    def prescaler(self, prescaler: Optional[int]=None) -> int:
        """ Set/get prescaler, leave blank to get prescaler

        Args:
            prescaler (int, optional): prescaler(0-65535), default is 0

        Returns:
            int: prescaler
        """
        if prescaler == None:
            return self._prescaler

        self._prescaler = int(prescaler)
        self._freq = self.CLOCK/(self._prescaler+1)/(self._period+1)
        self.write_data(self._prescaler_register, self._prescaler)
        return self._prescaler

    def period(self, period: Optional[int]=None) -> int:
        """ Set/get period, leave blank to get period

        Args:
            period (int, optional): period(0-65535), default is 0

        Returns:
            int: period
        """
        if period == None:
            return self._period

        self._period = int(period)
        self._freq = self.CLOCK/(self._prescaler+1)/(self._period+1)
        self._pulse_width_percent = round(self._pulse_width / (self._period+1) * 100, 2)
        self.write_data(self._period_register, self._period)
        return self._period

    def pulse_width(self, pulse_width: Optional[int]=None) -> int:
        """ Set/get pulse width, leave blank to get pulse width

        Args:
            pulse_width (int, optional): pulse width(0-65535), default is 0

        Returns:
            int: pulse width
        """
        if pulse_width == None:
            return self._pulse_width

        self._pulse_width = int(pulse_width)
        self._pulse_width_percent = round(pulse_width / (self._period+1) * 100, 2)
        self.write_data(self._pulse_width_register, self._pulse_width)
        return self._pulse_width

    def pulse_width_percent(self, pulse_width_percent: Optional[float]=None) -> float:   
        """ Set/get pulse width percentage, leave blank to get pulse width percentage

        Args:
            pulse_width_percent (float, optional): pulse width percentage(0-100), default is 0

        Returns:
            float: pulse width percentage
        """
        if pulse_width_percent == None:
            return self._pulse_width_percent

        self._pulse_width_percent = round(pulse_width_percent, 2)
        self._pulse_width = int((self._period+1) * pulse_width_percent / 100)
        self.write_data(self._pulse_width_register, self._pulse_width)
        return self._pulse_width_percent

    def write_data(self, reg: int, data: int) -> None:
        """ Write data to the PWM device

        Args:
            reg (int): register address
            data (int): data to write
        """
        self.write_word_data(reg, data, lsb=True)

#!/usr/bin/env python3
import math
from .i2c import I2C
from .device import __device__
from typing import Optional


timer = [{"arr": 1} for _ in range(7)]

class PWM(I2C):
    """PWM"""

    ADDR = 0x17
    CLOCK = 72000000.0

    # 3 timer2 for 12 channels
    REG_PSC_START = 0x40
    REG_PSC_END = 0x49

    REG_ARR_START = 0x50
    REG_ARR_END = 0x59

    REG_CCP_START = 0x60
    REG_CCP_END = 0x77

    CHANNEL_NUM = 12

    def __init__(self, channel: int, freq: int=50, addr: int=ADDR, *args, **kwargs):
        """
        Initialize PWM

        :param channel: PWM channel number(0-11/P0-P11)
        :type channel: int/str

        :param freq: PWM frequency
        :type freq: int (default: 50)

        :param addr: I2C address, default is 0x17
        :type addr: int
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

        self.psc_reg_addr = self.REG_PSC_START + self.timer_index
        self.arr_reg_addr = self.REG_ARR_START + self.timer_index
        self.ccp_reg_addr = self.REG_CCP_START + self.channel
        self.psc = 0
        self.arr = 0
        self.ccp = 0
        self.duty_cycle = 0.0
        self._freq = freq
        self.freq(freq)
        self.pulse_width(0)

    def freq(self, freq: Optional[float]=None) -> float:
        """
        Set/get frequency, leave blank to get frequency

        :param freq: frequency(0-65535)(Hz)
        :type freq: float
        :return: frequency
        :rtype: float
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
        self.psc = int(psc) - 1
        self.arr = int(arr) - 1
        self.prescaler(self.psc)
        self.period(self.arr)
        return self._freq

    def prescaler(self, psc: Optional[int]=None) -> int:
        """
        Set/get prescaler, leave blank to get prescaler

        :param psc: prescaler(0-65535)
        :type psc: int
        :return: prescaler
        :rtype: int
        """
        if psc == None:
            return self.psc

        self.psc = int(psc)
        self._freq = self.CLOCK/(self.psc+1)/(self.arr+1)
        psc_h = (self.psc >> 8) & 0xff
        psc_l = self.psc & 0xff
        data = [self.psc_reg_addr, psc_h, psc_l]
        self.write(data)
        return self.psc

    def period(self, arr: Optional[int]=None) -> int:
        """
        Set/get period, leave blank to get period

        :param arr: period(0-65535)
        :type arr: int
        :return: period
        :rtype: int
        """
        if arr == None:
            return self.arr

        self.arr = int(arr)
        self._freq = self.CLOCK/(self.psc+1)/(self.arr+1)
        self.duty_cycle = round(self.ccp / (self.arr+1) * 100, 2)
        arr_h = (self.arr >> 8) & 0xff
        arr_l = self.arr & 0xff
        data = [self.arr_reg_addr, arr_h, arr_l]
        self.write(data)
        return self.arr

    def pulse_width(self, ccp: Optional[int]=None) -> int:
        """
        Set/get pulse width, leave blank to get pulse width

        :param ccp: pulse width(0-65535)
        :type ccp: int
        :return: pulse width
        :rtype: int
        """
        if ccp == None:
            return self.ccp

        self.ccp = int(ccp)
        self.duty_cycle = round(self.ccp / (self.arr+1) * 100, 2)
        ccp_h = (self.ccp >> 8) & 0xff
        ccp_l = self.ccp & 0xff
        data = [self.ccp_reg_addr, ccp_h, ccp_l]
        self.write(data)
        return self.ccp

    def pulse_width_percent(self, duty_cycle: Optional[float]=None) -> float:   
        """
        Set/get pulse width percentage, leave blank to get pulse width percentage

        :param duty_cycle: pulse width percentage(0-100)
        :type duty_cycle: float
        :return: pulse width percentage
        :rtype: float
        """
        if duty_cycle == None:
            return duty_cycle

        self.duty_cycle = round(duty_cycle, 2)
        self.ccp = int((self.arr+1) * duty_cycle / 100)
        cpp_h = (self.ccp >> 8) & 0xff
        ccp_l = self.ccp & 0xff
        data = [self.ccp_reg_addr, cpp_h, ccp_l]
        self.write(data)
        return self.duty_cycle

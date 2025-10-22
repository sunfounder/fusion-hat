import math
from .device import I2C_ADDRESS
from ._i2c import I2C
from ._base import _Base
from typing import Optional

class PWM_GROUP(_Base):
    """ PWM group class to control multiple PWM channels

    PWM channels:
        PWM     MCU     TIM_Channel
    ------------------------------
        0       PA8      TIM0_CH0
        1       PA9      TIM0_CH1
        2       PA10     TIM0_CH2
        3       PA11     TIM0_CH3

        4       PB4      TIM2_CH0
        5       PB5      TIM2_CH1
        6       PB0      TIM2_CH2
        7       PB1      TIM2_CH3

        8       PB14     TIM14_CH0
        9       PB15     TIM14_CH1
        10      PB8      TIM15_CH0
        11      PB9      TIM16_CH1

    Args:
        channels (list): PWM channels
        freq (int, optional): PWM frequency, default is 50Hz
        addr (int, optional): I2C address, default is 0x17
        auto_write (bool, optional): Auto write to register, default is False
    """

    REG_PSC = 0x40 # Prescaler register prefix
    REG_ARR = 0x50 # Period registor prefix
    REG_CCP = 0x60 # Pluse width register prefix

    CLOCK = 72000000.0 # Clock frequency, 72MHz

    def __init__(self, channels:list, *args, freq: int=50, addr: int=I2C_ADDRESS, auto_write: bool=False, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.addr = addr
        self._i2c = I2C(addr)

        self.channels = channels
        self.channel_num = len(channels)
        self.ccp = [ 0 for _ in range(self.channel_num)]
        self.duty_cycle = [ 0.00 for _ in range(self.channel_num)] # duty cycle, 0~100

        self.timer_indexs = []
        for i in range(3):
            if i in channels:
                self.timer_indexs.append(0)
                break
        for i in range(3, 8):
            if i in channels:
                self.timer_indexs.append(1)
                break
        for i in range(8, 12):
            if i in channels:
                self.timer_indexs.append(2)
                break

        self._freq = freq
        self.freq(freq)

        self.auto_write = auto_write

    def freq(self, freq: Optional[int]=None) -> int:
        """ Return or set the current frequency

        Args:
            freq (int, optional): PWM frequency

        Returns:
            int: PWM frequency
        """

        if freq is None:
            return self._freq

        self._freq = int(freq)
        # --- calculate the prescaler and period ---
        assumed_psc = int(math.sqrt(self.CLOCK/self._freq)) # assumed prescaler, start from square root
        assumed_psc -= 5
        if assumed_psc < 0:
            assumed_psc = 0
        
        # Calculate arr and frequency errors
        psc_arr = []
        freq_errors = []
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
        """ Return or set the current prescaler

        Args:
            psc (int, optional): prescaler value

        Returns:
            int: prescaler value
        """
        # return the current prescaler
        if psc is None:
            return self.psc

        # set the prescaler
        self.psc = int(psc)

        for timer_index in self.timer_indexs:
            psc_h = (self.psc >> 8) & 0xff
            psc_l = self.psc & 0xff
            data = [self.REG_PSC+timer_index, psc_h, psc_l]
            self._i2c.write(data)
        
        return self.psc

    def period(self, arr: Optional[int]=None) -> int:
        """ Return or set the current period

        Args:
            arr (int, optional): period value

        Returns:
            int: period value
        """
        # return the current period
        if arr is None:
            return self.arr

        # set the period
        self.arr = int(arr)
        for timer_index in self.timer_indexs:
            arr_h = (self.arr >> 8) & 0xff
            arr_l = self.arr & 0xff
            data = [self.REG_ARR+timer_index, arr_h, arr_l]
            self._i2c.write(data)

        return self.arr

    def pulse_width(self, index: int, pulse_width: Optional[int]=None) -> int:
        """ Return or set the current pulse width

        Args:
            index (int): PWM channel index
            pulse_width (int, optional): pulse width value

        Returns:
            int: pulse width value
        """
        # return the current pulse width
        if pulse_width is None:
            return self.ccp[index]

        # set the pulse width
        self.ccp[index] = int(pulse_width)
        self.duty_cycle[index] = round(pulse_width / self.arr * 100, 2)
        ccp_h = (pulse_width >> 8) & 0xff
        ccp_l = pulse_width & 0xff
        data = [self.REG_CCP+index, ccp_h, ccp_l]
        self._i2c.write(data)

        return self.ccp[index]

    def pulse_width_all(self, pulse_widths: Optional[list]=None) -> None:
        """ Return or set the current pulse width list

        Args:
            pulse_widths (list, optional): pulse width list

        Returns:
            list: pulse width list
        """
        # return the current pulse width list
        if pulse_widths is None:
            return self.ccp

        # set the pulse width list
        pulse_widths = [int(pulse_width) for pulse_width in pulse_widths]
        _len = len(pulse_widths)
        if _len < self.channel_num:
            self.ccp = pulse_widths + self.ccp[_len:]
        else:
            self.ccp = pulse_widths[:self.channel_num]

        _send_times = int(_len / 10) + 1
        for i in range(_send_times):
            data = []
            _st = i * 10
            _end = _len if _len < (_st + 10) else (_st + 10)
            for j in range(_st, _end):
                self.duty_cycle[j] = round(pulse_widths[j] / self.arr * 100, 2)
                channel_index = self.channels[j]
                data.append(self.REG_CCP+channel_index)
                cpp_h = pulse_widths[j] >> 8
                cpp_l = pulse_widths[j] & 0xff
                data.extend([cpp_h, cpp_l])
            self._i2c.write(data)
    
        return self.ccp

    def pulse_width_perecent(self, index: int, percent: Optional[float]=None) -> float:
        """ Return or set the current pulse width percent

        Args:
            index (int): PWM channel index
            percent (float, optional): pulse width percent value

        Returns:
            float: pulse width percent value
        """
        # return the current pulse width percent
        if percent is None:
            return self.duty_cycle[index]

        # set the pulse width percent
        ccp = percent * self.arr / 100
        self.pulse_width(index, ccp)

        return self.duty_cycle[index]

    def pulse_width_perecent_all(self, percents: Optional[list]=None) -> None:
        """ Return or set the current pulse width percent list

        Args:
            percents (list, optional): pulse width percent list

        Returns:
            list: pulse width percent list
        """
        # return the current pulse width percent list
        if percents is None:
            return self.duty_cycle

        # set the pulse width percent list
        _len = len(percents)
        cpps = []
        for i in range(_len):
            ccp = int(percents[i] * self.arr / 100)
            cpps.append(ccp)
        self.pulse_width_all(cpps)

    def __setitem__(self, index: int, value: int) -> None:
        """ Set the pulse width percent value

        Args:
            index (int): PWM channel index
            value (int): pulse width percent value
        """
        self.ccp[index] = value
        if self.auto_write:
            self.pulse_width(index, value)

    def __getitem__(self, index: int) -> int:
        """ Get the pulse width percent value

        Args:
            index (int): PWM channel index

        Returns:
            int: pulse width percent value
        """
        return self.ccp[index]
    
    def write(self) -> None:
        """ Write the current pulse width percent list to the PWM group """
        self.pulse_width_all(self.ccp)

def test():
    pwm_group = PWM_GROUP([0,1,2,3,8,9,10,11,4,5,6,7])
    pwm_group.freq(1000)
    pwm_group.pulse_width(0, 1000)
    pwm_group[0] = 1000
    pwm_group.write()

if __name__ == '__main__':
    test()

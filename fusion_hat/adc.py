#!/usr/bin/env python3

from .i2c import I2C
from .device import I2C_ADDRESS
from typing import Optional

class ADC(I2C):
    """ Analog to digital converter

    Attributes:
    """
    REG_ADC_START = 0x10
    REG_ADC_END = 0x19
    CHANNEL_NUM = 5

    DEFAULT_REFERENCE_VOLTAGE = 3.3

    def __init__(self, chn: [int, str], address: int = I2C_ADDRESS, *args, **kwargs) -> None:
        """
        Analog to digital converter

        Args:
            chn (int/str): channel number (0-4/A0-A4)
            address (int, optional): I2C address, default is 0x17

        Raises:
            ValueError: If chn is not between 0-4 or A0-A4
        """
        super().__init__(*args, address=address, **kwargs)

        if isinstance(chn, str):
            # If chn is a string, assume it's a pin name, remove A and convert to int
            if chn.startswith("A"):
                chn = int(chn[1:])
            else:
                raise ValueError(
                    f'ADC channel should be between [A0, A4], not "{chn}"')
        elif isinstance(chn, int):
            # Make sure channel is between 0 and 4
            if chn < 0 or chn > self.CHANNEL_NUM - 1:
                raise ValueError(
                    f'ADC channel should be between [0, 4], not "{chn}"')
        else:
            raise ValueError(
                f'ADC channel should be between [0, 4], not "{chn}"')
        self.channel = chn
        self.reg_addr = self.REG_ADC_START + chn*2

    def read(self) -> int:
        """ Read the ADC value

        Returns:
            int: ADC value(0-4095)
        """
        data = self.read_word_data(self.reg_addr, lsb=True)
        self.log.debug(f"Read ADC channel {self.channel} value: {data}")
        return data

    def read_voltage(self) -> float:
        """ Read the ADC voltage

        Returns:
            float: ADC voltage(0-3.3V)
        """
        data = self.read()
        voltage = data * self.DEFAULT_REFERENCE_VOLTAGE / 4095
        self.log.debug(f"Read ADC channel {self.channel} voltage: {voltage:.3f}V")
        return voltage

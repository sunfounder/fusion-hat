#!/usr/bin/env python3

""" Fusion Hat on-board analog to digital converter

Example:

    Import ADC
    
    >>> from fusion_hat.adc import ADC

    Init ADC channel 0

    >>> a0 = ADC(0)

    Read ADC channel 0 value
    >>> print(a0.read())
    2048

    Read ADC channel 0 voltage
    >>> print(a0.read_voltage())
    1.65
"""

from ._i2c import I2C
from .device import I2C_ADDRESS

class ADC(I2C):
    """ Analog to digital converter

    Args:
        chn (int, str): channel number (0-4/A0-A4)
        address (int, optional): I2C address, default is 0x17
        *args: Parameters to pass to :class:`fusion_hat._i2c.I2C`.
        **kwargs: Keyword arguments to pass to :class:`fusion_hat._i2c.I2C`.

    Raises:
        ValueError: If chn is not between 0-4 or A0-A4
        I2CError: If I2C communication fails
    """
    REG_A0 = 0x10
    REG_A1 = 0x12
    REG_A2 = 0x14
    REG_A3 = 0x16
    REG_A4 = 0x18
    REG_CHANNELS = [REG_A0, REG_A1, REG_A2, REG_A3, REG_A4]
    CHANNEL_NUM = len(REG_CHANNELS)

    DEFAULT_REFERENCE_VOLTAGE = 3.3

    def __init__(self, chn: [int, str], address: int = I2C_ADDRESS, *args, **kwargs) -> None:
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
        self.reg_addr = self.REG_CHANNELS[chn]

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

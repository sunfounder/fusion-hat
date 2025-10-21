#!/usr/bin/env python3

from .i2c import I2C

class ADC(I2C):
    """ Analog to digital converter

    Attributes:
    """
    ADDR = [0x17]

    REG_ADC_START = 0x10
    REG_ADC_END = 0x19
    CHANNEL_NUM = 5

    def __init__(self, chn: int, address: list[int] = ADDR, *args, **kwargs) -> None:
        """
        Analog to digital converter

        Args:
            chn (int/str): channel number (0-4/A0-A4)

        Raises:
            ValueError: If chn is not between 0-4 or A0-A4
        """
        super().__init__(address, *args, **kwargs)

        if isinstance(chn, str):
            # If chn is a string, assume it's a pin name, remove A and convert to int
            if chn.startswith("A"):
                chn = int(chn[1:])
            else:
                raise ValueError(
                    f'ADC channel should be between [A0, A4], not "{chn}"')
        # Make sure channel is between 0 and 4
        if chn < 0 or chn > self.CHANNEL_NUM - 1:
            raise ValueError(
                f'ADC channel should be between [0, 4], not "{chn}"')
        self.channel = chn
        self.reg_addr = self.REG_ADC_START + chn*2

    def read(self) -> int:
        """ Read the ADC value

        Returns:
            int: ADC value(0-4095)
        """
        val_h, val_l = self.read_i2c_block_data(self.reg_addr, 2)
        val = (val_h << 8) | val_l
        return val

    def read_voltage(self) -> float:
        """ Read the ADC voltage

        Returns:
            float: ADC voltage(0-3.3V)
        """
        val = self.read()
        voltage = val * 3.3 / 4095
        return voltage

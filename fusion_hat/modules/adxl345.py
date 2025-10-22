from .._i2c import I2C
from typing import Union, List, Tuple, Optional

class ADXL345(I2C):
    """ADXL345 modules"""

    X = 0
    """X"""
    Y = 1
    """Y"""
    Z = 2
    """Z"""
    ADDR =  0x53
    _REG_DATA_X = 0x32  # X-axis data 0 (6 bytes for X/Y/Z)
    _REG_DATA_Y = 0x34  # Y-axis data 0 (6 bytes for X/Y/Z)
    _REG_DATA_Z = 0x36  # Z-axis data 0 (6 bytes for X/Y/Z)
    _REG_POWER_CTL = 0x2D  # Power-saving features control
    _AXISES = [_REG_DATA_X, _REG_DATA_Y, _REG_DATA_Z]

    def __init__(self, *args, address: int = ADDR, bus: int = 1, **kwargs):
        """
        Initialize ADXL345

        :param address: address of the ADXL345
        :type address: int
        """
        super().__init__(address=address, bus=bus, *args, **kwargs)
        self.address = address

    def read(self, axis: int = None) -> Union[float, List[float]]:
        """
        Read an axis from ADXL345

        :param axis: read value(g) of an axis, ADXL345.X, ADXL345.Y or ADXL345.Z, None for all axis
        :type axis: int
        :return: value of the axis, or list of all axis
        :rtype: float/list
        """
        if axis is None:
            return [self._read(i) for i in range(3)]
        else:
            return self._read(axis)

    def _read(self, axis: int) -> float:
        raw_2 = 0
        result = super().read()
        data = (0x08 << 8) + self._REG_POWER_CTL
        if result:
            self.write(data)
        self.mem_write(0, 0x31)
        self.mem_write(8, 0x2D)
        raw = self.mem_read(2, self._AXISES[axis])
       # The value read for the first time is always 0, so read it once more
        self.mem_write(0, 0x31)
        self.mem_write(8, 0x2D)
        raw = self.mem_read(2, self._AXISES[axis])
        if raw[1] >> 7 == 1:

            raw_1 = raw[1] ^ 128 ^ 127
            raw_2 = (raw_1 + 1) * -1
        else:
            raw_2 = raw[1]
        g = raw_2 << 8 | raw[0]
        value = g / 256.0
        return value
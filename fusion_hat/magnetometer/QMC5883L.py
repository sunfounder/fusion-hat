"""
QMC5883L magnetometer sensor driver

This module provides an implementation for the QMC5883L 3-axis magnetometer sensor.
"""

from smbus2 import SMBus
import time

class QMC5883L:
    """
    QMC5883L 3-axis magnetometer sensor driver class
    Used to measure Earth's magnetic field strength, is a common alternative to HMC5883L
    """
    # Class constant definition
    DEF_ADDR = 0x0D
    REG_CONTROL   = 0x09
    REG_SET_RESET = 0x0B
    REG_OUT_X_L   = 0x00

    def __init__(self, bus: SMBus, addr: int = DEF_ADDR):
        """
        Initialize QMC5883L magnetometer
        
        Parameters:
            bus: SMBus instance for I2C communication
            addr: Device I2C address, default is DEF_ADDR (0x0D)
        """
        self.bus = bus
        self.ADDR = addr
        
        try:
            self.bus.write_byte_data(self.ADDR, self.REG_SET_RESET, 0x01)
        except OSError:
            pass
        
        # Configure control register: 0b11110101
        # OSR2,OSR1=11 (512-sample averaging) | RNG1,RNG0=11 (±8 Gauss range)
        # ODR1,ODR0=10 (50 Hz output data rate) | MODE1,MODE0=01 (continuous measurement mode)
        self.bus.write_byte_data(self.ADDR, self.REG_CONTROL, 0b11110101)
        
        time.sleep(0.01)

        self.scale = 12000.0  

    def _read_word_le(self, reg_l):
        """
        Read a signed 16-bit integer from the sensor in little-endian format
        Note: QMC5883L uses little-endian format to store data
        
        Parameters:
            reg_l: Low byte register address
        
        Returns:
            val: Converted signed 16-bit integer
        """
        # First read the low byte
        low = self.bus.read_byte_data(self.ADDR, reg_l)
        # Then read the high byte
        high = self.bus.read_byte_data(self.ADDR, reg_l + 1)
        # Combine the two bytes into a 16-bit integer (note little-endian format)
        val = (high << 8) | low
        # Convert to signed integer
        if val >= 0x8000:
            val = -((65535 - val) + 1)
        return val

    def read_magnet(self):
        """
        Read magnetometer data
        
        Returns:
            x, y, z: X, Y, Z axis magnetic field strength values (unit: Gauss)
            Note: QMC5883L data register order is X, Y, Z (different from HMC5883L)
        """
        x = self._read_word_le(self.REG_OUT_X_L + 0)
        y = self._read_word_le(self.REG_OUT_X_L + 2)
        z = self._read_word_le(self.REG_OUT_X_L + 4)
        return (x / self.scale, y / self.scale, z / self.scale)
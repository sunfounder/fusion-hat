#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from smbus2 import SMBus
import time


class HMC5883L:
    """
    HMC5883L 3-axis magnetometer sensor driver class
    Used to measure Earth's magnetic field strength, suitable for direction detection and heading angle calculation
    """
    DEF_ADDR = 0x1E
    REG_CONFIG_A = 0x00
    REG_CONFIG_B = 0x01
    REG_MODE     = 0x02
    REG_OUT_X_H  = 0x03

    def __init__(self, bus: SMBus, addr: int = DEF_ADDR):
        self.bus = bus
        self.ADDR = addr
        self.bus.write_byte_data(self.ADDR, self.REG_CONFIG_A, 0b01110000)  # average 8 samples, 15Hz output rate
        self.bus.write_byte_data(self.ADDR, self.REG_CONFIG_B, 0x20)        # gain 1.3 Ga
        self.bus.write_byte_data(self.ADDR, self.REG_MODE, 0x00)            # continuous measurement mode
        
        time.sleep(0.006)
    
        self.scale = 1090.0

    def _read_word(self, reg_h):
        """
        Read a signed 16-bit integer from the sensor
        
        Parameters:
            reg_h: high-byte register address
        
        Returns:
            val: converted signed 16-bit integer
        """
        high = self.bus.read_byte_data(self.ADDR, reg_h)
        low  = self.bus.read_byte_data(self.ADDR, reg_h + 1)
        val = (high << 8) | low
        if val >= 0x8000:
            val = -((65535 - val) + 1)
        return val

    def read_magnet(self):
        """
        Read magnetometer data
        
        Returns:
            x, y, z: X, Y, Z axis magnetic field strength values (unit: Gauss)
            Note: HMC5883L data register order is X, Z, Y
        """
        x = self._read_word(self.REG_OUT_X_H)
        z = self._read_word(self.REG_OUT_X_H + 4)  # X Z Y
        y = self._read_word(self.REG_OUT_X_H + 2)

        return (x / self.scale, y / self.scale, z / self.scale)


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


class QMC5883P:
    """
    QMC5883P 3-axis magnetometer sensor driver class
    Another version of the QMC5883 series with I2C address 0x2C
    """
   
    DEF_ADDR = 0x2C
    REG_X_LSB   = 0x01
    REG_STATUS  = 0x09
    REG_MODE    = 0x0A
    REG_CONFIG  = 0x0B

    def __init__(self, bus: SMBus, addr: int = DEF_ADDR):
        """
        Initialize QMC5883P magnetometer
        
        Parameters:
            bus: SMBus instance for I2C communication
            addr: Device I2C address, default is DEF_ADDR (0x2C)
        """
        self.bus = bus
        self.ADDR = addr
      
      
        try:
            self.bus.write_byte_data(self.ADDR, self.REG_MODE, 0xCF)
            time.sleep(0.003)
            self.bus.write_byte_data(self.ADDR, self.REG_CONFIG, 0x08)
            time.sleep(0.003)
        except Exception:
            pass
        
        self.scale = 12000.0

    @staticmethod
    def _to_i16(lsb, msb):
        """
        Convert two bytes to a 16-bit signed integer
        
        Parameters:
            lsb: Low byte value
            msb: High byte value
        
        Returns:
            v: Converted 16-bit signed integer
        """
        v = (msb << 8) | lsb
        if v >= 0x8000:
            v -= 0x10000
        return v

    def read_magnet(self):
        """
        Read magnetometer data
        Reads 6 bytes starting from 0x01 register (little-endian signed format)
        Features: Returns zero on error, does not interrupt main loop
        
        Returns:
            x, y, z: X, Y, Z axis magnetic field strength values (unit: Gauss)
        """
        try:
            raw = self.bus.read_i2c_block_data(self.ADDR, self.REG_X_LSB, 6)
            # Data order: X_LSB, X_MSB, Y_LSB, Y_MSB, Z_LSB, Z_MSB
            x = self._to_i16(raw[0], raw[1])  # X axis data
            y = self._to_i16(raw[2], raw[3])  # Y axis data
            z = self._to_i16(raw[4], raw[5])  # Z axis data
            # Convert to Gauss unit and return
            return (x / self.scale, y / self.scale, z / self.scale)
        except Exception:
            return (0.0, 0.0, 0.0)
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from smbus2 import SMBus
import time


class BMP180:
    """
    BMP180 pressure/temperature sensor driver class
    Used to measure atmospheric pressure and temperature, and can calculate altitude
    This is a concise implementation version that uses floating-point calculations to improve accuracy
    """
    ADDR = 0x77
    REG_CAL  = 0xAA
    REG_CTRL = 0xF4
    REG_DATA = 0xF6
    CMD_TEMP = 0x2E
    CMD_PRES_BASE = 0x34

    def __init__(self, bus: SMBus, oversampling=3):
        """
        Initialize BMP180 sensor
        
        Parameters:
            bus: SMBus instance for I2C communication
            oversampling: Oversampling rate (0-3), higher value means higher accuracy but longer measurement time
                          0: Standard mode, fastest
                          3: Ultra-high precision mode, slowest
        """
        self.bus = bus
        self.oss = max(0, min(3, oversampling))
        self._read_calibration()

    def _readS16(self, reg):
        """
        Read a signed 16-bit integer from the specified register
        
        Parameters:
            reg: register address
        
        Returns:
            int: converted signed 16-bit integer value
        """
        high = self.bus.read_byte_data(self.ADDR, reg)
        low = self.bus.read_byte_data(self.ADDR, reg + 1)

        val = (high << 8) | low
        if val & 0x8000:
            val = -((~val & 0xFFFF) + 1)
        return val

    def _readU16(self, reg):
        """
        Read an unsigned 16-bit integer from the specified register
        
        Parameters:
            reg: register address
        
        Returns:
            int: converted unsigned 16-bit integer value
        """
        high = self.bus.read_byte_data(self.ADDR, reg)
        low = self.bus.read_byte_data(self.ADDR, reg + 1)

        return (high << 8) | low

    def _read_calibration(self):
        """
        Read calibration parameters of the sensor
        Each BMP180 chip has unique calibration parameters stored in internal EEPROM
        These parameters are used to compensate for individual differences of the sensor
        """
        # Read 11 calibration parameters, each is a 16-bit value
        # Note: AC1-AC3, B1, B2, MB, MC, MD are signed integers
        # AC4-AC6 are unsigned integers
        self.AC1 = self._readS16(self.REG_CAL + 0)
        self.AC2 = self._readS16(self.REG_CAL + 2)
        self.AC3 = self._readS16(self.REG_CAL + 4)
        self.AC4 = self._readU16(self.REG_CAL + 6)
        self.AC5 = self._readU16(self.REG_CAL + 8)
        self.AC6 = self._readU16(self.REG_CAL + 10)
        self.B1  = self._readS16(self.REG_CAL + 12)
        self.B2  = self._readS16(self.REG_CAL + 14)
        self.MB  = self._readS16(self.REG_CAL + 16)
        self.MC  = self._readS16(self.REG_CAL + 18)
        self.MD  = self._readS16(self.REG_CAL + 20)

    def _read_raw_temp(self):
        """
        Read raw temperature value
        Trigger temperature conversion and wait for completion, then read the result
        
        Returns:
            int: raw temperature value (16-bit unsigned integer)
        """
        self.bus.write_byte_data(self.ADDR, self.REG_CTRL, self.CMD_TEMP)
        time.sleep(0.005)
        msb = self.bus.read_byte_data(self.ADDR, self.REG_DATA)
        lsb = self.bus.read_byte_data(self.ADDR, self.REG_DATA + 1)
  
        return (msb << 8) | lsb

    def _read_raw_pressure(self):
        """
        Read raw pressure value
        Trigger pressure conversion and wait for completion, then read the result
        
        Returns:
            int: raw pressure value (16-bit unsigned integer)
        """
        # Write pressure measurement command, including oversampling setting (shifted left by 6 bits)
        self.bus.write_byte_data(self.ADDR, self.REG_CTRL, self.CMD_PRES_BASE + (self.oss << 6))
        
        # Select different wait times based on oversampling rate
        time.sleep({0: 0.005, 1: 0.008, 2: 0.014, 3: 0.026}[self.oss])
        
        # Read three bytes of raw pressure data
        msb = self.bus.read_byte_data(self.ADDR, self.REG_DATA)
        lsb = self.bus.read_byte_data(self.ADDR, self.REG_DATA + 1)
        xlsb = self.bus.read_byte_data(self.ADDR, self.REG_DATA + 2)
        
        # Combine into 24-bit value, then right shift according to oversampling rate
        raw = ((msb << 16) + (lsb << 8) + xlsb) >> (8 - self.oss)
        return raw

    def read(self):
        """
        Read and calculate temperature, pressure, and altitude
        Use standard formulas provided in BMP180 datasheet
        
        Returns:
            tuple: (temperature(°C), pressure(Pa), altitude(m))
        """
        # Read raw temperature and pressure values
        UT = self._read_raw_temp()
        UP = self._read_raw_pressure()

        # Temperature calculation section
        # Use floating point calculation for higher precision
        X1 = (UT - self.AC6) * self.AC5 / 32768.0
        X2 = (self.MC * 2048.0) / (X1 + self.MD)
        B5 = X1 + X2
        temp = (B5 + 8.0) / 16.0 / 10.0  # Convert to Celsius

        # Pressure calculation section
        B6 = B5 - 4000.0
        X1 = (self.B2 * (B6 * B6 / 4096.0)) / 2048.0
        X2 = (self.AC2 * B6) / 2048.0
        X3 = X1 + X2
        B3 = (((self.AC1 * 4.0 + X3) * (1 << self.oss)) + 2.0) / 4.0
        X1 = (self.AC3 * B6) / 8192.0
        X2 = (self.B1 * (B6 * B6 / 4096.0)) / 65536.0
        X3 = ((X1 + X2) + 2.0) / 4.0
        B4 = self.AC4 * (X3 + 32768.0) / 32768.0

        B7 = (UP - B3) * (50000.0 / (2 ** self.oss))


        if B7 < 0x80000000:
            p = (B7 * 2.0) / B4
        else:
            p = (B7 / B4) * 2.0


        X1 = (p / 256.0) ** 2
        X1 = (X1 * 3038.0) / 65536.0
        X2 = (-7357.0 * p) / 65536.0
        p = p + (X1 + X2 + 3791.0) / 16.0

        # Standard sea-level pressure is 101325 Pa
        altitude = 44330.0 * (1.0 - (p / 101325.0) ** (1/5.255))
        
        return float(temp), float(p), float(altitude)
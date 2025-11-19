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
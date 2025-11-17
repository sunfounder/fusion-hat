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
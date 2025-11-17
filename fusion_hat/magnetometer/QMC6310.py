from smbus2 import SMBus

class QMC6310:
    # https://www.qstcorp.com/upload/pdf/202202/%EF%BC%88%E5%B7%B2%E4%BC%A0%EF%BC%8913-52-17%20QMC6310%20Datasheet%20Rev.C(1).pdf

    # I2C address  of QMC6310 compass sensor
    DEF_ADDR = 0x1C

    '''
    # Define register address of QMC6310 compass sensor
    '''
    QMC6310_REG_DATA_START = 0x01
    QMC6310_REG_DTAT_X= 0x01 # 0x01, 0x02
    QMC6310_REG_DTAT_Y= 0x03 # 0x03, 0x04
    QMC6310_REG_DTAT_Z= 0x05 # 0x05, 0x06

    QMC6310_REG_STATUS     = 0x09
    QMC6310_REG_CONTROL_1  = 0x0A
    QMC6310_REG_CONTROL_2  = 0x0B

    '''
    # Define the register parameter configuration of the sensor
    '''
    QMC6310_VAL_MODE_SUSPEND    = 0 << 0
    QMC6310_VAL_MODE_NORMAL     = 1 << 0
    QMC6310_VAL_MODE_SINGLE     = 2 << 0
    QMC6310_VAL_MODE_CONTINUOUS = 3 << 0

    QMC6310_VAL_ODR_10HZ  = 0 << 2
    QMC6310_VAL_ODR_50HZ  = 1 << 2
    QMC6310_VAL_ODR_100HZ = 2 << 2
    QMC6310_VAL_ODR_200HZ = 3 << 2

    QMC6310_VAL_OSR1_8 = 0 << 4
    QMC6310_VAL_OSR1_4 = 1 << 4
    QMC6310_VAL_OSR1_2 = 2 << 4
    QMC6310_VAL_OSR1_1 = 3 << 4
    QMC6310_VAL_OSR2_1 = 0 << 6
    QMC6310_VAL_OSR2_2 = 1 << 6
    QMC6310_VAL_OSR2_4 = 2 << 6
    QMC6310_VAL_OSR2_8 = 3 << 6

    QMC6310_VAL_MODE_SET_RESET_ON  = 0 << 0
    QMC6310_VAL_MODE_SET_ON        = 1 << 0
    QMC6310_VAL_MODE_SET_RESET_OFF = 2 << 0

    RANGE = {
        "30G":0 << 2, # 1000 LSB/Gauss
        "12G":1 << 2, # 2500 LSB/Gauss
        "8G":2 << 2, # 3750 LSB/Gauss
        "2G":3 << 2, # 15000 LSB/Gauss
    }

    LSB = {
        "30G":1, # 1 LSB/mGauss
        "12G":2.5, # 2.5 LSB/mGauss
        "8G":3.75, # 3.75 LSB/mGauss
        "2G":15, # 15 LSB/mGauss
    }

    QMC6310_VAL_SELF_TEST_ON  = 1 << 6
    QMC6310_VAL_SELF_TEST_OFF = 0 << 6
    QMC6310_VAL_SOFT_RST_ON   = 1 << 7
    QMC6310_VAL_SOFT_RST_OFF  = 0 << 7

    def __init__(self, bus: SMBus, addr: int = DEF_ADDR, field_range="8G"):
        """
        Initialize QMC6310 magnetometer
        
        Parameters:
            bus: I2C bus
            addr: Device I2C address, default is DEF_ADDR (0x1C)
            field_range: Magnetic field range ("30G", "12G", "8G", "2G")
        """
        self.bus = bus
        self.ADDR = addr
        
        # Check if device is available
        try:
            self.bus.read_byte(self.ADDR)
        except Exception:
            raise IOError("QMC6310 is not available")
        
        if field_range in ["30G", "12G", "8G", "2G"]:
            self.field_range = field_range
        else:
            self.field_range = "8G"
            raise ValueError("field_range must be one of ['30G', '12G', '8G', '2G']")

        # Initialize
        self.bus.write_byte_data(self.ADDR, 0x29, 0x06)
        self.bus.write_byte_data(self.ADDR, self.QMC6310_REG_CONTROL_2, self.RANGE[field_range])
        self.bus.write_byte_data(self.ADDR, self.QMC6310_REG_CONTROL_1, 
            self.QMC6310_VAL_MODE_NORMAL | self.QMC6310_VAL_ODR_200HZ | self.QMC6310_VAL_OSR1_8 | self.QMC6310_VAL_OSR2_8)

    def read_raw(self):
        """
        Read raw magnetometer data
        
        Returns:
            list: [x, y, z] raw magnetic field values
        """
        # Read 6 bytes starting from data register
        result = self.bus.read_i2c_block_data(self.ADDR, self.QMC6310_REG_DATA_START, 6)
        x = convert_2_int16(result[1] << 8 | result[0])
        y = convert_2_int16(result[3] << 8 | result[2])
        z = convert_2_int16(result[5] << 8 | result[4])
        return [x, y, z]
        
    def read_magnet(self):
        """
        Read magnetometer data in Gauss units (consistent with other magnetometer classes)
        
        Returns:
            tuple: (x, y, z) magnetic field values in Gauss
        """
        raw_data = self.read_raw()
        lsb_value = self.LSB[self.field_range]
        # Convert to Gauss (divide by 1000 since LSB is in mGauss)
        return (raw_data[0] / (lsb_value * 1000), raw_data[1] / (lsb_value * 1000), raw_data[2] / (lsb_value * 1000))
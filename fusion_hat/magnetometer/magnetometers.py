from fusion_hat.modules.mpu6050 import MPU6050
from smbus2 import SMBus
from enum import Enum
import time

# I2C bus ID
I2C_BUS = 1 

class MagnetometerType(Enum):
    mag_QMC6310 = 1
    mag_QMC5883P = 2
    mag_QMC5883L = 3
    mag_HMC5883L = 4

def convert_2_int16(value):
    if value > 32767:
        value = -(65536 - value)
    return value

def i2c_ack(bus, addr):
    """
    Check if a device responds at the specified I2C address
    
    Parameters:
        bus: SMBus instance
        addr: I2C address to check
    
    Returns:
        bool: True if the device responds, False otherwise
    """
    try:
        bus.read_byte(addr)
        return True
    except Exception:
        return False

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


#----------------  magnetometer ----------------
class Magnetometer:
    """
    Magnetometer sensor driver class
    Integrates QMC6310, HMC5883L, QMC5883L, and QMC5883P magnetometers
    """
    
    def __init__(self, mag_type=None, field_range="8G"):
        """
        Initialize the magnetometer based on the specified type
        
        Parameters:
            mag_type: The type of magnetometer to initialize (use None for auto-detection)
            field_range: Magnetic field range for QMC6310 ("30G", "12G", "8G", "2G")
        """
        self.active_magnetometer = None
        self.mag_type = None
        self.mpu = None
        
        try:
            self.bus = SMBus(I2C_BUS)
            
            if mag_type == MagnetometerType.mag_QMC6310:
                try:
                    self.active_magnetometer = QMC6310(self.bus, addr=0x1C, field_range=field_range)
                    self.mag_type = "QMC6310"
                    print(f"Magnetometer: {self.mag_type} @0x1C")
                except Exception as e:
                    print(f"Failed to initialize QMC6310: {e}")
                    # If QMC6310 failed but was explicitly requested, don't try others
                    if mag_type == MagnetometerType.mag_QMC6310:
                        return
            else:
                try:
                    self.mpu = MPU6050(bus=I2C_BUS)
                    self.mpu.enable_bypass()
                    print("MPU6050 bypass enabled")
                except Exception as e:
                    print(f"MPU6050 bypass mode failed: {e}")
            
                if mag_type == MagnetometerType.mag_QMC5883P or (mag_type is None and i2c_ack(self.bus, 0x2C)):
                    try:
                        self.active_magnetometer = QMC5883P(self.bus, addr=0x2C)
                        self.mag_type = "QMC5883P"
                        print(f"Magnetometer: {self.mag_type} @0x2C")
                    except Exception as e:
                        print(f"Failed to initialize QMC5883P: {e}")
                
                if mag_type == MagnetometerType.mag_QMC5883L or (mag_type is None and i2c_ack(self.bus, 0x0D)):
                    try:
                        self.active_magnetometer = QMC5883L(self.bus, addr=0x0D)
                        self.mag_type = "QMC5883L"
                        print(f"Magnetometer: {self.mag_type} @0x0D")
                    except Exception as e:
                        print(f"Failed to initialize QMC5883L: {e}")
                
                if mag_type == MagnetometerType.mag_HMC5883L or (mag_type is None and i2c_ack(self.bus, 0x1E)):
                    try:
                        self.active_magnetometer = HMC5883L(self.bus, addr=0x1E)
                        self.mag_type = "HMC5883L"
                        print(f"Magnetometer: {self.mag_type} @0x1E")
                    except Exception as e:
                        print(f"Failed to initialize HMC5883L: {e}")
                
                if self.active_magnetometer is None:
                    print("No magnetometer found on 0x1C/0x2C/0x0D/0x1E; running without active_magnetometer.")
                    
        except Exception as e:
            print(f"Error during magnetometer initialization: {e}")
            self.active_magnetometer = None
    
    def read(self):
        """
        Read magnetometer data
        
        Returns:
            tuple: (x, y, z) magnetic field values in appropriate units based on sensor type
            None: if no magnetometer is initialized
        """
        if self.active_magnetometer is None:
            return None
        
        try:
            # Now all magnetometer classes have a consistent read_magnet method
            return self.active_magnetometer.read_magnet()
        except Exception as e:
            print(f"Error reading magnetometer: {e}")
            return None
    
    def get_type(self):
        """
        Get the type of initialized magnetometer
        
        Returns:
            str: Magnetometer type
        """
        return self.mag_type


# Example usage
if __name__ == "__main__":
    # Auto-detect magnetometer (default behavior)
    mag = Magnetometer()
    
    # Alternative: Specify magnetometer type using enum
    # mag = Magnetometer(mag_type=MagnetometerType.mag_QMC6310)
    # mag = Magnetometer(mag_type=MagnetometerType.mag_QMC5883P)
    # mag = Magnetometer(mag_type=MagnetometerType.mag_QMC5883L)
    # mag = Magnetometer(mag_type=MagnetometerType.mag_HMC5883L)
    
    print(f"Initialized magnetometer type: {mag.get_type()}")
    
    # Read and print data if magnetometer is initialized
    if mag.get_type():
        try:
            while True:
                data = mag.read()
                if data:
                    print(f"Magnetic field: X={data[0]:.2f}, Y={data[1]:.2f}, Z={data[2]:.2f}")
                time.sleep(0.5)
        except KeyboardInterrupt:
            print("\nMeasurement stopped by user")
    else:
        print("No magnetometer available")


from fusion_hat.modules.mpu6050 import MPU6050
from smbus2 import SMBus
from enum import Enum
import time
from mag_utils import i2c_ack
from HMC5883L import HMC5883L
from QMC5883L import QMC5883L
from QMC5883P import QMC5883P
from QMC6310 import QMC6310

# I2C bus ID
I2C_BUS = 1 

class MagnetometerType(Enum):
    mag_QMC6310 = 1
    mag_QMC5883P = 2
    mag_QMC5883L = 3
    mag_HMC5883L = 4

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


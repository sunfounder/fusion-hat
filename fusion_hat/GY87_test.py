#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from smbus2 import SMBus
import time
import math
from fusion_hat.modules.mpu6050 import MPU6050


I2C_BUS = 1  

def scan_i2c(bus_id=I2C_BUS):
    """
    Scan the I2C bus for all responding device addresses
    
    Parameters:
        bus_id: I2C bus number, defaults to I2C_BUS (1)
    
    Returns:
        found: list of all detected I2C device addresses
    """
    found = []
    with SMBus(bus_id) as b:
        for addr in range(0x03, 0x78):  # I2C address range (0x03–0x77)
            try:
                b.read_byte(addr)
                found.append(addr)
            except Exception:
                pass
    return found

# ------------------------ Tool Function ------------------------
def tilt_comp_heading(mx, my, mz, ax, ay, az, decl_deg=0.0):
    """
    Calculate tilt-compensated heading: Use accelerometer data to calculate roll/pitch angles, then compensate magnetometer data
    
    Parameters:
        mx, my, mz: Three-axis data from the magnetometer (Gauss)
        ax, ay, az: Three-axis data from the accelerometer (g)
        decl_deg: Magnetic declination (degrees), used to convert magnetic north to true north
    
    Returns:
        hdg: Compensated heading angle, range 0-360 degrees
    """

    roll = math.atan2(ay, az)
    pitch = math.atan2(-ax, max(1e-6, math.sqrt(ay*ay + az*az)))
    mx2 = mx * math.cos(pitch) + mz * math.sin(pitch)
    my2 = mx * math.sin(roll) * math.sin(pitch) + my * math.cos(roll) - mz * math.sin(roll) * math.cos(pitch)
    hdg = math.degrees(math.atan2(my2, mx2)) + decl_deg

    if hdg < 0: hdg += 360.0
    if hdg >= 360.0: hdg -= 360.0
    return hdg

class ExtendedMPU6050(MPU6050):
    """
    Enable MPU6050 bypass mode
    """
    # REG ADDER
    REG_INT_PIN_CFG = 0x37    # INT_PIN_CFG
    REG_USER_CTRL = 0x6A      # USER_CTRL
    REG_WHO_AM_I = 0x75       # WHO_AM_I
    
    def enable_bypass(self):
        """
        Enable MPU6050 bypass mode
        """

        self.bus.write_byte_data(self.address, self.REG_USER_CTRL, 0x00)
        time.sleep(0.002)  
        # open I2C bypass mode, connect SDA/SCL to auxiliary I2C device
        self.bus.write_byte_data(self.address, self.REG_INT_PIN_CFG, 0x02)
        time.sleep(0.002) 
        
        uc = self.bus.read_byte_data(self.address, self.REG_USER_CTRL)
        ic = self.bus.read_byte_data(self.address, self.REG_INT_PIN_CFG)
        print(f"Bypass enabled: USER_CTRL=0x{uc:02X}, INT_PIN_CFG=0x{ic:02X}")
    

# ------------------------ HMC5883L ------------------------
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

# ------------------------ QMC5883L ------------------------
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

# ------------------------ QMC5883P ------------------------
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

# ------------------------ BMP180 ------------------------
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

# ------------------------ GY-87  ------------------------
class GY87:
    """
    GY-87 sensor module main class
    Integrate MPU6050 (accelerometer + gyroscope), BMP180 (barometer), and magnetometer (support multiple models)
    Provide complete sensor data reading functionality, including self-recovery mechanism
    """
    
    def __init__(self, bus_id=I2C_BUS, decl_deg=0.0):
        self.bus = SMBus(bus_id)
        self.mpu = ExtendedMPU6050(bus=bus_id)
        self.bmp = BMP180(self.bus)
        self.decl_deg = float(decl_deg)

        # Enable MPU6050 I2C bypass mode
        self.mpu.enable_bypass()

        # ---- Intelligent magnetometer auto-detection mechanism ----
        # Try detecting different magnetometer models in priority order
        # 1. QMC5883P (@0x2C) → 2. QMC5883L (@0x0D) → 3. HMC5883L (@0x1E)
        self.mag = None
        
        def i2c_ack(addr):
            """
            Check if a device responds at the specified I2C address
            
            Parameters:
                addr: I2C address to check
            
            Returns:
                bool: True if the device responds, False otherwise
            """
            try:
                self.bus.read_byte(addr)
                return True
            except Exception:
                return False

        # Try initializing magnetometer in priority order
        if i2c_ack(0x2C):
            self.mag = QMC5883P(self.bus, addr=0x2C)
            print("Magnetometer: QMC5883P @0x2C")
        elif i2c_ack(0x0D):
            try:
                self.mag = QMC5883L(self.bus, addr=0x0D)
                print("Magnetometer: QMC5883L @0x0D")
            except Exception:
                pass
        elif i2c_ack(0x1E):
            try:
                self.mag = HMC5883L(self.bus, addr=0x1E)
                print("Magnetometer: HMC5883L @0x1E")
            except Exception:
                pass
        else:
            print("No magnetometer found on 0x2C/0x0D/0x1E; running without MAG.")

    def read_all(self):
        """
        Read all sensor data
        Include automatic error handling and self-recovery mechanism to ensure system stability
        
        Returns:
            dict: Dictionary containing all sensor data
                  {accel_g: (x,y,z), gyro_dps: (x,y,z), temp_mpu_c: float, 
                   temp_bmp_c: float, pressure_pa: float, altitude_m: float,
                   mag_gauss: (x,y,z), heading_deg: float}
        """
        def _safe(f, default):
            try:
                return f()
            except Exception:
                try:
                    self.mpu = ExtendedMPU6050(bus=I2C_BUS)
                    self.mpu.enable_bypass()
                except Exception:
                    pass
                try:
                    return f()
                except Exception:
                    return default

        # read MPU6050 sensor data
        ax, ay, az = _safe(lambda: self.mpu.get_accel_data(g=True), (0.0, 0.0, 0.0))  # unit: g
        gx, gy, gz = _safe(self.mpu.get_gyro_data,  (0.0, 0.0, 0.0))   # unit: dps
        t_mpu      = _safe(self.mpu.get_temp, 0.0)              # unit: °C
        
        # read BMP180 sensor data
        try:
            t_bmp, p_pa, alt = self.bmp.read()
        except Exception:
            t_bmp, p_pa, alt = (0.0, 0.0, 0.0)

        result = {
            "accel_g": (ax, ay, az),
            "gyro_dps": (gx, gy, gz),
            "temp_mpu_c": t_mpu,
            "temp_bmp_c": t_bmp,
            "pressure_pa": p_pa,
            "altitude_m": alt
        }
        
        if self.mag is not None:
            try:
                mx, my, mz = self.mag.read_magnet()
            except Exception:
                mx = my = mz = 0.0
            
            heading = tilt_comp_heading(mx, my, mz, ax, ay, az, decl_deg=self.decl_deg)

            result.update({"mag_gauss": (mx, my, mz), "heading_deg": heading})
        
        return result


# ------------------------ loop  ------------------------
def demo_loop():
    """
    GY-87 sensor module demo loop function
    
    Functions:
        1. Scan and display connected I2C devices
        2. Initialize the GY87 sensor module
        3. Continuously read and display all sensor data
        4. Adjust output format based on magnetometer presence
    
    Output format:
        - With magnetometer: displays acceleration, angular velocity, magnetic field strength, heading, temperature, pressure, and altitude
        - Without magnetometer: displays all data except magnetic field strength and heading
    
    Sampling frequency:
        ~5 Hz (0.2 s pause after each read)
    """
    addrs = scan_i2c()
    print("I2C devices found:", ["0x%02X" % a for a in addrs])


    # decl_deg: 磁偏角（度），根据实际地理位置设置，以提高航向角精度
    # 可在 https://www.magnetic-declination.com/ 查询当地磁偏角
    dev = GY87(decl_deg=0.0)
    
    print("reading data...(press Ctrl+C to exit)")
    
    has_mag = dev.mag is not None

    while True:
        d = dev.read_all()
        
        if has_mag:
            print(
                "ACC(g): x={:+.3f} y={:+.3f} z={:+.3f} | " 
                "GYR(dps): x={:+.1f} y={:+.1f} z={:+.1f} | "
                "MAG(G): x={:+.3f} y={:+.3f} z={:+.3f} | "
                "HDG(tilt-comp): {:6.1f}° | "
                "TMP(°C): MPU={:+.2f} BMP={:+.2f} | "
                "P(Pa): {:,.0f} | ALT(m): {:+.2f}".format(
                    *d["accel_g"], *d["gyro_dps"],
                    *d.get("mag_gauss", (0.0,0.0,0.0)), d.get("heading_deg", float("nan")),
                    d["temp_mpu_c"], d["temp_bmp_c"],
                    d["pressure_pa"], d["altitude_m"]
                )
            )
        else:
            print(
                "ACC(g): x={:+.3f} y={:+.3f} z={:+.3f} | " 
                "GYR(dps): x={:+.1f} y={:+.1f} z={:+.1f} | "
                "TMP(°C): MPU={:+.2f} BMP={:+.2f} | "
                "P(Pa): {:,.0f} | ALT(m): {:+.2f}".format(
                    *d["accel_g"], *d["gyro_dps"],
                    d["temp_mpu_c"], d["temp_bmp_c"],
                    d["pressure_pa"], d["altitude_m"]
                )
            )
        
        time.sleep(0.2)

if __name__ == "__main__":
    try:
        demo_loop()
    except KeyboardInterrupt:
        print("\n exit。")
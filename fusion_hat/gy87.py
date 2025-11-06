#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from smbus2 import SMBus
import time
import math
from fusion_hat.modules.mpu6050 import MPU6050
from fusion_hat.magnetometers import HMC5883L, QMC5883L, QMC5883P
from fusion_hat.bmp180 import BMP180

I2C_BUS = 1  

# ------------------------ I2C scan function ------------------------
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

# ------------------------ GY-87  ------------------------
class GY87:
    """
    GY-87 sensor module main class
    Integrate MPU6050 (accelerometer + gyroscope), BMP180 (barometer), and magnetometer (support multiple models)
    Provide complete sensor data reading functionality, including self-recovery mechanism
    """
    
    def __init__(self, bus_id=I2C_BUS, decl_deg=0.0):
        self.bus = SMBus(bus_id)
        self.mpu = MPU6050(bus=bus_id)
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
                    self.mpu = MPU6050(bus=I2C_BUS)
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


    # decl_deg: magnetic declination (degrees), set according to actual geographic location to improve heading accuracy
    # You can look up the local magnetic declination at https://www.magnetic-declination.com/
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
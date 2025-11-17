#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from smbus2 import SMBus
import time
import math
from fusion_hat.modules import Magnetometer,MPU6050,BMP180
 
I2C_BUS = 1  

# ------------------------ I2C scan function ------------------------
def scan_i2c_addr(bus_id=I2C_BUS):
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
        self.bmp = BMP180(self.bus)
        self.decl_deg = float(decl_deg)

        # Use Magnetometer class for auto-detection of magnetometer type
        self.magnetometer = Magnetometer(mag_type=None, field_range="8G")
        self.mag = self.magnetometer.active_magnetometer
        self.mpu = self.magnetometer.mpu

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
                    # try again to enable bypass mode
                    self.magnetometer.mpu = MPU6050(bus=I2C_BUS)
                    self.magnetometer.mpu.enable_bypass()
                    self.mpu = self.magnetometer.mpu  # update self.mpu reference
                except Exception:
                    print("Failed to reinitialize MPU6050")
                try:
                    return f()
                except Exception:
                    return default
        
        # read MPU6050 sensor data
        if self.mpu is not None:
            ax, ay, az = _safe(lambda: self.mpu.get_accel_data(g=True), (0.0, 0.0, 0.0))  # unit: g
            gx, gy, gz = _safe(self.mpu.get_gyro_data,  (0.0, 0.0, 0.0))   # unit: dps
            t_mpu      = _safe(self.mpu.get_temp, 0.0)              # unit: °C
        else:
            ax, ay, az = (0.0, 0.0, 0.0)
            gx, gy, gz = (0.0, 0.0, 0.0)
            t_mpu = 0.0
        
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
    addrs = scan_i2c_addr()
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
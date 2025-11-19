#!/usr/bin/env python3
# from robot_hat import I2C, fileDB

from fusion_hat._config import Config
from fusion_hat.modules import Magnetometer
from fusion_hat.modules.magnetometer import MagnetometerType
import time
from math import pi, atan2, degrees


class Compass(Magnetometer):
    """Compass module for reading and calculating heading angles from magnetometer data.
    
    This class extends the Magnetometer class to provide compass functionality
    that can be easily integrated into projects requiring heading information.
    
    Public Methods:
        read_raw(): Get raw magnetic field data
        read(): Get processed compass data including heading angle
        read_angle(): Get just the heading angle (with optional filtering)
        set_offset(): Calibrate the compass with offset values
        set_magnetic_declination(): Adjust for local magnetic declination
        clear_calibration(): Reset all calibration data
    """

    FILTER_SIZE = 30

    def __init__(self, placement=["x", "y", "z"], 
                 offset=[0, 0, 0, 0, 0, 0],
                 declination="0°0'W",
                 field_range="8G"):
        """Initialize the Compass module.
        
        Args:
            placement (list, optional): Axis orientation of the compass. Defaults to ["x", "y", "z"].
                Can include negative signs to indicate inverted axes (e.g., ["-x", "y", "z"]).
            offset (list, optional): Calibration offsets in mGauss. Format: [x_min, x_max, y_min, y_max, z_min, z_max].
                Defaults to [0, 0, 0, 0, 0, 0].
            declination (str, optional): Magnetic declination. Defaults to "0°0'W".
            field_range (str, optional): Magnetic field measurement range. Defaults to "8G".
        """

        super().__init__(mag_type=MagnetometerType.mag_QMC6310, field_range=field_range)

        self.placement = placement
        self.x_min = 0
        self.x_max = 0
        self.y_min = 0
        self.y_max = 0
        self.z_min = 0
        self.z_max = 0
        self.x_offset = 0
        self.y_offset = 0
        self.z_offset = 0
        self.x_scale = 0
        self.y_scale = 0
        self.z_scale = 0
        self.magnetic_declination_str = "0°0'W"
        self.magnetic_declination_angle = 0
        # set offset
        self.set_offset(offset)
        self.set_magnetic_declination(declination)
        # filter
        self.filter_buffer = [0]*self.FILTER_SIZE
        self.filter_index = 0
        self.filter_sum = 0
        # init filter
        for _ in range(self.FILTER_SIZE):
            self.read_angle(filter=True)
    
    def read_raw(self):
        """Read raw magnetometer data.
        
        Returns:
            list: Raw magnetic field data [x, y, z] in mGauss.
        """
        mag_data = Magnetometer.read(self)
        if mag_data is None:
            return [0, 0, 0]
        
        # Convert from Gauss to mGauss and return as list
        return [mag_data[0] * 1000, mag_data[1] * 1000, mag_data[2] * 1000]


    def angle_str_2_number(self, str):
        """Convert magnetic declination from string format to numerical value.
        
        Args:
            str (str): Magnetic declination in format "DD°MM'E" or "DD°MM'W".
            
        Returns:
            float: Magnetic declination in degrees (positive for East, negative for West).
        """
        parts = str.split("°")
        degree = int(parts[0])
        parts = parts[1].split("'")
        minute = int(parts[0])
        direction = parts[1]
        if direction == "W":
            return -degree - minute / 60
        elif direction == "E":
            return degree + minute / 60
        
    def angle_number_2_str(self, number):
        """Convert magnetic declination from numerical value to string format.
        
        Args:
            number (float): Magnetic declination in degrees (positive for East, negative for West).
            
        Returns:
            str: Magnetic declination in format "DD°MM'E" or "DD°MM'W".
        """
        degree = int(number)
        minute = int((number - degree) * 60)
        direction = "E"
        if number < 0:
            direction = "W"
            degree = -degree
        return str(degree) + "°" + str(minute) + "'" + direction

    def set_magnetic_declination(self, str):
        """Set magnetic declination from string format.
        
        Args:
            str (str): Magnetic declination in format "DD°MM'E" or "DD°MM'W".
        """
        self.magnetic_declination_angle = self.angle_str_2_number(str)

    def read(self):
        """Read processed compass data.
        
        Returns:
            tuple: Processed magnetic field data (x, y, z, angle) where:
                x, y, z are in mGauss after applying offsets,
                angle is the heading angle in degrees.
        """
        # Get data from magnetometer (already in Gauss)

        # mag_data = Magnetometer.read(self)
        # if mag_data is None:
        #     return (0, 0, 0, 0)
        
        # # Convert from Gauss to mGauss
        # x_mG = mag_data[0] * 1000
        # y_mG = mag_data[1] * 1000
        # z_mG = mag_data[2] * 1000

        mag_data = self.read_raw()
        if mag_data is None:
            return (0, 0, 0, 0)
        
        # Convert from Gauss to mGauss
        x_mG,y_mG,z_mG = mag_data
        
        # Apply offsets
        x_mG = x_mG - self.x_offset
        y_mG = y_mG - self.y_offset
        z_mG = z_mG - self.z_offset

        temp = {
            'x': [x_mG, self.x_offset],
            'y': [y_mG, self.y_offset],
            'z': [z_mG, self.z_offset],
            '-x': [-x_mG, -self.x_offset],
            '-y': [-y_mG, -self.y_offset],
            '-z': [-z_mG, -self.z_offset],
        }
        a = temp[self.placement[0]][0]
        b = temp[self.placement[1]][0]
        a_offset = temp[self.placement[0]][1]
        b_offset = temp[self.placement[1]][1]
        # a = a - a_offset
        # b = b - b_offset

        # angle = atan2(a, b) *180 / pi
        # if angle < 0:
        #     angle += 360

        angle = degrees(atan2(b, a)) - self.magnetic_declination_angle
        angle = (angle + 360) % 360

        return (x_mG, y_mG, z_mG, round(angle, 2))
    
    def read_angle(self, filter=False):
        """Read the current heading angle.
        
        Args:
            filter (bool, optional): Whether to apply moving average filter. Defaults to False.
            
        Returns:
            float: Heading angle in degrees (0-360).
        """
        _value = self.read()[3]
        if not filter:
            return _value
        else:
            self.filter_sum = self.filter_sum - self.filter_buffer[self.filter_index] + _value
            self.filter_buffer[self.filter_index] = _value
            self.filter_index += 1
            if self.filter_index >= self.FILTER_SIZE:
                self.filter_index = 0
            _value = self.filter_sum / self.FILTER_SIZE
            return round(_value, 2)

    def set_offset(self, offset):
        """Set calibration offsets for the magnetometer.
        
        Args:
            offset (list): Calibration offsets in mGauss. Format: [x_min, x_max, y_min, y_max, z_min, z_max].
        
        Reference:
            https://www.appelsiini.net/2018/calibrate-magnetometer/
        """
        self.x_min = offset[0]
        self.x_max = offset[1]
        self.y_min = offset[2]
        self.y_max = offset[3]
        self.z_min = offset[4]
        self.z_max = offset[5]
        # hard iron calibration
        self.x_offset = (self.x_min + self.x_max) / 2
        self.y_offset = (self.y_min + self.y_max) / 2
        self.z_offset = (self.z_min + self.z_max) / 2
        # soft iron calibration
        # avg_delta_x = (self.x_max - self.x_min) / 2
        # avg_delta_y = (self.y_max - self.y_min) / 2
        # avg_delta_z = (self.z_max - self.z_min) / 2
        # avg_delta = (avg_delta_x + avg_delta_y + avg_delta_z) / 3
        # self.x_scale = avg_delta / avg_delta_x
        # self.y_scale = avg_delta / avg_delta_y
        # self.z_scale = avg_delta / avg_delta_z
        # corrected_x = (sensor_x - offset_x) * x_scale
        # corrected_y = (sensor_y - offset_y) * y_scale
        # corrected_z = (sensor_z - offset_z) * z_scale

        # print(f"compass offset: {self.x_offset} {self.y_offset} {self.z_offset} scale: {self.x_scale} {self.y_scale} {self.z_scale}")

    def set_magnetic_declination(self, angle):
        """Set magnetic declination.
        
        Args:
            angle (str or float or int): Magnetic declination. Can be either:
                - String format: "DD°MM'E" or "DD°MM'W"
                - Numeric format: Degrees (positive for East, negative for West)
        """
        if isinstance(angle, str):
            self.magnetic_declination_str = angle
            self.magnetic_declination_angle = self.angle_str_2_number(angle)
        elif isinstance(angle, float) or isinstance(angle, int):
            self.magnetic_declination_angle = float(angle)
            self.magnetic_declination_str = self.angle_number_2_str(angle)

    def clear_calibration(self):
        """Clear all calibration data.
        
        Resets all minimum/maximum values and offsets to zero.
        """
        self.x_min = 0
        self.x_max = 0
        self.y_min = 0
        self.y_max = 0
        self.z_min = 0
        self.z_max = 0
        self.x_offset = 0
        self.y_offset = 0

        
        self.z_offset = 0

if __name__ == '__main__':
    compass = Compass(placement=['x', 'y', 'z'], field_range='8G')

    while True:
        x, y, z, angle = compass.read()
        print(f"x: {x:.2f} mGuass   y: {y:.2f} mGuass   z: {z:.2f} mGuass   angle: {angle}°")
        time.sleep(0.5)

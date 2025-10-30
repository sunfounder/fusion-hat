from ..adc import ADC
from .._utils import constrain

class Grayscale_Module(object):
    """3 channel Grayscale Module"""

    LEFT = 0
    """Left Channel"""
    MIDDLE = 1
    """Middle Channel"""
    RIGHT = 2
    """Right Channel"""

    REFERENCE_DEFAULT = [1000]*3

    def __init__(self, pin0: ADC, pin1: ADC, pin2: ADC, reference: int = None):
        """
        Initialize Grayscale Module

        :param pin0: ADC object or int for channel 0
        :type pin0: fusion_hat.ADC/int
        :param pin1: ADC object or int for channel 1
        :type pin1: fusion_hat.ADC/int
        :param pin2: ADC object or int for channel 2
        :type pin2: fusion_hat.ADC/int
        :param reference: reference voltage
        :type reference: 1*3 list, [int, int, int]
        """
        self.pins = (pin0, pin1, pin2)
        for i, pin in enumerate(self.pins):
            if not isinstance(pin, ADC):
                raise TypeError(f"pin{i} must be fusion_hat.ADC")
        self._reference = self.REFERENCE_DEFAULT

    def reference(self, ref: list = None) -> list:
        """
        Get Set reference value

        :param ref: reference value, None to get reference value
        :type ref: list
        :return: reference value
        :rtype: list
        """
        if ref is not None:
            if isinstance(ref, list) and len(ref) == 3:
                self._reference = ref
            else:
                raise TypeError("ref parameter must be 1*3 list.")
        return self._reference

    def read_status(self, datas: list = None) -> list:
        """
        Read line status

        :param datas: list of grayscale datas, if None, read from sensor
        :type datas: list
        :return: list of line status, 0 for white, 1 for black
        :rtype: list
        """
        if self._reference == None:
            raise ValueError("Reference value is not set")
        if datas == None:
            datas = self.read()
        return [0 if data > self._reference[i] else 1 for i, data in enumerate(datas)]

    def read(self, channel: int = None) -> list:
        """
        read a channel or all datas

        :param channel: channel to read, leave empty to read all. 0, 1, 2 or Grayscale_Module.LEFT, Grayscale_Module.CENTER, Grayscale_Module.RIGHT 
        :type channel: int/None
        :return: list of grayscale data
        :rtype: list
        """
        if channel == None:
            return [self.pins[i].read() for i in range(3)]
        else:
            return self.pins[channel].read()

class LineTracker(object):
    """Line Tracker"""
    LINE_DIFF = 200
    CLIFF_THRESHOLD = 120

    LINE_REFERENCE_UPDATE_RATE = 0.05

    def __init__(self, left: ADC, middle: ADC, right: ADC, slopes: list = None, offsets: list = None):
        """
        Initialize Line Tracker
        
        Args:
            left (ADC): ADC object for left sensor
            middle (ADC): ADC object for middle sensor
            right (ADC): ADC object for right sensor
        """
        self.left = left
        self.middle = middle
        self.right = right
        self.sensors = [left, middle, right]
        if slopes is None:
            slopes = [1, 1, 1]
        if offsets is None:
            offsets = [0, 0, 0]
        self.slopes = slopes
        self.offsets = offsets
        self.line_background_reference = 1000
        self.line_reference = 200
        self.cliff_threshold = self.CLIFF_THRESHOLD

    def read_channel(self, channel: int, raw: bool = False) -> int:
        """
        Read a channel

        Args:
            channel (int): channel to read, 0, 1, 2 or Grayscale_Module.LEFT, Grayscale_Module.CENTER, Grayscale_Module.RIGHT
            raw (bool): if True, return raw data, False to return calibrated data

        Returns:
            int: grayscale data
        """
        value = self.sensors[channel].read()
        if not raw:
            value = value * self.slopes[channel] + self.offsets[channel]
            value = round(value)
        return value

    def calibrate_data(self, data: list) -> list:
        """
        Calibrate grayscale data
        Args:
            data (list): list of grayscale data
        Returns:
            list: list of calibrated grayscale data
        """
        calibrated = []
        for i in range(3):
            value = data[i] * self.slopes[i] + self.offsets[i]
            value = int(round(value))
            calibrated.append(value)
        return calibrated

    def read(self, raw: bool = False) -> list:
        """
        Read line status

        Args:
            raw (bool): if True, return raw data, False to return calibrated data

        Returns:
            list: list of line status, 0 for white, 1 for black
        """
        return [self.read_channel(i, raw) for i in range(3)]

    def is_on_cliff(self, data: list = None) -> bool:
        """
        Check if robot is on cliff

        Args:
            data (list): list of grayscale data, leave empty to read from sensor

        Returns:
            bool: True if robot is on cliff, False otherwise
        """
        if data is None:
            left, middle, right = self.read()
        else:
            left, middle, right = data
        return left < self.cliff_threshold or middle < self.cliff_threshold or right < self.cliff_threshold

    def get_line_position(self, data: list = None):
        """
        Get line position

        Args:
            data (list): list of grayscale data, leave empty to read from sensor

        Returns:
            float: line position, -1 for left, 0 for center, 1 for right
        """

        if data is None:
            data = self.read()

        L, M, R = data

        # Calculate weight (grayscale value lower, weight higher)
        w_L = (self.line_background_reference - L) / (self.line_background_reference - self.line_reference)
        w_M = (self.line_background_reference - M) / (self.line_background_reference - self.line_reference)
        w_R = (self.line_background_reference - R) / (self.line_background_reference - self.line_reference)

        # contrain weight to 0-1
        w_L = constrain(w_L, 0, 1)
        w_M = constrain(w_M, 0, 1)
        w_R = constrain(w_R, 0, 1)

        # Calculate sum of weights
        sum_w = w_L + w_M + w_R

        # Return 0 if the difference is too small
        if sum_w < 0.2:
            return 0.0
        
        # Return 0 if the robot is not on the line
        if not self.is_on_line(data=data):
            return 0.0

        # Calculate position
        if (w_L >= 0.2 and w_M < 0.2 and w_R < 0.2):
            position = w_L - 1.8
        elif (w_R >= 0.2 and w_M < 0.2 and w_L < 0.2):
            position = 1.8 - w_R
        else:
            position = ( w_R -w_L )/ sum_w
            # Update background reference and line reference only at least two sensor is on line
            self.update_line_background_reference(data)
            self.update_line_reference(data)

        position = position / 1.5
        position = constrain(position, -1, 1)
        position = round(position, 2)
        return position

    def is_on_line(self, data: list = None) -> bool:
        """
        Check if robot is on line

        Args:
            data (list): list of grayscale data, leave empty to read from sensor

        Returns:
            bool: True if robot is on line, False otherwise
        """
        if data is None:
            data = self.read()

        if self.is_on_cliff(data=data):
            return False
        
        min_value = min(data)
        max_value = max(data)

        return max_value - min_value > self.LINE_DIFF

    def set_calibration_data(self, slopes: list, offsets: list):
        """
        Set calibration data
        Args:
            slopes (list): list of slopes
            offsets (list): list of offsets
        """
        self.slopes = slopes
        self.offsets = offsets

    def set_cliff_threshold(self, threshold: int):
        """
        Set cliff threshold
        Args:
            threshold (int): cliff threshold
        """
        self.cliff_threshold = threshold

    def get_calibration_data(self):
        """
        Get calibration data
        Returns:
            tuple: tuple of slopes and offsets
        """
        return self.slopes, self.offsets

    def calibrate(self, light_data: list, dark_data: list):
        """
        Calibrate line tracker
        Args:
            light_data (list): list of light data
            dark_data (list): list of dark data
        """
        # Find the maximum grayscale value and its index
        max_grayscale = max(light_data)
        max_index = light_data.index(max_grayscale)
        # Calculate the other twe with linear formula y=ax+b
        slopes = []
        offsets = []
        for i in range(3):
            # Use Max Value as reference, so no need to calibrate it
            if i == max_index:
                slopes.append(1)
                offsets.append(0)
            else:
                x1 = dark_data[i]
                y1 = dark_data[max_index]
                x2 = light_data[i]
                y2 = light_data[max_index]
                if x2 - x1 <= 0 or y2 - y1 <= 0:
                    raise ValueError(f"Black value should be less than white value., light_data: {light_data}, dark_data: {dark_data}")
                a = (y2 - y1) / (x2 - x1)
                b = y1 - a * x1
                slopes.append(round(a, 2))
                offsets.append(round(b, 2))
        
        # Set calibration data
        self.set_calibration_data(slopes, offsets)
        return slopes, offsets

    def update_line_background_reference(self, current_values):
        """ Update the line background value """
        max_val = max(current_values)
        keep_rate = 1 - self.LINE_REFERENCE_UPDATE_RATE
        update_rate = self.LINE_REFERENCE_UPDATE_RATE
        self.line_background_reference = keep_rate * self.line_background_reference + update_rate * max_val

    def update_line_reference(self, current_values):
        """ Update the line reference value """
        min_val = min(current_values)
        keep_rate = 1 - self.LINE_REFERENCE_UPDATE_RATE
        update_rate = self.LINE_REFERENCE_UPDATE_RATE
        self.line_reference = keep_rate * self.line_reference + update_rate * min_val

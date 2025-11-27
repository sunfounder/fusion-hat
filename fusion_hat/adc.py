

""" Fusion Hat on-board analog to digital converter

Example:

    Import ADC
    
    >>> from fusion_hat.adc import ADC

    Init ADC channel 0

    >>> a0 = ADC(0)

    Read ADC channel 0 value

    >>> a0.read()
    2048

    Read ADC channel 0 voltage

    >>> a0.read_voltage()
    1.65
"""

from ._base import _Base
from .device import raise_if_fusion_hat_not_ready
import os

class ADC(_Base):
    """ ADC class

    Args:
        channel (int or str): channel number or Str start with A
        *args: pass to :class:`fusion_hat._base._base`
        **kwargs: pass to :class:`fusion_hat._base._base`
    
    Raises:
        ValueError: channel must be channel number or Str start with A
    """
    DEVICE_NAME = "fusion-hat"
    IIO_DEVICE_PATH_PREFIX = "/sys/bus/iio/devices/iio:device"

    def __init__(self, channel: [int, str], *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        raise_if_fusion_hat_not_ready()

        if isinstance(channel, int):
            channel = f"{channel}"
        elif isinstance(channel, str) and channel.startswith("A"):
            channel = channel[1:]
        else:
            raise ValueError("channel must be channel number or Str start with A")
        
        # 查找ADC设备的路径
        self.device_index = self.find_device()
        self.device_path = f"{self.IIO_DEVICE_PATH_PREFIX}{self.device_index}"
        
        self._channel = channel
        self.raw_path = os.path.join(self.device_path, f"in_voltage{self._channel}_raw")
        self.scale_path = os.path.join(self.device_path, f"in_voltage{self._channel}_scale")
        
        if not os.path.exists(self.raw_path):
            raise ValueError(f"ADC channel {self._channel} not found, path not exist: {self.raw_path}")
        
        with open(self.scale_path, "r") as f:
            self.scale = float(f.read().strip())
            self.scale = round(self.scale, 2)
            self.log.debug(f"ADC channel {self._channel} scale: {self.scale}")

    def find_device(self) -> int:
        """ find adc device

        Returns:
            int: adc device index
        """
        index = -1
        for i in range(10):
            dev_path = f"/sys/bus/iio/devices/iio:device{i}"
            if os.path.isdir(dev_path):
                name_path = os.path.join(dev_path, "name")
                if os.path.exists(name_path):
                    with open(name_path, "r") as f:
                        name = f.read().strip()
                        if name == self.DEVICE_NAME:
                            index = i
                            break
        if index < 0:
            raise ValueError(f"Fusion Hat ADC device '{self.DEVICE_NAME}' not found")
        return index

    def read(self) -> int:
        """ read raw value

        Returns:
            int: raw value
        """
        return self.read_raw()

    def read_raw(self) -> int:
        """ read raw value

        Returns:
            int: raw value
        """
        with open(self.raw_path, "r") as f:
            raw_value = f.read().strip()
            raw_value = int(raw_value)
        return raw_value
        
    def read_voltage(self) -> float:
        """ read voltage value in V

        Returns:
            float: voltage value in V
        """
        voltage = self.read_raw() * self.scale / 1000
        voltage = round(voltage, 2)
        self.log.debug(f"ADC channel {self._channel} voltage: {voltage}")
        return voltage

    @property
    def channel(self) -> str:
        """ get channel

        Returns:
            str: channel number
        """
        return self._channel

    @property
    def voltage(self) -> int:
        """ get voltage

        Returns:
            int: voltage value in mV
        """
        return self.read_voltage()

    @property
    def raw(self) -> int:
        """ get raw value

        Returns:
            int: raw value
        """
        return self.read_raw()

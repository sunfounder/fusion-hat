""" Battery class

Read battery data from upower

Example:
    >>> battery = Battery()
    >>> print(battery)
    Fusion Hat SunFounder Discharging 76% 7935.00 mV
    >>> print(battery.present)
    True
    >>> print(battery.online)
    True
    >>> print(battery.status)
    Discharging
    >>> print(battery.capacity)
    76
    >>> print(battery.voltage_now)
    7935
    >>> print(battery.model_name)
    Fusion HAT
    >>> print(battery.manufacturer)
    SunFounder
"""

import os
from ._base import _Base
from .device import raise_if_fusion_hat_not_ready

class Battery(_Base):
    """ Battery class

    Read battery data from upower

    Args:
        *args: pass to :class:`fusion_hat._base._base`
        **kwargs: pass to :class:`fusion_hat._base._base`
    """
    DEVICE_NAME = "fusion-hat"
    PATH = f"/sys/class/power_supply/{DEVICE_NAME}"

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        raise_if_fusion_hat_not_ready()

        self.present_path = os.path.join(self.PATH, "present")
        self.online_path = os.path.join(self.PATH, "online")
        self.status_path = os.path.join(self.PATH, "status")
        self.capacity_path = os.path.join(self.PATH, "capacity")
        self.voltage_now_path = os.path.join(self.PATH, "voltage_now")
        self.model_name_path = os.path.join(self.PATH, "model_name")
        self.manufacturer_path = os.path.join(self.PATH, "manufacturer")

    @property
    def present(self) -> bool:
        """ check if battery is present

        Returns:
            bool: True if battery is present, False otherwise
        """
        with open(self.present_path, "r") as f:
            value = f.read().strip()
            return value == "1"

    @property
    def online(self) -> bool:
        """ check if battery is online

        Returns:
            bool: True if battery is online, False otherwise
        """
        with open(self.online_path, "r") as f:
            value = f.read().strip()
            return value == "1"

    @property
    def status(self) -> str:
        """ get battery status

        Returns:
            str: battery status
        """
        with open(self.status_path, "r") as f:
            value = f.read().strip()
            return value

    @property
    def capacity(self) -> int:
        """ get battery capacity

        Returns:
            int: battery capacity in percent
        """
        with open(self.capacity_path, "r") as f:
            value = f.read().strip()
            return int(value)

    @property
    def voltage(self) -> float:
        """ get battery voltage

        Returns:
            float: battery voltage in V
        """
        with open(self.voltage_now_path, "r") as f:
            value = f.read().strip()
            return round(float(value) / 1000000, 2)

    @property
    def model_name(self) -> str:
        """ get battery model name

        Returns:
            str: battery model name
        """
        with open(self.model_name_path, "r") as f:
            value = f.read().strip()
            return value

    @property
    def is_charging(self) -> bool:
        """ check if battery is charging

        Returns:
            bool: True if battery is charging, False otherwise
        """
        return self.status == "Charging"

    @property
    def manufacturer(self) -> str:
        """ get battery manufacturer

        Returns:
            str: battery manufacturer
        """
        with open(self.manufacturer_path, "r") as f:
            value = f.read().strip()
            return value

    def __str__(self) -> str:
        """ get battery info

        Returns:
            str: battery info
        """
        return f"{self.model_name} {self.manufacturer} {self.status} {self.capacity}% {self.voltage} mV"


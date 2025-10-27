#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fusion Hat 驱动基础测试脚本

分别测试各个驱动是否正确配置，包括：
1. ADC读数是否正确
"""

import os
import time

class ADC():
    """ ADC class
    """
    DEVICE_NAME = "fusion-hat"
    IIO_DEVICE_PATH_PREFIX = "/sys/bus/iio/devices/iio:device"

    def __init__(self, channel: [int, str]) -> None:
        if isinstance(channel, int):
            channel = f"{channel}"
        elif isinstance(channel, str) and channel.startswith("A"):
            channel = channel[1:]
        else:
            raise ValueError("channel must be channel number or Str start with A")
        
        # 查找ADC设备的路径
        self.device_index = self.find_device()
        self.device_path = f"{self.IIO_DEVICE_PATH_PREFIX}{self.device_index}"
        
        self.channel = channel
        self.raw_path = os.path.join(self.device_path, f"in_voltage{self.channel}_raw")
        self.scale_path = os.path.join(self.device_path, f"in_voltage{self.channel}_scale")
        
        if not os.path.exists(self.raw_path):
            raise ValueError(f"ADC channel {self.channel} not found, path not exist: {self.raw_path}")
        
        with open(self.scale_path, "r") as f:
            self.scale = float(f.read().strip())

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
        """ read voltage value in mV

        Returns:
            float: voltage value in mV
        """
        voltage = self.read_raw() * self.scale
        voltage = round(voltage, 2)
        return voltage

def adc_test():
    """ test adc
    """
    a0 = ADC("A0")
    a1 = ADC("A1")
    a2 = ADC("A2")
    a3 = ADC("A3")
    print("="*40)
    print(f"ADC 测试")
    print(f"通道 0: {a0.read()} {a0.read_voltage():.2f} mV")
    print(f"通道 1: {a1.read()} {a1.read_voltage():.2f} mV")
    print(f"通道 2: {a2.read()} {a2.read_voltage():.2f} mV")
    print(f"通道 3: {a3.read()} {a3.read_voltage():.2f} mV")
    print("="*40)

class Battery():
    """ Battery class

    Read battery data from upower
    """
    DEVICE_NAME = "fusion-hat"
    PATH = f"/sys/class/power_supply/{DEVICE_NAME}"

    def __init__(self) -> None:
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
    def voltage_now(self) -> float:
        """ get battery voltage

        Returns:
            float: battery voltage in mV
        """
        with open(self.voltage_now_path, "r") as f:
            value = f.read().strip()
            return float(value) / 1000

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
        return f"{self.model_name} {self.manufacturer} {self.status} {self.capacity}% {self.voltage_now:.2f} mV"


def battery_test():
    """ test battery
    """
    battery = Battery()
    print("="*40)
    print(f"电池测试")
    print(battery)
    print("="*40)

def main():
    print("Fusion Hat 驱动基础测试工具")
    while True:
        adc_test()
        battery_test()
        time.sleep(1)

if __name__ == "__main__":
    main()
""" Fusion Hat device related functions

Example:

    Import device module

    >>> from fusion_hat import device

    Enable speaker

    >>> device.enable_speaker()
    >>> device.get_speaker_state()
    True

    Disable speaker

    >>> device.disable_speaker()
    >>> device.get_speaker_state()
    False

    Get user button state

    >>> device.get_usr_btn()
    False

    Get shutdown request state

    >>> device.get_shutdown_request()
    0

    Toggle user LED

    >>> device.set_user_led(True)
    >>> device.set_user_led(False)
    >>> device.set_user_led(1)
    >>> device.set_user_led(0)

    Get firmware version

    >>> version = device.get_firmware_version()
    >>> ".".join([str(v) for v in version])
    '1.1.4'

    Set volume

    >>> device.set_volume(50)

    Get battery voltage

    >>> device.get_battery_voltage()
    8.4
"""

__all__ = [
    'NAME',
    'ID',
    'UUID',
    'PRODUCT_ID',
    'PRODUCT_VER',
    'VENDOR',
    'I2C_ADDRESS',
    'is_installed',
    'enable_speaker',
    'disable_speaker',
    'get_speaker_state',
    'get_usr_btn',
    'get_charge_state',
    'get_shutdown_request',
    'set_user_led',
    'get_firmware_version',
    'set_volume',
    'get_battery_voltage',
]

import os
from ._utils import run_command, simple_i2c_command
from enum import Enum

HAT_DEVICE_TREE = "/proc/device-tree/"

NAME = "Fusion Hat"
""" Name of the board """

ID = "fusion_hat"
""" ID of the board """

UUID = "9daeea78-0000-0774-000a-582369ac3e02"
""" UUID of the board """

PRODUCT_ID = 0x0774
""" Product ID of the board """

PRODUCT_VER = 0x000a
""" Product version of the board """

VENDOR = "SunFounder"
""" Vendor of the board """ 


DEVICE_PATH = "/sys/class/fusion_hat/fusion_hat/"


def is_installed() -> bool:
    """ Check if a Fusion Hat board is installed

    Returns:
        bool: True if installed, False otherwise
    """
    for file in os.listdir('/proc/device-tree/'):
        if 'hat' in file:
            if os.path.exists(f"/proc/device-tree/{file}/uuid") \
                and os.path.isfile(f"/proc/device-tree/{file}/uuid"):
                with open(f"/proc/device-tree/{file}/uuid", "r") as f:
                    uuid = f.read()[:-1] # [:-1] rm \x00
                    product_id = uuid.split("-")[2]
                    product_id = int(product_id, 16)
                    if product_id == PRODUCT_ID:
                        return True
    return False

def enable_speaker() -> None:
    """ Enable speaker """
    PATH = DEVICE_PATH + "speaker"
    with open(PATH, "w") as f:
        f.write("1")

def disable_speaker() -> None:
    """ Disable speaker """
    PATH = DEVICE_PATH + "speaker"
    with open(PATH, "w") as f:
        f.write("0")

def get_speaker_state() -> bool:
    """ Get speaker state

    Returns:
        bool: True if enabled
    """
    PATH = DEVICE_PATH + "speaker"
    with open(PATH, "r") as f:
        state = f.read()[:-1] # [:-1] rm \n
        return state == "1"

def get_usr_btn() -> bool:
    """ Get user button state

    Returns:
        bool: True if pressed
    """
    PATH = DEVICE_PATH + "button"
    with open(PATH, "r") as f:
        state = f.read()[:-1] # [:-1] rm \n
        return state == "1"

def get_charge_state() -> bool:
    """ [Deprecated] Get charge state

    Returns:
        bool: True if charging
    """
    print("Warning: get_charge_state is deprecated, please use get_charge_state instead.")
    path = f"/sys/class/power_supply/fusion-hat/charge_state"
    with open(path, "r") as f:
        state = f.read()[:-1] # [:-1] rm \n
        return state == "1"

def get_battery_voltage() -> float:
    """ [Deprecated] Get battery voltage

    Returns:
        float: battery voltage(V)
    """
    print("Warning: get_battery_voltage is deprecated, please use get_battery_voltage instead.")
    path = f"/sys/class/power_supply/fusion-hat/voltage_now"
    with open(path, "r") as f:
        voltage = f.read().strip()
        voltage = float(voltage) / 1000
    return voltage

def get_shutdown_request() -> None:
    """ [Deprecated] Get shutdown request """
    raise NotImplementedError("get_shutdown_request is deprecated.")

def set_led(state: [int, bool]) -> None:
    """ Set led state

    Args:
        state (int or bool): 0:off, 1:on, True:on, False:off
    """
    path = f"{DEVICE_PATH}led"
    with open(path, "w") as f:
        f.write(str(int(state)))

def get_firmware_version() -> list:
    """ Get firmware version

    Returns:
        list: firmware version
    """
    path = f"{DEVICE_PATH}firmware_version"
    with open(path, "r") as f:
        version = f.read().strip()
    return version

def set_volume(value: int) -> None:
    """ Set volume

    Args:
        value (int): volume(0~100)
    """
    value = min(100, max(0, value))
    cmd = "sudo amixer -M sset 'fusion_hat speaker' %d%%" % value
    os.system(cmd)

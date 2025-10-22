
import os
from ._utils import run_command, simple_i2c_command

HAT_DEVICE_TREE = "/proc/device-tree/"

NAME = "Fusion Hat"
""" Name of the board """

ID = "fusion_hat"
""" ID of the board """

I2C_ADDRESS = 0x17
""" I2C address of the board """

UUID = "9daeea78-0000-0774-000a-582369ac3e02"
""" UUID of the board """

PRODUCT_ID = 0x0774
""" Product ID of the board """

PRODUCT_VER = 0x000a
""" Product version of the board """

VENDOR = "SunFounder"
""" Vendor of the board """ 

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
    SPEAKER_REG_ADDR = 0x31
    simple_i2c_command("set", SPEAKER_REG_ADDR, 1)
    # play a short sound to fill data and avoid the speaker overheating
    run_command(f"play -n trim 0.0 0.5 2>/dev/null")

def disable_speaker() -> None:
    """ Disable speaker """
    SPEAKER_REG_ADDR = 0x31
    simple_i2c_command("set", SPEAKER_REG_ADDR, 0)

def get_speaker_state() -> bool:
    """ Get speaker state

    Returns:
        bool: True if enabled
    """
    SPEAKER_REG_ADDR = 0x31
    result = simple_i2c_command("get", SPEAKER_REG_ADDR, "b")
    return result == 1

def get_usr_btn() -> bool:
    """ Get user button state

    Returns:
        bool: True if pressed
    """
    USER_BTN_STATE_REG_ADDR = 0x24
    result = simple_i2c_command("get", USER_BTN_STATE_REG_ADDR, "b")
    return result == 1

def get_charge_state() -> bool:
    """ Get charge state

    Returns:
        bool: True if charging
    """
    CHARGE_STATE_REG_ADDR = 0x25
    result = simple_i2c_command("get", CHARGE_STATE_REG_ADDR, "b")
    return result == 1

def get_shutdown_request() -> int:
    """ Get shutdown request

    Returns:
        int: 0: no request, 1: low Battery request, 2: button shutdown request
    """
    SHUTDOWN_REQUEST_REG_ADDR = 0x26
    result = simple_i2c_command("get", SHUTDOWN_REQUEST_REG_ADDR, "b")
    return result

def set_user_led(state: int) -> None:
    """ Set user led state

    Args:
        state (int): 0:off, 1:on, 2:toggle
    """
    USER_LED_REG_ADDR = 0x30
    simple_i2c_command("set", USER_LED_REG_ADDR, state, "b")

def get_firmware_version() -> list:
    """ Get firmware version

    Returns:
        list: firmware version
    """
    VERSSION_REG_ADDR = 0x05
    version = simple_i2c_command("get", VERSSION_REG_ADDR, "i", 3)
    return version

def set_volume(value: int) -> None:
    """ Set volume

    Args:
        value (int): volume(0~100)
    """
    value = min(100, max(0, value))
    cmd = "sudo amixer -M sset 'PCM' %d%%" % value
    os.system(cmd)

def get_battery_voltage() -> float:
    """ Get battery voltage

    Returns:
        float: battery voltage(V)
    """
    from .adc import ADC
    adc = ADC("A4")
    raw_voltage = adc.read_voltage()
    voltage = raw_voltage * 3
    return voltage

__all__ = [
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

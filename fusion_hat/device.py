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

    >>> device.get_firmware_version()
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
    'is_detected',
    'is_driver_loaded',
    'doctor',
    'is_installed',
    'is_connected',
    'enable_speaker',
    'disable_speaker',
    'get_speaker_state',
    'get_usr_btn',
    'set_led',
    'get_firmware_version',
    'set_volume',
]

import os
from typing import Callable, Any

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

def is_detected() -> bool:
    """ Check if Fusion Hat EEPROM is detected by Raspberry Pi

    This function reads the device tree to check if the Fusion Hat's EEPROM
    information is accessible, which indicates the hat is physically installed.

    Returns:
        bool: True if detected, False otherwise
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

def is_driver_loaded() -> bool:
    """ Check if Fusion Hat driver is loaded

    This function checks if the Fusion Hat driver module is loaded by
    verifying the existence of /sys/class/fusion_hat/ directory.

    Returns:
        bool: True if driver is loaded, False otherwise
    """
    BASE_PATH = "/sys/class/fusion_hat/"
    return os.path.exists(BASE_PATH)

def is_installed() -> bool:
    """ Check if a Fusion Hat board is installed

    .. deprecated::
        Use :func:`is_detected` instead. This function will be removed in a future version.

    Returns:
        bool: True if installed, False otherwise
    """
    import warnings
    warnings.warn(
        "is_installed is deprecated, use is_detected instead.",
        DeprecationWarning,
        stacklevel=2
    )
    return is_detected()

def is_connected():
    """ Check if Fusion HAT is connected

    .. deprecated::
        Use :func:`is_driver_loaded` instead. This function will be removed in a future version.

    Returns:
        bool: True if connected
    """
    import warnings
    warnings.warn(
        "is_connected is deprecated, use is_driver_loaded instead.",
        DeprecationWarning,
        stacklevel=2
    )
    return is_driver_loaded()

def raise_if_fusion_hat_not_ready() -> bool:
    """ Check if Fusion HAT is ready

    Returns:
        bool: True if ready
    """
    if not is_detected():
        raise IOError(
            "Fusion Hat not detected. "
            "Please ensure the hat is properly seated on the Raspberry Pi."
        )

    if not is_driver_loaded():
        raise IOError(
            "Fusion Hat driver not loaded. "
            "Please ensure the Fusion Hat kernel module is installed properly."
        )
    
def doctor() -> dict:
    """ Comprehensive driver and hardware health check

    Checks EEPROM detection, kernel module file, DKMS registration,
    module load state, sysfs interface, and onboard MCU I2C presence
    at address 0x17 — mirroring the driver Makefile ``status`` target.

    Returns:
        dict with keys: detected, module_file, dkms_status, module_loaded,
        sysfs, i2c_0x17, and overall (bool for pass/fail checks)
    """
    import platform
    from ._utils import run_command

    result = {
        "detected": False,
        "module_file": False,
        "dkms_status": "",
        "module_loaded": False,
        "sysfs": False,
        "i2c_0x17": False,
        "overall": True,
    }

    # 1. EEPROM detection
    result["detected"] = is_detected()

    # 2. Module .ko file installed (check .ko and .ko.xz in standard paths)
    kv = platform.uname().release
    ko_paths = [
        f"/lib/modules/{kv}/extra/fusion_hat.ko",
        f"/lib/modules/{kv}/updates/fusion_hat.ko",
        f"/lib/modules/{kv}/extra/fusion_hat.ko.xz",
        f"/lib/modules/{kv}/updates/fusion_hat.ko.xz",
        f"/lib/modules/{kv}/updates/dkms/fusion_hat.ko.xz",
    ]
    result["module_file"] = any(os.path.exists(p) for p in ko_paths)

    # 3. DKMS registration
    _, dkms_out = run_command("dkms status fusion_hat 2>/dev/null || true")
    if dkms_out.strip():
        result["dkms_status"] = dkms_out.strip()
    else:
        _, has_dkms = run_command("command -v dkms >/dev/null 2>&1 && echo yes || echo no")
        if has_dkms.strip() == "yes":
            result["dkms_status"] = "not registered"
        else:
            result["dkms_status"] = "DKMS not installed"

    # 4. Module loaded (check /sys/module/fusion_hat)
    result["module_loaded"] = os.path.exists("/sys/module/fusion_hat")

    # 5. sysfs interface
    result["sysfs"] = is_driver_loaded()

    # 6. I2C 0x17 — onboard MCU
    result["i2c_0x17"] = False
    try:
        # Scan range covering the 0x10 row so i2cdetect emits -- placeholders
        _, i2c_out = run_command("i2cdetect -y 1 0x10 0x1f 2>/dev/null")
        if i2c_out.strip():
            for line in i2c_out.strip().split("\n"):
                if line.startswith("10:"):
                    entries = line[3:].strip().split()
                    # entries[7] corresponds to address 0x17 (0x10 + 7)
                    if len(entries) > 7 and entries[7] in ("17", "UU"):
                        result["i2c_0x17"] = True
                    break
    except Exception:
        pass

    # Overall pass: detected + module_file + module_loaded + sysfs + i2c_0x17
    result["overall"] = all([
        result["detected"],
        result["module_file"],
        result["module_loaded"],
        result["sysfs"],
        result["i2c_0x17"],
    ])

    return result

def require_fusion_hat(func: Callable[..., Any]) -> Callable[..., Any]:
    """ Decorator to require Fusion HAT

    Args:
        func (Callable[..., Any]): function to decorate

    Returns:
        Callable[..., Any]: decorated function
    """
    def wrapper(*arg, **kwargs):
        raise_if_fusion_hat_not_ready()
        return func(*arg, **kwargs)
    return wrapper

@require_fusion_hat
def enable_speaker() -> None:
    """ Enable speaker """
    PATH = DEVICE_PATH + "speaker"
    with open(PATH, "w") as f:
        f.write("1")

@require_fusion_hat
def disable_speaker() -> None:
    """ Disable speaker """
    PATH = DEVICE_PATH + "speaker"
    with open(PATH, "w") as f:
        f.write("0")

@require_fusion_hat
def get_speaker_state() -> bool:
    """ Get speaker state

    Returns:
        bool: True if enabled
    """
    PATH = DEVICE_PATH + "speaker"
    with open(PATH, "r") as f:
        state = f.read()[:-1] # [:-1] rm \n
        return state == "1"

@require_fusion_hat
def get_usr_btn() -> bool:
    """ Get user button state

    Returns:
        bool: True if pressed
    """
    PATH = DEVICE_PATH + "button"
    with open(PATH, "r") as f:
        state = f.read()[:-1] # [:-1] rm \n
        return state == "1"

@require_fusion_hat
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

@require_fusion_hat
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

@require_fusion_hat
def set_led(state: [int, bool]) -> None:
    """ Set led state

    Args:
        state (int or bool): 0:off, 1:on, True:on, False:off
    """
    path = f"{DEVICE_PATH}led"
    with open(path, "w") as f:
        f.write(str(int(state)))

@require_fusion_hat
def get_led() -> bool:
    """ Get led state

    Returns:
        bool: True if on
    """
    path = f"{DEVICE_PATH}led"
    with open(path, "r") as f:
        state = f.read().strip()
    return state == "1"

@require_fusion_hat
def get_firmware_version() -> str:
    """ Get firmware version

    Returns:
        str: firmware version
    """
    path = f"{DEVICE_PATH}firmware_version"
    with open(path, "r") as f:
        version = f.read().strip()
    return version

@require_fusion_hat
def get_driver_version() -> str:
    """ Get driver version
    
    Returns:
        str: driver version
    """
    path = f"{DEVICE_PATH}version"
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

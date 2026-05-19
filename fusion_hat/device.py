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
    'update_eeprom',
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


def _find_driver_src() -> str:
    """Find the Fusion Hat driver source directory.

    Returns:
        str: path to driver source directory, or empty string if not found
    """
    import platform
    candidates = []
    # Check alongside the fusion_hat Python package
    try:
        import fusion_hat
        pkg_dir = os.path.dirname(fusion_hat.__file__)
        repo = os.path.dirname(pkg_dir)
        candidates.append(os.path.join(repo, "driver"))
    except Exception:
        pass
    # Common install paths
    candidates += [
        "/home/pi/fusion-hat/driver",
        os.path.expanduser("~/fusion-hat/driver"),
    ]
    # DKMS source
    try:
        kv = platform.uname().release
        candidates.append(f"/usr/src/fusion_hat-{kv}")
    except Exception:
        pass
    for p in candidates:
        if os.path.isdir(p) and os.path.isfile(os.path.join(p, "Makefile")):
            return os.path.realpath(p)
    return ""


def doctor_fix() -> dict:
    """Run doctor and attempt to fix any issues found.

    Fixable issues:
    - Module not loaded (but file present): ``modprobe fusion_hat``
    - Module file missing (driver source found): ``make modules_install``

    Returns:
        dict with ``before`` (initial check), ``fixes`` (list of fix actions
        attempted), ``after`` (final check), and ``fixed`` (bool).
    """
    from ._utils import run_command

    before = doctor()
    fixes = []

    if before["overall"]:
        return {"before": before, "fixes": fixes, "after": before, "fixed": True}

    # Fix 1: module file exists but not loaded → modprobe
    if before["module_file"] and not before["module_loaded"]:
        fixes.append("modprobe fusion_hat")
        run_command("sudo modprobe fusion_hat 2>/dev/null")

    # Fix 2: module file missing → try to install
    if not before["module_file"]:
        driver_dir = _find_driver_src()
        if driver_dir:
            fixes.append(f"cd {driver_dir} && sudo make modules_install")
            run_command(
                f"cd {driver_dir} && sudo make modules_install 2>/dev/null"
            )
            run_command("sudo depmod -a 2>/dev/null")
            # Try loading after install
            if not before["module_loaded"]:
                fixes.append("modprobe fusion_hat (after install)")
                run_command("sudo modprobe fusion_hat 2>/dev/null")
        else:
            fixes.append("driver source not found — cannot auto-install")

    after = doctor()
    return {
        "before": before,
        "fixes": fixes,
        "after": after,
        "fixed": after["overall"],
    }

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

def _get_eepflash_script() -> str:
    """Get path to the bundled eepflash.sh script.

    Returns:
        str: path to eepflash.sh, or empty string if not found
    """
    try:
        import fusion_hat
        pkg_dir = os.path.dirname(fusion_hat.__file__)
        repo = os.path.dirname(pkg_dir)
        script = os.path.join(repo, "scripts", "eepflash.sh")
        if os.path.isfile(script):
            return script
    except Exception:
        pass
    return ""


def update_eeprom(erase: bool = False) -> bool:
    """Reflash the Fusion Hat EEPROM via I2C GPIO bit-banging.

    Uses the bundled eepflash.sh script and a bit-banged I2C bus on
    GPIO 0/1. The user must short the two outermost holes of the 5-pin
    header next to the EEPROM chip to enable writing.

    Args:
        erase: If True, only erase the EEPROM (write all 0xFF).
               The EEPROM binary is not downloaded in this mode.

    Returns:
        bool: True if the operation succeeded
    """
    import tempfile
    from ._utils import run_command

    EEPROM_URL = (
        "https://github.com/sunfounder/sunfounder-hat-helper/raw/refs/heads/"
        "main/eeproms/o1908v10_fusion_hat.eep"
    )

    # Check sudo access before starting
    _, sudo_check = run_command("sudo -v 2>&1")
    if sudo_check.strip():
        print("This command requires sudo access. Please run with a user that has sudo privileges.")
        return False

    # Find the bundled eepflash.sh
    eepflash = _get_eepflash_script()
    if not eepflash:
        print("  [FAIL] eepflash.sh not found. Is fusion-hat installed from source?")
        return False

    tmpdir = tempfile.mkdtemp(prefix="fusion_hat_eeprom_")

    try:
        print("")
        print("=" * 60)
        print("  Fusion Hat EEPROM", "Erase" if erase else "Update")
        print("=" * 60)
        print("")

        # 1. Prepare the file to write
        if erase:
            print("  [1/5] Preparing blank EEPROM image (4096 bytes of 0xFF)...")
            write_file = os.path.join(tmpdir, "blank.eep")
            with open(write_file, "wb") as f:
                f.write(b"\xff" * 4096)
            print(f"  [OK]  Created blank image")
        else:
            print("  [1/5] Downloading EEPROM binary...")
            write_file = os.path.join(tmpdir, "o1908v10_fusion_hat.eep")
            _, out = run_command(f"wget -q -O {write_file} {EEPROM_URL} 2>&1")
            if not os.path.isfile(write_file) or os.path.getsize(write_file) == 0:
                print(f"  [FAIL] Failed to download EEPROM binary from {EEPROM_URL}")
                return False
            print(f"  [OK]  Downloaded: {os.path.basename(write_file)} ({os.path.getsize(write_file)} bytes)")

        # 2. Set up I2C GPIO bus
        print("")
        print("  [2/5] Setting up I2C GPIO bus (bus 9 on GPIO 0/1)...")
        _, dtoverlay_out = run_command(
            "sudo dtoverlay i2c-gpio i2c_gpio_sda=0 i2c_gpio_scl=1 bus=9 2>&1"
        )
        if not os.path.exists("/dev/i2c-9"):
            print("  [FAIL] /dev/i2c-9 not created. Check if dtoverlay succeeded.")
            print(f"  Output: {dtoverlay_out.strip()}")
            return False
        print("  [OK]  /dev/i2c-9 created")

        # 3. Instruct user to short write-protect pins
        print("")
        print("  [3/5] Short write-protect pins")
        print("")
        print("  The EEPROM chip is write-protected. To enable writing,")
        print("  short the two OUTERMOST holes of the 5-pin header next to")
        print("  the EEPROM chip on the Fusion Hat board.")
        print("")
        print("  The 5-pin header looks like:  [o o o o o]")
        print("  Short these two:              [X o o o X]")
        print("")
        print("  WARNING: Be very careful to ONLY short the outer two holes.")
        print("  Shorting other holes may cause the Pi to shut down.")
        print("  If it does shut down, simply reboot.")
        print("")
        input("  Press ENTER after you have shorted the pins...")

        # 4. Write to EEPROM
        print("")
        if erase:
            print("  [4/5] Erase EEPROM...")
        else:
            print("  [4/5] Flash EEPROM...")
        _, flash_out = run_command(
            f"sudo {eepflash} -y -w -f={write_file} -t=24c32 -a=50 -d=9 2>&1"
        )
        print(flash_out)
        if "done" not in flash_out.lower():
            print("  [FAIL] EEPROM write failed. Check output above for details.")
            return False

        # 5. Remove short
        print("")
        print("  [5/5] Remove short from write-protect pins")
        print("")
        print("  Remove the short from the EEPROM write-protect pins now.")
        input("  Press ENTER after you have removed the short...")

        print("")
        print("  EEPROM", "erase" if erase else "flash", "complete.")
        print("  A reboot is required for the Raspberry Pi to detect the HAT.")
        print(f"  Temporary files kept at: {tmpdir}")
        print("")
        print("=" * 60)
        print("")

        return True

    except (KeyboardInterrupt, EOFError):
        print("")
        print("  Aborted by user.")
        print(f"  Temporary files kept at: {tmpdir}")
        return False
    except Exception as e:
        print(f"  [FAIL] Unexpected error: {e}")
        print(f"  Temporary files kept at: {tmpdir}")
        return False


def set_volume(value: int) -> None:
    """ Set volume

    Args:
        value (int): volume(0~100)
    """
    value = min(100, max(0, value))
    cmd = "sudo amixer -M sset 'fusion_hat speaker' %d%%" % value
    os.system(cmd)

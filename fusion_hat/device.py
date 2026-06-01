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
    'DTOVERLAY_NAME',
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
DTOVERLAY_NAME = "sunfounder-fusionhat"

def is_detected() -> bool:
    """ Check if Fusion Hat is detected by the kernel

    This function reads the device tree to check if the Fusion Hat's
    information is accessible, which indicates the hat is recognized
    (via dtoverlay in config.txt).

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

def _detect_hat_detail() -> dict:
    """Detect Fusion Hat via device-tree with step-by-step detail.

    Breaks down ``is_detected()`` into individual checks so callers can
    see exactly *why* detection failed instead of a binary yes/no.

    Returns:
        dict with keys:
        - detected (bool): overall detection result
        - hat_dir (str|None): path under /proc/device-tree/ (e.g. ``hat``)
        - uuid_file (bool): whether the uuid file exists
        - uuid_value (str|None): raw UUID string read from device-tree
        - product_id_match (bool|None): does the product_id segment match?
        - product_id_expected (str): expected hex product id
        - product_id_found (str|None): actual hex product id parsed
        - product_ver_expected (str): expected hex product version
        - product_ver_found (str|None): actual hex product version parsed
        - vendor_found (str|None): vendor string from device-tree
        - product_found (str|None): product string from device-tree
        - steps (list[dict]): ordered log of each diagnostic step
    """
    steps: list[dict] = []
    result: dict[str, Any] = {
        "detected": False,
        "hat_dir": None,
        "uuid_file": False,
        "uuid_value": None,
        "product_id_match": None,
        "product_id_expected": f"0x{PRODUCT_ID:04X}",
        "product_id_found": None,
        "product_ver_expected": f"0x{PRODUCT_VER:04X}",
        "product_ver_found": None,
        "vendor_found": None,
        "product_found": None,
        "steps": steps,
    }

    # Step 1 — scan ALL directories under /proc/device-tree/ for Fusion HAT UUID
    expected_hex = f"{PRODUCT_ID:04X}"
    hat_dir = None
    found_hats = []
    for entry in os.listdir(HAT_DEVICE_TREE):
        candidate = os.path.join(HAT_DEVICE_TREE, entry)
        uuid_path = os.path.join(candidate, "uuid")
        if not os.path.isdir(candidate) or not os.path.isfile(uuid_path):
            continue
        try:
            with open(uuid_path, "rb") as f:
                raw = f.read().rstrip(b"\x00")
            raw_uuid = raw.decode("utf-8", errors="replace").strip()
            found_hats.append((entry, raw_uuid))
            parts = raw_uuid.split("-")
            if len(parts) >= 3 and parts[2].upper() == expected_hex:
                hat_dir = candidate
                result["hat_dir"] = hat_dir
                result["uuid_file"] = True
                result["uuid_value"] = raw_uuid
                result["detected"] = True
                result["product_id_match"] = True
                result["product_id_found"] = f"0x{PRODUCT_ID:04X}"
                steps.append({
                    "step": "device-tree hat directory",
                    "ok": True,
                    "detail": f"Found Fusion HAT at {hat_dir} (UUID={raw_uuid})",
                })
                # Read vendor / product strings
                for field, label in [("vendor", "Vendor"), ("product", "Product")]:
                    p = os.path.join(hat_dir, field)
                    if os.path.isfile(p):
                        try:
                            with open(p, "rb") as f2:
                                val = f2.read().rstrip(b"\x00").decode("utf-8", errors="replace").strip()
                            result[f"{field}_found"] = val
                            steps.append({"step": f"{field} string", "ok": True, "detail": f"{label} = {val}"})
                        except Exception:
                            pass
                break
        except Exception:
            continue

    if not result["detected"]:
        if found_hats:
            names = [n for n, _ in found_hats]
            steps.append({
                "step": "device-tree hat directory",
                "ok": False,
                "detail": (
                    f"No Fusion HAT found. Detected other HAT(s): {', '.join(names)}. "
                    f"Expected product_id=0x{expected_hex}."
                ),
            })
        else:
            steps.append({
                "step": "device-tree hat directory",
                "ok": False,
                "detail": "No HAT device-tree entries found.",
            })
        return result


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

    Checks whether the sysfs interface exists (driver loaded and working).
    If not, prompts the user to run ``fusion_hat doctor`` to diagnose and fix.

    Returns:
        bool: True if ready
    """
    if not is_driver_loaded():
        raise IOError(
            "Fusion Hat driver not loaded (sysfs interface missing). "
            "Run 'fusion_hat doctor' to diagnose and fix."
        )

def _find_config_txt() -> str:
    """Locate the active Raspberry Pi config.txt file.

    Returns:
        str: path to config.txt (may not exist)
    """
    candidates = [
        "/boot/firmware/config.txt",
        "/boot/config.txt",
    ]
    for p in candidates:
        if os.path.isfile(p):
            return p
    return candidates[0]  # default for Bookworm


def _has_dtoverlay() -> bool:
    """Check if dtoverlay=sunfounder-fusionhat is already in config.txt.

    Returns:
        bool: True if the uncommented dtoverlay line exists
    """
    config = _find_config_txt()
    if not os.path.isfile(config):
        return False
    try:
        with open(config, "r") as f:
            for line in f:
                stripped = line.strip()
                if f"dtoverlay={DTOVERLAY_NAME}" in stripped and not stripped.startswith("#"):
                    return True
    except Exception:
        pass
    return False


def _add_dtoverlay() -> bool:
    """Append dtoverlay=sunfounder-fusionhat to config.txt if not present.

    Uses sudo tee -a since /boot/firmware/config.txt requires root.

    Returns:
        bool: True if the line was added or already present
    """
    from ._utils import run_command

    config = _find_config_txt()
    if not os.path.isfile(config):
        return False
    if _has_dtoverlay():
        return True
    try:
        line = f"dtoverlay={DTOVERLAY_NAME}"
        run_command(
            f"echo '{line}' | sudo tee -a {config} > /dev/null 2>&1",
            timeout=10,
        )
        return _has_dtoverlay()
    except Exception:
        return False


def _remove_dtoverlay() -> bool:
    """Remove dtoverlay=sunfounder-fusionhat from config.txt.

    Uses sudo sed since the file requires root.

    Returns:
        bool: True if the line was removed or not present
    """
    from ._utils import run_command

    config = _find_config_txt()
    if not os.path.isfile(config):
        return False
    if not _has_dtoverlay():
        return True
    try:
        run_command(
            f"sudo sed -i '/^dtoverlay={DTOVERLAY_NAME}/d' {config}",
            timeout=10,
        )
        return not _has_dtoverlay()
    except Exception:
        return False


I2C_SCAN_TIMEOUT = 5  # seconds timeout for i2cdetect


def doctor() -> dict:
    """Comprehensive driver and hardware health check.

    Two-phase approach:
    1. Quick check — sysfs, module, I2C MCU. If all pass, skip deep checks.
    2. Deep diagnostic — only when quick check fails: device-tree,
       dtoverlay in config.txt, module file, DKMS, dmesg.

    Returns:
        dict with keys: detected, i2c_enabled, dtoverlay,
        module_file, dkms_status, module_loaded, sysfs, i2c_0x17,
        overall, plus *hat_detail* sub-dict.
    """
    import platform
    from ._utils import run_command

    result = {
        "detected": False,
        "i2c_enabled": False,
        "dtoverlay": False,
        "module_file": False,
        "dkms_status": "",
        "module_loaded": False,
        "sysfs": False,
        "i2c_0x17": False,
        "overall": True,
        "deep_scan": False,  # True when deep diagnostic ran
        "hat_detail": None,
        "dmesg_hat": "",
    }

    # ── Phase 1: Quick health check ──
    result["sysfs"] = is_driver_loaded()
    result["module_loaded"] = os.path.exists("/sys/module/fusion_hat")

    # I2C 0x17 — onboard MCU (fast — main I2C bus)
    try:
        _, i2c_out = run_command("sudo i2cdetect -y 1 0x10 0x1f 2>/dev/null",
                                   timeout=I2C_SCAN_TIMEOUT)
        if i2c_out.strip():
            for line in i2c_out.strip().split("\n"):
                if line.startswith("10:"):
                    entries = line[3:].strip().split()
                    if len(entries) > 7 and entries[7] in ("17", "UU"):
                        result["i2c_0x17"] = True
                    break
    except Exception:
        pass

    # Module file — quick check
    kv = platform.uname().release
    ko_paths = [
        f"/lib/modules/{kv}/extra/fusion_hat.ko",
        f"/lib/modules/{kv}/updates/fusion_hat.ko",
        f"/lib/modules/{kv}/extra/fusion_hat.ko.xz",
        f"/lib/modules/{kv}/updates/fusion_hat.ko.xz",
        f"/lib/modules/{kv}/updates/dkms/fusion_hat.ko.xz",
    ]
    result["module_file"] = any(os.path.exists(p) for p in ko_paths)

    # Check dtoverlay in config.txt (required for fusion_hat)
    result["dtoverlay"] = _has_dtoverlay()

    result["overall"] = all([
        result["module_file"],
        result["module_loaded"],
        result["sysfs"],
        result["i2c_0x17"],
    ])

    # If all quick checks pass, skip deep diagnostic
    if result["overall"]:
        return result

    # ── Phase 2: Deep diagnostic (driver not working) ──
    result["deep_scan"] = True

    # I2C enabled?
    result["i2c_enabled"] = os.path.exists("/dev/i2c-1")

    # Device-tree detection (fast — reads /proc/device-tree)
    hat_detail = _detect_hat_detail()
    result["hat_detail"] = hat_detail
    result["detected"] = hat_detail["detected"]

    # DKMS registration
    _, dkms_out = run_command("dkms status fusion_hat 2>/dev/null || true")
    if dkms_out.strip():
        result["dkms_status"] = dkms_out.strip()
    else:
        _, has_dkms = run_command("command -v dkms >/dev/null 2>&1 && echo yes || echo no")
        if has_dkms.strip() == "yes":
            result["dkms_status"] = "not registered"
        else:
            result["dkms_status"] = "DKMS not installed"

    # dmesg — look for HAT / I2C / fusionhat boot messages
    _, dmesg_out = run_command(
        "dmesg 2>/dev/null | grep -i -E 'fusionhat|i2c.*error|i2c-0' | tail -20 || true"
    )
    if dmesg_out.strip():
        result["dmesg_hat"] = dmesg_out.strip()

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

    Focuses on ensuring dtoverlay=sunfounder-fusionhat is in config.txt
    (required for Fusion HAT), plus driver installation and loading.

    Returns:
        dict with ``before``, ``fixes``, ``after``, ``fixed``.
    """
    from ._utils import run_command

    before = doctor()
    fixes = []
    reboot = False

    if before["overall"]:
        return {"before": before, "fixes": fixes, "after": before, "fixed": True, "reboot": False}

    # ── I2C not enabled ──
    if not before["i2c_enabled"]:
        fixes.append("enable I2C")
        run_command("sudo raspi-config nonint do_i2c 0 2>/dev/null")
        run_command("sudo modprobe i2c-dev 2>/dev/null")

    # ── Module file missing → install driver ──
    if not before["module_file"]:
        driver_dir = _find_driver_src()
        if driver_dir:
            fixes.append(f"install driver from {driver_dir}")
            run_command(f"cd {driver_dir} && sudo make modules_install 2>/dev/null")
            run_command("sudo depmod -a 2>/dev/null")
        else:
            fixes.append("driver source not found — cannot auto-install")

    # ── Ensure dtoverlay is in config.txt (required for Fusion HAT) ──
    if not before["dtoverlay"]:
        if _add_dtoverlay():
            fixes.append("added dtoverlay=sunfounder-fusionhat to config.txt")
            reboot = True
        else:
            fixes.append("failed to add dtoverlay to config.txt")
    else:
        fixes.append("dtoverlay already in config.txt")

    # ── Module not loaded → modprobe ──
    if not before["module_loaded"]:
        fixes.append("modprobe fusion_hat")
        run_command("sudo modprobe fusion_hat 2>/dev/null")
        if not os.path.exists("/sys/module/fusion_hat"):
            reboot = True

    # ── Module loaded but sysfs missing → reload ──
    if before["module_loaded"] and not before["sysfs"]:
        fixes.append("reload fusion_hat module")
        run_command("sudo rmmod fusion_hat 2>/dev/null")
        run_command("sudo modprobe fusion_hat 2>/dev/null")

    after = doctor()

    if reboot and not after["overall"]:
        return {
            "before": before,
            "fixes": fixes,
            "after": after,
            "fixed": False,
            "reboot": True,
        }

    return {
        "before": before,
        "fixes": fixes,
        "after": after,
        "fixed": after["overall"],
        "reboot": reboot,
    }

def force_dt_overlay() -> bool:
    """Force-add dtoverlay=sunfounder-fusionhat to config.txt.

    This is the primary way to configure the Fusion HAT device-tree overlay.
    Required for the kernel driver to load and detect the HAT.

    Returns:
        bool: True if the line was added or already present
    """
    from ._utils import run_command

    if _has_dtoverlay():
        print("dtoverlay=sunfounder-fusionhat is already in config.txt.")
        return True
    if not _add_dtoverlay():
        print("Failed to write config.txt. Check permissions.")
        return False

    print("Added dtoverlay=sunfounder-fusionhat to config.txt.")
    try:
        answer = input("  Reboot now to apply? (y/N): ").strip().lower()
        if answer in ("y", "yes"):
            print("  Rebooting...")
            run_command("sudo reboot 2>&1")
        else:
            print("  Reboot later with: sudo reboot")
    except (KeyboardInterrupt, EOFError):
        print("")
        print("  Reboot later with: sudo reboot")
    return True


def remove_dt_overlay() -> bool:
    """Remove dtoverlay=sunfounder-fusionhat from config.txt.

    Returns:
        bool: True if the line was removed or not present
    """
    if not _has_dtoverlay():
        print("dtoverlay=sunfounder-fusionhat is not in config.txt.")
        return True
    if _remove_dtoverlay():
        print("Removed dtoverlay=sunfounder-fusionhat from config.txt.")
        print("Run 'sudo reboot' if the HAT was previously working via this overlay.")
        return True
    print("Failed to update config.txt. Check permissions.")
    return False


def uninstall() -> bool:
    """Uninstall Fusion HAT: driver, DKMS, overlay, config, Python package.

    Removes: loaded module, DKMS registration + source, .ko files,
    .dtbo overlay, dtoverlay from config.txt, and the Python package.

    Returns:
        bool: True if uninstall succeeded (or nothing to do)
    """
    import platform
    from ._utils import run_command

    print("")
    print("=" * 60)
    print("  Fusion HAT Uninstall")
    print("=" * 60)
    print("")

    kv = platform.uname().release
    ok = True

    # 1. Unload the module
    print("  [1/6] Unloading kernel module...")
    if os.path.exists("/sys/module/fusion_hat"):
        _, out = run_command("sudo rmmod fusion_hat 2>&1")
        if os.path.exists("/sys/module/fusion_hat"):
            print(f"  [FAIL] Could not unload fusion_hat: {out.strip()}")
            ok = False
        else:
            print("  [OK] fusion_hat module unloaded")
    else:
        print("  [OK] fusion_hat not loaded")

    # 2. DKMS uninstall
    print("  [2/6] Removing DKMS registration...")
    _, dkms_status = run_command("dkms status fusion_hat 2>/dev/null || true")
    if dkms_status.strip():
        for line in dkms_status.strip().split("\n"):
            ver = line.split("/")[1].split(",")[0].strip() if "/" in line else ""
            if ver:
                run_command(f"sudo dkms remove -m fusion_hat -v {ver} --all 2>/dev/null")
        _, dkms_after = run_command("dkms status fusion_hat 2>/dev/null || true")
        if not dkms_after.strip():
            print("  [OK] DKMS registration removed")
        else:
            print(f"  [!] DKMS may still have entries: {dkms_after.strip()}")
    else:
        print("  [OK] Not registered with DKMS")

    import glob as _glob
    for dkms_dir in _glob.glob("/usr/src/fusion_hat-*"):
        run_command(f"sudo rm -rf {dkms_dir} 2>/dev/null")

    # 3. Remove module files
    print("  [3/6] Removing kernel module files...")
    ko_paths = [
        f"/lib/modules/{kv}/extra/fusion_hat.ko",
        f"/lib/modules/{kv}/updates/fusion_hat.ko",
        f"/lib/modules/{kv}/extra/fusion_hat.ko.xz",
        f"/lib/modules/{kv}/updates/fusion_hat.ko.xz",
    ]
    removed = 0
    for p in ko_paths:
        if os.path.isfile(p):
            run_command(f"sudo rm -f {p} 2>/dev/null")
            if not os.path.isfile(p):
                removed += 1
    run_command("sudo depmod -a 2>/dev/null")
    print(f"  [OK] Removed {removed} module file(s)")

    # 4. Remove dtbo from overlays
    print("  [4/6] Removing device-tree overlay (.dtbo)...")
    dtbo_name = "sunfounder-fusionhat.dtbo"
    overlay_dirs = [
        "/boot/firmware/overlays",
        "/boot/overlays",
    ]
    dtbo_removed = False
    for d in overlay_dirs:
        p = os.path.join(d, dtbo_name)
        if os.path.isfile(p):
            run_command(f"sudo rm -f {p} 2>/dev/null")
            dtbo_removed = True
    print(f"  [OK] {'Removed' if dtbo_removed else 'Not found'}")

    # 5. Remove dtoverlay from config.txt
    print("  [5/6] Removing dtoverlay from config.txt...")
    if _has_dtoverlay():
        if _remove_dtoverlay():
            print("  [OK] dtoverlay removed from config.txt")
        else:
            print("  [FAIL] Could not remove dtoverlay from config.txt")
            ok = False
    else:
        print("  [OK] No dtoverlay in config.txt")

    # 6. Uninstall Python package
    print("  [6/6] Uninstall Python package...")
    _, pip_out = run_command(
        "pip show fusion-hat 2>/dev/null | grep -i location",
        timeout=10,
    )
    if pip_out.strip():
        _, out = run_command(
            "sudo pip uninstall -y fusion-hat --break-system-packages 2>&1",
            timeout=30,
        )
        if "Successfully uninstalled" in out:
            print("  [OK] Python package uninstalled")
        else:
            print(f"  [!] pip uninstall returned: {out.strip()[-120:]}")
    else:
        print("  [OK] Python package not found")

    print("")
    if ok:
        print("  Uninstall complete. Reboot to fully clean up.")
    else:
        print("  Uninstall completed with some issues. Check output above.")
    print("")
    print("=" * 60)
    print("")

    return ok


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

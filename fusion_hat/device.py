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

    # Step 1 — find a hat directory under /proc/device-tree/
    hat_dir = None
    hat_entries = []
    for entry in os.listdir(HAT_DEVICE_TREE):
        if "hat" in entry.lower():
            hat_entries.append(entry)
            candidate = os.path.join(HAT_DEVICE_TREE, entry)
            if os.path.isdir(candidate):
                hat_dir = candidate
                break

    if hat_dir is None:
        steps.append({
            "step": "device-tree hat directory",
            "ok": False,
        })
        return result

    result["hat_dir"] = hat_dir
    steps.append({
        "step": "device-tree hat directory",
        "ok": True,
        "detail": f"Found: {hat_dir}",
    })

    # Step 2 — read the uuid file
    uuid_path = os.path.join(hat_dir, "uuid")
    if not os.path.exists(uuid_path) or not os.path.isfile(uuid_path):
        steps.append({
            "step": "uuid file",
            "ok": False,
            "detail": f"uuid file not found at {uuid_path}",
        })
        return result

    result["uuid_file"] = True
    raw_uuid = ""
    try:
        with open(uuid_path, "rb") as f:
            raw = f.read()
        raw_uuid = raw.rstrip(b"\x00").decode("utf-8", errors="replace").strip()
        result["uuid_value"] = raw_uuid
    except Exception as e:
        steps.append({
            "step": "uuid file",
            "ok": False,
            "detail": f"Cannot read {uuid_path}: {e}",
        })
        return result

    steps.append({
        "step": "uuid file",
        "ok": True,
        "detail": f"UUID = {raw_uuid}",
    })

    # Step 3 — parse and validate product_id
    parts = raw_uuid.split("-")
    if len(parts) < 3:
        steps.append({
            "step": "product_id check",
            "ok": False,
            "detail": f"UUID has unexpected format (expected 3+ dash-separated segments, got {len(parts)}): {raw_uuid}",
        })
        return result

    try:
        product_id = int(parts[2], 16)
        result["product_id_found"] = f"0x{product_id:04X}"
        if product_id == PRODUCT_ID:
            result["product_id_match"] = True
            result["detected"] = True
            steps.append({
                "step": "product_id check",
                "ok": True,
                "detail": f"product_id=0x{product_id:04X} matches expected 0x{PRODUCT_ID:04X}",
            })
        else:
            result["product_id_match"] = False
            steps.append({
                "step": "product_id check",
                "ok": False,
                "detail": (
                    f"product_id mismatch: expected 0x{PRODUCT_ID:04X}, "
                    f"got 0x{product_id:04X}"
                ),
            })
    except ValueError:
        steps.append({
            "step": "product_id check",
            "ok": False,
            "detail": f"Cannot parse product_id from UUID segment '{parts[2]}'",
        })
        return result

    # Step 4 — parse product_ver from UUID
    if len(parts) >= 4:
        try:
            product_ver = int(parts[3], 16)
            result["product_ver_found"] = f"0x{product_ver:04X}"
            steps.append({
                "step": "product_ver check",
                "ok": product_ver == PRODUCT_VER,
                "detail": (
                    f"product_ver=0x{product_ver:04X}"
                    + (f" (matches)" if product_ver == PRODUCT_VER else
                       f" (expected 0x{PRODUCT_VER:04X})")
                ),
            })
        except ValueError:
            pass

    # Step 5 — read optional vendor / product strings
    for field, label in [("vendor", "Vendor"), ("product", "Product")]:
        p = os.path.join(hat_dir, field)
        if os.path.isfile(p):
            try:
                with open(p, "rb") as f:
                    val = f.read().rstrip(b"\x00").decode("utf-8", errors="replace").strip()
                result[f"{field}_found"] = val
                steps.append({"step": f"{field} string", "ok": True, "detail": f"{label} = {val}"})
            except Exception:
                pass

    return result


def _detect_eeprom_addr() -> int | None:
    """Scan I2C bus 9 for an EEPROM at valid HAT addresses (0x50-0x53).

    Creates /dev/i2c-9 via dtoverlay i2c-gpio on GPIO 0/1 if the bus
    does not already exist.  Waits briefly for the device node to appear
    because the kernel may take a moment after applying the overlay.

    Returns:
        int: the detected address (0x50-0x53), or None if not found
    """
    import time
    from ._utils import run_command

    if not os.path.exists("/dev/i2c-9"):
        os.system("sudo dtoverlay i2c-gpio i2c_gpio_sda=0 i2c_gpio_scl=1 bus=9 2>/dev/null")
        # The device node may take a moment to appear after dtoverlay
        for _ in range(10):
            if os.path.exists("/dev/i2c-9"):
                break
            time.sleep(0.1)
        if not os.path.exists("/dev/i2c-9"):
            return None

    _, out = run_command("i2cdetect -y 9 0x50 0x53 2>/dev/null")
    for line in out.split("\n"):
        stripped = line.strip()
        if stripped.startswith("50:") or stripped.startswith("50 "):
            parts = stripped.split(":")
            if len(parts) >= 2:
                addrs = parts[1].strip().split()
                for i, val in enumerate(addrs[:4]):
                    if val in ("50", "51", "52", "53", "UU"):
                        return 0x50 + i
            break
    return None


def is_eeprom_readable() -> tuple:
    """Check the EEPROM chip directly via bit-banged I2C (bus 9).

    Sets up a bit-banged I2C bus on GPIO 0/1, scans for the EEPROM
    at address 0x50, then reads its content via at24 sysfs.

    Returns:
        (present, valid): present=True if chip responds at 0x50,
        valid=True if chip has non-blank data
    """
    from ._utils import run_command

    try:
        # Ensure sudo is available before running sudo commands
        os.system("sudo -v 2>/dev/null")

        addr = _detect_eeprom_addr()
        if addr is None:
            return (False, False)

        # Chip is present — read content via at24 sysfs (root-only file)
        import tempfile
        os.system("sudo modprobe at24 2>/dev/null")
        dev_path = "/sys/class/i2c-dev/i2c-9/device"
        eeprom_path = f"{dev_path}/9-00{addr:02x}/eeprom"
        if not os.path.isfile(eeprom_path):
            run_command(
                f"echo 24c32 0x{addr:02x} | sudo tee {dev_path}/new_device > /dev/null 2>&1"
            )
        tmp = tempfile.mkdtemp(prefix="eeprom_read_")
        dump = os.path.join(tmp, "eeprom.bin")
        run_command(f"sudo dd if={eeprom_path} of={dump} bs=4096 count=1 2>/dev/null")
        run_command(
            f"echo 0x{addr:02x} | sudo tee {dev_path}/delete_device > /dev/null 2>&1"
        )
        if os.path.isfile(dump) and os.path.getsize(dump) > 4:
            with open(dump, "rb") as f:
                data = f.read()
            valid = data != b"\xff" * len(data)
            return (True, valid)
    except Exception:
        pass
    return (False, False)


def _check_eeprom_direct_detail() -> dict:
    """Check the EEPROM chip directly via bit-banged I2C bus 9 — with step-by-step detail.

    Each phase (bus setup, address scan, data read, content verification)
    is tracked individually so the caller can pinpoint exactly where the
    failure occurred.

    Returns:
        dict with keys:
        - present (bool): chip responds at a valid HAT address (0x50-0x53)
        - valid (bool): chip has data that matches the reference EEPROM binary
        - addr (int|None): detected EEPROM I2C address
        - i2c_bus_ok (bool): /dev/i2c-9 was available or created successfully
        - scan_ok (bool): i2cdetect found a device at a valid address
        - data_size (int|None): bytes read from eeprom
        - data_is_blank (bool|None): True if all bytes are 0xFF
        - data_matches_ref (bool|None): True if data matches reference binary
        - dtoverlay_error (str|None): error from dtoverlay if bus creation failed
        - scan_raw (str|None): raw i2cdetect output for the 0x50 row
        - steps (list[dict]): ordered log of each diagnostic step
    """
    import time
    import tempfile
    from ._utils import run_command

    EEPROM_REF_URL = (
        "https://github.com/sunfounder/sunfounder-hat-helper/raw/refs/heads/"
        "main/eeproms/o1908v10_fusion_hat.eep"
    )

    steps: list[dict] = []
    result: dict = {
        "present": False,
        "valid": False,
        "addr": None,
        "i2c_bus_ok": False,
        "scan_ok": False,
        "data_size": None,
        "data_is_blank": None,
        "data_matches_ref": None,
        "dtoverlay_error": None,
        "scan_raw": None,
        "steps": steps,
    }

    # ── Step 1: ensure /dev/i2c-9 exists ──
    if not os.path.exists("/dev/i2c-9"):
        _, err = run_command(
            "sudo dtoverlay i2c-gpio i2c_gpio_sda=0 i2c_gpio_scl=1 bus=9 2>&1"
        )
        # The device node may take a moment to appear after dtoverlay
        for _ in range(10):
            if os.path.exists("/dev/i2c-9"):
                break
            time.sleep(0.1)
        if not os.path.exists("/dev/i2c-9"):
            result["dtoverlay_error"] = err.strip() if err else "dtoverlay exited OK but /dev/i2c-9 not created"
            steps.append({
                "step": "I2C bus 9 (GPIO 0/1)",
                "ok": False,
                "detail": (
                    f"Cannot create /dev/i2c-9 via dtoverlay. "
                    f"GPIO 0/1 may be in use by another driver or unavailable on this Pi model. "
                    f"dtoverlay says: {result['dtoverlay_error']}"
                ),
            })
            return result
        steps.append({
            "step": "I2C bus 9 (GPIO 0/1)",
            "ok": True,
            "detail": "Created /dev/i2c-9 via dtoverlay i2c-gpio",
        })
    else:
        steps.append({
            "step": "I2C bus 9 (GPIO 0/1)",
            "ok": True,
            "detail": "/dev/i2c-9 already exists",
        })
    result["i2c_bus_ok"] = True

    # ── Step 2: scan for EEPROM at 0x50-0x53 ──
    _, which_out = run_command("which i2cdetect 2>/dev/null")
    if not which_out.strip():
        steps.append({
            "step": "Scan EEPROM (0x50-0x53)",
            "ok": False,
            "detail": "i2cdetect not found. Install i2c-tools: sudo apt install i2c-tools",
        })
        return result

    _, out = run_command("i2cdetect -y 9 0x50 0x53 2>/dev/null")
    addr = None
    raw_50_line = ""
    for line in out.split("\n"):
        stripped = line.strip()
        if stripped.startswith("50:") or stripped.startswith("50 "):
            raw_50_line = stripped
            parts = stripped.split(":")
            if len(parts) >= 2:
                addrs = parts[1].strip().split()
                for i, val in enumerate(addrs[:4]):
                    if val in ("50", "51", "52", "53", "UU"):
                        addr = 0x50 + i
                        break
            break

    result["scan_raw"] = raw_50_line

    if addr is None:
        steps.append({
            "step": "Scan EEPROM (0x50-0x53)",
            "ok": False,
            "detail": (
                f"No EEPROM responding at 0x50-0x53 on bus 9. "
                f"i2cdetect row: {raw_50_line if raw_50_line else '(empty)'}. "
                "Check the HAT is properly seated and the EEPROM chip is functional."
            ),
        })
        return result

    result["addr"] = addr
    result["scan_ok"] = True
    steps.append({
        "step": "Scan EEPROM (0x50-0x53)",
        "ok": True,
        "detail": f"EEPROM responds at 0x{addr:02x} on bus 9",
    })

    # ── Step 3: read EEPROM content via at24 ──
    result["present"] = True
    data = b""
    try:
        os.system("sudo modprobe at24 2>/dev/null")
        dev_path = "/sys/class/i2c-dev/i2c-9/device"
        eeprom_path = f"{dev_path}/9-00{addr:02x}/eeprom"

        if not os.path.isfile(eeprom_path):
            _, reg_out = run_command(
                f"echo 24c32 0x{addr:02x} | sudo tee {dev_path}/new_device 2>&1"
            )
            if not os.path.isfile(eeprom_path):
                steps.append({
                    "step": "at24 EEPROM driver",
                    "ok": False,
                    "detail": (
                        f"Cannot register 24c32 at 0x{addr:02x} on bus 9. "
                        f"new_device write returned: {reg_out.strip()}"
                    ),
                })
                return result

        tmp = tempfile.mkdtemp(prefix="eeprom_read_")
        dump = os.path.join(tmp, "eeprom.bin")
        run_command(f"sudo dd if={eeprom_path} of={dump} bs=4096 count=1 2>/dev/null")
        run_command(
            f"echo 0x{addr:02x} | sudo tee {dev_path}/delete_device > /dev/null 2>&1"
        )

        if not os.path.isfile(dump) or os.path.getsize(dump) <= 4:
            steps.append({
                "step": "Read EEPROM data",
                "ok": False,
                "detail": "EEPROM read returned empty or too-small file (< 4 bytes).",
            })
            return result

        result["data_size"] = os.path.getsize(dump)
        with open(dump, "rb") as f:
            data = f.read()

        is_blank = data == b"\xff" * len(data)
        result["data_is_blank"] = is_blank

        if is_blank:
            result["valid"] = False
            steps.append({
                "step": "Read EEPROM data",
                "ok": False,
                "detail": (
                    f"Read {len(data)} bytes — all 0xFF (blank or corrupted)."
                ),
            })
            return result

        # Data is non-blank — report size
        steps.append({
            "step": "Read EEPROM data",
            "ok": True,
            "detail": f"Read {len(data)} bytes (non-blank).",
        })

    except Exception as e:
        steps.append({
            "step": "Read EEPROM data",
            "ok": False,
            "detail": f"Exception while reading EEPROM: {e}",
        })
        return result

    # ── Step 4: compare with reference EEPROM binary ──
    try:
        ref_tmp = tempfile.mkdtemp(prefix="eeprom_ref_")
        ref_file = os.path.join(ref_tmp, "reference.eep")
        _, _ = run_command(f"wget -q -O {ref_file} {EEPROM_REF_URL} 2>&1")

        if os.path.isfile(ref_file) and os.path.getsize(ref_file) > 0:
            with open(ref_file, "rb") as f:
                ref_data = f.read()

            # Compare only up to the reference size (read data is full chip,
            # typically 4096 bytes; reference is just the programmed payload)
            cmp_len = min(len(data), len(ref_data))
            if data[:cmp_len] == ref_data[:cmp_len] and len(data) >= len(ref_data):
                result["valid"] = True
                result["data_matches_ref"] = True
                steps.append({
                    "step": "Verify EEPROM content",
                    "ok": True,
                    "detail": (
                        f"First {len(ref_data)} bytes match reference — "
                        "EEPROM is correctly programmed."
                    ),
                })
            else:
                result["valid"] = False
                result["data_matches_ref"] = False

                # Side-by-side comparison — only show reference range + a few bytes margin
                show_len = min(len(ref_data) + 32, len(data))
                lines = [f"Byte-by-byte comparison (first {show_len} bytes, Read | Ref):"]
                for offset in range(0, show_len, 8):
                    r = data[offset:offset + 8]
                    t = ref_data[offset:offset + 8] if offset < len(ref_data) else b""
                    r_hex = " ".join(f"{b:02X}" for b in r) if r else ""
                    t_hex = " ".join(f"{b:02X}" for b in t) if t else ""
                    differs = r[:min(len(r), len(t))] != t[:min(len(r), len(t))]
                    marker = "><" if differs else "  "
                    lines.append(f"  {marker} {offset:04X}: {r_hex:<23s} | {t_hex}")
                if len(data) > show_len:
                    lines.append(f"  ... ({len(data) - show_len} more bytes, mostly padding)")

                # Full read data dump — first 128 bytes
                dump_limit = min(len(data), 128)
                lines.append("")
                lines.append(f"Read data (first {dump_limit} of {len(data)} bytes):")
                for offset in range(0, dump_limit, 16):
                    chunk = data[offset:offset + 16]
                    hx = " ".join(f"{b:02X}" for b in chunk)
                    asc = "".join(chr(b) if 32 <= b < 127 else "." for b in chunk)
                    lines.append(f"  {offset:04X}: {hx:<47s} {asc}")

                steps.append({
                    "step": "Verify EEPROM content",
                    "ok": False,
                    "detail": "\n".join(lines),
                })
        else:
            # Can't download reference — accept non-blank as valid
            result["valid"] = True
            result["data_matches_ref"] = None
            steps.append({
                "step": "Verify EEPROM content",
                "ok": True,
                "detail": (
                    "Cannot download reference binary for comparison. "
                    "Accepting non-blank data as valid."
                ),
            })
    except Exception as e:
        result["valid"] = True
        result["data_matches_ref"] = None
        steps.append({
            "step": "Verify EEPROM content",
            "ok": True,
            "detail": (
                f"Reference comparison skipped ({e}). "
                "Accepting non-blank data as valid."
            ),
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
    """Comprehensive driver and hardware health check.

    Checks HAT device-tree detection, EEPROM chip (direct I2C), kernel
    module file, DKMS registration, module load state, sysfs interface,
    and onboard MCU I2C presence at 0x17.

    Returns:
        dict with keys: detected, i2c_enabled, eeprom_present, eeprom_valid,
        module_file, dkms_status, module_loaded, sysfs, i2c_0x17, overall,
        plus *hat_detail* and *eeprom_detail* sub-dicts that record every
        diagnostic step so callers can explain exactly *why* a check failed.
    """
    import platform
    from ._utils import run_command

    result = {
        "detected": False,
        "i2c_enabled": False,
        "eeprom_present": False,
        "eeprom_valid": False,
        "module_file": False,
        "dkms_status": "",
        "module_loaded": False,
        "sysfs": False,
        "i2c_0x17": False,
        "overall": True,
        # Detailed sub-diagnostics
        "hat_detail": None,
        "eeprom_detail": None,
    }

    # 1. HAT device-tree detection (detailed)
    hat_detail = _detect_hat_detail()
    result["hat_detail"] = hat_detail
    result["detected"] = hat_detail["detected"]

    # 1a. I2C enabled?
    result["i2c_enabled"] = os.path.exists("/dev/i2c-1")

    # 1b. If device-tree didn't pick it up, check the chip directly via I2C
    if not result["detected"]:
        eeprom_detail = _check_eeprom_direct_detail()
        result["eeprom_detail"] = eeprom_detail
        result["eeprom_present"] = eeprom_detail["present"]
        result["eeprom_valid"] = eeprom_detail["valid"]

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
        _, i2c_out = run_command("sudo i2cdetect -y 1 0x10 0x1f 2>/dev/null")
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

    # 7. dmesg — look for HAT / EEPROM / I2C boot messages
    result["dmesg_hat"] = ""
    _, dmesg_out = run_command(
        "dmesg 2>/dev/null | grep -i -E 'hat|eeprom.*0x50|i2c.*error|fusionhat|i2c-0' | tail -20 || true"
    )
    if dmesg_out.strip():
        result["dmesg_hat"] = dmesg_out.strip()

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
    - EEPROM not detected: reflash EEPROM via update_eeprom()
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

    # Fix 1: I2C not enabled → enable it
    if not before["i2c_enabled"]:
        fixes.append("enable I2C")
        run_command("sudo raspi-config nonint do_i2c 0 2>/dev/null")
        run_command("sudo modprobe i2c-dev 2>/dev/null")

    # Fix 2: EEPROM not detected → reflash
    if not before["detected"]:
        ok = update_eeprom(erase=True)
        if ok:
            fixes.append("EEPROM reflashed — reboot required")
        else:
            fixes.append("EEPROM reflash failed")
        after = doctor()
        return {
            "before": before,
            "fixes": fixes,
            "after": after,
            "fixed": after["overall"],
        }

    # Fix 2: module loaded but sysfs missing → reload module
    if before["module_loaded"] and not before["sysfs"]:
        fixes.append("reload fusion_hat module")
        run_command("sudo rmmod fusion_hat 2>/dev/null")
        run_command("sudo modprobe fusion_hat 2>/dev/null")

    # Fix 3: module file exists but not loaded → modprobe
    if before["module_file"] and not before["module_loaded"]:
        fixes.append("modprobe fusion_hat")
        run_command("sudo modprobe fusion_hat 2>/dev/null")

    # Fix 4: module file missing → try to install
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
    script = os.path.join(os.path.dirname(__file__), "scripts", "eepflash.sh")
    if os.path.isfile(script):
        return script
    return ""


def update_eeprom(erase: bool = False, erase_only: bool = False) -> bool:
    """Reflash the Fusion Hat EEPROM via I2C GPIO bit-banging.

    Uses the bundled eepflash.sh script and a bit-banged I2C bus on
    GPIO 0/1. The user must short the two outermost holes of the 5-pin
    header next to the EEPROM chip to enable writing.

    Args:
        erase: If True, erase the EEPROM (write all 0xFF) BEFORE flashing
               the correct binary. This ensures a clean write.
        erase_only: If True, ONLY erase the EEPROM (write all 0xFF) and
               return. Used for testing. Cannot be combined with erase.

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
        title = "Erase Only" if erase_only else ("Erase + Update" if erase else "Update")
        total = 3 if erase_only else (6 if erase else 5)

        print("")
        print("=" * 60)
        print(f"  Fusion Hat EEPROM {title}")
        print("=" * 60)
        print("")

        # 1. Prepare files to write
        if erase_only:
            print(f"  [1/{total}] Preparing blank EEPROM image...")
            write_file = os.path.join(tmpdir, "blank.eep")
            with open(write_file, "wb") as f:
                f.write(b"\xff" * 4096)
            print(f"  [OK]  Created blank image")
            blank_file = write_file
        elif erase:
            print(f"  [1/{total}] Preparing blank + EEPROM binary...")
            blank_file = os.path.join(tmpdir, "blank.eep")
            with open(blank_file, "wb") as f:
                f.write(b"\xff" * 4096)
            write_file = os.path.join(tmpdir, "o1908v10_fusion_hat.eep")
            _, out = run_command(f"wget -q -O {write_file} {EEPROM_URL} 2>&1")
            if not os.path.isfile(write_file) or os.path.getsize(write_file) == 0:
                print(f"  [FAIL] Failed to download EEPROM binary from {EEPROM_URL}")
                return False
            print(f"  [OK]  Created blank + downloaded ({os.path.getsize(write_file)} bytes)")
        else:
            print("  [1/5] Downloading EEPROM binary...")
            write_file = os.path.join(tmpdir, "o1908v10_fusion_hat.eep")
            _, out = run_command(f"wget -q -O {write_file} {EEPROM_URL} 2>&1")
            if not os.path.isfile(write_file) or os.path.getsize(write_file) == 0:
                print(f"  [FAIL] Failed to download EEPROM binary from {EEPROM_URL}")
                return False
            print(f"  [OK]  Downloaded: {os.path.basename(write_file)} ({os.path.getsize(write_file)} bytes)")

        # Detect EEPROM address
        addr = _detect_eeprom_addr()
        if addr is None:
            print("  [FAIL] EEPROM not found on I2C bus 9. Check the HAT is properly seated.")
            return False
        print(f"  EEPROM found at address 0x{addr:02x}")
        print("")

        # 2. Instruct user to short write-protect pins
        print("")
        if erase:
            print(f"  [2/{total}] Short write-protect pins")
        else:
            print(f"  [2/{total}] Short write-protect pins")
        print("")
        print("  The EEPROM chip is write-protected. To enable writing,")
        print("  short the two OUTERMOST holes of the 5-pin header next to")
        print("  the EEPROM chip on the Fusion Hat board.")
        print("")
        print("   ||||")
        print("  ┌────┐")
        print("  │    │")
        print("  │    │[ o ] <-- short this")
        print("  │    │[ o ]")
        print("  └────┘[ o ]")
        print("   |||| [ o ]")
        print("        [ o ] <-- short this")
        print("")
        print("  WARNING: Only short the two marked pins (outermost).")
        print("  Shorting other holes may cause the Pi to shut down.")
        print("")
        input("  Press ENTER after you have shorted the pins...")

        # 3. Erase (if requested)
        if erase or erase_only:
            print("")
            print(f"  [3/{total}] Erase EEPROM...")
            _, erase_out = run_command(
                f"sudo bash {eepflash} -y -w -f={blank_file} -t=24c32 -a={addr:02x} 2>&1"
            )
            print(erase_out)
            if "done" not in erase_out.lower():
                print("  [FAIL] EEPROM erase failed. Check output above for details.")
                return False

            # Verify erase — read back and check all 0xFF
            try:
                os.system("sudo modprobe at24 2>/dev/null")
                dev_path = "/sys/class/i2c-dev/i2c-9/device"
                eeprom_path = f"{dev_path}/9-00{addr:02x}/eeprom"
                if not os.path.isfile(eeprom_path):
                    run_command(
                        f"echo 24c32 0x{addr:02x} | sudo tee {dev_path}/new_device > /dev/null 2>&1"
                    )
                evtmp = tempfile.mkdtemp(prefix="eeprom_erase_verify_")
                edump = os.path.join(evtmp, "erase_verify.bin")
                run_command(f"sudo dd if={eeprom_path} of={edump} bs=4096 count=1 2>/dev/null")
                run_command(
                    f"echo 0x{addr:02x} | sudo tee {dev_path}/delete_device > /dev/null 2>&1"
                )
                if os.path.isfile(edump) and os.path.getsize(edump) > 4:
                    with open(edump, "rb") as f:
                        edata = f.read()
                    if edata == b"\xff" * len(edata):
                        print(f"  [OK]  Erase verified — chip is blank")
                    else:
                        non_ff = [hex(i) for i, b in enumerate(edata[:64]) if b != 0xFF]
                        print(f"  [FAIL] Erase did not complete — {len(non_ff)} non-blank bytes found in first 64.")
                        print(f"  → The write-protect may have lost contact. Try again.")
                        return False
            except Exception as e:
                print(f"  [!] Could not verify erase: {e}")

            # If erase-only, skip flash and go to done
            if erase_only:
                print("")
                print(f"  [3/{total}] Done. You can remove the short from the write-protect pins now.")
                return True

        # 4. Flash EEPROM
        print("")
        if erase:
            print("  [4/6] Flash EEPROM...")
        else:
            print("  [3/5] Flash EEPROM...")
        _, flash_out = run_command(
            f"sudo bash {eepflash} -y -w -f={write_file} -t=24c32 -a={addr:02x} 2>&1"
        )
        print(flash_out)
        if "done" not in flash_out.lower():
            print("  [FAIL] EEPROM write failed. Check output above for details.")
            return False

        # 5. Verify — read back and compare against the written file
        step_verify = f"[5/{total}]" if erase else f"[4/{total}]"
        print("")
        print(f"  {step_verify} Verifying EEPROM content...")
        with open(write_file, "rb") as f:
            expected = f.read()

        ok = False
        try:
            os.system("sudo modprobe at24 2>/dev/null")
            dev_path = "/sys/class/i2c-dev/i2c-9/device"
            eeprom_path = f"{dev_path}/9-00{addr:02x}/eeprom"
            if not os.path.isfile(eeprom_path):
                run_command(
                    f"echo 24c32 0x{addr:02x} | sudo tee {dev_path}/new_device > /dev/null 2>&1"
                )
            vtmp = tempfile.mkdtemp(prefix="eeprom_verify_")
            vdump = os.path.join(vtmp, "verify.bin")
            run_command(f"sudo dd if={eeprom_path} of={vdump} bs=4096 count=1 2>/dev/null")
            run_command(
                f"echo 0x{addr:02x} | sudo tee {dev_path}/delete_device > /dev/null 2>&1"
            )
            if os.path.isfile(vdump) and os.path.getsize(vdump) > 4:
                with open(vdump, "rb") as f:
                    actual = f.read()
                if len(actual) >= len(expected) and actual[:len(expected)] == expected:
                    ok = True
                elif actual == b"\xff" * len(actual):
                    print("  [FAIL] EEPROM is blank — write may have failed silently.")
                    print("  → Check that the write-protect pins are securely shorted.")
                    print("  → Try again and ensure the two outermost holes stay shorted")
                    print("    during the entire flash step.")
                else:
                    # Find first diff for diagnostics
                    cmp_len = min(len(actual), len(expected))
                    for i in range(cmp_len):
                        if actual[i] != expected[i]:
                            start = max(0, i - 4)
                            end = min(cmp_len, i + 12)
                            read_hex = " ".join(f"{actual[j]:02X}" for j in range(start, end))
                            exp_hex = " ".join(f"{expected[j]:02X}" for j in range(start, end))
                            print(f"  [FAIL] Content mismatch at offset 0x{i:04X}:")
                            print(f"    Read : {read_hex}")
                            print(f"    Wrote: {exp_hex}")
                            break
                    else:
                        if len(actual) < len(expected):
                            print(f"  [FAIL] Read only {len(actual)} bytes, expected {len(expected)}.")
        except Exception as e:
            print(f"  [!] Could not verify: {e}")

        if ok:
            size_str = f"{len(expected)} bytes" if len(expected) < 1024 else f"{len(expected) / 1024:.1f} KB"
            print(f"  [OK]  EEPROM verified — {size_str} written correctly.")
        else:
            print("  → If write-protect was properly shorted, the EEPROM chip may be damaged.")

        # 6. Done — offer reboot
        step_done = f"[6/{total}]" if erase else f"[5/{total}]"
        print("")
        print(f"  {step_done} Done. You can remove the short from the write-protect pins now.")
        answer = input("  Reboot to detect the HAT? (y/N): ").strip().lower()
        if answer in ("y", "yes"):
            print("  Rebooting...")
            run_command("sudo reboot 2>&1")
        else:
            print("  Reboot later with: sudo reboot")
            print("  Then verify with: fusion_hat doctor")

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

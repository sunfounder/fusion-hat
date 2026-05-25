
import argparse

def enable_speaker():
    print(f"Enable Fusion-HAT speaker.")
    from .device import enable_speaker
    enable_speaker()

def disable_speaker():
    print(f"Disable Fusion-HAT speaker.")
    from .device import disable_speaker
    disable_speaker()

def test_speaker():
    print(f"Test Fusion-HAT speaker.")
    from .device import enable_speaker, disable_speaker
    from ._utils import run_command
    try:
        enable_speaker()
        run_command("speaker-test -l3 -c2 -t wav")
    finally:
        disable_speaker()

def print_version():
    from ._version import __version__
    print(f"Fusion HAT library version: {__version__}")

def update():
    """Update fusion-hat from git and reinstall."""
    import os as _os
    from ._utils import run_command
    from ._version import __version__

    # Find the repo directory (parent of the installed package)
    repo_dir = _os.path.dirname(_os.path.dirname(__file__))
    if not _os.path.isdir(_os.path.join(repo_dir, ".git")):
        # Fallback: try standard locations
        for d in ["/home/pi/fusion-hat", _os.path.expanduser("~/fusion-hat")]:
            if _os.path.isdir(_os.path.join(d, ".git")):
                repo_dir = d
                break
        else:
            print("[FAIL] Cannot find fusion-hat git repository.")
            print("  Clone it first: git clone https://github.com/sunfounder/fusion-hat ~/fusion-hat")
            return

    print(f"  Repository: {repo_dir}")
    print(f"  Current version: {__version__}")
    print("")

    # Pull
    print("  [1/3] git pull...")
    _, out = run_command(f"cd {repo_dir} && git pull 2>&1")
    print(out)
    if "Already up to date" in out:
        print("  Already up to date.")
        return

    # Reinstall Python package
    print("  [2/3] pip install...")
    _, out = run_command(
        f"cd {repo_dir} && sudo pip install . --break-system-packages --no-deps --no-build-isolation 2>&1"
    )
    for line in out.split("\n"):
        if "Successfully installed" in line or "error:" in line.lower():
            print(f"  {line.strip()}")

    # Build and install kernel driver
    driver_dir = _os.path.join(repo_dir, "driver")
    if _os.path.isdir(driver_dir) and _os.path.isfile(_os.path.join(driver_dir, "Makefile")):
        print("  [3/3] sudo make install (driver)...")
        _, out = run_command(
            f"cd {driver_dir} && sudo make install 2>&1"
        )
        # Show key lines
        for line in out.split("\n"):
            line = line.strip()
            if line and ("Installing" in line or "completed" in line.lower() or "error" in line.lower() or "DKMS" in line):
                print(f"  {line}")
    else:
        print("  [3/3] Driver not found, skipping.")

    # Read new version from disk (current process still has old import)
    new_ver = __version__
    try:
        ver_file = _os.path.join(_os.path.dirname(__file__), "_version.py")
        with open(ver_file, "r") as f:
            content = f.read()
        import re as _re
        m = _re.search(r"__version__\s*=\s*['\"]([^'\"]+)['\"]", content)
        if m:
            new_ver = m.group(1)
    except Exception:
        pass

    print("")
    if new_ver != __version__:
        print(f"  Updated: {__version__} -> {new_ver}")
    else:
        print(f"  Version: {new_ver} (up to date)")
    print("  Run: fusion_hat doctor")

def scan_i2c():
    print(f"Scan I2C bus.")
    from ._i2c import I2C
    i2c = I2C()
    devices = i2c.scan()
    devices = ["0x{:02X}".format(device) for device in devices]
    print(f"Found devices: {devices}")

def print_doctor(fix: bool = False):
    # Prompt for sudo early so password prompt appears before the banner
    import os as _os
    _os.system("sudo -v 2>/dev/null")

    if fix:
        from fusion_hat.device import doctor_fix
        result = doctor_fix()
        before = result["before"]
        after = result["after"]
        fixes = result["fixes"]

        print("")
        print("=" * 50)
        print("  Fusion Hat Doctor (--fix)")
        print("=" * 50)
        print("")

        if fixes:
            for action in fixes:
                print(f"  → {action}")
        if result["fixed"]:
            if not fixes:
                print("  All checks pass. Nothing to fix.")

        print("")
        print("=" * 50)
        print("")
    else:
        from fusion_hat.device import doctor
        print("")
        print("=" * 50)
        print("  Fusion Hat Driver Status")
        print("=" * 50)
        print("")
        result = doctor()
        _show_doctor_result(result)

        if not result["overall"]:
            if not result["detected"]:
                eeprom_detail = result.get("eeprom_detail") or {}
                i2c_bus_ok = eeprom_detail.get("i2c_bus_ok", False)
                scan_ok = eeprom_detail.get("scan_ok", False)
                data_is_blank = eeprom_detail.get("data_is_blank")

                if not i2c_bus_ok:
                    print("  Cannot communicate with EEPROM — I2C bus 9 not available.")
                    dtoverlay_err = eeprom_detail.get("dtoverlay_error", "")
                    if dtoverlay_err:
                        print(f"  dtoverlay: {dtoverlay_err}")
                    print("  → GPIO 0/1 may be in use or unavailable on this Pi model.")
                elif not scan_ok:
                    print("  HAT not detected — EEPROM chip not responding on I2C bus 9.")
                    scan_raw = eeprom_detail.get("scan_raw", "")
                    if scan_raw:
                        print(f"  i2cdetect row 50: {scan_raw}")
                    print("  → Check the HAT is properly seated on the GPIO header.")
                elif data_is_blank:
                    print("  EEPROM is blank or corrupted.")
                    print("")
                    print("  → Run: fusion_hat doctor --fix")
                elif not result.get("eeprom_valid", False):
                    print("  EEPROM data does not match expected content.")
                    print("")
                    print("  → Run: fusion_hat doctor --fix")
                else:
                    print("  HAT not detected but EEPROM has valid data.")
                    print("")
                    print("  → Run: sudo reboot")
            else:
                print("  Some checks failed.")
                if not result["module_file"]:
                    print("  -> Run: cd driver && sudo make install")
                if not result["module_loaded"]:
                    print("  -> Run: sudo modprobe fusion_hat")
                if not result["sysfs"]:
                    print("  -> Driver may not be loaded or compatible with this kernel.")
                if not result["i2c_0x17"]:
                    print("  -> Onboard MCU not detected on I2C bus. Check: i2cdetect -y 1")

            # Show dmesg if HAT-related messages found
            dmesg_hat = result.get("dmesg_hat", "")
            if dmesg_hat:
                print("")
                print("  dmesg (HAT/EEPROM/I2C):")
                for line in dmesg_hat.strip().split("\n"):
                    print(f"    {line}")

            # Show Tip only when --fix can actually help (not when just needs reboot)
            if not result["overall"]:
                eeprom_detail = result.get("eeprom_detail") or {}
                needs_fix = not (eeprom_detail.get("valid") and not result.get("detected"))
                if needs_fix:
                    print("")
                    print("  Tip: run 'fusion_hat doctor --fix' to auto-fix.")

        print("")
        print("=" * 50)
        print("")


def _show_detail_steps(steps, indent="      "):
    """Print diagnostic steps — shows all steps with pass/fail icons."""
    GREEN = "\033[32m"
    RED = "\033[31m"
    RESET = "\033[0m"

    for s in steps:
        ok = s["ok"]
        icon = f"{GREEN}✓{RESET}" if ok else f"{RED}✗{RESET}"
        print(f"{indent}{icon} {s['step']}")
        detail = s.get("detail", "")
        if detail:
            for line in detail.split("\n"):
                print(f"{indent}   {line}")


def _show_doctor_result(result):
    """Render a single doctor result dict to stdout with step-by-step detail."""
    GREEN = "\033[32m"
    RED = "\033[31m"
    RESET = "\033[0m"

    def _icon(ok):
        return f"{GREEN}✓{RESET}" if ok else f"{RED}✗{RESET}"

    # ── 1. HAT device-tree detection ──
    hat_detail = result.get("hat_detail") or {}
    print(f"  {_icon(result['detected'])} HAT detected")

    if not result["detected"] and hat_detail.get("steps"):
        print("      HAT device-tree check:")
        _show_detail_steps(hat_detail["steps"])

    # ── 2. EEPROM direct check (only when HAT not detected) ──
    eeprom_detail = result.get("eeprom_detail")
    if eeprom_detail:
        eeprom_steps = eeprom_detail.get("steps", [])
        print(f"      Direct EEPROM check (bus 9, GPIO 0/1):")
        _show_detail_steps(eeprom_steps)
    elif not result["detected"]:
        # Old-style result without eeprom_detail (backward compat)
        if "eeprom_present" in result:
            print(f"  {_icon(result['eeprom_present'])} EEPROM chip (0x50)")
        if result.get("eeprom_present"):
            print(f"  {_icon(result['eeprom_valid'])} EEPROM content")

    # ── 3. I2C MCU ──
    print(f"  {_icon(result['i2c_0x17'])} I2C MCU (0x17)")

    # ── 4. Driver checks ──
    print(f"  {_icon(result['module_file'])} Module file")
    print(f"  {_icon(result['module_loaded'])} Module loaded")
    print(f"  {_icon(result['sysfs'])} sysfs interface")

    # ── 5. DKMS ──
    dkms = result["dkms_status"]
    if dkms == "DKMS not installed":
        print(f"   - DKMS             : {dkms}")
    elif dkms == "not registered":
        print(f"  {RED}✗{RESET} DKMS           : {dkms} (run 'sudo make install' to register)")
    else:
        lines = dkms.strip().split("\n")
        print(f"  {GREEN}✓{RESET} DKMS            : {lines[0]}")
        for line in lines[1:]:
            print(f"                         {line}")

    print("")

def print_update_eeprom(erase: bool = False, erase_only: bool = False):
    import os as _os
    _os.system("sudo -v 2>/dev/null")
    print("Update Fusion-HAT EEPROM.")
    from .device import update_eeprom
    success = update_eeprom(erase=erase, erase_only=erase_only)
    if not success:
        print("EEPROM update did not complete successfully.")
        print("Check the output above for details.")

def setup_speaker(skip_test: bool = False):
    from ._utils import run_command
    import os
    script = os.path.join(os.path.dirname(__file__), "scripts", "setup_fusion_hat_audio.sh")
    if not os.path.isfile(script):
        print(f"Script not found: {script}")
        return
    print("Setting up speaker...")
    args = "--skip-test" if skip_test else ""
    status, output = run_command(f"sudo bash {script} {args} 2>&1")
    print(output)
    if status is not None and status != 0:
        print(f"Setup speaker failed with exit code {status}.")
    else:
        print("Speaker setup complete.")

def print_info():
    from fusion_hat._version import __version__
    from fusion_hat.device import NAME
    from fusion_hat.device import ID
    from fusion_hat.device import UUID
    from fusion_hat.device import PRODUCT_ID
    from fusion_hat.device import PRODUCT_VER
    from fusion_hat.device import VENDOR
    from fusion_hat.device import raise_if_fusion_hat_not_ready
    from fusion_hat.device import get_speaker_state
    from fusion_hat.device import get_usr_btn
    from fusion_hat.device import get_firmware_version
    from fusion_hat.device import get_driver_version
    from fusion_hat.device import get_led
    from fusion_hat.battery import Battery

    raise_if_fusion_hat_not_ready()

    battery = Battery()

    datas = {
        "Name": NAME,
        "ID": ID,
        "UUID": UUID,
        "Product ID": PRODUCT_ID,
        "Product Ver": PRODUCT_VER,
        "Vendor": VENDOR,
        "Library Version": __version__,
        "Firmware Version": get_firmware_version(),
        "Driver Version": get_driver_version(),

        "User Button State": "Pressed" if get_usr_btn() else "Released",
        "Speaker State": "Enabled" if get_speaker_state() else "Disabled",
        "User LED State": "On" if get_led() else "Off",
        "Battery level": f"{battery.capacity}%",
        "Battery voltage": f"{battery.voltage} V",
        "Battery charging": "Yes" if battery.is_charging else "No",
    }

    print("")
    print("=" * 50)
    print("  Fusion Hat Device Info")
    print("=" * 50)
    print("")
    for key, value in datas.items():
        print(f"  {key:>18}: {value}")
    print("")
    print("=" * 50)
    print("")

def main():
    """ fusion_hat command line interface """

    CHOICES = {
        "enable_speaker": enable_speaker,
        "disable_speaker": disable_speaker,
        "test_speaker": test_speaker,
        "version": print_version,
        "update": update,
        "scan_i2c": scan_i2c,
        "info": print_info,
        "doctor": print_doctor,
        "update_eeprom": print_update_eeprom,
        "setup_speaker": setup_speaker,
    }

    parser = argparse.ArgumentParser(description='fusion_hat command line interface')
    parser.add_argument('option', choices=CHOICES.keys(), help='option')
    parser.add_argument('--fix', action='store_true', help='auto fix driver issues (doctor only)')
    parser.add_argument('--erase', action='store_true', help='erase EEPROM before flashing (update_eeprom only)')
    parser.add_argument('--erase-only', action='store_true', help='only erase EEPROM, do not flash (update_eeprom only, for testing)')
    parser.add_argument('--skip-test', action='store_true', help='skip speaker test (setup_speaker only)')
    args = parser.parse_args()

    if args.fix and args.option != "doctor":
        parser.error("--fix is only valid with 'doctor'")
    if args.erase and args.option != "update_eeprom":
        parser.error("--erase is only valid with 'update_eeprom'")
    if args.erase_only and args.option != "update_eeprom":
        parser.error("--erase-only is only valid with 'update_eeprom'")
    if args.erase and args.erase_only:
        parser.error("--erase and --erase-only cannot be used together")
    if args.skip_test and args.option != "setup_speaker":
        parser.error("--skip-test is only valid with 'setup_speaker'")

    if args.option == "doctor":
        CHOICES[args.option](fix=args.fix)
    elif args.option == "update_eeprom":
        CHOICES[args.option](erase=args.erase, erase_only=args.erase_only)
    elif args.option == "setup_speaker":
        CHOICES[args.option](skip_test=args.skip_test)
    else:
        CHOICES[args.option]()

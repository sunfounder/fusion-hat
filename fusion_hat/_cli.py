
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

def scan_i2c():
    print(f"Scan I2C bus.")
    from ._i2c import I2C
    i2c = I2C()
    devices = i2c.scan()
    devices = ["0x{:02X}".format(device) for device in devices]
    print(f"Found devices: {devices}")

def print_doctor(fix: bool = False):
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
                if not result.get("eeprom_present", False):
                    print("  HAT not detected — EEPROM chip not found on I2C.")
                    print("  → Check the HAT is properly seated on the GPIO header.")
                elif not result.get("eeprom_valid", False):
                    print("  HAT not detected — EEPROM is blank or has invalid data.")
                    print("  → Run: fusion_hat doctor --fix")
                else:
                    print("  HAT not detected but EEPROM has valid data.")
                    print("  → If you just flashed the EEPROM, reboot to apply: sudo reboot")
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
                print("")
                print("  Tip: run 'fusion_hat doctor --fix' to auto-fix.")

        print("")
        print("=" * 50)
        print("")


def _show_doctor_result(result):
    """Render a single doctor result dict to stdout."""
    GREEN = "\033[32m"
    RED = "\033[31m"
    RESET = "\033[0m"

    def _icon(ok):
        return f"{GREEN}✓{RESET}" if ok else f"{RED}✗{RESET}"

    lines = [
        (_icon(result["detected"]), "HAT detected"),
    ]

    # If not detected, show EEPROM diagnosis via I2C bus 9
    if not result["detected"]:
        if "eeprom_present" in result:
            lines.append((_icon(result["eeprom_present"]), "EEPROM chip (0x50)"))
        if result.get("eeprom_present"):
            lines.append((_icon(result["eeprom_valid"]), "EEPROM content"))

    lines += [
        (_icon(result["i2c_0x17"]), "I2C MCU (0x17)"),
    ]

    lines += [
        (_icon(result["module_file"]), "Module file"),
        (_icon(result["module_loaded"]), "Module loaded"),
        (_icon(result["sysfs"]), "sysfs interface"),
    ]

    for icon, label in lines:
        print(f"  {icon} {label}")

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

def print_update_eeprom(erase: bool = False):
    print("Update Fusion-HAT EEPROM.")
    from .device import update_eeprom
    success = update_eeprom(erase=erase)
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
    parser.add_argument('--skip-test', action='store_true', help='skip speaker test (setup_speaker only)')
    args = parser.parse_args()

    if args.fix and args.option != "doctor":
        parser.error("--fix is only valid with 'doctor'")
    if args.erase and args.option != "update_eeprom":
        parser.error("--erase is only valid with 'update_eeprom'")
    if args.skip_test and args.option != "setup_speaker":
        parser.error("--skip-test is only valid with 'setup_speaker'")

    if args.option == "doctor":
        CHOICES[args.option](fix=args.fix)
    elif args.option == "update_eeprom":
        CHOICES[args.option](erase=args.erase)
    elif args.option == "setup_speaker":
        CHOICES[args.option](skip_test=args.skip_test)
    else:
        CHOICES[args.option]()

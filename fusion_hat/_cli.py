
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

def print_doctor():
    from fusion_hat.device import doctor

    print("")
    print("=" * 50)
    print("  Fusion Hat Driver Status")
    print("=" * 50)
    print("")

    result = doctor()

    status_icon = {True: "OK", False: "FAIL"}

    checks = [
        ("EEPROM detected", result["detected"]),
        ("Module file   ", result["module_file"]),
        ("Module loaded ", result["module_loaded"]),
        ("sysfs interface", result["sysfs"]),
    ]

    for label, ok in checks:
        icon = status_icon[ok]
        print(f"  [{icon}]  {label}")

    # DKMS is informational
    dkms = result["dkms_status"]
    if dkms == "DKMS not installed":
        print(f"  [ -]  DKMS          : {dkms}")
    elif dkms == "not registered":
        print(f"  [WARN] DKMS        : {dkms} (run 'sudo make install' to register)")
    else:
        print(f"  [OK]  DKMS          : {dkms}")

    print("")

    if not result["overall"]:
        print("  Some checks failed.")
        if not result["detected"]:
            print("  -> Is the Fusion Hat properly seated on the GPIO header?")
        if not result["module_file"]:
            print("  -> Run: cd driver && sudo make install")
        if not result["module_loaded"]:
            print("  -> Run: sudo modprobe fusion_hat")
        if not result["sysfs"]:
            print("  -> Driver may not be loaded or compatible with this kernel.")

    print("")
    print("=" * 50)
    print("")

def print_info():
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

    # Run doctor check first
    print_doctor()

    raise_if_fusion_hat_not_ready()

    battery = Battery()

    datas = {
        "Name": NAME,
        "ID": ID,
        "UUID": UUID,
        "Product ID": PRODUCT_ID,
        "Product Ver": PRODUCT_VER,
        "Vendor": VENDOR,
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
    print("="*50)
    print("")
    for key, value in datas.items():
        print(f"{key:>20}: {value}")

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
    }

    parser = argparse.ArgumentParser(description='fusion_hat command line interface')
    parser.add_argument('option', choices=CHOICES.keys(), help='option')
    args = parser.parse_args()

    CHOICES[args.option]()

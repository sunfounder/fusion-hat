from fusion_hat.device import NAME
from fusion_hat.device import ID
from fusion_hat.device import UUID
from fusion_hat.device import PRODUCT_ID
from fusion_hat.device import PRODUCT_VER
from fusion_hat.device import VENDOR
from fusion_hat.device import is_installed
from fusion_hat.device import enable_speaker
from fusion_hat.device import disable_speaker
from fusion_hat.device import set_led
from fusion_hat.device import get_speaker_state
from fusion_hat.device import get_usr_btn
from fusion_hat.device import get_firmware_version
from fusion_hat.device import get_driver_version
from fusion_hat.battery import Battery

import time

battery = Battery()

def main():
    led_status = False

    while True:
        # Toggle user LED
        led_status = not led_status
        set_led(led_status)
        
        # Toggle speaker
        if get_speaker_state():
            disable_speaker()
        else:
            enable_speaker()

        datas = {
            "Name": NAME,
            "ID": ID,
            "UUID": UUID,
            "Product ID": PRODUCT_ID,
            "Product Ver": PRODUCT_VER,
            "Vendor": VENDOR,
            "Firmware Version": get_firmware_version(),
            "Driver Version": get_driver_version(),

            "Is Installed": is_installed(),
            "User Button State": "Pressed" if get_usr_btn() else "Released",
            "Speaker State": "Enabled" if get_speaker_state() else "Disabled",
            "User LED State": "On" if led_status else "Off",
            "Battery level": f"{battery.capacity}%",
            "Battery voltage": f"{battery.voltage} V",
            "Battery charging": "Yes" if battery.is_charging else "No",
        }

        print("")
        print("="*50)
        print("")
        for key, value in datas.items():
            print(f"{key:>20}: {value}")

        time.sleep(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Exiting...")
    finally:
        disable_speaker()
        set_led(False)

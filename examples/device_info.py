from fusion_hat.device import *
from fusion_hat.utils import get_battery_voltage
from fusion_hat.utils import get_usr_btn
from fusion_hat.utils import get_speaker_state
from fusion_hat.utils import get_charge_state
from fusion_hat.utils import get_firmware_version
import time

while True:
    datas = {
        "Name": NAME,
        "ID": ID,
        "UUID": UUID,
        "Product ID": PRODUCT_ID,
        "Product Ver": PRODUCT_VER,
        "Vendor": VENDOR,
        "Firmware Version": ".".join([str(v) for v in get_firmware_version()]),

        "I2C Address": f"0x{I2C_ADDRESS:02X}",
        "Is Installed": is_installed(),
        "Battery Voltage": f"{round(get_battery_voltage(), 2)} V",
        "Charge State": "Charging" if get_charge_state() else "Not Charging",
        "User Button State": "Pressed" if get_usr_btn() else "Released",
        "Speaker State": "Enabled" if get_speaker_state() else "Disabled",
    }

    for key, value in datas.items():
        print(f"{key:>20}: {value}")

    time.sleep(1)
    print("="*40)
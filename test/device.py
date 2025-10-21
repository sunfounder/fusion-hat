""" Devices constants """

import os


HAT_DEVICE_TREE = "/proc/device-tree/"

NAME = "Fusion Hat"
ID = "fusion_hat"
I2C_ADDRESS = 0x17
UUID = "9daeea78-0000-0774-000a-582369ac3e02"

PRODUCT_ID = 0x0774
PRODUCT_VER = 0x000a
VENDOR = "SunFounder"

def is_installed() -> bool:
    """ Check if a fusion hat is installed

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

if __name__ == "__main__":
    print(f"Name: {NAME}")
    print(f"ID: {ID}")
    print(f"I2C Address: {I2C_ADDRESS}")
    print(f"UUID: {UUID}")
    print(f"Product ID: 0x{PRODUCT_ID:04X}")
    print(f"Product Ver: 0x{PRODUCT_VER:04X}")
    print(f"Vendor: {VENDOR}")
    print(f"Is Installed: {is_installed()}")

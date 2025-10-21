from fusion_hat.device import *
from fusion_hat.utils import get_battery_voltage
from fusion_hat.utils import get_usr_btn


print(f"Name: {NAME}")
print(f"ID: {ID}")
print(f"I2C Address: {I2C_ADDRESS}")
print(f"UUID: {UUID}")
print(f"Product ID: 0x{PRODUCT_ID:04X}")
print(f"Product Ver: 0x{PRODUCT_VER:04X}")
print(f"Vendor: {VENDOR}")
print(f"Is Installed: {is_installed()}")
print(f"Battery Voltage: {get_battery_voltage()} V")
print(f"User Button State: {get_usr_btn()}")


import argparse

def main():
    """ fusion_hat command line interface """

    parser = argparse.ArgumentParser(description='fusion_hat command line interface')
    parser.add_argument('option', choices=['enable_speaker', 'disable_speaker', 'version', 'info'], help='option')
    args = parser.parse_args()

    if args.option == "enable_speaker":
        print(f"Enable Fusion-HAT speaker.")
        from .device import enable_speaker
        enable_speaker()
    elif args.option == "disable_speaker":
        print(f"Disable Fusion-HAT speaker.")
        from .device import disable_speaker
        disable_speaker()
    elif args.option == "version":
        print(f"fusion-hat library version: {__version__}")
    elif args.option == "info":
        from .device import NAME, PRODUCT_ID, PRODUCT_VER, VENDOR, get_firmware_version
        print(f'HAT name: {NAME}')
        print(f'PCB ID: O{PRODUCT_ID}V{PRODUCT_VER}')
        print(f'Vendor: {VENDOR}')
        firmware_ver = get_firmware_version()
        firmware_ver = f'{firmware_ver[0]}.{firmware_ver[1]}.{firmware_ver[2]}'
        print(f"Firmare version: {firmware_ver}")

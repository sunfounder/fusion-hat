from .version import __version__
from .device import __device__
import argparse

from .utils import enable_speaker, \
    disable_speaker, \
    get_firmware_version, \
    get_shutdown_request, \
    info, \
    warn

def fusion_hat_cmd():
    """ fusion_hat command line interface """
    parser = argparse.ArgumentParser(description='fusion_hat command line interface')
    parser.add_argument('option', type=str, help='option')
    args = parser.parse_args()

    if args.option == "enable_speaker":
        info(f"Enable Fusion-HAT speaker.")
        enable_speaker()
    elif args.option == "disable_speaker":
        info(f"Disable Fusion-HAT speaker.")
        disable_speaker()
    elif args.option == "version":
        info(f"fusion-hat library version: {__version__}")
    elif args.option == "info":
        info(f'HAT name: {__device__.name}')
        info(f'PCB ID: O{__device__.product_id}V{__device__.product_ver}')
        info(f'Vendor: {__device__.vendor}')
        firmware_ver = get_firmware_version()
        firmware_ver = f'{firmware_ver[0]}.{firmware_ver[1]}.{firmware_ver[2]}'
        info(f"Firmare version: {firmware_ver}")
    else:
        warn(f"Unknown option: {args.option}")

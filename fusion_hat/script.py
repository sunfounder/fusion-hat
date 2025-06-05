from .version import __version__
from .device import __device__

from .utils import enable_speaker, \
    disable_speaker, \
    get_firmware_version, \
    get_shutdown_request, \
    info, \
    warn, \
    reset_mcu

# fusion_hat script
# =============================================================
def __fusion_hat_cmd_usage__():
    print('''
Usage: fusion_hat [option]

reset_mcu               reset mcu on fusion-hat
enable_speaker          enable speaker
disable_speaker         disable speaker
version                 get fusion-hat libray version
info                    get hat info
    ''')

def fusion_hat_cmd():
    import sys
    if len(sys.argv) == 2:
        if sys.argv[1] == "reset_mcu":
            reset_mcu()
            info("Onboard MCU reset.")
        elif sys.argv[1] == "enable_speaker":
            info(f"Enable Fusion-HAT speaker.")
            enable_speaker()
        elif sys.argv[1] == "disable_speaker":
            info(f"Disable Fusion-HAT speaker.")
            disable_speaker()
        elif sys.argv[1] == "version":
            info(f"fusion-hat library version: {__version__}")
        elif sys.argv[1] == "info":
            info(f'HAT name: {__device__.name}')
            info(f'PCB ID: O{__device__.product_id}V{__device__.product_ver}')
            info(f'Vendor: {__device__.vendor}')
            firmware_ver = get_firmware_version()
            firmware_ver = f'{firmware_ver[0]}.{firmware_ver[1]}.{firmware_ver[2]}'
            info(f"Firmare version: {firmware_ver}")
        elif sys.argv[1] == "-h":
            __fusion_hat_cmd_usage__()
            quit()
        else:
            warn("Unknown option.")
            __fusion_hat_cmd_usage__()
            quit()
    else:
        __fusion_hat_cmd_usage__()
        quit()

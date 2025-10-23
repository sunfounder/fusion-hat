
from .device import get_shutdown_request, ShutdownRequestCode
import os
import time
from ._logger import Logger

def main():
    """ Safe shutdown main loop """
    SAFE_SHUTDOWN_LOG_PATH = '/var/log/fusion_hat_safe_shutdown.log'
    log = Logger("Fusion HAT Safe Shutdown", file=SAFE_SHUTDOWN_LOG_PATH)

    log.info(f'Fusion HAT safe shutdown service started')
    INTERVAL = 1 # seconds
    while True:
        if get_shutdown_request() == ShutdownRequestCode.LOW_BATTERY:
            log.info(f'Low battery shutdown request received, shutting down now')
            os.system('sudo shutdown now')
        elif get_shutdown_request() == ShutdownRequestCode.BUTTON:
            log.info(f'Button shutdown request received, shutting down now')
            os.system('sudo shutdown now')
        time.sleep(INTERVAL)

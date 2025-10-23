from .device import get_shutdown_request, ShutdownRequestCode
from datetime import datetime
import os
import time

SAFE_SHUTDOWN_LOG_PATH = '/var/log/fusion_hat_safe_shutdown.log'

def __main__():
    """ Safe shutdown main loop """

    print(f'Fusion HAT safe shutdown service started')
    with open(SAFE_SHUTDOWN_LOG_PATH, 'a') as f:
        f.write(f'{datetime.now()} - service started\n')
    INTERVAL = 1 # seconds
    while True:
        if get_shutdown_request() == ShutdownRequestCode.LOW_BATTERY:
            with open(SAFE_SHUTDOWN_LOG_PATH, 'a') as f:
                f.write(f'{datetime.now()} - shutdown: low battery\n')
            os.system('sudo shutdown now')
        elif get_shutdown_request() == ShutdownRequestCode.BUTTON:
            with open(SAFE_SHUTDOWN_LOG_PATH, 'a') as f:
                f.write(f'{datetime.now()} - shutdown: button\n')
            os.system('sudo shutdown now')

        time.sleep(INTERVAL)

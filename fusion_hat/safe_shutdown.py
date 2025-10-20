from .utils import get_shutdown_request
from datetime import datetime
import os
import time


SHUTDOWN_REQUEST_CODE = {
    0:'none',
    1:'low_battery',
    2:'button',
}

SAFE_SHUTDOWN_LOG_PATH = '/var/log/fusion_hat_safe_shutdown.log'


def __main__():
    """ Safe shutdown main loop """

    print(f'Fusion HAT safe shutdown service started')
    with open(SAFE_SHUTDOWN_LOG_PATH, 'a') as f:
        f.write(f'{datetime.now()} - service started\n')
    INTERVAL = 1 # seconds
    while True:
        if get_shutdown_request() == 1:
            with open(SAFE_SHUTDOWN_LOG_PATH, 'a') as f:
                f.write(f'{datetime.now()} - shutdown: low battery\n')
            os.system('sudo shutdown now')
        elif get_shutdown_request() == 2:
            with open(SAFE_SHUTDOWN_LOG_PATH, 'a') as f:
                f.write(f'{datetime.now()} - shutdown: button\n')
            os.system('sudo shutdown now')

        time.sleep(INTERVAL)

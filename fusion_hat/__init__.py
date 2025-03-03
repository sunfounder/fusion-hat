#!/usr/bin/env python3
"""
Fusion Hat Library
"""
from .version import __version__
from .device import __device__

from .adc import ADC
from .filedb import fileDB
from .config import Config
from .i2c import I2C
from .music import Music
from .motor import Motor, Motors
from .pin import Pin
from .pwm import PWM
from .pwm_group import PWM_GROUP
from .servo import Servo
from .tts import TTS
from .utils import *
from .robot import Robot
import time
st = time.time()
from .modules  import *
print("fusion-hat modules load time: ", time.time() - st)


def __usage__():
    print('''
Usage: fusion_hat [option]

reset_mcu               reset mcu on fusion-hat
enable_speaker          enable speaker
disable_speaker         disable speaker
version                 get fusion-hat libray version
info                    get hat info
    ''')
    quit()

def get_firmware_version():
    ADDR = __device__.i2c_addr
    VERSSION_REG_ADDR = 0x05
    i2c = I2C(ADDR)
    version = i2c.mem_read(3, VERSSION_REG_ADDR)
    return version

def __main__():
    import sys
    import os
    if len(sys.argv) == 2:
        if sys.argv[1] == "reset_mcu":
            reset_mcu()
            info("Onboard MCU reset.")
        elif sys.argv[1] == "enable_speaker":
            info(f"Enable Fusion-HAT speaker.")
            utils.enable_speaker()
        elif sys.argv[1] == "disable_speaker":
            info(f"Disable Fusion-HAT speaker.")
            utils.disable_speaker()
        elif sys.argv[1] == "version":
            info(f"fusion-hat library version: {__version__}")
        elif sys.argv[1] == "info":
            info(f'HAT name: {__device__.name}')
            info(f'PCB ID: O{__device__.product_id}V{__device__.product_ver}')
            info(f'Vendor: {__device__.vendor}')
            firmware_ver = get_firmware_version()
            firmware_ver = f'{firmware_ver[0]}.{firmware_ver[1]}.{firmware_ver[2]}'
            info(f"Firmare version: {firmware_ver}")
        else:
            warn("Unknown option.")
            __usage__()
    else:
        __usage__()

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
# st = time.time()
from .modules  import *
# print("fusion-hat modules load time: ", time.time() - st)

#!/usr/bin/env python3
import os
import sys

# color:
# https://gist.github.com/rene-d/9e584a7dd2935d0f461904b9f2950007
# 1;30:gray 31:red, 32:green, 33:yellow, 34:blue, 35:purple, 36:dark green, 37:white
GRAY = '1;30'
RED = '0;31'
GREEN = '0;32'
YELLOW = '0;33'
BLUE = '0;34'
PURPLE = '0;35'
DARK_GREEN = '0;36'
WHITE = '0;37'

def print_color(msg, end='\n', file=sys.stdout, flush=False, color=''):
    print('\033[%sm%s\033[0m'%(color, msg), end=end, file=file, flush=flush)

def info(msg, end='\n', file=sys.stdout, flush=False):
    print_color(msg, end=end, file=file, flush=flush, color=WHITE)

def debug(msg, end='\n', file=sys.stdout, flush=False):
    print_color(msg, end=end, file=file, flush=flush, color=GRAY)

def warn(msg, end='\n', file=sys.stdout, flush=False):
    print_color(msg, end=end, file=file, flush=flush, color=YELLOW)

def error(msg, end='\n', file=sys.stdout, flush=False):
    print_color(msg, end=end, file=file, flush=flush, color=RED)

def set_volume(value):
    """
    Set volume

    :param value: volume(0~100)
    :type value: int
    """
    value = min(100, max(0, value))
    cmd = "sudo amixer -M sset 'PCM' %d%%" % value
    os.system(cmd)


def command_exists(cmd):
    import subprocess
    try:
        subprocess.check_output(['which', cmd], stderr=subprocess.STDOUT)
        return True
    except subprocess.CalledProcessError:
        return False


def run_command(cmd):
    """
    Run command and return status and output

    :param cmd: command to run
    :type cmd: str
    :return: status, output
    :rtype: tuple
    """
    import subprocess
    p = subprocess.Popen(
        cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    result = p.stdout.read().decode('utf-8')
    status = p.poll()
    return status, result

def command_exists(cmd):
    import subprocess
    try:
        subprocess.check_output(['which', cmd], stderr=subprocess.STDOUT)
        return True
    except subprocess.CalledProcessError:
        return False

def is_installed(cmd):
    """
    Check if command is installed

    :param cmd: command to check
    :type cmd: str
    :return: True if installed
    :rtype: bool
    """
    status, _ = run_command(f"which {cmd}")
    if status in [0, ]:
        return True
    else:
        return False


def mapping(x, in_min, in_max, out_min, out_max):
    """
    Map value from one range to another range

    :param x: value to map
    :type x: float/int
    :param in_min: input minimum
    :type in_min: float/int
    :param in_max: input maximum
    :type in_max: float/int
    :param out_min: output minimum
    :type out_min: float/int
    :param out_max: output maximum
    :type out_max: float/int
    :return: mapped value
    :rtype: float/int
    """
    return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min


def get_ip(ifaces=['wlan0', 'eth0']):
    """
    Get IP address

    :param ifaces: interfaces to check
    :type ifaces: list
    :return: IP address or False if not found
    :rtype: str/False
    """
    import re

    if isinstance(ifaces, str):
        ifaces = [ifaces]
    for iface in list(ifaces):
        search_str = 'ip addr show {}'.format(iface)
        result = os.popen(search_str).read()
        com = re.compile(r'(?<=inet )(.*)(?=\/)', re.M)
        ipv4 = re.search(com, result)
        if ipv4:
            ipv4 = ipv4.groups()[0]
            return ipv4
    return False


def reset_mcu():
    """
    Reset mcu on Robot Hat.

    This is helpful if the mcu somehow stuck in a I2C data
    transfer loop, and Raspberry Pi getting IOError while
    Reading ADC, manipulating PWM, etc.
    """
    import time
    from .pin import Pin

    mcu_reset = Pin("MCURST")
    mcu_reset.off()
    time.sleep(0.01)
    mcu_reset.on()
    time.sleep(0.01)

    mcu_reset.close()


def get_battery_voltage():
    """
    Get battery voltage

    :return: battery voltage(V)
    :rtype: float
    """
    from .adc import ADC
    adc = ADC("A4")
    raw_voltage = adc.read_voltage()
    voltage = raw_voltage * 3
    return voltage

def get_username():
    return os.popen('echo ${SUDO_USER:-$LOGNAME}').readline().strip()

def enable_speaker():
    """
    Enable speaker
    """
    from .device import __device__
    if __device__.spk_en == "I2C_0x31":
        debug("Enable speaker on I2C reg 0x31")
        run_command('i2cset -y 1 0x17 0x31 1')
    else:
        pincmd = ''
        if command_exists("pinctrl"):
            pincmd = 'pinctrl'
        elif command_exists("raspi-gpio"):
            pincmd = 'raspi-gpio'
        else:
            error("Can't find `pinctrl` or `raspi-gpio` to enable speaker")
            return
        debug(f"{pincmd} set {__device__.spk_en} op dh")
        run_command(f"{pincmd} set {__device__.spk_en} op dh")
    # play a short sound to fill data and avoid the speaker overheating
    run_command(f"play -n trim 0.0 0.5 2>/dev/null")

def disable_speaker():
    """
    Disable speaker
    """
    from . import __device__
    pincmd = ''
    if command_exists("pinctrl"):
        pincmd = 'pinctrl'
    elif command_exists("raspi-gpio"):
        pincmd = 'raspi-gpio'
    else:
        error("Can't find `pinctrl` or `raspi-gpio` to disable speaker")
        return

    debug(f"{pincmd} set {__device__.spk_en} op dl")
    run_command(f"{pincmd} set {__device__.spk_en} op dl")


def get_usr_btn():
    """
    Get user button state

    :return: True if pressed
    :rtype: bool
    """
    from .device import __device__
    from .i2c import I2C
    ADDR = __device__.i2c_addr
    USER_BTN_STATE_REG_ADDR = 0x24
    i2c = I2C(ADDR)
    usr_btn_state = i2c._read_byte_data(USER_BTN_STATE_REG_ADDR)
    return usr_btn_state & 0x01

def get_charge_state():
    """
    Get charge state

    :return: True if charging
    :rtype: bool
    """
    from .device import __device__
    from .i2c import I2C
    ADDR = __device__.i2c_addr
    CHARGE_STATE_REG_ADDR = 0x25
    i2c = I2C(ADDR)
    charge_state = i2c._read_byte_data(CHARGE_STATE_REG_ADDR)
    return charge_state & 0x01

def get_shutdown_request():
    """
    Get shutdown request

    :return: 0: no request, 1: low Battery request, 2: button shutdown request
    :rtype: bool
    """
    from .device import __device__
    from .i2c import I2C
    ADDR = __device__.i2c_addr
    SHUTDOWN_REQUEST_REG_ADDR = 0x26
    i2c = I2C(ADDR)
    shutdown_request = i2c._read_byte_data(SHUTDOWN_REQUEST_REG_ADDR)
    return shutdown_request

def set_user_led(state):
    """
    Set user led state

    :param state: 0:off, 1:on, 2:toggle
    :type state: bool
    """
    from .device import __device__
    from .i2c import I2C
    ADDR = __device__.i2c_addr
    USER_LED_REG_ADDR = 0x30
    i2c = I2C(ADDR)
    i2c._write_byte_data(USER_LED_REG_ADDR, state)

def get_firmware_version():
    from .device import __device__
    from .i2c import I2C

    ADDR = __device__.i2c_addr
    VERSSION_REG_ADDR = 0x05
    i2c = I2C(ADDR)
    version = i2c.mem_read(3, VERSSION_REG_ADDR)
    return version
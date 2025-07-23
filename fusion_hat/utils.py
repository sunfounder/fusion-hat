#!/usr/bin/env python3
import os
import sys
import time

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
    if __device__.spk_en == "I2Cn_0x31":
        debug("Enable speaker on I2C reg 0x31")
        run_command('i2cset -y 1 0x17 0x31 1')
    # play a short sound to fill data and avoid the speaker overheating
    run_command(f"play -n trim 0.0 0.5 2>/dev/null")

def disable_speaker():
    """
    Disable speaker
    """
    from .device import __device__
    if __device__.spk_en == "I2Cn_0x31":
        debug("Disable speaker on I2C reg 0x31")
        run_command('i2cset -y 1 0x17 0x31 0')


def get_usr_btn():
    """
    Get user button state

    :return: True if pressed
    :rtype: bool
    """
    from .device import __device__
    ADDR = __device__.i2c_addr
    USER_BTN_STATE_REG_ADDR = 0x24
    cmd = f"i2cget -y 1 {ADDR} {USER_BTN_STATE_REG_ADDR}"
    status, output = run_command(cmd)
    if status != 0:
        error(f"Get user button state failed, status: {status}, output: {output}")
        return False
    usr_btn_state = int(output, 16)
    return usr_btn_state == 1

def get_charge_state():
    """
    Get charge state

    :return: True if charging
    :rtype: bool
    """
    from .device import __device__
    ADDR = __device__.i2c_addr
    CHARGE_STATE_REG_ADDR = 0x25
    cmd = f"i2cget -y 1 {ADDR} {CHARGE_STATE_REG_ADDR}"
    status, output = run_command(cmd)
    if status != 0:
        error(f"Get charge state failed, status: {status}, output: {output}")
        return False
    charge_state = int(output, 16)
    return charge_state == 1

def get_shutdown_request():
    """
    Get shutdown request

    :return: 0: no request, 1: low Battery request, 2: button shutdown request
    :rtype: bool
    """
    from .device import __device__
    ADDR = __device__.i2c_addr
    SHUTDOWN_REQUEST_REG_ADDR = 0x26
    cmd = f"i2cget -y 1 {ADDR} {SHUTDOWN_REQUEST_REG_ADDR}"
    status, output = run_command(cmd)
    if status != 0:
        error(f"Get shutdown request failed, status: {status}, output: {output}")
        return False
    shutdown_request = int(output, 16)
    return shutdown_request

def set_user_led(state):
    """
    Set user led state

    :param state: 0:off, 1:on, 2:toggle
    :type state: bool
    """
    from .device import __device__
    ADDR = __device__.i2c_addr
    USER_LED_REG_ADDR = 0x30
    cmd = f"i2cset -y 1 {ADDR} {USER_LED_REG_ADDR} {state}"
    status, output = run_command(cmd)
    if status != 0:
        error(f"Set user led state failed, status: {status}, output: {output}")
        return False

def get_firmware_version():
    from .device import __device__
    ADDR = __device__.i2c_addr
    VERSSION_REG_ADDR = 0x05
    cmd = f"i2cget -y 1 {ADDR} {VERSSION_REG_ADDR} i 3"
    status, output = run_command(cmd)
    if status != 0:
        error(f"Get firmware version failed, status: {status}, output: {output}")
        return False
    version = output.split(" ")
    version = [int(v, 16) for v in version]
    return version

def constrain(value, min_value, max_value):
    return min(max(value, min_value), max_value)

class LazyReader():
    ''' Lazy reader. Read something in a given interval,
    even if you read it multiple times in a short time.
    For those who don't need to read it too frequently.
    '''
    def __init__(self, read_function, interval=10):
        ''' Initialize the lazy reader.

        Args:
            read_function (function): The function to read.
            interval (int): The interval to read.
        '''
        self.read_function = read_function
        self.interval = interval
        self.value = None
        self.last_read_time = 0

    def read(self):
        ''' Read the value.

        Returns:
            The value.
        '''
        if time.time() - self.last_read_time > self.interval:
            self.value = self.read_function()
            self.last_read_time = time.time()
        return self.value

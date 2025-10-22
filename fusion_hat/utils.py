#!/usr/bin/env python3
import os
import sys
import time
from typing import Callable, Any

def set_volume(value: int) -> None:
    """ Set volume

    Args:
        value (int): volume(0~100)
    """
    value = min(100, max(0, value))
    cmd = "sudo amixer -M sset 'PCM' %d%%" % value
    os.system(cmd)

def command_exists(cmd: str) -> bool:
    """ Check if command exists

    Args:
        cmd (str): command to check

    Returns:
        bool: True if exists
    """
    import subprocess
    try:
        subprocess.check_output(['which', cmd], stderr=subprocess.STDOUT)
        return True
    except subprocess.CalledProcessError:
        return False

def run_command(cmd: str) -> tuple:
    """ Run command and return status and output

    Args:
        cmd (str): command to run

    Returns:
        tuple: status, output
    """
    import subprocess
    p = subprocess.Popen(
        cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    result = p.stdout.read().decode('utf-8')
    status = p.poll()
    return status, result

def command_exists(cmd: str) -> bool:
    """ Check if command exists

    Args:
        cmd (str): command to check

    Returns:
        bool: True if exists
    """
    import subprocess
    try:
        subprocess.check_output(['which', cmd], stderr=subprocess.STDOUT)
        return True
    except subprocess.CalledProcessError:
        return False

def is_installed(cmd: str) -> bool:
    """ Check if command is installed

    Args:
        cmd (str): command to check

    Returns:
        bool: True if installed
    """
    status, _ = run_command(f"which {cmd}")
    if status in [0, 127]:
        return True
    else:
        return False

def mapping(x: float, in_min: float, in_max: float, out_min: float, out_max: float) -> float:   
    """ Map value from one range to another range

    Args:
        x (float): value to map
        in_min (float): input minimum
        in_max (float): input maximum
        out_min (float): output minimum
        out_max (float): output maximum

    Returns:
        float: mapped value
    """
    return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

def get_ip(ifaces: list=['wlan0', 'eth0']) -> str:
    """ Get IP address

    Args:
        ifaces (list, optional): interfaces to check, defaults to ['wlan0', 'eth0']

    Returns:
        str/False: IP address or False if not found
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

def get_battery_voltage() -> float:
    """ Get battery voltage

    Returns:
        float: battery voltage(V)
    """
    from .adc import ADC
    adc = ADC("A4")
    raw_voltage = adc.read_voltage()
    voltage = raw_voltage * 3
    return voltage

def get_username() -> str:
    """ Get username

    Returns:
        str: username
    """
    return os.popen('echo ${SUDO_USER:-$LOGNAME}').readline().strip()

def simple_i2c_command(method: str, reg: int, type: str, *args) -> tuple:
    """ Simple i2c command

    Args:
        method (str): i2c method
        reg (int): register address
        type (str): data type
        args (int/float): value to set

    Returns:
        tuple: status, output
    """
    from .device import I2C_ADDRESS
    args = [str(arg) for arg in args]
    cmd = f"i2c{method} -y 1 0x{I2C_ADDRESS:02X} 0x{reg:02X} {type} {' '.join(args)}"
    status, output = run_command(cmd)
    if status != 0 and status != None:
        raise Exception(f"I2C {method} command failed, command: {cmd}, status: {status}, output: {output}")
    if method == "get":
        value = output.split(" ")
        value = [int(v, 16) for v in value]
        if len(value) == 1:
            value = value[0]
        return value

def enable_speaker() -> None:
    """ Enable speaker """
    SPEAKER_REG_ADDR = 0x31
    simple_i2c_command("set", SPEAKER_REG_ADDR, 1)
    # play a short sound to fill data and avoid the speaker overheating
    run_command(f"play -n trim 0.0 0.5 2>/dev/null")

def disable_speaker() -> None:
    """ Disable speaker """
    SPEAKER_REG_ADDR = 0x31
    simple_i2c_command("set", SPEAKER_REG_ADDR, 0)

def get_speaker_state() -> bool:
    """ Get speaker state

    Returns:
        bool: True if enabled
    """
    SPEAKER_REG_ADDR = 0x31
    result = simple_i2c_command("get", SPEAKER_REG_ADDR, "b")
    return result == 1

def get_usr_btn() -> bool:
    """ Get user button state

    Returns:
        bool: True if pressed
    """
    USER_BTN_STATE_REG_ADDR = 0x24
    result = simple_i2c_command("get", USER_BTN_STATE_REG_ADDR, "b")
    return result == 1

def get_charge_state() -> bool:
    """ Get charge state

    Returns:
        bool: True if charging
    """
    CHARGE_STATE_REG_ADDR = 0x25
    result = simple_i2c_command("get", CHARGE_STATE_REG_ADDR, "b")
    return result == 1

def get_shutdown_request() -> int:
    """ Get shutdown request

    Returns:
        int: 0: no request, 1: low Battery request, 2: button shutdown request
    """
    SHUTDOWN_REQUEST_REG_ADDR = 0x26
    result = simple_i2c_command("get", SHUTDOWN_REQUEST_REG_ADDR, "b")
    return result

def set_user_led(state: int) -> None:
    """ Set user led state

    Args:
        state (int): 0:off, 1:on, 2:toggle
    """
    USER_LED_REG_ADDR = 0x30
    simple_i2c_command("set", USER_LED_REG_ADDR, state, "b")

def get_firmware_version() -> list:
    """ Get firmware version

    Returns:
        list: firmware version
    """
    VERSSION_REG_ADDR = 0x05
    version = simple_i2c_command("get", VERSSION_REG_ADDR, "i", 3)
    return version

def constrain(value: float, min_value: float, max_value: float) -> float:
    """ Constrain value to a range

    Args:
        value (float): value to constrain
        min_value (float): minimum value
        max_value (float): maximum value

    Returns:
        float: constrained value
    """
    return min(max(value, min_value), max_value)

class LazyReader():
    """ Lazy reader
    Read something in a given interval,
    even if you read it multiple times in a short time.
    For those who don't need to read it too frequently.
    """
    def __init__(self, read_function: Callable, interval: int=10) -> None:
        """ Initialize the lazy reader.

        Args:
            read_function (Callable): The function to read.
            interval (int, optional): The interval to read. Defaults to 10.
        """ 
        self.read_function = read_function
        self.interval = interval
        self.value = None
        self.last_read_time = 0

    def read(self) -> Any:
        """ Read the value.

        Returns:
            Any: The value.
        """ 
        if time.time() - self.last_read_time > self.interval:
            self.value = self.read_function()
            self.last_read_time = time.time()
        return self.value

def check_executable(executable: str) -> bool:
    """ Check if executable is installed

    Args:
        executable (str): executable name

    Returns:
        bool: True if installed
    """
    from distutils.spawn import find_executable
    executable_path = find_executable(executable)
    found = executable_path is not None
    return found

def redirect_error_2_null() -> int:
    """ Redirect error to null device

    Returns:
        int: old stderr file descriptor
    """
    # https://github.com/spatialaudio/python-sounddevice/issues/11

    devnull = os.open(os.devnull, os.O_WRONLY)
    old_stderr = os.dup(2)
    sys.stderr.flush()
    os.dup2(devnull, 2)
    os.close(devnull)
    return old_stderr

def cancel_redirect_error(old_stderr: int) -> None:
    """ Cancel redirect error to null device

    Args:
        old_stderr (int): old stderr file descriptor
    """
    os.dup2(old_stderr, 2)
    os.close(old_stderr)

class ignore_stderr():
    """ Ignore stderr """
    def __init__(self) -> None:
        """ Initialize the ignore stderr class """
        self.old_stderr = redirect_error_2_null()

    def __enter__(self) -> None:
        """ Enter the ignore stderr context """
        pass

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """ Exit the ignore stderr context

        Args:
            exc_type (type): exception type
            exc_val (Exception): exception value
            exc_tb (traceback): exception traceback
        """ 
        cancel_redirect_error(self.old_stderr)

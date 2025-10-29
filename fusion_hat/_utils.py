#!/usr/bin/env python3
import os
import time
from typing import Callable, Any

def retry(times: int = 5):
    """ Retry decorator retry specified times if any error occurs

    Args:
        times (int, optional): number of times to retry. Defaults to 5.

    Returns:
        function: wrapper function
    """
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        def wrapper(*arg, **kwargs):
            for _ in range(times):
                try:
                    return func(*arg, **kwargs)
                except OSError:
                    continue
            else:
                return False

        return wrapper
    return decorator

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

def get_username() -> str:
    """ Get username

    Returns:
        str: username
    """
    return os.popen('echo ${SUDO_USER:-$LOGNAME}').readline().strip()

def i2c_get(reg: int, type: str, count: int=1) -> tuple:
    """ Simple i2c get command

    Args:
        reg (int): register address
        type (str): data type
        count (int, optional): number of values to read. Defaults to 1.

    Returns:
        tuple: status, output

    Raises:
        Exception: I2C get command failed
    """
    from .device import I2C_ADDRESS
    cmd = f"i2cget -y 1 0x{I2C_ADDRESS:02X} 0x{reg:02X} {type} {count}"
    status, output = run_command(cmd)
    if status != 0 and status != None:
        raise Exception(f"I2C get command failed: \n  - command: {cmd}\n  - status: {status}\n  - output: {output}")
    if count == 1:
        value = int(output, 16)
    else:
        value = output.split(" ")
        value = [int(v, 16) for v in value]
        if len(value) == 1:
            value = value[0]
    return value

def i2c_set(reg: int, type: str, *args) -> None:
    """ Simple i2c set command

    Args:
        reg (int): register address
        type (str): data type
        args (int/float): value to set

    Raises:
        Exception: I2C set command failed
    """
    from .device import I2C_ADDRESS
    args = [str(arg) for arg in args]
    cmd = f"i2cset -y 1 0x{I2C_ADDRESS:02X} 0x{reg:02X} {type} {' '.join(args)}"
    status, output = run_command(cmd)
    if status != 0 and status != None:
        raise Exception(f"I2C set command failed: \n  - command: {cmd}\n  - status: {status}\n  - output: {output}")

def simple_i2c_command(method: str, reg: int, *args) -> tuple:
    """ Simple i2c command

    Args:
        method (str): i2c method, "get" or "set"
        reg (int): register address
        type (str): data type
        args (int/float): value to set, including type and count

    Returns:
        tuple: status, output

    Raises:
        ValueError: Invalid method, must be 'get' or 'set'
    """
    if method not in ["get", "set"]:
        raise ValueError(f"Invalid method {method}, must be 'get' or 'set'")
    from .device import I2C_ADDRESS
    args = [str(arg) for arg in args]
    cmd = f"i2c{method} -y 1 0x{I2C_ADDRESS:02X} 0x{reg:02X} {' '.join(args)}"
    status, output = run_command(cmd)
    if status != 0 and status != None:
        raise Exception(f"I2C {method} command failed: \n  - command: {cmd}\n  - status: {status}\n  - output: {output}")
    if method == "get":
        value = output.split(" ")
        value = [int(v, 16) for v in value]
        if len(value) == 1:
            value = value[0]
        return value

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


__all__ = [
    'retry',
    'command_exists',
    'run_command',
    'is_installed',
    'mapping',
    'get_ip',
    'get_username',
    'simple_i2c_command',
    'constrain',
]

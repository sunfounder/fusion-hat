#!/usr/bin/env python3
from .utils import run_command
from smbus2 import SMBus

def _retry_wrapper(func):
    """ Retry wrapper for I2C bus read/write functions """

    def wrapper(self, *arg, **kwargs):
        """ Retry wrapper for I2C bus read/write functions """
        for _ in range(self.RETRY):
            try:
                return func(self, *arg, **kwargs)
            except OSError:
                continue
        else:
            return False

    return wrapper


class I2C():
    """ I2C bus read/write functions """
    RETRY = 5
    _bus = 1

    def __init__(self, address: int = None, bus: int = 1) -> None:
        """ Initialize the I2C bus

        Args:
            address (int): I2C device address
            bus (int): I2C bus number
        """
        self._bus = bus
        self._smbus = SMBus(self._bus)
        if isinstance(address, list):
            connected_devices = self.scan()
            for _addr in address:
                if _addr in connected_devices:
                    self.address = _addr
                    break
            else:
                self.address = address[0]
        else:
            self.address = address

    @_retry_wrapper
    def _write_byte(self, data: int) -> bool:
        """ Write a byte to the I2C bus

        Args:
            data (int): byte to write

        Returns:
            bool: True if the byte is written successfully, False otherwise
        """
        result = self._smbus.write_byte(self.address, data)
        return result

    @_retry_wrapper
    def _write_byte_data(self, reg: int, data: int) -> bool:
        """ Write a byte to the I2C bus

        Args:
            reg (int): register address
            data (int): byte to write

        Returns:
            bool: True if the byte is written successfully, False otherwise
        """
        return self._smbus.write_byte_data(self.address, reg, data)

    @_retry_wrapper
    def _write_word_data(self, reg: int, data: int) -> bool:
        """ Write a word to the I2C bus

        Args:
            reg (int): register address
            data (int): word to write

        Returns:
            bool: True if the word is written successfully, False otherwise
        """
        return self._smbus.write_word_data(self.address, reg, data)

    @_retry_wrapper
    def _write_i2c_block_data(self, reg: int, data: list) -> bool:
        """ Write a block of data to the I2C bus

        Args:
            reg (int): register address
            data (list): block of data to write

        Returns:
            bool: True if the block of data is written successfully, False otherwise
        """
        return self._smbus.write_i2c_block_data(self.address, reg, data)

    @_retry_wrapper
    def _read_byte(self) -> int:
        """ Read a byte from the I2C bus

        Returns:
            int: byte read from the I2C bus
        """
        result = self._smbus.read_byte(self.address)
        return result

    @_retry_wrapper
    def _read_byte_data(self, reg: int) -> int:
        """ Read a byte from the I2C bus

        Args:
            reg (int): register address

        Returns:
            int: byte read from the I2C bus
        """
        result = self._smbus.read_byte_data(self.address, reg)
        return result

    @_retry_wrapper
    def _read_word_data(self, reg: int) -> list:
        """ Read a word from the I2C bus

        Args:
            reg (int): register address

        Returns:
            list: word read from the I2C bus
        """
        result = self._smbus.read_word_data(self.address, reg)
        result_list = [result & 0xFF, (result >> 8) & 0xFF]
        return result_list

    @_retry_wrapper
    def _read_i2c_block_data(self, reg: int, num: int) -> list:
        """ Read a block of data from the I2C bus

        Args:
            reg (int): register address
            num (int): number of bytes to read

        Returns:
            list: block of data read from the I2C bus
        """
        result = self._smbus.read_i2c_block_data(self.address, reg, num)
        return result

    @_retry_wrapper
    def is_ready(self) -> bool:
        """Check if the I2C device is ready

        Returns:
            bool: True if the I2C device is ready, False otherwise
        """
        addresses = self.scan()
        if self.address in addresses:
            return True
        else:
            return False

    @staticmethod
    def scan(bus: int = None) -> list:
        """Scan the I2C bus for devices

        Args:
            bus (int): I2C bus number

        Returns:
            list: List of I2C addresses of devices found
        """
        if bus is None:
            bus = I2C._bus
        cmd = f"i2cdetect -y {bus}"
        # Run the i2cdetect command
        _, output = run_command(cmd)

        # Parse the output
        outputs = output.split('\n')[1:]
        addresses = []
        addresses_str = []
        for tmp_addresses in outputs:
            if tmp_addresses == "":
                continue
            tmp_addresses = tmp_addresses.split(':')[1]
            # Split the addresses into a list
            tmp_addresses = tmp_addresses.strip().split(' ')
            for address in tmp_addresses:
                if address != '--':
                    addresses.append(int(address, 16))
                    addresses_str.append(f'0x{address}')
        return addresses

    def write(self, data: int | list | bytearray) -> None:
        """ Write data to the I2C device

        Args:
            data (int | list | bytearray): Data to write

        Raises:
            ValueError: if write is not an int, list or bytearray
        """
        if isinstance(data, bytearray):
            data_all = list(data)
        elif isinstance(data, int):
            if data == 0:
                data_all = [0]
            else:
                data_all = []
                while data > 0:
                    data_all.append(data & 0xFF)
                    data >>= 8
        elif isinstance(data, list):
            data_all = data
        else:
            raise ValueError(
                f"write data must be int, list, or bytearray, not {type(data)}"
            )

        # Write data
        if len(data_all) == 1:
            data = data_all[0]
            self._write_byte(data)
        elif len(data_all) == 2:
            reg = data_all[0]
            data = data_all[1]
            self._write_byte_data(reg, data)
        elif len(data_all) == 3:
            reg = data_all[0]
            data = (data_all[2] << 8) + data_all[1]
            self._write_word_data(reg, data)
        else:
            reg = data_all[0]
            data = list(data_all[1:])
            self._write_i2c_block_data(reg, data)

    def read(self, length: int = 1) -> list:
        """ Read data from I2C device

        Args:
            length (int): Number of bytes to receive

        Returns:
            list: Received data
        """
        if not isinstance(length, int):
            raise ValueError(f"length must be int, not {type(length)}")

        result = []
        for _ in range(length):
            result.append(self._read_byte())
        return result

    def mem_write(self, data: int | list | bytearray, memaddr: int) -> None:
        """ Write data to specific register address

        Args:
            data (int | list | bytearray): Data to send
            memaddr (int): Register address

        Raises:
            ValueError: If data is not int, list, or bytearray
        """
        if isinstance(data, bytearray):
            data_all = list(data)
        elif isinstance(data, list):
            data_all = data
        elif isinstance(data, int):
            data_all = []
            if data == 0:
                data_all = [0]
            else:
                while data > 0:
                    data_all.append(data & 0xFF)
                    data >>= 8
        else:
            raise ValueError(
                "memery write require arguement of bytearray, list, int less than 0xFF"
            )
        self._write_i2c_block_data(memaddr, data_all)

    def mem_read(self, length: int, memaddr: int) -> list:
        """ Read data from specific register address

        Args:
            length (int): Number of bytes to receive
            memaddr (int): Register address

        Returns:
            list: Received bytearray data or False if error
        """
        result = self._read_i2c_block_data(memaddr, length)
        return result

    def is_avaliable(self) -> bool:
        """ Check if the I2C device is avaliable

        Returns:
            bool: True if the I2C device is avaliable, False otherwise
        """
        return self.address in self.scan()

if __name__ == "__main__":
    i2c = I2C(address=[0x17, 0x15], debug_level='debug')

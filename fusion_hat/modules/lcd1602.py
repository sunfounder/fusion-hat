from .._i2c import I2C
from time import sleep

class LCD1602():
    """LCD1602 module."""
    DEFAULT_ADDRESS_1 = 0x27
    DEFAULT_ADDRESS_2 = 0x3f

    def __init__(self, address=None, backlight:bool=True, bus=1):
        """Initialize the LCD1602 module."""
        self.bus = bus
        self.address = address
        self._backlight = backlight

        _addr_list = I2C.scan(bus=1)
        if self.address is None:
            if self.DEFAULT_ADDRESS_1 in _addr_list:
                self.address = self.DEFAULT_ADDRESS_1
            elif self.DEFAULT_ADDRESS_2 in _addr_list:
                self.address = self.DEFAULT_ADDRESS_2
            else:
                raise OSError(f"No LCD1602 found on I2C:0x{self.DEFAULT_ADDRESS_1:0X} or I2C:0x{self.DEFAULT_ADDRESS_2:0X}")
        else:
            if self.address not in _addr_list:
                raise OSError(f"No LCD1602 found on I2C:0x{self.address:0X}")
            
        self.i2c = I2C(self.address, self.bus)

        self.send_command(0x33) # Must initialize to 8-line mode at first
        sleep(0.005)
        self.send_command(0x32) # Then initialize to 4-line mode
        sleep(0.005)
        self.send_command(0x28) # 2 Lines & 5*7 dots
        sleep(0.005)
        self.send_command(0x0C) # Enable display without cursor
        sleep(0.005)
        self.clear() # Clear Screen
        sleep(0.005)
        self.open_back_light() # Turn on the back light

    def write_byte(self, data):
        temp = data
        if self._backlight == 1:
            temp |= 0x08
        else:
            temp &= 0xF7
        self.i2c.write_byte(temp)
    
    def send_command(self, cmd):
        # Send bit7-4 firstly
        buf = cmd & 0xF0
        buf |= 0x04               # RS = 0, RW = 0, EN = 1
        self.write_byte(buf)
        sleep(0.002)
        buf &= 0xFB               # Make EN = 0
        self.write_byte(buf)

        # Send bit3-0 secondly
        buf = (cmd & 0x0F) << 4
        buf |= 0x04               # RS = 0, RW = 0, EN = 1
        self.write_byte(buf)
        sleep(0.002)
        buf &= 0xFB               # Make EN = 0
        self.write_byte(buf)
    
    def send_data(self, data):
        # Send bit7-4 firstly
        buf = data & 0xF0
        buf |= 0x05               # RS = 1, RW = 0, EN = 1
        self.write_byte(buf)
        sleep(0.002)
        buf &= 0xFB               # Make EN = 0
        self.write_byte(buf)

        # Send bit3-0 secondly
        buf = (data & 0x0F) << 4
        buf |= 0x05               # RS = 1, RW = 0, EN = 1
        self.write_byte(buf)
        sleep(0.002)
        buf &= 0xFB               # Make EN = 0
        self.write_byte(buf)
    
    def clear(self):
        self.send_command(0x01) # Clear Screen
        
    def open_back_light(self):  # Enable the backlight
        self.i2c.write_byte(0x08)

    def close_back_light(self): # Disable the backlight
        self.i2c.write_byte(0x00)
    
    def write(self, x, y, str):
        if x < 0:
            x = 0
        if x > 15:
            x = 15
        if y < 0:
            y = 0
        if y > 1:
            y = 1

        # Move cursor
        addr = 0x80 + 0x40 * y + x
        self.send_command(addr)

        for chr in str:
            self.send_data(ord(chr))
    
    def message(self, text):
        #print("message: %s"%text)
        for char in text:
            if char == '\n':
                self.send_command(0xC0) # next line
            else:
                self.send_data(ord(char))
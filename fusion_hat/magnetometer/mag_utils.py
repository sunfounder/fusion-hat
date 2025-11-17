from smbus2 import SMBus

def convert_2_int16(value):
    if value > 32767:
        value = -(65536 - value)
    return value

def i2c_ack(bus, addr):
    """
    Check if a device responds at the specified I2C address
    
    Parameters:
        bus: SMBus instance
        addr: I2C address to check
    
    Returns:
        bool: True if the device responds, False otherwise
    """
    try:
        bus.read_byte(addr)
        return True
    except Exception:
        return False
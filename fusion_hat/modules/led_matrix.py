from luma.led_matrix.device import max7219
from luma.core.interface.serial import spi, noop
from luma.core.render import canvas

class LedMatrix:
    """
    SPI RGB Matrix class
    """

    def __init__(self, rotate=0):
        """
        Constructor
        """
        self.serial = spi(port=0, device=0, gpio=noop())
        self.device = max7219(self.serial, width=8, rotate=0)

    def display_pattern(self, pattern):
        """
        Display a pattern on the matrix
        """
        with canvas(self.device ) as draw:
            for y, row in enumerate(pattern):
                for x in range(8):
                    bit = 1 << x
                    if row & bit:
                        draw.point((y, x), fill="white")

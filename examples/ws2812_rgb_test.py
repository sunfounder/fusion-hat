''' Warning
For Pi3:
You may need to set the CPU clock to 250MHz to get the SPI working.
    core_freq=250

For Pi4:
You may need to set the core clock and core_freq_min to get the SPI working.
    core_freq=500
    core_freq_min=500

'''
# https://github.com/adafruit/Adafruit_CircuitPython_NeoPixel_SPI
# https://github.com/jgarff/rpi_ws281x
# pip3 install adafruit-circuitpython-neopixel-spi

import time
import board
import neopixel_spi as neopixel

spi = board.SPI()
LED_COUNT = 8  # Number of LED pixels.
PIXEL_ORDER = neopixel.GRB

strip = neopixel.NeoPixel_SPI(spi, LED_COUNT, pixel_order=PIXEL_ORDER, auto_write=False)
time.sleep(0.01)
strip.fill(0)
strip.show()

while True:
    print("RGB test")
    print("Red")
    strip.fill((255, 0, 0))
    strip.show()
    time.sleep(1)
    print("Green")
    strip.fill((0, 255, 0))
    strip.show()
    time.sleep(1)
    print("Blue")
    strip.fill((0, 0, 255))
    strip.show()
    time.sleep(1)
    print("Off for 10 seconds")
    strip.fill((0, 0, 0))
    strip.show()
    time.sleep(10)
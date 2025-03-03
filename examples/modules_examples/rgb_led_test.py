# Import RGB_LED and PWM class
from fusion_hat import RGB_LED, PWM

# Create RGB_LED object for common anode RGB LED
rgb = RGB_LED(PWM(0), PWM(1), PWM(2), common=RGB_LED.ANODE)
# or for common cathode RGB LED
rgb = RGB_LED(PWM(0), PWM(1), PWM(2), common=RGB_LED.CATHODE)

# Set color with 24 bit int
rgb.color(0xFF0000) # Red
# Set color with RGB tuple
rgb.color((0, 255, 0)) # Green
# Set color with RGB List
rgb.color([0, 0, 255]) # Blue
# Set color with RGB hex string starts with “#”
rgb.color("#FFFF00") # Yellow
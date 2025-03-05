from fusion_hat import Rotary_Encoder
from signal import pause  # Import pause function from signal module

encoder = Rotary_Encoder(clk=17, dt=4)  # Rotary Encoder connected to GPIO pins 17 (CLK) and 4 (DT)

def rotary_change():
    """ Update the counter based on the rotary encoder's rotation. """
    print('Counter =', encoder.steps())  # Display current counter value

encoder.when_rotated = rotary_change  # Call the function when the rotary encoder is rotated

print("CTRL + C to exit")
pause()
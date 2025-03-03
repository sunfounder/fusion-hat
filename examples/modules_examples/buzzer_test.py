# Import Buzzer class
from fusion_hat import Buzzer, PWM

# Create Buzzer object
buzzer = Buzzer(PWM(0))

# Play a note
buzzer.play("C0", 0.5)



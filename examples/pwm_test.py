from fusion_hat.pwm import PWM
from time import sleep

p0 = PWM(0)
p0.freq(50)
p0.pulse_width_percent(50)
p0.pulse_width_percent(80)

p1 = PWM(1)
p1.freq(50)
p1.pulse_width_percent(50)
p1.pulse_width_percent(80)

p4 = PWM("P4")
p4.freq(100)
p4.pulse_width_percent(0)

while True:
    for i in range(0, 101, 10):
        p4.pulse_width_percent(i)
        sleep(0.2)
    sleep(1)
    
    for i in range(100, -1, -10):
        p4.pulse_width_percent(i)
        sleep(0.2)
    sleep(1)
    
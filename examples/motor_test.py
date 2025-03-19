from fusion_hat import Motor, PWM, Pin
from time import sleep

# m0 = Motor(PWM(11), PWM(10), is_reversed=True)
# m1 = Motor(PWM(9), PWM(8), is_reversed=True)
# m2 = Motor(PWM(7), PWM(6), is_reversed=False)
# m3 = Motor(PWM(5), PWM(4), is_reversed=False)

m0 = Motor("M0", is_reversed=True)
m1 = Motor("M1", is_reversed=True)
m2 = Motor("M2", is_reversed=False)
m3 = Motor("M3", is_reversed=False)

try:
    while True:
        m0.speed(-50)
        m1.speed(-50)
        m2.speed(-50)
        m3.speed(-50)
        sleep(1)
        m0.speed(50)
        m1.speed(50)
        m2.speed(50)
        m3.speed(50)
        sleep(1)
        m0.stop()
        m1.stop()
        m2.stop()
        m3.stop()
finally:
    m0.stop()
    m1.stop()
    m2.stop()
    m3.stop()
    sleep(.1)

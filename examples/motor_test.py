from fusion_hat.motor import Motor
from time import sleep

m0 = Motor("M0", is_reversed=True)
m1 = Motor("M1", is_reversed=True)
m2 = Motor("M2", is_reversed=False)
m3 = Motor("M3", is_reversed=False)


try:
    while True:
        print("Forward")
        m0.power(-50)
        m1.power(-50)
        m2.power(-50)
        m3.power(-50)
        sleep(1)
        print("Backward")
        m0.power(50)
        m1.power(50)
        m2.power(50)
        m3.power(50)
        sleep(1)
        print("Stop")
        m0.stop()
        m1.stop()
        m2.stop()
        m3.stop()
        sleep(1)

finally:
    m0.stop()
    m1.stop()
    m2.stop()
    m3.stop()
    sleep(.1)

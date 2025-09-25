from fusion_hat.motor import Motor
from time import sleep

m0 = Motor("M0", is_reversed=True)
m1 = Motor("M1", is_reversed=True)
m2 = Motor("M2", is_reversed=False)
m3 = Motor("M3", is_reversed=False)

m0.power(0)
m1.power(0)
m2.power(0)
m3.power(0)
# try:
#     while True:
#         m0.speed(-50)
#         m1.speed(-50)
#         m2.speed(-50)
#         m3.speed(-50)
#         print('run1')
#         sleep(1)
#         m0.speed(50)
#         m1.speed(50)
#         m2.speed(50)
#         m3.speed(50)
#         print('run2')
#         sleep(1)
#         m0.stop()
#         m1.stop()
#         m2.stop()
#         m3.stop()
#         print('run3')
        
# finally:
#     m0.stop()
#     m1.stop()
#     m2.stop()
#     m3.stop()
#     sleep(.1)

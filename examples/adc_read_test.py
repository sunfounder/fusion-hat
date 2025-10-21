from fusion_hat.adc import ADC
import time

a0 = ADC(0)
a1 = ADC(1)
a2 = ADC(2)
a3 = ADC(3)


while True:
    v0 = a0.read_voltage()
    v1 = a1.read_voltage()
    v2 = a2.read_voltage()
    v3 = a3.read_voltage()
    print(f'A0: {v0:.2f}V, A1: {v1:.2f}V, A2: {v2:.2f}V, A3: {v3:.2f}V')
    time.sleep(0.5)
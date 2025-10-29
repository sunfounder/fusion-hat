from fusion_hat.adc import ADC
import time

a0 = ADC(0)
a1 = ADC(1)
a2 = ADC(2)
a3 = ADC(3)

while True:
    value0 = a0.read()
    value1 = a1.read()
    value2 = a2.read()
    value3 = a3.read()

    voltage0 = a0.read_voltage()
    voltage1 = a1.read_voltage()
    voltage2 = a2.read_voltage()
    voltage3 = a3.read_voltage()
    print(f'A0: {voltage0:.2f}V({value0}), A1: {voltage1:.2f}V({value1}), A2: {voltage2:.2f}V({value2}), A3: {voltage3:.2f}V({value3})')    
    time.sleep(0.5)
from fusion_hat.modules.dht11 import DHT11
from time import sleep

dht11 = DHT11(pin=17)

while True:
    result = dht11.read()
    if result:
        humidity, temperature = result
        print ("humidity: %s %%,  Temperature: %s C" % (humidity, temperature))
    else:
        print("time out")
    sleep(1)
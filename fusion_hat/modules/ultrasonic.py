import time
from ..pin import Pin
import threading

class Ultrasonic():
    SOUND_SPEED = 343.3 # ms

    def __init__(self, trig, echo, timeout=0.02):
        if not isinstance(trig, Pin):
            raise TypeError("trig must be robot_hat.Pin object")
        if not isinstance(echo, Pin):
            raise TypeError("echo must be robot_hat.Pin object")

        self.timeout = timeout

        trig.close()
        echo.close()
        self.trig = Pin(trig._pin_num)
        self.echo = Pin(echo._pin_num, mode=Pin.IN, pull=Pin.PULL_DOWN)

        self.thread_read_interval = 0.02
        self.thread = None
        self.thread_started = False
        self.thread_value = -1

    def read_raw(self):
        self.trig.off()
        time.sleep(0.001)
        self.trig.on()
        time.sleep(0.00001)
        self.trig.off()

        pulse_end = 0
        pulse_start = 0
        timeout_start = time.time()

        while self.echo.gpio.value == 0:
            pulse_start = time.time()
            if pulse_start - timeout_start > self.timeout:
                return -1
        while self.echo.gpio.value == 1:
            pulse_end = time.time()
            if pulse_end - timeout_start > self.timeout:
                return -1
        if pulse_start == 0 or pulse_end == 0:
            return -2

        during = pulse_end - pulse_start
        cm = round(during * self.SOUND_SPEED / 2 * 100, 2)
        return cm

    def read_with_retry(self, times=10):
        for _ in range(times):
            value = self.read_raw()
            if value > 0:
                return value
        return -1

    def read(self):
        if self.thread is not None and self.thread_started:
            return self.thread_value
        else:
            return self.read_with_retry()

    def thread_read_loop(self):
        while self.thread_started:
            self.thread_value = self.read_with_retry()
            time.sleep(self.thread_read_interval)

    def start_thread(self, interval=0.01):
        if self.thread is None:
            self.thread_started = True
            self.thread_read_interval = interval
            self.thread = threading.Thread(target=self.thread_read_loop, daemon=True)
            self.thread.start()
    
    def stop_thread(self):
        self.thread_started = False
        if self.thread is not None:
            self.thread.join()
            self.thread = None

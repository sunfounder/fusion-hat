from fusion_hat.servo import Servo
import time



servos = [Servo(i) for i in range(12)]

while True:
    for angle in range(-90, 91, 1):
        print(f"Servo angle: {angle}")
        for servo in servos:
            servo.angle(angle)
            time.sleep(0.01)
    time.sleep(1)
    for angle in range(90, -91, -1):
        print(f"Servo angle: {angle}")
        for servo in servos:
            servo.angle(angle)
            time.sleep(0.01)
    time.sleep(1)

from fusion_hat.modules import MPU6050
from time import sleep

mpu = MPU6050()

# mpu.set_accel_range(MPU6050.ACCEL_RANGE_2G)
# mpu.set_gyro_range(MPU6050.GYRO_RANGE_250DEG)


while True:
    temp = mpu.get_temp()
    acc_x, acc_y, acc_z  = mpu.get_accel_data()
    gyro_x, gyro_y, gyro_z = mpu.get_gyro_data()
    print(
        f"Temp: {temp:0.2f} 'C",
        f"  |  ACC: {acc_x:8.5f}g {acc_y:8.5f}g {acc_z:8.5f}g",
        f"  |  GYRO: {gyro_x:8.5f}deg/s {gyro_y:8.5f}deg/s {gyro_z:8.5f}deg/s"
    )
    sleep(0.2)

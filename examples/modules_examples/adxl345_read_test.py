# Import ADXL345 class
from fusion_hat.modules import ADXL345

# Create ADXL345 object
adxl = ADXL345()
# or with a custom I2C address
adxl = ADXL345(address=0x53)

# Read acceleration of each axis
x = adxl.read(adxl.X)
y = adxl.read(adxl.Y)
z = adxl.read(adxl.Z)
print(f"Acceleration: {x}, {y}, {z}")

# Or read all axis at once
x, y, z = adxl.read()
print(f"Acceleration: {x}, {y}, {z}")
# Or print all axis at once
print(f"Acceleration: {adxl.read()}")

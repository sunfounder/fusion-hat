from fusion_hat import SPI_RGB_Matrix

rgb_matrix = SPI_RGB_Matrix(rotate=0)

pattern = [
    0b01111110,
    0b01000000,
    0b00111100,
    0b00000010,
    0b00000001,
    0b00000001,
    0b01000010,
    0b00111100
]

rgb_matrix.display_pattern(pattern, color='red') 
from fusion_hat.modules import LCD1602
from time import sleep

lcd = LCD1602(address=0x27, backlight=1)

while True:
    lcd.clear()
    lcd.write(0, 0, 'Greetings!')
    lcd.write(1, 1, 'From SunFounder')
    sleep(1)
    lcd.clear()
    lcd.message('Hello\n   World!')
    sleep(1)


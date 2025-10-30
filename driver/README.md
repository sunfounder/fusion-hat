# Fusion Hat driver

## Install

```
make all
sudo make install
```

## Debug record

```
cd ~/fusion-hat/driver && make all && sudo make install

upower -i /org/freedesktop/UPower/devices/battery_fusion_hat
dmesg

cat /sys/class/fusion_hat/fusion_hat/pwm/pwm0/enable
echo 1 > /sys/class/fusion_hat/fusion_hat/pwm/pwm0/enable
echo 20000 > /sys/class/fusion_hat/fusion_hat/pwm/pwm0/period
cat /sys/class/fusion_hat/fusion_hat/pwm/pwm0/period
cat /sys/class/fusion_hat/fusion_hat/pwm/pwm0/duty_cycle
echo 1500 > /sys/class/fusion_hat/fusion_hat/pwm/pwm0/duty_cycle
echo 2000 > /sys/class/fusion_hat/fusion_hat/pwm/pwm0/duty_cycle

echo 1 > /sys/class/fusion_hat/fusion_hat/pwm/pwm1/enable
echo 20000 > /sys/class/fusion_hat/fusion_hat/pwm/pwm1/period
echo 1500 > /sys/class/fusion_hat/fusion_hat/pwm/pwm1/duty_cycle
echo 2000 > /sys/class/fusion_hat/fusion_hat/pwm/pwm1/duty_cycle

# Prescaller 22
i2cset -y 1 0x17 0x40 0x1600 w
# Set period to 65535
i2cset -y 1 0x17 0x50 0xFFFF w
# Set duty cycle to 32767
i2cset -y 1 0x17 0x62 0xFF7F w
```
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
```
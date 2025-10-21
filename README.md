# Fusion Hat

Fusion Hat Python library for Raspberry Pi.

Quick Links:

- [Fusion Hat](#fusion-hat)
  - [About Fusion Hat](#about-fusion-hat)
  - [Installation](#installation)
  - [Debug record](#debug-record)
  - [About SunFounder](#about-sunfounder)
  - [Contact us](#contact-us)

## About Fusion Hat

Fusion HAT is a multifunctional expansion board that allows Raspberry Pi to be quickly turned into a robot. An MCU is on board to extend the PWM output and ADC input for the Raspberry Pi, as well as a motor driver chip. I2S audio module and mono speaker. As well as the GPIOs that lead out of the Raspberry Pi itself.

## Installation

Install Fusion Hat

```bash
curl -sSL https://raw.githubusercontent.com/sunfounder/sunfounder-installer-scripts/main/install-fusion-hat-v1.1.sh | sudo bash
```

After install finished, please reboot your Raspberry Pi. After reboot, Run this command again to enable audio

```bash
sudo /opt/setup_fusion_hat_audio.sh
```


## Debug record

```bash
sudo pip uninstall --break fusion_hat -y && sudo pip install --break git+https://github.com/sunfounder/fusion-hat.git@1.1.x
sudo pip uninstall --break fusion_hat -y && sudo pip install --break ~/fusion-hat/ --break-system-packages --no-deps --no-build-isolation
```

## About SunFounder

SunFounder is a technology company focused on Raspberry Pi and Arduino open source community development. Committed to the promotion of open source culture, we strives to bring the fun of electronics making to people all around the world and enable everyone to be a maker. Our products include learning kits, development boards, robots, sensor modules and development tools. In addition to high quality products, SunFounder also offers video tutorials to help you make your own project. If you have interest in open source or making something cool, welcome to join us!

----------------------------------------------

## Contact us

website:
    www.sunfounder.com

E-mail:
    service@sunfounder.com, support@sunfounder.com


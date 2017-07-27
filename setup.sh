#!/bin/bash

sudo apt-get update

yes | sudo apt-get upgrade

sudo rpi-update

sudo apt-get -y install  libi2c-dev i2c-tools python-smbus libfuse-dev python-imaging git git-core vim wiringpi ttf-freefont python-pip

sudo pip install pyowm pillow gitpython

git clone https://github.com/repaper/gratis

cd gratis

make rpi PANEL_VERSION='V231_G2'

sudo make rpi-install PANEL_VERSION='V231_G2'

sudo systemctl enable epd-fuse.service

sudo reboot


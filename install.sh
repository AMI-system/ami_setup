#!/bin/bash

echo "Installing Bluetooth for Ami-Trap..."

echo "    1/4 Installing dependencies..."

# Install bluez-peripheral from file bluez_peripheral-0.1.7-py3-none-any.whl
sudo python3 -m pip install dbus_next-0.2.3-py3-none-any.whl
sudo python3 -m pip install bluez_peripheral-0.1.7-py3-none-any.whl

echo "    2/4 Enabling bluetooth on boot..."

# Enable Bluetooth on boot
sudo sed -i 's/^dtoverlay=disable-bt/#&/' /boot/config.txt

echo "    3/4 Adding command to rc.local for start-up after boot..."

# Add command to rc.local
script_dir=$(dirname "$(readlink -f "$0")")
sudo sed -i -e '$i \sudo python3 '"$script_dir"'/ami-trap-raspi-bluetooth.py &\n' /etc/rc.local

echo "    4/4 Tweak other commands in rc.local..."

# Add "&" behind commands "motion -m" and "home/pi/scripts/setCamera.sh"
sudo sed -i 's/^motion -m/motion -m \&/' /etc/rc.local
sudo sed -i 's/^\/home\/pi\/scripts\/setCamera.sh/\/home\/pi\/scripts\/setCamera.sh \&/' /etc/rc.local

echo "Installation complete. Please reboot to enable Bluetooth."

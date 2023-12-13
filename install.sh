#!/bin/bash

echo "Installing Bluetooth for Ami-Trap (Rock Pi)..."

echo "    1/3 Installing pip..."

# Download and install pip
sudo curl https://bootstrap.pypa.io/get-pip.py -o /home/rock/get-pip.py
sudo python3 /home/rock/get-pip.py

echo "    2/3 Installing dependencies..."

# Install bluez-peripheral
sudo python3 -m pip install bluez-peripheral

echo "    3/3 Adding command to rc.local for start-up after boot..."

# Add command to rc.local
script_dir=$(dirname "$(readlink -f "$0")")
sudo sed -i -e '$i \sudo python3 '"$script_dir"'/ami-trap-rockpi-bluetooth.py &\n' /etc/rc.local

echo "Installation complete. Please reboot to enable Bluetooth."

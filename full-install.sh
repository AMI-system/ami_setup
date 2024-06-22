#!/bin/bash

echo "Installing cellular connectivity for Ami-Trap..."

echo "    1/4 Installing dependencies..."

# Install Python dependencies
sudo python3.9 -m pip install python_periphery-2.4.1-py2.py3-none-any.whl
sudo python3.9 -m pip install filelock-3.12.2-py3-none-any.whl
sudo python3.9 -m pip install note_python-1.5.0-py3-none-any.whl
sudo python3.9 -m pip install pillow

echo "    2/4 Configuring cellular connection..."

script_dir=$(dirname "$(readlink -f "$0")")
sudo python3.9 "$script_dir"/ami-trap-raspi-cellular-config.py

echo "    3/4 Adding command to rc.local for start-up after boot..."

# Add command to rc.local
sudo sed -i -e '$i \sudo python3 '"$script_dir"'/ami-trap-raspi-cellular.py &\n' /etc/rc.local

echo "    4/4 Tweak other commands in rc.local..."

# Add "&" behind commands "motion -m" and "home/pi/scripts/setCamera.sh"
sudo sed -i 's/^motion -m/motion -m \&/' /etc/rc.local
sudo sed -i 's/^\/home\/pi\/scripts\/setCamera.sh/\/home\/pi\/scripts\/setCamera.sh \&/' /etc/rc.local

echo "Installation complete. Please reboot to enable cellular connectivity."

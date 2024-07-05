#!/bin/bash

echo "Installing cellular connectivity for Ami-Trap..."

script_dir=$(dirname "$(readlink -f "$0")")

echo "    1/4 Creating virtual environment..."

# Create a virtual environment
python -m venv "$script_dir"/cellular-env

echo "    2/4 Installing dependencies..."

# Install Python dependencies
"$script_dir"/cellular-env/bin/python -m pip install python_periphery-2.4.1-py2.py3-none-any.whl
"$script_dir"/cellular-env/bin/python -m pip install filelock-3.12.2-py3-none-any.whl
"$script_dir"/cellular-env/bin/python -m pip install note_python-1.5.0-py3-none-any.whl

# echo "    2/4 Configuring cellular connection..."

# "$script_dir"/cellular-env/bin/python "$script_dir"/ami-trap-raspi-cellular-config.py

echo "    3/4 Adding command to rc.local for start-up after boot..."

# Add command to rc.local
sudo sed -i -e '$i \sudo '"$script_dir/cellular-env/bin/python"' '"$script_dir"'/ami-trap-raspi-cellular.py &\n' /etc/rc.local

echo "    4/4 Tweak other commands in rc.local..."

# Add "&" behind commands "motion -m" and "home/pi/scripts/setCamera.sh"
sudo sed -i 's/^motion -m/motion -m \&/' /etc/rc.local
sudo sed -i 's/^\/home\/pi\/scripts\/setCamera.sh/\/home\/pi\/scripts\/setCamera.sh \&/' /etc/rc.local

echo "Installation complete. Please reboot to enable cellular connectivity."

#!/bin/bash
# file: afterStartup.sh
#
# This script will run after Raspberry Pi boot up and finish running the schedule script.
# If you want to run your commands after boot, you can place them here.
#
# Remarks: please use absolute path of the command, or it can not be found (by root user).
# Remarks: you may append '&' at the end of command to avoid blocking the main daemon.sh.
#

# Send telemtry beacon
sudo python3 /home/pi/ami_setup-cellular-dev/ami-trap-raspi-cellular-send_and_receive.py >> /home/pi/wittypi/telemetry.log & 

# Extract and save sunrise and sunset times
sudo python3 /home/pi/scripts/determine_sunrise_sunset_times.py

# Calculate moths recording schedule
sudo python3 /home/pi/scripts/moths_schedule.py

# Calculate bats recording schedule
sudo python3 /home/pi/scripts/bats_schedule.py

# Calculate bats recording schedule
sudo python3 /home/pi/scripts/birds_schedule.py

# Update the camera settings
sudo /home/pi/scripts/setCamera.sh

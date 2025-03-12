#!/bin/bash
# file: afterStartup.sh
#
# This script will run after Raspberry Pi boot up and finish running the schedule script.
# If you want to run your commands after boot, you can place them here.
#
# Remarks: please use absolute path of the command, or it can not be found (by root user).
# Remarks: you may append '&' at the end of command to avoid blocking the main daemon.sh.
#

# Wireless connectivity (Bluetooth and cellular) invoked in /etc/rc.local

# Check the system time, and if incorrect, reset time and reset weekly schedule. Either way update sunrise/set times and update moth, bird, bat recording schedules
sudo /home/pi/scripts/check_datetime.sh

# Update the camera settings
sudo /home/pi/scripts/setCamera.sh

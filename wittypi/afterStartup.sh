#!/bin/bash
# file: afterStartup.sh
#
# This script will run after Raspberry Pi boot up and finish running the schedule script.
# If you want to run your commands after boot, you can place them here.
#
# Remarks: please use absolute path of the command, or it can not be found (by root user).
# Remarks: you may append '&' at the end of command to avoid blocking the main daemon.sh.
#

#Send telemtry beacon
sudo python3 /home/pi/ami_setup-cellular-dev/ami-trap-raspi-cellular-send_and_receive.py >> /home/pi/wittypi/telemetry.log &

#Start motion software
#sudo /usr/bin/motion -m
#Set camera settings
#sudo /home/pi/scripts/setCamera.sh
#Turn ON lights
#sudo python /home/pi/scripts/control_ON_lights.py

#Calculate moths recording schedule
sudo python3 /home/pi/scripts/moths_schedule.py

#Calculate bats recording schedule
sudo python3 /home/pi/scripts/bats_schedule.py

#Calculate bats recording schedule
sudo python3 /home/pi/scripts/birds_schedule.py

#Configure motion to capture metadata in config.json
sudo python3 /home/pi/scripts/update_motion_config.py

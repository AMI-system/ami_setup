#!/bin/bash
# file: power_profiling.sh
# 
# Remarks: testing telemtry power cons
# Remarks: you may append '&' at the end of command to avoid blocking the main daemon.sh.
#
#Send telemtry beacon
sudo python3 /home/pi/ami_setup-cellular-dev/ami-trap-raspi-cellular-send_and_receive.py >> /home/pi/wittypi/telemetry.log 
sudo python3 /home/pi/ami_setup-cellular-dev/ami-trap-raspi-cellular-send_and_receive.py >> /home/pi/wittypi/telemetry.log 
sudo python3 /home/pi/ami_setup-cellular-dev/ami-trap-raspi-cellular-send_and_receive.py >> /home/pi/wittypi/telemetry.log 
sudo python3 /home/pi/ami_setup-cellular-dev/ami-trap-raspi-cellular-send_and_receive.py >> /home/pi/wittypi/telemetry.log 
sudo python3 /home/pi/ami_setup-cellular-dev/ami-trap-raspi-cellular-send_and_receive.py >> /home/pi/wittypi/telemetry.log
sudo python3 /home/pi/ami_setup-cellular-dev/ami-trap-raspi-cellular-send_and_receive.py >> /home/pi/wittypi/telemetry.log 

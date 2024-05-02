#!/usr/bin/env python3
#-*- coding: utf-8 -*-

import subprocess
import json
from pathlib import Path
import os
from datetime import datetime, timedelta
from crontab import CronTab


def get_sunset_sunrise_times(latitude, longitude, date):
    # Construct the Helicron command
    # heliocron --latitude 52.752845 --longitude -3.253449 report --json
    command = ["/home/pi/scripts/heliocron", "--latitude", str(latitude), "--longitude", str(longitude), "report", "--json"]

    # Run the command
    result = subprocess.run(command, capture_output=True, text=True)
    # print(result)

    # Check if the command was successful
    if result.returncode == 0:
        # Split the output by newlines and return civil dawn and civil dusk times
        stdout = json.loads(result.stdout)
        #print(stdout)
        sunset = stdout['sunset']
        sunrise = stdout['sunrise']
        return sunset, sunrise
    else:
        # Handle error
        print("Error:", result.stderr)
        return None, None

# Read the config file
config_path = Path('/home/pi/config.json')
with config_path.open() as fp:
    config = json.load(fp)

# Get the camera setting from the config file
camera_settings = config["camera_operation"]

# Find today's and tomorrow's dates
today = datetime.now()
tomorrow = today + timedelta(1)

# Get civil dawn and dusk for today and tomorrow
sunset, _ = get_sunset_sunrise_times(config['device_settings']['lat'], config['device_settings']['lon'], today)
_, sunrise = get_sunset_sunrise_times(config['device_settings']['lat'], config['device_settings']['lon'], tomorrow)

# Calculate when the moth's recording should start and finish
motion_start = datetime.strptime(sunset, '%Y-%m-%dT%H:%M:%S%z')
motion_end = datetime.strptime(sunrise, '%Y-%m-%dT%H:%M:%S%z')

# Access the user crontab
ami_cron = CronTab(user='pi')

# Remove any existing jobs
ami_cron.remove_all(comment='motion on')
ami_cron.remove_all(comment='motion off')

# Define start cron job
motion_on_job = ami_cron.new(command="sudo motion -m & sudo /home/pi/scripts/setCamera.sh & sudo python /home/pi/scripts/control_ON_lights.py", comment="motion on")
motion_on_job.setall(f'{motion_start.time().minute} {motion_start.time().hour} * * 1,3,5') # Mon, Wed, Fri

# Defien end cron job
motion_off_job = ami_cron.new(command="sudo pkill motion & sudo python /home/pi/scripts/control_OFF_lights.py", comment="motion off")
motion_off_job.setall(f'{motion_end.time().minute} {motion_end.time().hour-1} * * 2,4,6') # Tue, Thu, Sat

# Write new cron job into the user crontab
ami_cron.write()

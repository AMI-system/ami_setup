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
    # heliocron -date 2020-02-25 --latitude 52.752845 --longitude -3.253449 report --json
    command = ["/home/pi/scripts/heliocron", "--date", date.strftime("%Y-%m-%d"), "--latitude", str(latitude), "--longitude", str(longitude), "report", "--json"]

    # Run the command
    result = subprocess.run(command, capture_output=True, text=True)
    # print(result)

    # Check if the command was successful
    if result.returncode == 0:
        # Split the output by newlines and return civil dawn and civil dusk times
        stdout = json.loads(result.stdout)
        #print(stdout)
        sunset = datetime.strptime(stdout['sunset'], '%Y-%m-%dT%H:%M:%S%z')
        sunrise = datetime.strptime(stdout['sunrise'], '%Y-%m-%dT%H:%M:%S%z')
        return sunset.replace(tzinfo=None), sunrise.replace(tzinfo=None)
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

# Get sunset and sunrise for today and tomorrow
sunset, _ = get_sunset_sunrise_times(config['device_settings']['lat'], config['device_settings']['lon'], today)
_, sunrise = get_sunset_sunrise_times(config['device_settings']['lat'], config['device_settings']['lon'], tomorrow)

# Access the user crontab
ami_cron = CronTab(user='pi')

# Remove any existing jobs
ami_cron.remove_all(comment='motion on')
ami_cron.remove_all(comment='motion off')

# Step 1: Create integers of days of the week to start
start_days = [1, 3, 5] # Monday, Tue, Thu, Sat
end_days = [(x + 1 if (x + 1) != 7 else 0) for x in start_days] # one day later

# Step 2: Convert the list to a string "1,2,4,6"
start_day_str = ",".join(map(str, start_days))
end_day_str = ",".join(map(str, end_days))

# Define start cron job
motion_on_job = ami_cron.new(command="sudo motion -m & sudo /home/pi/scripts/setCamera.sh & sudo python /home/pi/scripts/control_ON_lights.py", comment="motion on")
motion_on_job.setall(f'{sunset.time().minute} {sunset.time().hour} * * {start_day_str}') # Mon, Wed, Fri

# Define end cron job
motion_off_job = ami_cron.new(command="sudo pkill motion & sudo python /home/pi/scripts/control_OFF_lights.py", comment="motion off")
motion_off_job.setall(f'{sunrise.time().minute} {sunrise.time().hour-1} * * {end_day_str}') # Tue, Thu, Sat

# Write new cron job into the user crontab
ami_cron.write()

# Creating a list of weekdays
weekdays = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
selected_weekdays = [weekdays[i] for i in start_days]

# Update the start and end time in the config.json
config["camera_operation"]["start_time"] = datetime.strptime(motion_start, '%H:%M:%S')
config["camera_operation"]["end_time"] = datetime.strptime(motion_end, '%H:%M:%S')
config["camera_operation"]["start_days"] = selected_weekdays

# Save the updated config.json
with open('/home/pi/config.json', 'w') as file:
    json.dump(config, file, indent=4)
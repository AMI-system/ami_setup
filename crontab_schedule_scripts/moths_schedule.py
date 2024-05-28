#!/usr/bin/env python3
#-*- coding: utf-8 -*-

import json
from pathlib import Path
from datetime import datetime
from crontab import CronTab

from utils.shared_functions import read_json_config


if __name__ == "__main__":
    # Read the config file
    config_path = Path('/home/pi/config.json')

    # Read the JSON configuration file
    config = read_json_config(config_path)

    # Get the camera setting from the config file
    camera_settings = config["camera_operation"]

    # Get sunset and sunrise for today and tomorrow
    sunset_str = config["sunrise_sunset_times"]["sunset_time"]
    sunrise_str = config["sunrise_sunset_times"]["sunrise_time"]

    # Convert to datetime object
    sunset = datetime.strptime(sunset_str, '%H:%M:%S%z')
    sunrise = datetime.strptime(sunrise_str, '%H:%M:%S%z')

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
    motion_on_job = ami_cron.new(command="sudo python3 /home/pi/scripts/update_motion_config.py && sudo python3 /home/pi/scripts/control_ON_lights.py && sudo motion -m", comment="motion on")
    motion_on_job.setall(f'{sunset.time().minute} {sunset.time().hour} * * {start_day_str}') # Mon, Wed, Fri

    # Define end cron job
    motion_off_job = ami_cron.new(command="sudo pkill motion && sudo python3 /home/pi/scripts/control_OFF_lights.py", comment="motion off")
    motion_off_job.setall(f'{sunrise.time().minute} {sunrise.time().hour-1} * * {end_day_str}') # Tue, Thu, Sat

    # Write new cron job into the user crontab
    ami_cron.write()

    # Creating a list of weekdays
    weekdays = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
    selected_weekdays = [weekdays[i] for i in start_days]

    # Update the start and end time in the config.json
    config["camera_operation"]["start_time"] = sunset.strftime('%H:%M:%S%z')
    config["camera_operation"]["end_time"] = sunrise.strftime('%H:%M:%S%z')
    config["camera_operation"]["start_days"] = selected_weekdays

    # Save the updated config.json
    with open('/home/pi/config.json', 'w') as file:
        json.dump(config, file, indent=4)

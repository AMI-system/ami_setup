#!/usr/bin/env python3
#-*- coding: utf-8 -*-

import json
from pathlib import Path
from datetime import datetime, timedelta
from crontab import CronTab

from utils.shared_functions import read_json_config, get_current_time

if __name__ == "__main__":
    # Read the config file
    config_path = Path('/home/pi/config.json')

    # Read the JSON configuration file
    config = read_json_config(config_path)

    # Get the audio_settings settings from the config file
    audio_settings = config['audio_settings']

    # Find today's and tomorrow's dates
    today = datetime.now()
    tomorrow = today + timedelta(1)

    # Access the user crontab
    ami_cron = CronTab(user = 'pi')

    # Remove any existing jobs
    ami_cron.remove_all(comment='birds 1')
    ami_cron.remove_all(comment='birds 2')

    # Step 1: Create integers of days of the week to start
    start_days = [2, 4, 6] # Tue, Thu, Sat
    end_days = [(x + 1 if (x + 1) != 7 else 0) for x in start_days]

    # Step 2: Convert the list to a string "1,2,4,6"
    start_day_str = ",".join(map(str, start_days))
    end_day_str = ",".join(map(str, end_days))

    # Define cron job
    job = "sudo python3 /home/pi/scripts/birds_recording.py"

    # There are two jobs, one from Mon, Wed and Fri at 12pm to Tue, Thu and Sat 23:53pm and one from tomorrow midnight to 11:59am
    birds_job_1 = ami_cron.new(command=job, comment="birds 1")
    birds_job_1.setall(f'*/5 12-23 * * {start_day_str}') # Tue, Thu, Sun

    birds_job_2 = ami_cron.new(command=job, comment="birds 2")
    birds_job_2.setall(f'*/5 0-11 * * {end_day_str}') # Wed, Fri, Sat

    # Write new cron job into the user crontab
    ami_cron.write()

    # Creating a list of weekdays
    weekdays = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
    selected_weekdays = [weekdays[i] for i in start_days]

    # Read the JSON configuration file
    config = read_json_config(config_path)

    # Obtain the daved latitude and longitude of the deployment
    latitude = config["device_settings"]["lat"]
    longitude = config["device_settings"]["lon"]

    # Get current time in ISO 8601 format
    current_time_zone = get_current_time(latitude, longitude).strftime('%z')
    
    # Update the start and end time in the config.json
    config["audio_operation"]["start_time"] = f'12:00:00{current_time_zone}'
    config["audio_operation"]["end_time"] = f'11:55:00{current_time_zone}'
    config["audio_operation"]["start_days"] = selected_weekdays

    # Save the updated config.json
    with open('/home/pi/config.json', 'w') as file:
        json.dump(config, file, indent=4)

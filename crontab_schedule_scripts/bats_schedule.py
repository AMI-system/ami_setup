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

    # Get the ultrasonic_settings settings from the config file
    ultrasonic_settings = config['ultrasonic_settings']

    # Get sunset and sunrise for today and tomorrow
    sunset_str = config["sunrise_sunset_times"]["sunset_time"]
    sunrise_str = config["sunrise_sunset_times"]["sunrise_time"]

    # Convert to datetime object
    sunset = datetime.strptime(sunset_str, '%H:%M:%S%z')
    sunrise = datetime.strptime(sunrise_str, '%H:%M:%S%z')

    # Access the user crontab
    ami_cron = CronTab(user='pi')

    # Remove any existing jobs
    ami_cron.remove_all(comment='bats sunset 1')
    ami_cron.remove_all(comment='bats sunset 2')

    ami_cron.remove_all(comment='bats sunrise 1')
    ami_cron.remove_all(comment='bats sunrise 2')

    # Step 1: Create integers of days of the week to start
    start_days = [1, 2, 4, 6] # Monday, Tue, Thu, Sat
    end_days = [(x + 1 if (x + 1) != 7 else 0) for x in start_days] # one day later

    # Step 2: Convert the list to a string "1,2,4,6"
    start_day_str = ",".join(map(str, start_days))
    end_day_str = ",".join(map(str, end_days))

    # Define cron job
    job = "sudo python3 /home/pi/scripts/bats_recording.py"

    # Recording schedule from today's sunse to midnight
    evening_hour = sunset.time().hour # Sunset hour
    evening_minute = sunset.time().minute # Sunset minute
    offset_minute = evening_minute % 5 # Sunset minute offset

    # Check if offset minute is multiple of 5, if so to avoid overlap with bird's recording we will add 2 minutes
    if offset_minute == 0:
        evening_minute = evening_minute + 2
        offset_minute = offset_minute + 2
    # Check if offset minute is 1 or 6, if so to avoid overlap with bird's recording we will add 1 minute
    elif offset_minute == 1:
        evening_minute = evening_minute + 1
        offset_minute = offset_minute + 1

    # First job has to run between sunset minute to the end of sunset hour
    bats_evening_job_1 = ami_cron.new(command=job, comment="bats sunset 1")
    bats_evening_job_1.setall(f'{evening_minute}-59/5 {evening_hour} * * {start_day_str}')

    # If sunset hour plus 1 is smaller or equal to 23
    if evening_hour+1 <= 23:
        bats_evening_job_2 = ami_cron.new(command=job, comment="bats sunset 2")
        bats_evening_job_2.setall(f'{offset_minute}-59/5 {evening_hour+1}-23 * * {start_day_str}')

    # Recording schedule from midnight to tomorrow's sunrise
    morning_hour = sunrise.time().hour # Sunrise hour
    morning_minute = sunrise.time().minute # Sunrise minute

    # If sunrise hour is equal to midnight and offset minute is smaller than sunrise minute
    if morning_hour == 0 and offset_minute < morning_minute:
        bats_morning_job_1 = ami_cron.new(command=job, comment="bats sunrise 1")
        bats_morning_job_1.setall(f'{offset_minute}-{morning_minute}/5 0 * * {end_day_str}') # Wed, Fri, Sun

    # If sunrise hour is equal to 1, we need a cron job for midnight to 1
    elif morning_hour == 1:
        bats_morning_job_1 = ami_cron.new(command=job, comment="bats sunrise 1")
        bats_morning_job_1.setall(f'{offset_minute}-59/5 0 * * {end_day_str}') # Wed, Fri, Sun

        # If offset minute is smaller that sunrise minute, we need an extra cron job
        if offset_minute < morning_minute:
            bats_morning_job_2 = ami_cron.new(command=job, comment="bats sunrise 2")
            bats_morning_job_2.setall(f'{offset_minute}-{morning_minute}/5 {morning_hour} * * {end_day_str}') # Wed, Fri, Sun

    # If sunrise hour is bigger than 1, the first job runs between midnight to sunrise hour minus one from offset minute to 59
    elif morning_hour > 1:
        bats_morning_job_1 = ami_cron.new(command=job, comment="bats sunrise 1")
        bats_morning_job_1.setall(f'{offset_minute}-59/5 0-{morning_hour-1} * * {end_day_str}') # Wed, Fri, Sun

        # If offset minute is smaller that sunrise minute, we need an extra cron job for the sunrise hour
        if offset_minute < morning_minute:
            bats_morning_job_2 = ami_cron.new(command=job, comment="bats sunrise 2")
            bats_morning_job_2.setall(f'{offset_minute}-{morning_minute}/5 {morning_hour} * * {end_day_str}') # Wed, Fri, Sun

    # Write new cron job into the user crontab
    ami_cron.write()

    # Creating a list of weekdays
    weekdays = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
    selected_weekdays = [weekdays[i] for i in start_days]

    # Update the start and end time in the config.json
    config["ultrasonic_operation"]["start_time"] = sunset.strftime('%H:%M:%S%z')
    config["ultrasonic_operation"]["end_time"] = sunrise.strftime('%H:%M:%S%z')
    config["ultrasonic_operation"]["start_days"] = selected_weekdays

    # Save the updated config.json
    with open('/home/pi/config.json', 'w') as file:
        json.dump(config, file, indent=4)

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

# Get the ultrasonic_settings settings from the config file
ultrasonic_settings = config['ultrasonic_settings']

# Find today's and tomorrow's dates
today = datetime.now()
tomorrow = today + timedelta(1)

# Create folders if they don't exist
Path(f"{ultrasonic_settings['target_path']}").mkdir(parents=True, exist_ok=True)
Path(f"{ultrasonic_settings['target_path']}/{today.strftime('%Y_%m_%d')}").mkdir(parents=True, exist_ok=True)
Path(f"{ultrasonic_settings['target_path']}/{tomorrow.strftime('%Y_%m_%d')}").mkdir(parents=True, exist_ok=True)


# Get civil dawn and dusk for today and tomorrow
sunset, _ = get_sunset_sunrise_times(config['device_settings']['lat'], config['device_settings']['lon'], today)
_, sunrise = get_sunset_sunrise_times(config['device_settings']['lat'], config['device_settings']['lon'], tomorrow)

print("Todays's sunset:", sunset)
print("Tomorrow's sunrise", sunrise)

# Calculate when the bat's recording should start and finish
bats_start = datetime.strptime(sunset, '%Y-%m-%dT%H:%M:%S%z')
bats_end = datetime.strptime(sunrise, '%Y-%m-%dT%H:%M:%S%z')

# Access the user crontab
ami_cron = CronTab(user='pi')

# Remove any existing jobs
ami_cron.remove_all(comment='bats sunset 1')
ami_cron.remove_all(comment='bats sunset 2')

ami_cron.remove_all(comment='bats sunrise 1')
ami_cron.remove_all(comment='bats sunrise 2')

# Define cron job
job = "sudo python3 /home/pi/scripts/bats_recording.py"

# Recording schedule from today's sunse to midnight
evening_hour = bats_start.time().hour # Sunset hour
evening_minute = bats_start.time().minute # Sunset minute
offset_minute = evening_minute % 5 # Sunset minute offset

# Check if offset minute is multiple of 5, if so to avoid overlap with bird's recording we will add 2 minute
if offset_minute == 0:
    evening_minute = evening_minute + 2
    offset_minute = offset_minute + 2

# First job has to run between sunset minute to the en of sunset hour
bats_evening_job_1 = ami_cron.new(command=job, comment="bats sunset 1")
bats_evening_job_1.setall(f'{evening_minute}-59/5 {evening_hour} * * 1,2,4,6') # Tue, Thu, Sat

# If sunset hour plus 1 is smaller or equal to 23
if evening_hour+1 <= 23:
    bats_evening_job_2 = ami_cron.new(command=job, comment="bats sunset 2")
    bats_evening_job_2.setall(f'{offset_minute}-59/5 {evening_hour+1}-23 * * 1,2,4,6') # Tue, Thu, Sat


# Recording schedule from midnight to tomorrow's sunrise
morning_hour = bats_end.time().hour # Sunrise hour
morning_minute = bats_end.time().minute # Sunrise minute

# If sunrise hour is equal to midnight and offset minute is smaller than sunrise minute
if morning_hour == 0 and offset_minute < morning_minute:
    bats_morning_job_1 = ami_cron.new(command=job, comment="bats sunrise 1")
    bats_morning_job_1.setall(f'{offset_minute}-{morning_minute}/5 0 * * 2,3,5,0') # Wed, Fri, Sun

# If sunrise hour is equal to 1, we need a cron job for midnight to 1
elif morning_hour == 1:
    bats_morning_job_1 = ami_cron.new(command=job, comment="bats sunrise 1")
    bats_morning_job_1.setall(f'{offset_minute}-59/5 0 * * 2,3,5,0') # Wed, Fri, Sun

    # If offset minute is smaller that sunrise minute, we need an extra cron job
    if offset_minute < morning_minute:
        bats_morning_job_2 = ami_cron.new(command=job, comment="bats sunrise 2")
        bats_morning_job_2.setall(f'{offset_minute}-{morning_minute}/5 {morning_hour} * * 2,3,5,0') # Wed, Fri, Sun

# If sunrise hour is bigger than 1, the first job runs between midnight to sunrise hour minus one from offset minute to 59
elif morning_hour > 1:
    bats_morning_job_1 = ami_cron.new(command=job, comment="bats sunrise 1")
    bats_morning_job_1.setall(f'{offset_minute}-59/5 0-{morning_hour-1} * * 2,3,5,0') # Wed, Fri, Sun

    # If offset minute is smaller that sunrise minute, we need an extra cron job for the sunrise hour
    if offset_minute < morning_minute:
        bats_morning_job_2 = ami_cron.new(command=job, comment="bats sunrise 2")
        bats_morning_job_2.setall(f'{offset_minute}-{morning_minute}/5 {morning_hour} * * 2,3,5,0') # Wed, Fri, Sun

# Write new cron job into the user crontab
ami_cron.write()




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


# Load the config paramters from the JSON file
def read_json_config(json_path):
    with open(json_path, 'r') as json_file:
        return json.load(json_file)


def get_previous_sunday():
    # Get today's date
    today = datetime.now()
    
    # Get the day of the week (0 = Monday, 6 = Sunday)
    day_of_week = today.weekday()
    
    if day_of_week == 6:  # If today is Sunday
        return today
    else:
        # Calculate the date for the previous Sunday
        previous_sunday = today - timedelta(days=day_of_week + 1)
        return previous_sunday


# Time differecne between two dates
def time_difference(start_date, end_date):
    time_delta = end_date - start_date

    # Get the total seconds in the time difference
    total_seconds = time_delta.total_seconds()

    # Convert time delta to days, hours, and minutes
    days = int(total_seconds) // (24 * 3600)
    hours = (int(total_seconds) % (24 * 3600)) // 3600
    minutes = int(total_seconds % 3600) // 60

    return days, hours, minutes


# Replace 'config.json' with the actual path to your JSON configuration file
json_config_path = 'config.json'

# Read the JSON configuration file
json_config = read_json_config(json_config_path)

# Extracting the device_settings part
device_settings = json_config['device_settings']

# Find today's and tomorrow's dates
sunday_dt = get_previous_sunday()
monday_dt = sunday_dt + timedelta(1)
tuesday_dt = sunday_dt + timedelta(2)
wednesday_dt = sunday_dt + timedelta(3)
thursday_dt = sunday_dt + timedelta(4)
friday_dt = sunday_dt + timedelta(5)
saturday_dt = sunday_dt + timedelta(6)
next_sunday_dt = sunday_dt + timedelta(7)

# Get sunset and sunrise for each day
monday_sunset, _ = get_sunset_sunrise_times(device_settings['lat'], device_settings['lon'], monday_dt)
_, tuesday_sunrise = get_sunset_sunrise_times(device_settings['lat'], device_settings['lon'], tuesday_dt)
wednesday_sunset, _ = get_sunset_sunrise_times(device_settings['lat'], device_settings['lon'], wednesday_dt)
_, thursday_sunrise = get_sunset_sunrise_times(device_settings['lat'], device_settings['lon'], thursday_dt)
friday_sunset, _ = get_sunset_sunrise_times(device_settings['lat'], device_settings['lon'], friday_dt)
_, saturday_sunrise = get_sunset_sunrise_times(device_settings['lat'], device_settings['lon'], saturday_dt)

# Every schedule starts on a Monday and ends on a Sunday, total Witty Pi schedule to cover this full week schedule
# Overlapping schedule starts 10 minutes earlier to the nearest schedule and ends 10 minutes later to the last schedule
start_time = monday_sunset - timedelta(minutes=10)
end_time = datetime(next_sunday_dt.year, next_sunday_dt.month, next_sunday_dt.day, 12, 20)

# 1- ON from Monday sunset-10min to Tuesday sunrise+10min
on_from_1 = start_time
on_to_1 = tuesday_sunrise + timedelta(minutes=10)
on_duration_days_1, on_duration_hours_1, on_duration_minutes_1 = time_difference(on_from_1, on_to_1)

# 2- OFF from Tuesday sunrise+10min to Tuesday 11:50
off_from_2 = on_to_1
off_to_2 = datetime(tuesday_dt.year, tuesday_dt.month, tuesday_dt.day, 11, 50)
off_duration_days_2, off_duration_hours_2, off_duration_minutes_2 = time_difference(off_from_2, off_to_2)

# 3- ON from Tuesday 11:50 to Wednesday 12:10
on_from_3 = off_to_2
on_to_3 = datetime(wednesday_dt.year, wednesday_dt.month, wednesday_dt.day, 12, 10)
on_duration_days_3, on_duration_hours_3, on_duration_minutes_3 = time_difference(on_from_3, on_to_3)

# 4- OFF from Wednesday 12:10 to Wednesday sunset-10min
off_from_4 = on_to_3
off_to_4 = wednesday_sunset - timedelta(minutes=10)
off_duration_days_4, off_duration_hours_4, off_duration_minutes_4 = time_difference(off_from_4, off_to_4)

# 5- ON from Wednesday sunset-10min to Thursday sunrise+10min
on_from_5 = off_to_4
on_to_5 = thursday_sunrise + timedelta(minutes=10)
on_duration_days_5, on_duration_hours_5, on_duration_minutes_5 = time_difference(on_from_5, on_to_5)

# 6- OFF from Thursday sunrise+10min to Thursday 11:50
off_from_6 = on_to_5
off_to_6 = datetime(thursday_dt.year, thursday_dt.month, thursday_dt.day, 11, 50)
off_duration_days_6, off_duration_hours_6, off_duration_minutes_6 = time_difference(off_from_6, off_to_6)

# 7- ON from Thursday 11:50 to Friday 12:10
on_from_7 = off_to_6
on_to_7 = datetime(friday_dt.year, friday_dt.month, friday_dt.day, 12, 10)
on_duration_days_7, on_duration_hours_7, on_duration_minutes_7 = time_difference(on_from_7, on_to_7)

# 8- OFF from Friday 12:10 to Friday sunset-10min
off_from_8 = on_to_7
off_to_8 = friday_sunset - timedelta(minutes=10)
off_duration_days_8, off_duration_hours_8, off_duration_minutes_8 = time_difference(off_from_8, off_to_8)

# 9- ON from Friday sunset-10min to Saturday sunrise+10min
on_from_9 = off_to_8
on_to_9 = saturday_sunrise + timedelta(minutes=10)
on_duration_days_9, on_duration_hours_9, on_duration_minutes_9 = time_difference(on_from_9, on_to_9)

# 10- OFF from Saturday sunrise+10min to Saturday 11:50
off_from_10 = on_to_9
off_to_10 = datetime(saturday_dt.year, saturday_dt.month, saturday_dt.day, 11, 50)
off_duration_days_10, off_duration_hours_10, off_duration_minutes_10 = time_difference(off_from_10, off_to_10)

# 11- ON from Saturday 11:50 to Sunday 12:10
on_from_11 = off_to_10
on_to_11 = datetime(next_sunday_dt.year, next_sunday_dt.month, next_sunday_dt.day, 12, 10)
on_duration_days_11, on_duration_hours_11, on_duration_minutes_11 = time_difference(on_from_11, on_to_11)

# 12- OFF from Sunday 12:10 to Sunday 12:20
off_from_12 = on_to_11
off_to_12 = datetime(next_sunday_dt.year, next_sunday_dt.month, next_sunday_dt.day, 12, 20)
off_duration_days_12, off_duration_hours_12, off_duration_minutes_12 = time_difference(off_from_12, off_to_12)


# Generate Witty Pi schedule
# Turn on Raspberry Pi at predetermined time of the week, keep ON state for a determined time
witty_pi_schedule = f"""
BEGIN {start_time}
END {end_time}
ON D{on_duration_days_1} H{on_duration_hours_1} M{on_duration_minutes_1}
OFF D{off_duration_days_2} H{off_duration_hours_2} M{off_duration_minutes_2}
ON D{on_duration_days_3} H{on_duration_hours_3} M{on_duration_minutes_3}
OFF D{off_duration_days_4} H{off_duration_hours_4} M{off_duration_minutes_4}
ON D{on_duration_days_5} H{on_duration_hours_5} M{on_duration_minutes_5}
OFF D{off_duration_days_6} H{off_duration_hours_6} M{off_duration_minutes_6}
ON D{on_duration_days_7} H{on_duration_hours_7} M{on_duration_minutes_7}
OFF D{off_duration_days_8} H{off_duration_hours_8} M{off_duration_minutes_8}
ON D{on_duration_days_9} H{on_duration_hours_9} M{on_duration_minutes_9}
OFF D{off_duration_days_10} H{off_duration_hours_10} M{off_duration_minutes_10}
ON D{on_duration_days_11} H{on_duration_hours_11} M{on_duration_minutes_11}
OFF D{off_duration_days_12} H{off_duration_hours_12} M{off_duration_minutes_12}
"""

# print(witty_pi_schedule)

# Specify the target path for the schedule file
target_path = '/home/pi/scripts/'

# Save the schedule to the target path
schedule_file_path = f'{target_path}witty_pi_schedule.wpi'

with open(schedule_file_path, 'w') as file:
    file.write(witty_pi_schedule)

# print(f"Witty Pi schedule generated and saved to {schedule_file_path}.")

# Move the schedule file to the target path
#shutil.move('schedule.wpi', schedule_file_path)

# Run the runschedule.sh script from the target path
#subprocess.run(["bash", f"{target_path}runScript.sh"])

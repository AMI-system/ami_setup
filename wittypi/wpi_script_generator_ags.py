#!/usr/bin/env python3
#-*- coding: utf-8 -*-


import subprocess
from datetime import datetime, timedelta
from crontab import CronTab
import shutil

from utils.shared_functions import get_sunset_sunrise_times, read_json_config, get_previous_sunday, time_difference


if __name__ == "__main__":
    # Replace 'config.json' with the actual path to your JSON configuration file
    json_config_path = '/home/pi/config.json'

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
    monday_sunset, _ = get_sunset_sunrise_times(device_settings['lat'], device_settings['lon'], monday_dt).replace(tzinfo=None)
    _, tuesday_sunrise = get_sunset_sunrise_times(device_settings['lat'], device_settings['lon'], tuesday_dt).replace(tzinfo=None)
    wednesday_sunset, _ = get_sunset_sunrise_times(device_settings['lat'], device_settings['lon'], wednesday_dt).replace(tzinfo=None)
    _, thursday_sunrise = get_sunset_sunrise_times(device_settings['lat'], device_settings['lon'], thursday_dt).replace(tzinfo=None)
    friday_sunset, _ = get_sunset_sunrise_times(device_settings['lat'], device_settings['lon'], friday_dt).replace(tzinfo=None)
    _, saturday_sunrise = get_sunset_sunrise_times(device_settings['lat'], device_settings['lon'], saturday_dt).replace(tzinfo=None)

    # Every schedule starts on a Monday and ends on a Sunday, total Witty Pi schedule to cover this full week schedule
    # Overlapping schedule starts 10 minutes earlier to the nearest schedule and ends 10 minutes later to the last schedule
    start_time = datetime(sunday_dt.year, sunday_dt.month, sunday_dt.day, 12, 00)
    end_time = datetime(next_sunday_dt.year, next_sunday_dt.month, next_sunday_dt.day, 12, 10)

    # 0- ON from Sunday noon to Sunday noon+10min [Setup time]
    on_from_0 = start_time
    on_to_0 = datetime(sunday_dt.year, sunday_dt.month, sunday_dt.day, 12, 10)
    on_duration_days_0, on_duration_hours_0, on_duration_minutes_0 = time_difference(on_from_0, on_to_0)

    # 0- OFF from Sunday 12:10 to Monday sunset-10min [Schedule begins]
    off_from_0 = on_to_0
    off_to_0 = monday_sunset - timedelta(minutes=10)
    off_duration_days_0, off_duration_hours_0, off_duration_minutes_0 = time_difference(off_from_0, off_to_0)

    # 1- ON from Monday sunset-10min to Tuesday sunrise+10min
    on_from_1 = off_to_0
    on_to_1 = tuesday_sunrise + timedelta(minutes=10)
    on_duration_days_1, on_duration_hours_1, on_duration_minutes_1 = time_difference(on_from_1, on_to_1)

    # 1- OFF from Tuesday sunrise+10min to Tuesday 11:50
    off_from_1 = on_to_1
    off_to_1 = datetime(tuesday_dt.year, tuesday_dt.month, tuesday_dt.day, 11, 50)
    off_duration_days_1, off_duration_hours_1, off_duration_minutes_1 = time_difference(off_from_1, off_to_1)

    # 2- ON from Tuesday 11:50 to Wednesday 12:10
    on_from_2 = off_to_1
    on_to_2 = datetime(wednesday_dt.year, wednesday_dt.month, wednesday_dt.day, 12, 10)
    on_duration_days_2, on_duration_hours_2, on_duration_minutes_2 = time_difference(on_from_2, on_to_2)

    # 2- OFF from Wednesday 12:10 to Wednesday sunset-10min
    off_from_2 = on_to_2
    off_to_2 = wednesday_sunset - timedelta(minutes=10)
    off_duration_days_2, off_duration_hours_2, off_duration_minutes_2 = time_difference(off_from_2, off_to_2)

    # 3- ON from Wednesday sunset-10min to Thursday sunrise+10min
    on_from_3 = off_to_2
    on_to_3 = thursday_sunrise + timedelta(minutes=10)
    on_duration_days_3, on_duration_hours_3, on_duration_minutes_3 = time_difference(on_from_3, on_to_3)

    # 3- OFF from Thursday sunrise+10min to Thursday 11:50
    off_from_3 = on_to_3
    off_to_3 = datetime(thursday_dt.year, thursday_dt.month, thursday_dt.day, 11, 50)
    off_duration_days_3, off_duration_hours_3, off_duration_minutes_3 = time_difference(off_from_3, off_to_3)

    # 4- ON from Thursday 11:50 to Friday 12:10
    on_from_4 = off_to_3
    on_to_4 = datetime(friday_dt.year, friday_dt.month, friday_dt.day, 12, 10)
    on_duration_days_4, on_duration_hours_4, on_duration_minutes_4 = time_difference(on_from_4, on_to_4)

    # 4- OFF from Friday 12:10 to Friday sunset-10min
    off_from_4 = on_to_4
    off_to_4 = friday_sunset - timedelta(minutes=10)
    off_duration_days_4, off_duration_hours_4, off_duration_minutes_4 = time_difference(off_from_4, off_to_4)

    # 5- ON from Friday sunset-10min to Saturday sunrise+10min
    on_from_5 = off_to_4
    on_to_5 = saturday_sunrise + timedelta(minutes=10)
    on_duration_days_5, on_duration_hours_5, on_duration_minutes_5 = time_difference(on_from_5, on_to_5)

    # 5- OFF from Saturday sunrise+10min to Saturday 11:50
    off_from_5 = on_to_5
    off_to_5 = datetime(saturday_dt.year, saturday_dt.month, saturday_dt.day, 11, 50)
    off_duration_days_5, off_duration_hours_5, off_duration_minutes_5 = time_difference(off_from_5, off_to_5)

    # 6- ON from Saturday 11:50 to Sunday 12:10
    on_from_6 = off_to_5
    on_to_6 = datetime(next_sunday_dt.year, next_sunday_dt.month, next_sunday_dt.day, 12, 10)
    on_duration_days_6, on_duration_hours_6, on_duration_minutes_6 = time_difference(on_from_6, on_to_6)

    # 6- OFF from Sunday 12:10 to Sunday 12:20
    off_from_6 = on_to_6
    off_to_6 = datetime(next_sunday_dt.year, next_sunday_dt.month, next_sunday_dt.day, 12, 20)
    off_duration_days_6, off_duration_hours_6, off_duration_minutes_6 = time_difference(off_from_6, off_to_6)


    # Generate Witty Pi schedule
    # Turn on Raspberry Pi at predetermined time of the week, keep ON state for a determined time
    witty_pi_schedule = f"""
    BEGIN {start_time}
    END {end_time}
    ON D{on_duration_days_0} H{on_duration_hours_0} M{on_duration_minutes_0}
    OFF D{off_duration_days_0} H{off_duration_hours_0} M{off_duration_minutes_0}
    ON D{on_duration_days_1} H{on_duration_hours_1} M{on_duration_minutes_1}
    OFF D{off_duration_days_1} H{off_duration_hours_1} M{off_duration_minutes_1}
    ON D{on_duration_days_2} H{on_duration_hours_2} M{on_duration_minutes_2}
    OFF D{off_duration_days_2} H{off_duration_hours_2} M{off_duration_minutes_2}
    ON D{on_duration_days_3} H{on_duration_hours_3} M{on_duration_minutes_3}
    OFF D{off_duration_days_3} H{off_duration_hours_3} M{off_duration_minutes_3}
    ON D{on_duration_days_4} H{on_duration_hours_4} M{on_duration_minutes_4}
    OFF D{off_duration_days_4} H{off_duration_hours_4} M{off_duration_minutes_4}
    ON D{on_duration_days_5} H{on_duration_hours_5} M{on_duration_minutes_5}
    OFF D{off_duration_days_5} H{off_duration_hours_5} M{off_duration_minutes_5}
    ON D{on_duration_days_6} H{on_duration_hours_6} M{on_duration_minutes_6}
    OFF D{off_duration_days_6} H{off_duration_hours_6} M{off_duration_minutes_6}
    """

    # print(witty_pi_schedule)

    # Specify the target path for the schedule file
    target_path = '/home/pi/wittypi/schedules/'
    execute_path = '/home/pi/wittypi/'

    # Save the schedule to the target path
    schedule_file_path = f'{target_path}witty_pi_schedule_{sunday_dt.year}_{sunday_dt.month}_{sunday_dt.day}.wpi'

    with open(schedule_file_path, 'w') as file:
        file.write(witty_pi_schedule)

    print(f"Witty Pi schedule generated and saved to {schedule_file_path}.")

    # Move the schedule file to the target path
    shutil.copy(schedule_file_path, '/home/pi/wittypi/schedule.wpi')

    # Run the runschedule.sh script from the target path
    subprocess.run(["bash", f"{execute_path}runScript.sh"])


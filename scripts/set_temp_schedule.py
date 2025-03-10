#!/usr/bin/env python3
#-*- coding: utf-8 -*-

from datetime import datetime, timedelta
from crontab import CronTab
import shutil
import os
import subprocess
from utils.shared_functions import time_difference

if __name__ == "__main__": 
    
    # Get today's date
    start_time = datetime.now()
    start_time = datetime(start_time.year, start_time.month, start_time.day, start_time.hour, start_time.minute)
    
    # Get date 7 days from now
    end_time = start_time + timedelta(days=7, hours=2)
    end_time = datetime(end_time.year, end_time.month, end_time.day, end_time.hour, end_time.minute)
    
    # ON period
    on_from = start_time
    on_to = start_time + timedelta(days=7)
    on_duration_days, on_duration_hours, on_duration_minutes, on_duration_seconds = time_difference(on_from, on_to)

    # OFF period
    off_from = on_to
    off_to = on_to + timedelta(hours=2)
    off_duration_days, off_duration_hours, off_duration_minutes, off_duration_seconds = time_difference(off_from, off_to)
    
    # Generate Witty Pi schedule
    # Turn on Raspberry Pi at predetermined time of the week, keep ON state for a determined time
    witty_pi_schedule = f"""
    BEGIN {start_time}
    END {end_time}
    ON D{on_duration_days} H{on_duration_hours} M{on_duration_minutes} S{on_duration_seconds}
    OFF D{off_duration_days} H{off_duration_hours} M{off_duration_minutes} S{off_duration_seconds}
    """

    print(witty_pi_schedule)

    # Specify the target path for the schedule file
    target_path = '/home/pi/wittypi/schedules'
    execute_path = '/home/pi/wittypi'

    # Save the schedule to the target path
    schedule_file_path = os.path.join(target_path, f'witty_pi_temp_schedule_{start_time.year}_{start_time.month}_{start_time.day}.wpi')

    with open(schedule_file_path, 'w') as file:
        file.write(witty_pi_schedule)

    print(f"Temp Witty Pi schedule generated and saved to {schedule_file_path}.")

    # Move the schedule file to the target path
    shutil.copy(schedule_file_path, os.path.join(execute_path, 'schedule.wpi'))

    # Run the runschedule.sh script from the target path
    subprocess.run(["bash", os.path.join(execute_path, "runScript.sh")])


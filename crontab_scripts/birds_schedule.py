#!/usr/bin/env python3
#-*- coding: utf-8 -*-

import json
from pathlib import Path
from datetime import datetime, timedelta
from crontab import CronTab


# Read the config file
config_path = Path('/home/pi/config.json')
with config_path.open() as fp:
    config = json.load(fp)

# Get the audio_settings settings from the config file
audio_settings = config['audio_settings']

# Find today's and tomorrow's dates
today = datetime.now()
tomorrow = today + timedelta(1)

# Create folders if they don't exist
Path(f"{audio_settings['target_path']}").mkdir(parents=True, exist_ok=True)
Path(f"{audio_settings['target_path']}/{today.strftime('%Y_%m_%d')}").mkdir(parents=True, exist_ok=True)
Path(f"{audio_settings['target_path']}/{tomorrow.strftime('%Y_%m_%d')}").mkdir(parents=True, exist_ok=True)

# Access the user crontab
ami_cron = CronTab(user='pi')

# Remove any existing jobs
ami_cron.remove_all(comment='birds 1')
ami_cron.remove_all(comment='birds 2')

# Define cron job
job = "sudo python3 /home/pi/scripts/birds_recording.py"

# There are two jobs, one from Mon, Wed and Fri at 12pm to Tue, Thu and Sat23:53pm and one from tomorrow midnight to 11:59am
birds_job_1 = ami_cron.new(command=job, comment="birds 1")
birds_job_1.setall(f'*/5 12-23 * * 2,4,6') # Mon, Tue, Fri

birds_job_2 = ami_cron.new(command=job, comment="birds 2")
birds_job_2.setall(f'*/5 0-11 * * 3,5,0') # Tue, Thu, Sat

# Write new cron job into the user crontab
ami_cron.write()





#!/usr/bin/env python3
#-*- coding: utf-8 -*-

import subprocess
import json
from pathlib import Path
from datetime import datetime, timedelta


# Read the config file
config_path = Path('/home/pi/config.json')
with config_path.open() as fp:
    config = json.load(fp)

# Get the ultrasonic_settings settings from the config file
ultrasonic_settings = config['ultrasonic_settings']

today = datetime.now()
command = ["sudo", "arecord", "-D", ultrasonic_settings['device'], "-f", ultrasonic_settings['data_format'], "-r", ultrasonic_settings['sample_rate'], "-d", ultrasonic_settings['rec_interval'],
          f"{ultrasonic_settings['target_path']}/{today.strftime('%Y_%m_%d')}/{today.strftime('%Y%m%d_%H%M%S')}.wav"]

# Run the command
result = subprocess.run(command, capture_output=True, text=True)
print(result)
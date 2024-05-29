#!/usr/bin/env python3
#-*- coding: utf-8 -*-

import json
from pathlib import Path
from datetime import datetime, timedelta

from utils.shared_functions import read_json_config, get_sunset_sunrise_times

CONFIG_PATH = Path('/home/pi/config.json')

if __name__ == "__main__":
    # Read the config file
    config_path = CONFIG_PATH

    # Read the JSON configuration file
    config = read_json_config(config_path)

    # Find today's and tomorrow's dates
    today = datetime.now()
    tomorrow = today + timedelta(1)

    # Get civil sunset and sunrise for today and tomorrow
    sunset, _ = get_sunset_sunrise_times(config['device_settings']['lat'], config['device_settings']['lon'], today)
    _, sunrise = get_sunset_sunrise_times(config['device_settings']['lat'], config['device_settings']['lon'], today)

    # print("Todays's sunset:", sunset)
    # print("Tomorrow's sunrise", sunrise)

    # Save sunrise and sunset times
    config["sunrise_sunset_times"]["sunset_time"] = sunset.strftime('%H:%M:%S%z')
    config["sunrise_sunset_times"]["sunrise_time"] = sunrise.strftime('%H:%M:%S%z')

    # Save the updated config.json
    with open(CONFIG_PATH, 'w') as file:
        json.dump(config, file, indent=4)

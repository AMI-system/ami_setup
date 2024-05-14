#!/usr/bin/env python3
#-*- coding: utf-8 -*-

import json
from pathlib import Path
from datetime import datetime, timedelta

from utils.shared_functions import read_json_config, get_sunset_sunrise_times


if __name__ == "__main__":
    # Read the config file
    config_path = Path('/home/pi/config.json')

    # Read the JSON configuration file
    config = read_json_config(config_path)

    # Find today's and tomorrow's dates
    today = datetime.now()

    # Get civil sunset and sunrise for today and tomorrow
    sunset, sunrise = get_sunset_sunrise_times(config['device_settings']['lat'], config['device_settings']['lon'], today)

    # print("Todays's sunset:", sunset)
    # print("Tomorrow's sunrise", sunrise)

    # Save sunrise and sunset times
    config["sunrise_sunset_times"]["sunset_time"] = sunset.strftime('%H:%M:%S')
    config["sunrise_sunset_times"]["sunrise_time"] = sunrise.strftime('%H:%M:%S')

    # Save the updated config.json
    with open('/home/pi/config.json', 'w') as file:
        json.dump(config, file, indent=4)

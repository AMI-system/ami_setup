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

# Find today's and tomorrow's dates
today = datetime.now()

# Get civil sunset and sunrise for today and tomorrow
sunset, sunrise = get_sunset_sunrise_times(config['device_settings']['lat'], config['device_settings']['lon'], today)

print("Todays's sunset:", sunset)
print("Tomorrow's sunrise", sunrise)

# Save sunrise and sunset times
config["sunrise_sunset_times"]["sunset_time"] = sunset.strftime('%H:%M:%S')
config["sunrise_sunset_times"]["sunrise_time"] = sunrise.strftime('%H:%M:%S')

# Save the updated config.json
with open('/home/pi/config.json', 'w') as file:
    json.dump(config, file, indent=4)

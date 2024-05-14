#!/usr/bin/env python3
#-*- coding: utf-8 -*-

import subprocess
import json
from pathlib import Path
from datetime import datetime, timedelta
from timezonefinder import TimezoneFinder
import os
import pytz
import taglib

# Read the config file
config_path = Path('/home/pi/config.json')
with config_path.open() as fp:
    config = json.load(fp)

# Get the ultrasonic_settings settings from the config file
ultrasonic_settings = config['ultrasonic_settings']

def get_current_time(lat, lng):
    # Get the timezone name from coordinates
    tf = TimezoneFinder()
    timezone_str = tf.timezone_at(lat=lat, lng=lng)
    if timezone_str is None:
        return "Timezone could not be determined"

    # Convert to timezone-aware datetime object
    timezone = pytz.timezone(timezone_str)
    current_time = datetime.now(timezone)

    # Format the datetime in ISO 8601 format
    return current_time

# Obtain the daved latitude and longitude of the deployment
latitude = config["device_settings"]["lat"]
longitude = config["device_settings"]["lon"]

# Get current time in ISO 8601 format
current_time = get_current_time(latitude, longitude)

# Find today date
date = current_time.strftime('%Y_%m_%d')

# Create folders if they don't exist
Path(f"{ultrasonic_settings['target_path']}").mkdir(parents=True, exist_ok=True)
Path(f"{ultrasonic_settings['target_path']}/{date}").mkdir(parents=True, exist_ok=True)

# Generate the full path
full_path = f"{ultrasonic_settings['target_path']}/{current_time.strftime('%Y_%m_%d')}/{current_time.strftime('%Y%m%d_%H%M%S')}.wav"

# Prepare comand
command = ["sudo", "arecord", "-D", ultrasonic_settings['device'], "-f", ultrasonic_settings['data_format'], "-r", ultrasonic_settings['sample_rate'], "-d", ultrasonic_settings['rec_interval'],
          full_path]

# Record
result = subprocess.run(command, capture_output=True, text=True)
print(result)

### Metadata collection ###
# Get the current date and time

# obtain IDs
location_id = config["base_ids"]["location_id"]
system_id = config["base_ids"]["system_id"]
hardware_id = config["base_ids"]["hardware_id"]

# obtain survey period start and end time
start_time_str = config["ultrasonic_operation"]["start_time"]
end_time_str = config["ultrasonic_operation"]["end_time"]

# Note recording type
audio_type = "ultrasonic_microphone"

# Generate parent event ID
parent_event_id = f"{system_id}__{audio_type}__{start_time_str}__{end_time_str}"

# Generate event ID
current_time_str = current_time.strftime('%Y-%m-%dT%H:%M:%S%z')
eventID = f"{system_id}__{audio_type}__{current_time_str}"

# Function to obtain survey period start and end time
def get_survey_start_end_datetimes(current_time, start_time_str, end_time_str):

    # Convert start and end time strings to time objects
    start_time = datetime.strptime(start_time_str, "%H:%M:%S").time()
    end_time = datetime.strptime(end_time_str, "%H:%M:%S").time()

    # Extract date from specified datetime
    current_date = current_time.date()

    # Initialise start and end datetime
    start_datetime = datetime.combine(current_date, start_time, current_time.tzinfo)
    end_datetime = datetime.combine(current_date, end_time, current_time.tzinfo)

    if start_datetime <= current_time and current_time >= end_datetime:
        end_datetime = end_datetime + timedelta(days=1)

    elif start_datetime >= current_time and current_time <= end_datetime:
        start_datetime = start_datetime - timedelta(days=1)

    else:
        raise ValueError("This script cannot be run outside of the survey start and end hours.")

    return start_datetime.strftime('%Y-%m-%dT%H:%M:%S%z'), end_datetime.strftime('%Y-%m-%dT%H:%M:%S%z')

# Example usage
# current_time_str = '2023-05-09T23:45:00-0000'

# Convert string to datetime object
current_time = datetime.strptime(current_time_str, '%Y-%m-%dT%H:%M:%S%z')

# Calculate the survey period start and end time
start_datetime_str, end_datetime_str = get_survey_start_end_datetimes(current_time, start_time_str, end_time_str)

#Save metadata as dictionary using same heirarchical structure as the config dictionary
metadata = {

     "audible_microphone_event_data":{

      "event_ids": {
         "parent_event_id": parent_event_id,
         "event_id": eventID
      },

    "date_fields": {
        "event_date": current_time_str,
        "recording_period_start_time": start_datetime_str,
        "recording_period_end_time": end_datetime_str
        },

    "file_characteristics":{
         "file_path": full_path,
         "file_type": audio_type
        }
   }

   }

# Update the config json
config.update(metadata)

# Ignore fields that will vary between surveying components
fields_ignore = ["audio_settings", "camera_settings", "motion_settings", "camera_operation", "audio_operation"]
config = dict((field, config[field]) for field in config if field not in fields_ignore)

# Filter comments
keys_to_remove = [key for key in metadata if key == "COMMENT"]
for key in keys_to_remove:
    del metadata[key]

def remove_comments(data):
    if isinstance(data, dict):
        # Check if 'COMMENT' key exists and has the specific value
        if "COMMENT" in data:
            del data["COMMENT"]
        # Recursively process each value in dictionary
        for key, value in list(data.items()):
            remove_comments(value)

# Removing specific comments
remove_comments(config)

# Save within the audio file
recording_file = taglib.File(full_path)
recording_file.tags["TITLE"] = json.dumps(config)
recording_file.save()


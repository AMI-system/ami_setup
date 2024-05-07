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

# Get the audio_settings settings from the config file
audio_settings = config['audio_settings']

today = datetime.now()
# if not os.path.exists(f"{audio_settings['target_path']}/{today.strftime('%Y_%m_%d')}"):
#     os.makedirs(path)

full_path = f"{audio_settings['target_path']}/{today.strftime('%Y_%m_%d')}/{today.strftime('%Y%m%d_%H%M%S')}.wav"

command = ["sudo", "arecord", "-D", audio_settings['device'], "-f", audio_settings['data_format'], "-r", audio_settings['sample_rate'], "-d", audio_settings['rec_interval'],
          full_path]

# Run the command
result = subprocess.run(command, capture_output=True, text=True)
print(result)

### Metadata collection ###
# Get the current date and time

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
    return current_time.strftime('%Y-%m-%dT%H:%M:%S%z')

# Obtain the daved latitude and longitude of the deployment
latitude = config["device_settings"]["lat"]
longitude = config["device_settings"]["lon"]

# Get current time in ISO 8601 format
current_time = get_current_time(latitude, longitude)

# obtain IDs
location_id = config["base_ids"]["location_id"]
system_id = config["base_ids"]["system_id"]
hardware_id = config["base_ids"]["hardware_id"]

# obtain survey period start and end time
start_time = config["audio_operation"]["start_time"]
end_time = config["audio_operation"]["end_time"]

# Note recording type
audio_type = "audible_microphone"

# Generate parent event ID
parent_event_id = f"{system_id}__{audio_type}__{start_time}__{end_time}"

# Obtain the number of files already within the directory
files = os.listdir(f"{audio_settings['target_path']}/{today.strftime('%Y_%m_%d')}")

# Filter the files to include only those with a .wav extension
wav_files = [file for file in files if file.endswith('.wav')]

# Get the number of .wav files
order_number = len(wav_files) + 1

# Generate event ID
eventID = f"{system_id}__{audio_type}__{current_time}__{order_number}"

#Save metadata as dictionary using same heirarchical structure as the config dictionary
metadata = {
     
     "audible_microphone_event_data":{
     
      "event_ids": {
         "parent_event_id": parent_event_id,
         "event_id": eventID
      },

    "date_fields": {
        "event_date": current_time,
        "recording_period_start_time": start_time,
        "recording_period_end_time": end_time
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
fields_ignore = ["ultrasonic_settings", "camera_settings", "motion_settings", "camera_operation", "ultrasonic_operation"]
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
with taglib.File(full_path, save_on_exit=True) as recording:

    recording.tags["TITLE"] = json.dumps(config)
    print("Metadata added to recording")

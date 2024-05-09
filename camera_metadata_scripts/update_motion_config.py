#!/usr/bin/env python3
#-*- coding: utf-8 -*-
import re
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

# Obtain the saved latitude and longitude of the deployment
latitude = config["device_settings"]["lat"]
longitude = config["device_settings"]["lon"]

# Get current time in ISO 8601 format
current_time = get_current_time(latitude, longitude)

# Find today date
date = current_time.strftime('%Y_%m_%d')

# Obtain IDs
location_id = config["base_ids"]["location_id"]
system_id = config["base_ids"]["system_id"]
hardware_id = config["base_ids"]["hardware_id"]

# Obtain survey period start and end time
start_time_str = config["camera_operation"]["start_time"]
end_time_str = config["camera_operation"]["end_time"]

# Note recording type
file_type = "camera"

# Generate parent event ID
parent_event_id = f"{system_id}__{file_type}__{start_time_str}__{end_time_str}"

# Extract the timezone into the desired format
timezone_str = current_time.strftime('%Y-%m-%d %H:%M:%S %z')[-5:].replace(':', '')

# Generate event ID with conversion specifiers
current_time_str = f'%Y-%m-%dT%H:%M:%S{timezone_str}'
eventID_insert = f"{system_id}__{file_type}__{current_time_str}"

# Obtain the date only and start and end time of the survey
current_date = current_time.date()
start_time = datetime.strptime(start_time_str, "%H:%M:%S").time()
end_time = datetime.strptime(end_time_str, "%H:%M:%S").time()

# Create strings to insert with conversion specifiers
start_datetime = datetime.combine(current_date, start_time, current_time.tzinfo)
end_datetime = datetime.combine(current_date, end_time, current_time.tzinfo) + timedelta(days=1)

start_datetime_str = start_datetime.strftime('%Y-%m-%dT%H:%M:%S%z')
end_datetime_str = end_datetime.strftime('%Y-%m-%dT%H:%M:%S%z')

#Save metadata as dictionary using same heirarchical structure as the config dictionary
metadata = {
     
     "motion_event_data":{
     
      "event_ids": {
         "parent_event_id": parent_event_id,
         "event_id": eventID_insert
      },

    "date_fields": {
        "event_date": current_time_str,
        "recording_period_start_time": start_datetime_str,
        "recording_period_end_time": end_datetime_str
        },

    "file_characteristics":{
         "file_path": None,
         "file_type": file_type
        }
   }

   }

# Update the config json
config.update(metadata)

# Ignore fields that will vary between surveying components
fields_ignore = ["ultrasonic_settings", "audio_settings", "audio_operation", "ultrasonic_operation"]
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

# Update camera and motion configuration and store metadata
def update_motion_config(script_path, config_data):
    with open(script_path, 'r') as script_file:
        script_lines = script_file.readlines()

    # For each line in the motion.config file
    for i, line in enumerate(script_lines):

        # Ignore lines starting with #
        if line.strip().startswith('#'):
            continue

        # List every motion configuration parameter and addionally specify the camera ID (videodevice) and exif_text (field for metadata storage)
        field_search = "exif_text"

        # Search for the occurence of the field name, followed by one or more whitespaces
        pattern = fr'({field_search} )(\S+)'
        match = re.search(pattern, line)

        if match:
            
            # Obtain the field name
            field,_ = line.split(' ', 1)

            # Stops the capture of field name mentions within the exif_text string
            # The exif_text field also includes a semicolon before the field name
            if field == field_search or field == f";{field_search}":

                # Ignore fields that will vary between surveying components
                fields_ignore = ["ultrasonic_operation", "ultrasonic_settings", "audio_operation", "audio_settings"]
                metadata =  dict((field, config_data[field]) for field in config_data if field not in fields_ignore)

                # Replace the whole line to remove the semicolon
                new_line = line.replace(line, f"exif_text \'{json.dumps(metadata)}\'\n")
                print(f"Updated exif metadata configuration") 
                script_lines[i] = new_line

                break

            else:
                continue

    # Write the updated script content back to the file
    with open(script_path, 'w') as script_file:
        script_file.writelines(script_lines)

# Replace with the actual path to your motion configuration file as needed
motion_script_path = "/etc/motion/motion.conf"

# Update motion settings in the shell script file
update_motion_config(motion_script_path, config)
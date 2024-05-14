#!/usr/bin/env python3
#-*- coding: utf-8 -*-

import json
from pathlib import Path
from datetime import datetime, timedelta
import os
import taglib

from utils.shared_functions import read_json_config, get_current_time, remove_comments, update_motion_config


if __name__ == "__main__":
    # Read the config file
    config_path = Path('/home/pi/config.json')

    # Read the JSON configuration file
    config = read_json_config(config_path)

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

    # Removing specific comments
    remove_comments(config)

    # Replace with the actual path to your motion configuration file as needed
    motion_script_path = "/etc/motion/motion.conf"

    # Update motion settings in the shell script file
    update_motion_config(motion_script_path, config)

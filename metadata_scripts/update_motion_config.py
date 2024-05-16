#!/usr/bin/env python3
#-*- coding: utf-8 -*-

from pathlib import Path
from datetime import datetime, timedelta

from utils.shared_functions import read_json_config, get_current_time, remove_comments, update_motion_config, custom_format_datetime

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

    # Obtain system ID
    system_id = config["base_ids"]["system_id"]

    # Obtain survey period start and end time
    start_time_str = config["camera_operation"]["start_time"]
    end_time_str = config["camera_operation"]["end_time"]

    # Note recording type
    file_type = "camera"

    # Extract the timezone into the desired format
    timezone_str = current_time.strftime('%z')

    # Generate event ID with conversion specifiers
    current_time_str = f'%Y-%m-%dT%H:%M:%S{timezone_str}'

    # Compile an event ID with conversion specifiers
    timezone_str_formatted = timezone_str.replace('+', '_plus_').replace('-', '_minus_')
    current_time_str_formatted = f'%Y_%m_%d__%H_%M_%S_{timezone_str_formatted}'
    eventID_insert = f"{system_id}__{file_type}__{current_time_str_formatted}"

    # Obtain the date only and start and end time of the survey
    current_date = current_time.date()
    start_time = datetime.strptime(start_time_str, "%H:%M:%S%z").time()
    end_time = datetime.strptime(end_time_str, "%H:%M:%S%z").time()

    # Create survey start and end datetimes
    start_datetime = datetime.combine(current_date, start_time, current_time.tzinfo)
    end_datetime = datetime.combine(current_date, end_time, current_time.tzinfo) + timedelta(days=1)

    # Convert survey start and end datetimes into a string
    start_datetime_str = start_datetime.strftime('%Y-%m-%dT%H:%M:%S%z')
    end_datetime_str = end_datetime.strftime('%Y-%m-%dT%H:%M:%S%z')

    #Compile a parent event id
    start_datetime_str_formatted = custom_format_datetime(start_datetime)
    end_datetime_str_formatted = custom_format_datetime(end_datetime)
    parent_event_id = f"{system_id}__{file_type}__{start_datetime_str_formatted}__{end_datetime_str_formatted}"

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

#!/usr/bin/env python3
#-*- coding: utf-8 -*-

from pathlib import Path
from datetime import datetime
import subprocess
import os
import taglib
import json

from utils.shared_functions import read_json_config, get_current_time, get_survey_start_end_datetimes, remove_comments, custom_format_datetime

if __name__ == "__main__":
    # Read the config file
    config_path = Path('/home/pi/config.json')

    # Read the JSON configuration file
    config = read_json_config(config_path)

    # Get the audio_settings settings from the config file
    audio_settings = config['audio_settings']

    # Obtain the daved latitude and longitude of the deployment
    latitude = config["device_settings"]["lat"]
    longitude = config["device_settings"]["lon"]

    # Get current time in ISO 8601 format
    current_time = get_current_time(latitude, longitude)

    # Find today date
    date = current_time.strftime('%Y_%m_%d')

    # Create folders if they don't exist
    Path(f"{audio_settings['target_path']}").mkdir(parents=True, exist_ok=True)
    Path(f"{audio_settings['target_path']}/{date}").mkdir(parents=True, exist_ok=True)

    # Generate the full path
    full_path = f"{audio_settings['target_path']}/{current_time.strftime('%Y_%m_%d')}/{current_time.strftime('%Y%m%d_%H%M%S')}.wav"

    # Prepare comand
    command = ["sudo", "arecord", "-D", audio_settings['device'], "-f", audio_settings['data_format'], "-r", audio_settings['sample_rate'], "-d", audio_settings['rec_interval'],
            full_path]

    # Record
    result = subprocess.run(command, capture_output=True, text=True)
    print(result)

    ### Metadata collection ###

    # obtain IDs
    system_id = config["base_ids"]["system_id"]

    # obtain survey period start and end time
    start_time_str = config["audio_operation"]["start_time"]
    end_time_str = config["audio_operation"]["end_time"]

    # Note recording type
    audio_type = "audible_microphone"

    # Generate event ID
    current_time_str = current_time.strftime('%Y-%m-%dT%H:%M:%S%z')
    current_time_str_formatted = custom_format_datetime(current_time)
    eventID = f"{system_id}__{audio_type}__{current_time_str_formatted}"

    # Calculate the survey period start and end time
    start_datetime, end_datetime = get_survey_start_end_datetimes(current_time, start_time_str, end_time_str)

    # convert start and end datetimes to strings
    start_datetime_str = start_datetime.strftime('%Y-%m-%dT%H:%M:%S%z')
    end_datetime_str = end_datetime.strftime('%Y-%m-%dT%H:%M:%S%z')

    # Generate parent event ID
    start_datetime_str_formatted = custom_format_datetime(start_datetime)
    end_datetime_str_formatted = custom_format_datetime(end_datetime)
    parent_event_id = f"{system_id}__{audio_type}__{start_datetime_str_formatted}__{end_datetime_str_formatted}"

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
    fields_ignore = ["ultrasonic_settings", "camera_settings", "motion_settings", "camera_operation", "ultrasonic_operation"]
    config = dict((field, config[field]) for field in config if field not in fields_ignore)

    # Filter comments
    keys_to_remove = [key for key in metadata if key == "COMMENT"]
    for key in keys_to_remove:
        del metadata[key]

    # Removing specific comments
    remove_comments(config)

    # Save within the audio file
    recording_file = taglib.File(full_path)
    recording_file.tags["TITLE"] = json.dumps(config)
    recording_file.save()
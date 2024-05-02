#!/usr/bin/env python3

"""Python script run by crontab at intervals within the targetted time for bird acoustic recording"""
 
__author__ = 'Grace Skinner'

# ===========================================================================================================================

### imports ###

from pathlib import Path # pathlib part of python standard library. Used to make new directories
import datetime # datetime part of python standard library. Used to get date and time 
import subprocess # Used to run bash arecord from python
#import birdconfig # Used to configure settings for bird recording. Access variables defined in birdconfig.py
import json # Used to configure settings for bird recording. Access variables defined in system_config.JSON

# To store metadata
import taglib
import os
from datetime import timedelta
import pytz
from timezonefinder import TimezoneFinder

# ===========================================================================================================================

### Import metadata variables including system configuration ###
with open("config.json", 'r') as file:
        json_config = json.load(file)

# ===========================================================================================================================

### Set up directory and file name/path ###

## Make directory to store files based on date

# Get date and time
date_and_time = datetime.datetime.now()

# Make directory path name (use directory specified by user as the one where they want the audio files to be stored)
# Match year_month_day format
path_to_file_storage = str(json_config["microphone"]["directory_saved"] + "%s_%s_%s" % (date_and_time.year, date_and_time.month, date_and_time.day)) # e.g. '/media/bird-pi/PiImages/BIRD/raw_audio/2023_2_8'
# Create directory with this name
Path(path_to_file_storage).mkdir(exist_ok=True) # If exists already, then doesn't throw an error

## Make name for file to store in this directory

# Match LID_x__SID_x__HID_x__year_month_day__hour_minute_second format
file_to_store = str(json_config["base_ids"]['location_id'] + "__" + json_config["base_ids"]['system_id'] + "__" + json_config["base_ids"]['hardware_id'] + "__%s_%s_%s__%s_%s_%s" % (date_and_time.year, date_and_time.month, date_and_time.day, date_and_time.hour, date_and_time.minute, date_and_time.second))

# Obtain the number of files already within the directory
files = os.listdir(path_to_file_storage)

# Filter the files to include only those with a .wav extension
wav_files = [file for file in files if file.endswith('.wav')]

# Get the number of .wav files
order_number = len(wav_files) + 1

## Combine directory and file names into 1 path
full_path = path_to_file_storage + "/" + file_to_store + "__order_" + str(order_number) + "." +  json_config["file extension"] # '/media/bird-pi/PiImages/BIRD/raw_audio/2023_2_8/LID_test__SID_test__HID_test__2023_2_8__17_42_7.wav'

# ===========================================================================================================================

### Recording ###

## Process arguments - Make list of arecord function and arguments used by arecord

# For reference:
# (Can change these settings using the system_config.JSON file)
# -D plughw:dodoMic,0 is the recording Device - this may need to be done in set-up of each AMI? Can't use card number as it occasionally changes (usually 1). 
# -c 1 is the number of channels, here 1
# -d 60 is the duration, here 60 seconds 
# -r 24000 is the sampling rate, here 24000Hz (needs to be at least double the highest frequency bird call we want to sample)
# -f S32_LE is the format, here S32_LE
# -t wav is the file type to save, here wav file
# -V mono is the type, here mono (could also be stereo)
# -v is verbose 
# full_path specifies the file path to save the file to (as defined above) 

# Arguments set at default
#proc_args = ['arecord', '-D', 'plughw:dodoMic,0', '-c', '1', '-d', '60', '-r', '24000', '-f', 'S32_LE', '-t', 'wav', '-V', 'mono', '-v', full_path]

# Arguments read in from the system_config.JSON file (which can be altered)
proc_args = ['arecord', '-D', json_config['microphone']['microphone_brand_name'], '-c', json_config['microphone']['number_of_channels'], '-d', json_config['microphone']["recording_duration"], '-r', json_config['microphone']['sampling_frequency'], '-f', json_config['microphone']['data_format'], '-t', json_config['microphone']["file_extension"], '-V', json_config['microphone']['recording_type'], '-v', full_path]

## Recording process - run the arecord function from Python
rec_proc = subprocess.Popen(proc_args)

# Verbose
# pid = process id
print("Start recording with arecord > rec_proc pid = " + str(rec_proc.pid))
print("Start recording with arecord > recording started")

# Make sure it waits for the recording to be complete before moving on
rec_proc.wait()

# Final verbose
print("Stop recording with arecord > Recording stopped") 

# ===========================================================================================================================

### Metadata collection ###
# Get the current date and time
current_date = datetime.datetime.now()

# Get the current UTC time
current_utc_time = datetime.datetime.utcnow()

# Calculate the hour difference
hour_difference = str((current_date - current_utc_time).total_seconds() / 3600)[:-2]
if len(hour_difference) == 1:
    hour_difference = "0" + hour_difference

# format the time
formatted_date = current_date.strftime("%Y-%m-%dT%H:%M:%S")

# Define a function that determines if deployment is in daylight saving time at the location and datetime
def is_dst(latitude, longitude, dt):
    # Get the timezone name for the given latitude and longitude
    timezone_finder = TimezoneFinder()
    timezone_name = timezone_finder.timezone_at(lat=latitude, lng=longitude)

    # Get the timezone object for the determined timezone name
    timezone = pytz.timezone(timezone_name)

    # Localize the datetime to the specified timezone
    localized_dt = timezone.localize(dt)

    # Check if the datetime is in daylight saving time
    return localized_dt.dst() != timedelta(0)

# Obtain the daved latitude and longitude of the deployment
latitude = json_config["location"]["lat"]
longitude = json_config["location"]["lon"]

# 1 if in daylight saving time, 0 if not
dst = is_dst(latitude, longitude, current_date)

# Define function to obtain file size
def get_file_size_kb(file_path):
    # Get the size of the file in bytes
    file_size_bytes = os.path.getsize(file_path)

    # Convert bytes to kilobytes
    file_size_kb = file_size_bytes / 1024

    return file_size_kb

#Obtain file size
file_size_kb = get_file_size_kb(full_path)

# obtain IDs
location_id = json_config["base_ids"]["location_id"]
system_id = json_config["base_ids"]["system_id"]
hardware_id = json_config["base_ids"]["hardwareid"]

# Note recording type
audio_type = "audible"

# Generate parent event ID
parentEventID = f"{system_id}__{audio_type}__start_time__end_time"

# Obtain datetime with underscore seperator
id_datetime = current_date.strftime("%Y_%m_%d__%H_%M_%S")

# Generate event ID
eventID = f"{system_id}__{audio_type}__{id_datetime}__{order_number}"

#Save metadata as dictionary using same heirarchical structure as the config dictionary
metadata = {
     
      "event_ids": {
         "parent_event_id": parentEventID,
         "event_id": eventID
      },

    "date_fields": {
        "event_date": f"{formatted_date}-{hour_difference}00",
        "daylight_saving_time": dst,
        "recording_period_start_time": None,
        "recording_period_end_time": None
        },

    "file_characteristics":{
         "file_size_kb": file_size_kb,
         "file_path": full_path,
         "file_type": audio_type
        }
   }

# Update the config dictionary
json_config["motion_event_data"].update(metadata)

# Ignore fields that will vary between surveying components
fields_ignore = ["operation", "motion_event_data"]
json_config = dict((field, json_config[field]) for field in json_config if field not in fields_ignore)

# Save within the audio file
with taglib.File(path_to_file_storage, save_on_exit=True) as recording:

    recording.tags["TITLE"] = json.dumps(metadata)
    print("Metadata added to recording")

# ## Additionally, create a json file with the same name as the file
# # Define the new file name with a JSON extension
# new_file_name = path_to_file_storage + "/" + file_to_store + "__order_" + order_number + ".json"

# # Define the subfolder name
# subfolder = "audio/json_scripts"

# # Create subfolder
# if not os.path.exists(subfolder):
#     os.makedirs(subfolder)

# # Create the new JSON file in the subfolder
# new_file_path = os.path.join(subfolder, os.path.basename(new_file_name))

# # Save metadata
# with open(new_file_path, 'w') as file:
#     json.dump(metadata, file, indent=4)
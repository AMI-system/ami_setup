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


# ===========================================================================================================================

### Import variables from config files ###

# Get variables from system config file 	
with open('/home/bird-pi/ami_setup/system_config.JSON') as system_config_file: 

	system_variables = json.load(system_config_file)

# ===========================================================================================================================

### Set up directory and file name/path ###

## Make directory to store files based on date

# Get date and time
date_and_time = datetime.datetime.now()

# Make directory path name (use directory specified by user as the one where they want the audio files to be stored)
# Match year_month_day format
path_to_file_storage = str(system_variables['birds']['directory_to_save_audio'] + "%s_%s_%s" % (date_and_time.year, date_and_time.month, date_and_time.day)) # e.g. '/media/bird-pi/PiImages/BIRD/raw_audio/2023_2_8'
# Create directory with this name
Path(path_to_file_storage).mkdir(exist_ok=True) # If exists already, then doesn't throw an error


## Make name for file to store in this directory

# Match LID_x__SID_x__HID_x__year_month_day__hour_minute_second format
file_to_store = str(system_variables['system']['LID'] + "__" + system_variables['system']['SID'] + "__" + system_variables['birds']['HID'] + "__%s_%s_%s__%s_%s_%s.wav" % (date_and_time.year, date_and_time.month, date_and_time.day, date_and_time.hour, date_and_time.minute, date_and_time.second))


## Combine directory and file names into 1 path
full_path = path_to_file_storage + "/" + file_to_store # '/media/bird-pi/PiImages/BIRD/raw_audio/2023_2_8/LID_test__SID_test__HID_test__2023_2_8__17_42_7.wav'

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
proc_args = ['arecord', '-D', system_variables['birds']['device_name'], '-c', system_variables['birds']['number_of_channels'], '-d', system_variables['birds']['duration'], '-r', system_variables['birds']['sampling_rate'], '-f', system_variables['birds']['data_format'], '-t', system_variables['birds']['file_type'], '-V', system_variables['birds']['recording_type'], '-v', full_path]

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




























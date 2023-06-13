#!/bin/bash

### Bash script run daily by crontab to analyse the raw audio using birdnet

# ===========================================================================================================================

# Define latitude and longitude - read in from system_config.JSON 
lat=$(jq '.location.lat' ../system_config.JSON)
lon=$(jq '.location.lon' ../system_config.JSON)

# Get yesterday's date (will analyse data collected the previous day)
yesterday=$(date -d "1 day ago" '+%Y_%-m_%-d') 

# make a new directory (named according to yesterday's date) 
sudo mkdir /media/bird-pi/PiImages/BIRD/analysed_audio/$yesterday # e.g. /media/bird-pi/PiImages/BIRD/analysed_audio/2023_04_04

# Run analyze.py from birdnet 
sudo python3 /home/bird-pi/BirdNET-Analyzer/analyze.py --i /media/bird-pi/PiImages/BIRD/raw_audio/$yesterday/ --o /media/bird-pi/PiImages/BIRD/analysed_audio/$yesterday/ --lat $lat --lon $lon --rtype 'r'

# ===========================================================================================================================



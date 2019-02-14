#!/usr/bin/env python3
#-*- coding: utf-8 -*-

#from utils.shared_functions import get_cellular_time
#from datetime import datetime

from datetime import datetime, timedelta
from periphery import I2C
import notecard
from notecard import card
import pytz

# from timezonefinder import TimezoneFinder
# import json
# import subprocess
# import re

# Use python-periphery on a Linux desktop or RPi
#from time import sleep

def main():
	try:
		i2c_path = "/dev/i2c-1"
		port = I2C(i2c_path)
		nCard = notecard.OpenI2C(port, 0, 0)
		timeout = 60
		got_time = False
		
		for iteration in range(timeout):
			response = card.time(nCard)
			time = response["time"]
			zone = response["zone"].split(",")[1]
			if zone != "Unknown":
				got_time = True
				utc_datetime = datetime.utcfromtimestamp(time)
				local_timezone = pytz.timezone(zone)
				local_datetime = utc_datetime.astimezone(local_timezone)
				local_datetime = local_datetime.strftime('%Y-%m-%d %H:%M:%S')
				break
				sleep(1)
			if not got_time:
				raise Exception("Failed to set local time of day via card time after 60 attempts")
			
		print(local_datetime)
				
	
	except Exception as e:
		print(f"Error: {e}")
		exit(1)
		
			

# def main():
    # try:
        # # current_datetime = get_cellular_time()
        # # print(current_datetime.strftime('%Y-%m-%d %H:%M:%S'))
	
        # # current_datetime = get_cellular_time().strftime('%Y-%m-%d %H:%M:%S')
		
        # #current_datetime_1 = "2024-09-18 17:02:29"
        # #current_datetime_1 = f"{current_datetime_1[:13]}:00:00"
        # #print(f"1: {current_datetime_1} (Type: {type(current_datetime_1)})")
        # #current_datetime_2 = get_cellular_time().strftime('%Y-%m-%d %H:%M:%S')
        # #current_datetime_2 = f"{current_datetime_2[:13]}:00:00"
        # #print(f"2: {current_datetime_2} (Type: {type(current_datetime_2)})")
        
        # # if current_datetime_1 == current_datetime_2:
            # # print("They match")
        # # else:
            # # print("They don't match")
		
        # #print(current_datetime_1)
        # #print(f"Type: {type(current_datetime)}")
        
        # #print(f"{current_datetime_2}")
        
        
        # # Configure I2C (connection between Notecard and RPi)
        # i2c_path = "/dev/i2c-1"
        # port = I2C(i2c_path)
        # # Connect to Notecard via I2C
        # nCard = notecard.OpenI2C(port, 0, 0)
		
        # #print("Wait for Notecard to acquire time of day")
        # timeout = 60
        # got_time = False
		
        # for iteration in range(timeout):
            # response = card.time(nCard)
            # time = response["time"]
            # #print(time)
            # zone = response["zone"].split(",")[1]
            # if zone != "Unknown":
                # got_time = True
                # utc_datetime = datetime.utcfromtimestamp(time)
                # utc_datetime = utc_datetime.replace(tzinfo=pytz.utc)
                # local_timezone = pytz.timezone(zone)
                # local_datetime = utc_datetime.astimezone(local_timezone)
                # local_datetime = local_datetime.strftime('%Y-%m-%d %H:%M:%S')
                # break
                # sleep(1)
            # if not got_time:
                # raise Exception("Failed to set local time of day via card time after 60 attempts")
            
            # print(local_datetime)
        
    # except Exception as e:
		# print(f"Error: {e}")
		# exit(1)

if __name__ == "__main__":
	main()

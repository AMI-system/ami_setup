#!/usr/bin/env python3
#-*- coding: utf-8 -*-


from crontab import CronTab
from functions import *
from datetime import datetime


def main():
	config = json_config('/home/pi/Documents/system_config.JSON') # Update to correct path

	sunrise, sunset = calculate_sunrise_and_sunset_times(config["location"]['lat'], 
														 config["location"]['lon'])
	# print(f"Sunset: {sunset.strftime('%H:%M:%S')}")
	# print(f"Sunrise: {sunrise.strftime('%H:%M:%S')}")

	# Determine times for motion activation and deactivation
	motion_start, motion_end = calculate_motion_times(sunset, 
													  sunrise, 
													  config["motion"]['start'], 
													  config["motion"]['end'])
	# print(f"Motion starts: {motion_start.strftime('%H:%M:%S')}")
	# print(f"Motion ends: {motion_end.strftime('%H:%M:%S')}")


	# Determine times for bird's sound recording
	start_sunrise, end_sunrise = calculate_birds_time(sunrise, 
													  config["birds"]['sunrise']['start'], 
													  config["birds"]['sunrise']['end'])
	start_sunset, end_sunset = calculate_birds_time(sunset, 
													config["birds"]['sunset']['start'], 
													config["birds"]['sunset']['end'])
	# print(f"Birds sunrise starts: {start_sunrise.strftime('%H:%M:%S')}")
	# print(f"Birds sunrise ends: {end_sunrise.strftime('%H:%M:%S')}")
	# print(f"Birds sunset starts: {start_sunset.strftime('%H:%M:%S')}")
	# print(f"Birds sunset ends: {end_sunset.strftime('%H:%M:%S')}")


	# Update contrab jobs
	ami_cron = CronTab(user='pi') 

	ami_cron = update_crontab_motion(ami_cron, 
									 motion_start, 
									 motion_end)
	
	### Test
	# start_sunrise = datetime(2023, 5, 31, 3, 26, 0)
	# end_sunrise = datetime(2023, 5, 31, 6, 12, 0)
	ami_cron = update_crontab_birds(ami_cron, 
									start_sunrise, 
									end_sunrise, 
									config["birds"]['interval'], 
									'morning')
	ami_cron = update_crontab_birds(ami_cron, 
									start_sunset, 
									end_sunset, 
									config["birds"]['interval'], 
									'evening')

	ami_cron.write()

if __name__ == "__main__":
    main()

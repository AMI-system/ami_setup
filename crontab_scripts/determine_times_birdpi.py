#!/usr/bin/env python3
#-*- coding: utf-8 -*-

from crontab import CronTab
from functions import *
from datetime import datetime


def main():
	config = json_config('/home/bird-pi/ami_setup/system_config.JSON') # Update to correct path

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
	# Calculate sunrise recording times if user wants to record around sunrise
	if config["birds"]['sunrise']['record'] == "yes":
		start_sunrise, end_sunrise = calculate_birds_time(sunrise, 
														  config["birds"]['sunrise']['start'], 
														  config["birds"]['sunrise']['end'])
	# Calculate sunset recording times if user wants to record around sunset											  
	if config["birds"]['sunset']['record'] == "yes":
		start_sunset, end_sunset = calculate_birds_time(sunset,
														config["birds"]['sunset']['start'], 
														config["birds"]['sunset']['end'])
	# print(f"Birds sunrise starts: {start_sunrise.strftime('%H:%M:%S')}")
	# print(f"Birds sunrise ends: {end_sunrise.strftime('%H:%M:%S')}")
	# print(f"Birds sunset starts: {start_sunset.strftime('%H:%M:%S')}")
	# print(f"Birds sunset ends: {end_sunset.strftime('%H:%M:%S')}")
	

	# Check if the sunrise and sunset schedules overlap in the nighttime 
	if config["birds"]['sunrise']['record'] == "yes" and config["birds"]['sunset']['record'] == "yes": # If user is recording around both sunrise and sunset
		
		# Need to add 1 day to the sunrise schedule so the sunrise schedule always happens the day after the sunset one (only way to correctly test whether there is overlap)
		start_sunrise_day_before = start_sunrise + timedelta(days=1)
		end_sunrise_day_before = end_sunrise + timedelta(days=1)
		
		# print("Schedule before changes:", start_sunset, "-", end_sunset, "and", start_sunrise_day_before, "-", end_sunrise_day_before) 
		
		if start_sunrise_day_before < end_sunset: # i.e. if the sunrise schedule starts before the sunset one finishes
			# print("Overlap in night")
			end_sunset = start_sunrise_day_before - timedelta(minutes=1) # There is overlap so make the sunset schedule finish the minute before the sunrise one begins 
			# print("Schedule after changes: ", start_sunset, "-", end_sunset, "and", start_sunrise_day_before, "-", end_sunrise_day_before) 

	
	# Repeat to check if the sunrise and sunset schedules overlap in the daytime	
	if config["birds"]['sunrise']['record'] == "yes" and config["birds"]['sunset']['record'] == "yes":
		
		# No need to add day this time as if they overlap in the daytime, it will be on the same day 
		
		# print("Schedule before changes:", start_sunset, "-", end_sunset, "and", start_sunrise, "-", end_sunrise) 
		
		if start_sunset < end_sunrise: # i.e. if the sunset schedule starts before the sunrise one finishes
			# print("Overlap in day")
			end_sunrise = start_sunset - timedelta(minutes=1) # There is overlap so make the sunrise schedule finish the minute before the sunset one begins 
			# print("Schedule after changes: ", start_sunset, "-", end_sunset, "and", start_sunrise, "-", end_sunrise) 



	# Update contrab jobs                                                                                                                                                                          
	ami_cron = CronTab(user='bird-pi') 
	
	# Moth/motion jobs
	ami_cron = update_crontab_motion(ami_cron, 
									 motion_start, 
									 motion_end)
	
	# Bird jobs
	### Test
	# start_sunrise = datetime(2023, 5, 31, 3, 26, 0)
	# end_sunrise = datetime(2023, 5, 31, 6, 12, 0)
	
	# sunrise
	if config["birds"]['sunrise']['record'] == "yes":
		ami_cron = update_crontab_birds(ami_cron, 
										start_sunrise, 
										end_sunrise, 
										config["birds"]['interval'], 
										'morning')
	else:
		delete_job_birds(ami_cron, "morning") # delete all morning jobs
	
	# sunset
	if config["birds"]['sunset']['record'] == "yes":
		ami_cron = update_crontab_birds(ami_cron, 
										start_sunset, 
										end_sunset, 
										config["birds"]['interval'], 
										'evening')
	else:
		delete_job_birds(ami_cron, "evening") # delete all evening jobs 

	ami_cron.write()

if __name__ == "__main__":
    main()

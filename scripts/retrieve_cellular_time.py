#!/usr/bin/env python3
#-*- coding: utf-8 -*-

from datetime import datetime, timedelta
from periphery import I2C
import notecard
from notecard import card
import pytz
from time import sleep
import sys

# def main():
	# i2c_path = "/dev/i2c-1"
	# port = I2C(i2c_path)
	# nCard = notecard.OpenI2C(port, 0, 0)
	# timeout = 300
	# got_time = False
	
	# for iteration in range(timeout):
		# try:
			# #print(f"Attempt {iteration+1}:")
			# response = card.time(nCard) # Get time from modem if finished booting and established cellular connectivity
			# #print(response)
			# #print(x)
			# if "time" in response and "err" not in response: # Check if modem returned a time
				# time = response["time"]
				# #print(time)
				# if "zone" in response and len(response["zone"].split(",")) > 0: # Check if modem returned a timezone
					# zone = response["zone"].split(",")[1] # Extract timezone
					# if zone != "Unknown": # check timezone is valid
						# got_time = True
						# utc_datetime = datetime.utcfromtimestamp(time)
						# local_timezone = pytz.timezone(zone)
						# local_datetime = utc_datetime.astimezone(local_timezone)
						# local_datetime = local_datetime.strftime('%Y-%m-%d %H:%M:%S')
						# print(local_datetime)
						# break
			# else:
				# raise Exception("Retrieving time did not work")
		# except Exception as e:
			# #print(f"Attempt {iteration+1} failed with error: {e}. Retrying in 1 second...")
			# sleep(1)
	
	# else: # If the for loop runs without success (i.e. break never initiated)
		# print("All attempts failed")
		# raise Exception(f"Failed to set local time of day via card time after {iteration+1} attempts")
		

# def main():
	# i2c_path = "/dev/i2c-1"
	# port = I2C(i2c_path)
	# nCard = notecard.OpenI2C(port, 0, 0)
	# timeout = 300
	# got_time = False
	
	# for iteration in range(timeout):
		# try:
			# #print(f"Attempt {iteration+1}:")
			# response = card.time(nCard) # Get time from modem if finished booting and established cellular connectivity
			# #print(response)
			# #print(x)
			# if "time" in response and "err" not in response: # Check if modem returned a time
				# time = response["time"]
				# #print(time)
				# if "zone" in response and len(response["zone"].split(",")) > 0: # Check if modem returned a timezone
					# zone = response["zone"].split(",")[1] # Extract timezone
					# #print(zone)
					# if zone != "Unknown": # check timezone is valid
						# got_time = True
						# datetime_time = datetime.fromtimestamp(time)
						# print(datetime_time)
						# # local_timezone = pytz.timezone(zone)
						# # print(local_timezone)
						# # local_datetime = utc_datetime.astimezone(local_timezone)
						# # print(local_datetime)
						# # local_datetime = local_datetime.strftime('%Y-%m-%d %H:%M:%S')
						# # print(local_datetime)
						# break
			# else:
				# raise Exception("Retrieving time did not work")
		# except Exception as e:
			# #print(f"Attempt {iteration+1} failed with error: {e}. Retrying in 1 second...")
			# sleep(1)
	
	# else: # If the for loop runs without success (i.e. break never initiated)
		# print("All attempts failed")
		# raise Exception(f"Failed to set local time of day via card time after {iteration+1} attempts")

# def main():
	# i2c_path = "/dev/i2c-1"
	# port = I2C(i2c_path)
	# nCard = notecard.OpenI2C(port, 0, 0)
	# timeout = 1800
	# got_time = False
	
	# for iteration in range(timeout):
		# try:
			# #print(f"Attempt {iteration+1}:")
			# response = card.time(nCard) # Get time from modem if finished booting and established cellular connectivity
			# #print(response)
			# #print(x)
			# if "time" in response and "err" not in response: # Check if modem returned a time
				# time = response["time"]
				# #print(time)
				# if "zone" in response and len(response["zone"].split(",")) > 0: # Check if modem returned a timezone
					# zone = response["zone"].split(",")[1] # Extract timezone
					# #print(zone)
					# if zone != "Unknown": # check timezone is valid
						# got_time = True
						# datetime_time = datetime.fromtimestamp(time)
						# print(datetime_time)
						# # local_timezone = pytz.timezone(zone)
						# # print(local_timezone)
						# # local_datetime = utc_datetime.astimezone(local_timezone)
						# # print(local_datetime)
						# # local_datetime = local_datetime.strftime('%Y-%m-%d %H:%M:%S')
						# # print(local_datetime)
						# break
			# else:
				# raise Exception("Retrieving time did not work")
		# except Exception as e:
			# #print(f"Attempt {iteration+1} failed with error: {e}. Retrying in 1 second...")
			# sleep(1)
	
	# else: # If the for loop runs without success (i.e. break never initiated)
		# print("All attempts failed")
		# raise Exception(f"Failed to set local time of day via card time after {iteration+1} attempts")
		
def main():
	i2c_path = "/dev/i2c-1"
	port = I2C(i2c_path)
	nCard = notecard.OpenI2C(port, 0, 0)
	timeout = 604800 # Max total wait time is 7 days = 604800 seconds
	start_time = datetime.now()
	got_time = False
	
	while True:
		# Calculate elapsed time in seconds
		elapsed_time = (datetime.now() - start_time).total_seconds()
		
		# Determine the wait time if fails to retrieve time
		if elapsed_time <= 60: # for the first minute: retry every second
			wait_time = 1
		elif elapsed_time <= 3600: # for the next hour: retry every minute
			wait_time = 60
		elif elapsed_time <= 86400: # for the next day: retry every hour
			wait_time = 3600
		elif elapsed_time <= 604800: # for the next week: retry every day
			wait_time = 86400
		else:
			print("All attempts failed. Failed to set local time of day via card time after 7 days.")
			sys.exit(1) # exit if timeout exceeded
		
		try:
			#print(f"Attempt {iteration+1}:")
			response = card.time(nCard) # Get time from modem if finished booting and established cellular connectivity
			#print(response)
			#print(x)
			if "time" in response and "err" not in response: # Check if modem returned a time
				time = response["time"]
				#print(time)
				if "zone" in response and len(response["zone"].split(",")) > 0: # Check if modem returned a timezone
					zone = response["zone"].split(",")[1] # Extract timezone
					#print(zone)
					if zone != "Unknown": # check timezone is valid
						got_time = True
						datetime_time = datetime.fromtimestamp(time)
						print(datetime_time)
						# local_timezone = pytz.timezone(zone)
						# print(local_timezone)
						# local_datetime = utc_datetime.astimezone(local_timezone)
						# print(local_datetime)
						# local_datetime = local_datetime.strftime('%Y-%m-%d %H:%M:%S')
						# print(local_datetime)
						break
			else:
				raise Exception("Retrieving time did not work")
		except Exception as e:
			#print(f"Attempt failed with error: {e}. Retrying in {wait_time} seconds...")
			sleep(wait_time)

if __name__ == "__main__":
	main()

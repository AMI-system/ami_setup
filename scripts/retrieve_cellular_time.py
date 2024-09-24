#!/usr/bin/env python3
#-*- coding: utf-8 -*-

from datetime import datetime, timedelta
from periphery import I2C
import notecard
from notecard import card
import pytz
from time import sleep

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

def main():
	i2c_path = "/dev/i2c-1"
	port = I2C(i2c_path)
	nCard = notecard.OpenI2C(port, 0, 0)
	timeout = 1800
	got_time = False
	
	for iteration in range(timeout):
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
			#print(f"Attempt {iteration+1} failed with error: {e}. Retrying in 1 second...")
			sleep(1)
	
	else: # If the for loop runs without success (i.e. break never initiated)
		print("All attempts failed")
		raise Exception(f"Failed to set local time of day via card time after {iteration+1} attempts")

if __name__ == "__main__":
	main()

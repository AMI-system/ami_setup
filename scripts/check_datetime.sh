#!/bin/bash

# Get system time
system_time=$(sudo date +%s)
echo "$system_time"

# Cutoff datetime
cutoff_datetime="2020-01-01 00:00"
echo "$cutoff_datetime"
cutoff_datetime=$(date -d "$cutoff_datetime" +%s)
echo "$cutoff_datetime"

# Compare system to cutoff
if [[ "$system_time" -lt "$cutoff_datetime" ]]; then
	echo "System datetime ($system_time) is before cutoff datetime ($cutoff_datetime)."
	echo "Setting system time via cellular"

	# Create temporary schedule to keep system on for the next 7 days
	# sudo python3 /home/pi/scripts/set_temp_schedule.py
	
	# Retrieve time from cellular
	current_datetime=$(sudo python3 /home/pi/scripts/retrieve_cellular_time.py)
	if [ $? -eq 0 ]; then
		echo "Python script succeeded"
		echo "$current_datetime"
		echo "I have just printed the current datetime"
		
		# Set datetime from cellular
		sudo date -s "${current_datetime}"
		echo "I have just set the date from cellular"
	
		# What about setting rtc time after this??
		expect <<EOF
spawn sudo /home/pi/wittypi/wittyPi.sh
expect "What do you want to do? (1~13)"
send "1\r"
expect "What do you want to do? (1~13)"
send "13\r"
expect eof
EOF
	else
		echo "Python script failed"
		exit 1
	fi

	# Calculate sunrise and sunset times
	# sudo python3 /home/pi/scripts/determine_sunrise_sunset_times.py

	# Calculate the weekly schedule
	# sudo python3 /home/pi/scripts/wpi_script_generator_ags.py

	# Calculate moths recording schedule and set in crontab
	# sudo python3 /home/pi/scripts/moths_schedule.py

	# Calculate birds recording schedule and set in crontab
	# sudo python3 /home/pi/scripts/birds_schedule.py

	# Calculate bats recording schedule and set in crontab
	# sudo python3 /home/pi/scripts/bats_schedule.py
	
else
	echo "System datetime ($system_time) is after cutoff datetime ($cutoff_datetime)." 
	echo "No change required."
fi




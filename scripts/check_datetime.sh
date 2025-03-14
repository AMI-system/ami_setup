#!/bin/bash

# Get system time
system_time=$(sudo date +%s)
echo "$system_time"

# Cutoff datetime
cutoff_datetime="2024-01-01 00:00"
echo "$cutoff_datetime"
cutoff_datetime=$(date -d "$cutoff_datetime" +%s)
echo "$cutoff_datetime"

## Set up to check if the current time is within the current schedule. If not, the schedule is likely out-of-date and needs re-generating. 
# Path to schedule file
schedule_file="/home/pi/wittypi/schedule.wpi"
# Initialise variables for the start and end time of the schedule
schedule_start=""
schedule_end=""
# Extract start and end time from schedule.wpi (given the schedule.wpi file exists)
if [[ -f "$schedule_file" ]]; then
	schedule_start=$(grep -m1 "BEGIN" "$schedule_file" | awk '{print $2, $3}')
	schedule_end=$(grep -m1 "END" "$schedule_file" | awk '{print $2, $3}')
fi
# Convert extracted schedule start and end times (in format YYYY-MM-DD HH:MM:SS) to timestamps (number of seconds since Jan 1, 1970)
if [[ -n "$schedule_start" && -n "$schedule_end" ]]; then # If schedule start and end as non-empty 
	schedule_start_timestamp=$(date -d "$schedule_start" +%s)
	schedule_end_timestamp=$(date -d "$schedule_end" +%s)
	echo "Schedule start: $schedule_start ($schedule_start_timestamp)"
	echo "Schedule end: $schedule_end ($schedule_end_timestamp)"
else
	echo "Error: Could not read schedule start and end times"
	schedule_start_timestamp=0
	schedule_end_timestamp=0
fi
	 

# Compare system to cutoff
if [[ "$system_time" -lt "$cutoff_datetime" ]]; then
	echo "System datetime ($system_time) is before cutoff datetime ($cutoff_datetime)."

	# Create temporary schedule to keep system on for the next 7 days
	echo "Setting temporary schedule to keep Pi on for next 7 days while it attempts to reset time"
	sudo python3 /home/pi/scripts/set_temp_schedule.py
	
	# Retrieve time from cellular
	echo "Setting system time via cellular"
	current_datetime=$(sudo python3 /home/pi/scripts/retrieve_cellular_time.py)
	if [ $? -eq 0 ]; then
		echo "Python script to retieve time from cellular succeeded"
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
	echo "Calculating sunrise and sunset times"
	sudo python3 /home/pi/scripts/determine_sunrise_sunset_times.py

	# Calculate the weekly schedule
	echo "Calculate the weekly schedule"
	sudo python3 /home/pi/scripts/wpi_script_generator_ags.py

	# Calculate moths recording schedule and set in crontab
	echo "Calculate moth recording schedule and set in crontab"
	sudo python3 /home/pi/scripts/moths_schedule.py

	# Calculate birds recording schedule and set in crontab
	echo "Calculate birds recording schedule and set in crontab"
	sudo python3 /home/pi/scripts/birds_schedule.py

	# Calculate bats recording schedule and set in crontab
	echo "Calculate bats recording schedule and set in crontab"
	sudo python3 /home/pi/scripts/bats_schedule.py
	
elif [[ "$system_time" -lt "$schedule_start_timestamp" || "$system_time" -gt "$schedule_end_timestamp" ]]; then # Else if the system time is outside of the schedule
	echo "Time is correct but current time is outside of the schedule. Regenerating the schedule."
	
	# Calculate sunrise and sunset times
	echo "Calculating sunrise and sunset times"
	sudo python3 /home/pi/scripts/determine_sunrise_sunset_times.py

	# Calculate the weekly schedule
	echo "Calculate the weekly schedule"
	sudo python3 /home/pi/scripts/wpi_script_generator_ags.py

	# Calculate moths recording schedule and set in crontab
	echo "Calculate moth recording schedule and set in crontab"
	sudo python3 /home/pi/scripts/moths_schedule.py

	# Calculate birds recording schedule and set in crontab
	echo "Calculate birds recording schedule and set in crontab"
	sudo python3 /home/pi/scripts/birds_schedule.py

	# Calculate bats recording schedule and set in crontab
	echo "Calculate bats recording schedule and set in crontab"
	sudo python3 /home/pi/scripts/bats_schedule.py	
	
else
	echo "System datetime ($system_time) is after cutoff datetime ($cutoff_datetime)." 
	echo "No time change required."
	echo "System datetime is within the current schedule"
	echo "No need to reset schedule."

	# Caluclate sunrise and sunset times
	echo "Calculating sunrise and sunset times"
	sudo python3 /home/pi/scripts/determine_sunrise_sunset_times.py

	# Don't calculate weekly schedule as time is good and schedule is still up-to-date

	# Update moths recording schedule and set in crontab
	echo "Calculate moth recording schedule and set in crontab"
	sudo python3 /home/pi/scripts/moths_schedule.py

	# Update birds recording schedule and set in crontab
	echo "Calculate birds recording schedule and set in crontab"
	sudo python3 /home/pi/scripts/birds_schedule.py

	# Update bats recording schedule and set in crontab
	echo "Calculate bats recording schedule and set in crontab"
	sudo python3 /home/pi/scripts/bats_schedule.py

fi

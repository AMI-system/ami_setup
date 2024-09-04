#!/bin/bash

# Get system time
system_time=$(sudo date +%s)
echo $system_time

# Cutoff datetime
cutoff_datetime="2020-01-01 00:00"
cutoff_datetime=$(date -d "$cutoff_datetime" +%s)
echo $cutoff_datetime

# Compare system to cutoff
if [[ "$system_time" -lt "$cutoff_datetime" ]]; then
	echo "System datetime ($system_time) is before cutoff datetime ($cutoff_datetime)."
	echo "Setting system time via cellular"
	
	# Retrieve time from cellular
	current_datetime=$(python3 /home/pi/scripts/retrieve_cellular_time.py)
	#echo "${current_datetime%+*}"
	
	# Set datetime from cellular
	sudo date -s "${current_datetime%+*}"
	
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
	echo "System datetime ($system_time) is after cutoff datetime ($cutoff_datetime)." 
	echo "No change required."
fi


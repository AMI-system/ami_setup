#!/usr/bin/env python

from crontab import CronTab

ami_cron = CronTab(user='crontab') 

timer_job = ami_cron.new(command='python3 /home/pi/scripts/determine_times.py ', comment='timer')
timer_job.every_reboot()

motion_on_job = ami_cron.new(command='sudo motion', comment='motion on')
motion_on_job.hour.on(21)

motion_off_job = ami_cron.new(command='sudo pkill motion', comment='motion off')
motion_off_job.hour.on(6)

bird_morning_job = ami_cron.new(command='python3 /home/pi/scripts/birds_script.py', comment='birds morning schedule')
bird_morning_job.hour.on(6)

bird_evening_job = ami_cron.new(command='python3 /home/pi/scripts/birds_script.py', comment='birds evening schedule')
bird_evening_job.hour.on(21)

ami_cron.write()


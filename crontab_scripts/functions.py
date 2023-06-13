#!/usr/bin/env python3
#-*- coding: utf-8 -*-

from suntime import Sun, SunTimeException
import json
from pathlib import Path
from datetime import datetime, timedelta, date


def json_config(config_file):
    """
    Returns a JSON object with the config file content. 

    Parameters
    ----------
    config_file : str
        Full path to the config file. 

    Returns
    -------
    json
        JSON file containing the config information. 

    """
    config_path = Path(config_file)
    with config_path.open() as fp:
        return json.load(fp)

def calculate_sunrise_and_sunset_times(lat, lon):
    """
    Returns sunrise and sunset time based on your location and current date. 

    Parameters
    ----------
    lat : float
        Latitude coordinate of your location. 
    lon : float
        Longitude coordinate of your location. 

    Returns
    -------
    sunrise_time : datetime
        Sunrise time based on your location and current date. 
    sunset_time : datetime
        Sunset time based on your location and current date. 
    """
    today = date.today()

    sun = Sun(lat, lon)
    sunrise_time = sun.get_local_sunrise_time(today)
    sunset_time = sun.get_local_sunset_time(today)
    
    return sunrise_time, sunset_time

def calculate_motion_times(sunset, sunrise, config_start, config_end):
    """
    Determines what time the motion software has to start running and what time to stop. 

    Parameters
    ----------
    sunset : datetime
        Sunset time based on your location and current date. 
    sunrise : datetime
        Sunrise time based on your location and current date. 
    config_start : time
        How much time before sunset to start. 
    config_end : time
        How much time before sunrise to end. 

    Returns
    -------
    start : datetime
        Exact time to start running the job. 
    end : datetime
        Exact time to stop running the job. 
    """
    time_start = datetime.strptime(config_start, '%H::%M::%S').time()
    start = sunset - timedelta(hours=time_start.hour, minutes=time_start.minute) # changed from plus to minus

    time_end = datetime.strptime(config_end, '%H::%M::%S').time()
    end = sunrise + timedelta(hours=time_end.hour, minutes=time_end.minute) # changed from minus to plus

    return start, end

def calculate_birds_time(ref_time, config_start, config_end):
    """
    Determines what times the microphone will record bird's sound. 

    Parameters
    ----------
    ref_time : datetime
        Sunrise or sunset time based on your location and current date. 
    config_start : time
        How much time before sunset to start. 
    config_end : time
        How much time before sunrise to end. 

    Returns
    -------
    start : datetime
        Exact time to start running the job. 
    end : datetime
        Exact time to stop running the job. 
    """
    time_start = datetime.strptime(config_start, '%H::%M::%S').time()
    start = ref_time - timedelta(hours=time_start.hour, minutes=time_start.minute) 
    
    time_end = datetime.strptime(config_end, '%H::%M::%S').time()
    end = ref_time + timedelta(hours=time_end.hour, minutes=time_end.minute) 

    return start, end
    
    
def update_crontab_motion(ami_cron, motion_start, motion_end):
    """
    Update the crontab schedule for the motion software. 

    Parameters
    ----------
    ami_cron : crontab.CronTab
        Crontab object to be updated. 
    motion_start : datetime
        Exact time to start the motion software. 
    motion_end : time
        Exact time to end the motion software. 

    Returns
    -------
    ami_cron : crontab.CronTab
        Crontab object with the correct times. 
    """
    for job in ami_cron:
        if job.comment == 'motion on':
            job.hour.on(motion_start.hour)
            job.minute.on(motion_start.minute)        
            
        elif job.comment == 'motion off':
            job.hour.on(motion_end.hour)
            job.minute.on(motion_end.minute)
    return ami_cron
    
def create_cron_job(ami_cron, command, comment): # just for birds
    """
    Update the crontab schedule for the motion software. 

    Parameters
    ----------
    ami_cron : crontab.CronTab
        Crontab object to be updated. 
    command : str
        Command line to be execute.
    comment : str
        Comment associate with the cron job. 

    Returns
    -------
    job : crontab.CronItem
        New crontab job item
    """
    job = ami_cron.new(command=command, comment=comment)
    return job

def schedule_cron_job(job, start_minute, end_minute, interval, start_hour, end_hour):
    """
    Update the crontab schedule for the motion software. 

    Parameters
    ----------
    job : crontab.CronItem
        Crontab item to be defined. 
    start_minute : int
        Integer minute where the job has to start from.
    end_minute : int
        Integer minute where the job has to finish at.
    interval : int
        Frequency in minutes to run the job. 
    start_hour : int
        Integer hour where the job has to start from.
    end_hour : int
        Integer hour where the job has to finish at.
     
    Returns
    -------
    job_schedule : str
        String containing the schedueling information for that job.
    """
    job_schedule = '{start_minute}-{end_minute}/{interval} {hour_start}-{hour_end} * * *'.format(start_minute=start_minute, end_minute=end_minute, interval=interval, hour_start=start_hour, hour_end=end_hour)
    return job_schedule

def update_crontab_birds(ami_cron, start_time, end_time, interval, day_time):
    """
    Update the crontab schedule for the birds. 

    Parameters
    ----------
    ami_cron : crontab.CronTab
        Crontab object to be updated. 
    start_time : datetime
        Exact time to start the sound recording. 
    end_time : time
        Exact time to end the sound recording. 
    interval : int
        Every how many minutes to record sound.
    day_time : str
        Which time of the day, valid options 'morning' and 'evening'.

    Returns
    -------
    ami_cron : crontab.CronTab
        Crontab object with the correct times. 
    """
    # Delete the old cron jobs 
    for job in ami_cron:
        if 'birds {day_time}'.format(day_time=day_time) in job.comment:
            ami_cron.remove(job)
    
    comment = 'birds {day_time} {num}'.format(day_time=day_time, num=1)
    command = 'python3 /home/bird-pi/ami_setup/bird_scripts/birdRecording.py'
    
    num_hours = end_time.hour - start_time.hour
    # e.g. from 3:15am to 3:55am
    if num_hours == 0:
        job = create_cron_job(ami_cron, command, comment)
        job_schedule = schedule_cron_job(job, start_time.minute, end_time.minute, interval, start_time.hour, start_time.hour)
        job.setall(job_schedule)
    # e.g. from 3:00am to 5:00am
    elif start_time.minute == 0 and end_time.minute == 0:
        job = create_cron_job(ami_cron, command, comment)
        job_schedule = schedule_cron_job(job, 0, 59, interval, start_time.hour, end_time.hour)
        job.setall(job_schedule)
    # e.g. from 3:13am to 5:27am
    else:       
        minutes_left = start_time.minute
        for i in range(num_hours+1):
            comment = 'birds {day_time} {num}'.format(day_time=day_time, num=i+1)
            #rest_minutes = (60 - minutes_left) % 5 ### Will this 5 need to be changed to 'interval'????? # Using the 60 bit was causing the 5am hour to be weird 
            rest_minutes = minutes_left % 5
            # from 3:13am to 4:00am
            if i == 0:
                job = create_cron_job(ami_cron, command, comment)
                job_schedule = schedule_cron_job(job, start_time.minute, 59, interval, start_time.hour, start_time.hour)
                job.setall(job_schedule)
            # from 4:00am to 5:00
            elif start_time.hour+i == end_time.hour and end_time.minute != 0:
                job = create_cron_job(ami_cron, command, comment)
                job_schedule = schedule_cron_job(job, rest_minutes, end_time.minute, interval, end_time.hour, end_time.hour)
                job.setall(job_schedule)
            elif start_time.hour+i == end_time.hour :
                break
            # from 5:00am to 5:27
            else:
                job = create_cron_job(ami_cron, command, comment)
                job_schedule = schedule_cron_job(job, rest_minutes, 59, interval, start_time.hour+i, start_time.hour+i)
                job.setall(job_schedule)
            #minutes_left = (60 - minutes_left) % 5 ### Will this 5 need to be changed to 'interval'????? # Using the 60 bit was causing the 5am hour to be weird 
            minutes_left = minutes_left % 5
			
    return ami_cron

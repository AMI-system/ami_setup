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
        How much time after sunset to start. 
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
    start = sunset + timedelta(hours=time_start.hour, minutes=time_start.minute) 

    time_end = datetime.strptime(config_end, '%H::%M::%S').time()
    end = sunrise - timedelta(hours=time_end.hour, minutes=time_end.minute) 

    return start, end

def calculate_birds_time(ref_time, config_start, config_end):
    """
    Determines what times the microphone will record bird's sound. 

    Parameters
    ----------
    ref_time : datetime
        Sunrise or sunset time based on your location and current date. 
    config_start : time
        How much time before sunrise/set to start. 
    config_end : time
        How much time before sunrise/set to end. 

    Returns
    -------
    start : datetime
        Exact time to start running the job. 
    end : datetime
        Exact time to stop running the job. 
    """
    time_start = datetime.strptime(config_start, '%H::%M').time() # Just do hours and minutes as cron can't schedule based on seconds 
    start = ref_time - timedelta(hours=time_start.hour, minutes=time_start.minute) 
    
    time_end = datetime.strptime(config_end, '%H::%M').time()
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
    Update the crontab schedule for the motion/birds software when interval is needed. 

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
        String containing the scheduling information for that job.
    """
    job_schedule = '{start_minute}-{end_minute}/{interval} {hour_start}-{hour_end} * * *'.format(start_minute=start_minute, end_minute=end_minute, interval=interval, hour_start=start_hour, hour_end=end_hour)
    return job_schedule

    
def schedule_cron_job_no_interval(job, start_minute, end_minute, start_hour, end_hour):
    """
    Update the crontab schedule for the motion/bird software when an interval is not needed. 

    Parameters
    ----------
    job : crontab.CronItem
        Crontab item to be defined. 
    start_minute : int
        Integer minute where the job has to start from.
    end_minute : int
        Integer minute where the job has to finish at.
    start_hour : int
        Integer hour where the job has to start from.
    end_hour : int
        Integer hour where the job has to finish at.
     
    Returns
    -------
    job_schedule : str
        String containing the scheduling information for that job.
    """
    job_schedule = '{start_minute}-{end_minute} {hour_start}-{hour_end} * * *'.format(start_minute=start_minute, end_minute=end_minute, hour_start=start_hour, hour_end=end_hour)
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
    
    # calculate number of recording hours
    if start_time.hour < end_time.hour: # e.g. 02:00-04:00 or 21:00-23:00
        num_hours = end_time.hour - start_time.hour
    else: # e.g. 23:00-04:00 or 23:00-01:00
        num_hours = end_time.hour - start_time.hour + 24
    # create cronjobs for each recording hour
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
        first_minute = start_time.minute # first_minute is the first minute in the hour to record at 
        for i in range(num_hours+1):
            comment = 'birds {day_time} {num}'.format(day_time=day_time, num=i+1)
            # from 3:13am to 4:00am
            if i == 0: # first job
                job = create_cron_job(ami_cron, command, comment)
                if start_time.minute != 59: # add catch here to see if need cronjob with or without interval - only need interval if start and end minute are different 
                    job_schedule = schedule_cron_job(job, start_time.minute, 59, interval, start_time.hour, start_time.hour)
                    job.setall(job_schedule)
                else:
                    job_schedule = schedule_cron_job_no_interval(job, start_time.minute, 59, start_time.hour, start_time.hour)
                    job.setall(job_schedule)
            # from 4:00am to 5:00  
            elif (start_time.hour+i == end_time.hour and end_time.minute != 0) or (start_time.hour+i > 23 and start_time.hour+i-24 == end_time.hour and end_time.minute != 0): # last job # 2nd statement (below) deals with schedules that cross midnight
                if (end_time.minute >= first_minute): # will catch scenarios where end_time.minute is less than first minute - can't do cronjob with 4-2 as the minutes. In these cases, no need to make last job. 
                    job = create_cron_job(ami_cron, command, comment)                
                    if first_minute != end_time.minute: # add catch here to see if need cronjob with or without interval - only need interval if first_minute and end_time.minute are different
                         job_schedule = schedule_cron_job(job, first_minute, end_time.minute, interval, end_time.hour, end_time.hour)
                         job.setall(job_schedule)
                    else:
                        job_schedule = schedule_cron_job_no_interval(job, first_minute, end_time.minute, end_time.hour, end_time.hour)
                        job.setall(job_schedule)  						
            elif (start_time.hour+i == end_time.hour) or (start_time.hour+i > 23 and start_time.hour+i-24 == end_time.hour): # don't need to make a last job # 2nd elseif statement deals with schedules that cross midnight		 
                break
            # from 5:00am to 5:27
            else: # middle jobs 
                # make sure hour is not greater than 23, and adjust if it is
                start_hour = start_time.hour+i
                if start_time.hour+i > 23:
                    start_hour = start_time.hour+i-24				
                job = create_cron_job(ami_cron, command, comment)
                job_schedule = schedule_cron_job(job, first_minute, 59, interval, start_hour, start_hour)
                job.setall(job_schedule)
            # calculate new first minute for next hour
            mins_diff = 60 - first_minute
            if mins_diff % interval == 0: # does the minutes difference divide wholly into the interval (i.e. no remainder)
                first_minute = 0 # if so, the first minute in the next hour will be on the hour e.g. 06:00
            else:
                first_minute = interval - (mins_diff % interval) # else, need to calculate what the first minute in the next hour will be e.g. 06:03	
				
			
    return ami_cron
    
def delete_job_birds(ami_cron, day_time):
    """
    Delete the morning and/or evening jobs if user does not wish to record around sunrise and/or sunset for the birds. 

    Parameters
    ----------
    ami_cron : crontab.CronTab
        Crontab object to be updated. 
    day_time : str
        Which time of the day, valid options 'morning' and 'evening'.

    Returns
    -------
    None
        No explicit return. 
    """
    # Delete
    for job in ami_cron:
        if 'birds {day_time}'.format(day_time=day_time) in job.comment:
            ami_cron.remove(job)
    
 
    return None

         

		
    

    
    
    
    
    
    
    
    
    
    
    
    

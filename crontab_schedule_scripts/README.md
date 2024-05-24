# Crontab and scheduling scripts

- **crontab_example.txt**  
This is a copy of the content of the file into a txt. In the Pi the crontab can be checked using this command ```crontab -l``` or modified using this command ```crontab -e```  

<br/>

- **determine_sunrise_sunset_times.py**  
  In the Pi it can be found in this path: ```/home/pi/scripts/determine_sunrise_sunset_times.py```

  1. Read the config file to get the latitude and the longitude coordinates.  
  2. Calulates the today’s sunset time and tomorrow’s sunrise time by sending the coordinates to the function “get_sunset_sunrise_times”.  
  3. Update the parameters for sunset and sunrise time in the config file.  

<br/>

- **moths_scheduling.py**  
  In the Pi it can be found in this path: ```/home/pi/scripts/moths_scheduling.py```  

  1. Read the config file to get the sunset and sunrise times.  
  2. Access the user crontab and delete any jobs related to motion.  
  3. Define the start job which will start the motion software, update the camera settings, and switch on the lights.  
  4. Set the cron job times, it will run at today’s sunset (exact minute and hour) on Mon, Wed, Fri (1,3,5).  
  5. Define the end job which will stop the motion and switch off the lights.
  6. Set the cron job times, it will run at tomorrow’s sunrise (exact minute, but hour – 1) on Tue, Thu, Sat (2,4,6).  
  7. Finally, it saves the job in the crontab.  

<br/>

- **bats_scheduling.py**  
  In the Pi it can be found in this path: ```/home/pi/scripts/bats_scheduling.py```  

  1. Read the config file to get the sunset and sunrise times and the ultrasonic settings.  
  2. Check if the target folder from the ultrasonic settings exists in the SSD hard drive and create it if not.  
  3. Send the coordinates to the function “get_sunset_sunrise_times” to get today’s sunset time and tomorrow’s sunrise time.  
  4. Access the user crontab and delete any jobs related to bats recording.  
  5. Defines the job which will run the recording script.  
  6. Avoid overlap with the bids recording:  
      1. Check if the remainder of dividing the sunset minute by 5 is 0, add 2 minutes.  
      2. Check if the remainder of dividing the sunset minute by 5 is 1, add 1 minute.
  7. There are two different sets of times:  
      1. From today’s sunset until 11:59 pm running on Mon, Tue, Thu and Sat (1,2,4,6).
          1. The first job will run every 5 minutes from sunset exact time until complete the hour.  
          **Note:** the file checks if the minute is a multiple of 5. If so, to prevent the script to run at the same time as the bird's recording, 2 minuts are added.  
          1. Then it checks if the sunset time hour plus 1 hour is equal or smaller than 23 to define an extra job until midnight.  
      2. From tomorrow’s midnight until sunrise time running on Wed, Fri and Sun (2,3,5,0).  
          1. First, it checks if the sunrise hour is 0 (midnight) and if the sunrise minute is bigger than the starting minute to create the job.  
          2. Otherwise, it checks if the sunrise hour is 1, and then it creates a job for the midnight hour first. And then it checks if the sunrise minute is bigger than the starting minute to create an extra job.  
          3. Finally, if none of the above, checks if the sunrise hour is bigger than 1, then it creates a job from midnight to the sunrise hour minus one. And then it checks if the sunrise minute is bigger than the starting minute to create an extra job for the sunrise hour.  
  7. Finally, it saves the job in the crontab.  

<br/>

- **birds_scheduling.py**  
  In the Pi it can be found in this path: ```/home/pi/scripts/birds_scheduling.py```

  1. At the moment, this script gets the audio settings from the config file.  
  2. Check if the target folder exists and create it if not.  
  3. Access the user crontab and delete any jobs related to bird recording.  
  4. Defines the job which will the recording script.  
  5. Creates two sets of times:  
      1. Record an audio file every 5 minutes from 12 to 23 hours on Tue, Thu and Sat (2,4,6).  
      2. Record an audio file every 5 minutes from 0 to 11:59 hours on Wed, Fri and Sun (3,5,0).  
  6. In the future, it will need to look similar to the bats scheduling file.  

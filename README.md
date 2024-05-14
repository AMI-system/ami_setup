# AMI configuration files for AgZero+ (Season 2024)

Summary of the recording hours that we have agreed on:

1. **Moth images + lights**: Mon, Wed, and Fri from Sunset to Sunrise-1h.
2. **Bird's audio**: Tue, Thu, and Sat from 12 pm to 11:59 am the next day (24h).
3. **Bat's ultrasonic**: Mon, Tue, Thu, and Sat from Sunset to Sunrise.

## WittyPi

The WittyPi will determine when the system will be on and off. According to the recording times above it will operate like the table below:

| Day of the week   | OFF      | ON     |
| :---------------- | :------: | -----: |
| Monday            |          | Sunset |
| Tuesday           | Sunrise  | 12 pm  |
| Wednesday         | 11:59 am | Sunset |
| Thursday          | Sunrise  | 12 pm  |
| Friday            | 11:59 am | Sunset |
| Saturday          | Sunrise  | 12 pm  |
| Sunday            | 11:59 am |        |

When the Pi starts the WittyPi will run 3 different Python scripts that will create cron jobs for the recordings.

- **wittypi/afterStartup.sh**  
  In the Pi it can be found in this path: ```/home/pi/wittypi/afterStartup.sh```
  
  File that the WittyPi runs every time it switches ON the system. At the moment, it starts the telemetry and runs the scripts to determine the recording times.

- **wpi_script_generator.py**  
  In the pi t can be found in this path: ```/home/pi/scripts/wpi_script_generator.py```

  This scripts generates every week the scheduling for the Raspberry Pi to switch on and off based on the recording times we defined. 

## Config file

- **config.json**  
  In the Pi it can be found in this path: ```/home/pi/config.json```

## Utils files

- **shared_functions.py**  
  In the Pi it can be found in this path: ```/home/pi/scritps/utils/shared_functions.py```

  This scripts contains all the functions that the recording and schedueling files need to run.

## Schedueling and recording files

- **crontab_scripts/moths_scheduling.py**  
  In the Pi it can be found in this path: ```/home/pi/scripts/moths_scheduling.py```

  1. Read the config file to get the latitude and the longitude coordinates.
  2. Send the coordinates to the function “get_sunset_sunrise_times” to get today’s sunset time and tomorrow’s sunrise time.
  3. Access the user crontab and delete any jobs related to motion.
  4. Define the start job which will start the motion software, update the camera settings, and switch on the lights.
  5. Set the cron job times, it will run at today’s sunset (exact minute and hour) on Mon, Wed, Frid (1,3,5).
  6. Define the end job which will stop the motion and switch off the lights.
  7. Set the cron job times, it will run at tomorrow’s sunrise (exact minute, but hour – 1) on Tue, Thu, Sat (2,4,6).
  8. Finally, it saves the job in the crontab.

- **crontab_scripts/bats_scheduling.py**  
  In the Pi it can be found in this path: ```/home/pi/scripts/bats_scheduling.py```

  1. Read the config file to get the latitude and the longitude coordinates and the ultrasonic settings.
  2. Check if the target folder from the ultrasonic settings exists in the SSD hard drive and create it if not.
  3. Send the coordinates to the function “get_sunset_sunrise_times” to get today’s sunset time and tomorrow’s sunrise time.
  4. Access the user crontab and delete any jobs related to bats recording.
  5. Defines the job which will run the recording script.
  6. There are two different sets of times:
    1. From today’s sunset until 11:59 pm running on Mon, Tue, Thu and Sat (1,2,4,6).
        1. The first job will run every 5 minutes from sunset exact time until complete the hour.  
          **Note:** the file checks if the minute is a multiple of 5. If so, to prevent the script to run at the same time as the bird's recording, 2 minuts are added.  
        2. Then it checks if the sunset time hour plus 1 hour is equal or smaller than 23 to define an extra job until midnight.
    2. From tomorrow’s midnight until sunrise time running on Wed, Fri and Sun (2,3,5,0).
        1. First, it checks if the sunrise hour is 0 (midnight) and if the sunrise minute is bigger than the starting minute to create the job.
        2. Otherwise, it checks if the sunrise hour is 1, and then it creates a job for the midnight hour first. And then it checks if the sunrise minute is bigger than the starting minute to create an extra job.
        3. Finally, if none of the above, checks if the sunrise hour is bigger than 1, then it creates a job from midnight to the sunrise hour minus one. And then it checks if the sunrise minute is bigger than the starting minute to create an extra job for the sunrise hour.
  7. Finally, it saves the job in the crontab.

- **crontab_scripts/birds_scheduling.py**  
  In the Pi it can be found in this path: ```/home/pi/scripts/birds_scheduling.py```

  1. At the moment, this script gets the audio settings from the config file.
  2. Check if the target folder exists and create it if not.
  3. Access the user crontab and delete any jobs related to bird recording.
  4. Defines the job which will the recording script.
  5. Creates two sets of times:
    1. Record an audio file every 5 minutes from 12 to 23 hours on Mon, Wed and Fri (1,3,5).
    2. Record an audio file every 5 minutes from 0 to 11:59 hours on Tue, Thu and Sat (2,4,6).
  6. In the future, it will need to look similar to the bats scheduling file.

- **bird_scripts/birds_recording.py** and **bat_scripts/bats_recording.py**  
  In the Pi they can be found in these paths: ```/home/pi/scripts/birds_recording.py``` and ```/home/pi/scripts/bats_recording.py```
  
  Both files have the same structure:
  1. Read the config file to get audio/ultrasonic settings. Check if the target folder from the audio/ultrasonic settings exists in the SSD hard drive and create it if not.
  2. Define the ```arecord``` command and run it.

## Motion files
- **motion.conf**  
  In the Pi it can be found in this path: ```/etc/motion/motion.conf.json```

  This file has been modified in order to save the images in the correct path for the new developments. 

- **control_ON_lights.py** and **control_OFF_light.py**  
  In the Pi they can be found in these paths: 
  ```/home/pi/scripts/control_ON_lights.py``` and 
  ```/home/pi/scripts/control_OFF_light.py```

  These files control all the lights, the LepiLED and the LEDs strip around the camera.  

## SSD folder structure

New folder structure in the SSD hard drive to save the audio and image files.

Example:
```
PiImages
│
└───images
│   │
│   └───2024_04_24
│       │   image1.jpeg
│       │   image2.jpeg
│       │   ...
│   
└───audio
│   │
│   └───2024_04_24
│       │   audio1.wav
│       │   audio2.wav
│       │   ...
│   
└───ultrasonic
│   │
│   └───2024_04_24
│       │   ultrasonic1.wav
│       │   ultrasonic2.wav
│       │   ...
```
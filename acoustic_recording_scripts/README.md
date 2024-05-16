# Acoustic recording files

- **birds_recording.py** and **bats_recording.py**  
  In the Pi they can be found in these paths: ```/home/pi/scripts/birds_recording.py``` and ```/home/pi/scripts/bats_recording.py```
  
  1. Read the config file to get audio/ultrasonic settings.  
  2. Check if the target folder from the audio/ultrasonic settings exists in the SSD hard drive and create it if not.  
  3. Define the ```arecord``` command and run it.  
  4. Once the acoustic file is being save it write the corresponding metadata on it.  

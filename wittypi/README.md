# WittyPi scritps

- **afterStartup.sh**  
  In the Pi it can be found in this path: ```/home/pi/wittypi/afterStartup.sh```  
  
  File that the WittyPi runs every time it switches ON the system. At the moment, it starts the telemetry and runs the scripts to determine the recording times.  

</br>

- **beforeShutdown.sh**  
  In the Pi it can be found in this path: ```/home/pi/wittypi/beforeShutdown.sh```  
  
  File that the WittyPi runs every time it switches OFF the system. At the moment, it stops the motion and turn OFF the lights.  

</br>

- **wpi_script_generator_ags.py**  
  In the pi t can be found in this path: ```/home/pi/scripts/wpi_script_generator_ags.py```  

  This script runs every Sunday and generates the weekly schedule for the Raspberry Pi to switch on and off based on the recording times we define.  
  
# AMI configuration files for AgZero+ (Season 2024)

Summary of the recording hours that we have agreed on:

1. **Moth images + lights**: Mon, Wed, and Fri from Sunset to Sunrise-1h.
2. **Bird's audio**: Tue, Thu, and Sat from 12 pm to 11:59 am the next day (24h).
3. **Bat's ultrasonic**: Mon, Tue, Thu, and Sat from Sunset to Sunrise.

According to the recording times above it will operate like the table below:

| Day of the week   | OFF       | ON       |
| :---------------: | :------:  | :------: |
| Monday            |           |  Sunset  |
| Tuesday           | Sunrise   |  12 pm   |
| Wednesday         | 11:59 am  |  Sunset  |
| Thursday          | Sunrise-1h|  12 pm   |
| Friday            | 11:59 am  |  Sunset  |
| Saturday          | Sunrise-1h|  12 pm   |
| Sunday            | 11:59 am  |          |

The ON and OFF times are control by the WittyPi refer to the ```wittypi``` folder for more details.

## SSD folder structure

Folder structure in the SSD hard drive to save the audio and image files.

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

## Files

- **config.json**  
  In the Pi it can be found in this path: ```/home/pi/config.json```  

<br/>

- **rc.local.txt**  
  This is a copy of the content of the file into a txt. In the Pi the original file can be found in this path: ```/etc/rc.local```  

  This is an example on how the rc.local file looks. It is responsible for running the bluetooth connection.  

For more especific information about motion, recording acoustics and scheduling refer to each folder.  

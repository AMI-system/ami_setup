# ami_setup (cellular)

Publish information from an Ami-System with a cellular connection to the cloud.

*Author: Jonas Beuchert (UKCEH)*

*Date: March 2024*

## Table of Contents

- [Hardware setup](#hardware-setup)
- [Software setup](#software-setup)
    - [Setup via install script](#setup-via-install-script)
    - [Manual setup](#manual-setup)
- [File structure](#file-structure)
- [Remotely sending and receiving data](#remotely-sending-and-receiving-data)
    - [Web app (work in progress)](#web-app-work-in-progress)
    - [Blues notehub](#blues-notehub)
    - [Command interface](#command-interface)
- [Function listing for `amitrap_cellular.py`](#function-listing-for-amitrap_cellularpy)
- [Notes](#notes)

## Hardware setup

* Get a [Blues Notecard](https://blues.com/products/notecard/) and a [Blues Notecarrier Pi](https://blues.com/products/notecarrier/notecarrier-pi/).
* Remove the screw from the Notecarrier.
* Insert the Notecard into the slot on the Notecarrier.
* Secure it with the screw.
* Connect the antenna to the `MAIN` socket on the Notecard.
* Ensure that all swicthes on the back of the Notecarrier are in the `off` position.
* Stack the Notecarrier on the Raspberry Pi or Rock Pi pin header.

## Software setup

Clone/copy this repository to your Ami-System. (In exisiting Ami-System images, it can be found in `home/pi/ami_setup-cellular-dev`).

Open the file `amitrap_cellular.py` and replace the string `todo:replace-with-your-product-uid` with the desired product UID.
Ask [@JonasBchrt](https://github.com/JonasBchrt) if unsure.

### Setup via install script

Run:
```bash
sudo ./install.sh
```

After installation, reboot:

```bash
sudo reboot
```

[🪳Troubleshooting](#troubleshooting)

If there is a cellular connection available, then the information from the Ami-Trap should now be pushed to the cloud every 6 h.
You can change this interval in `ami-trap-raspi-cellular.py` in `__main__` using the `interval_minutes` parameter.
The synchronisation mode of the Notecard can be configured in the `cellular_configure` function in `amitrap_cellular.py`.
You can find the available modes [here](https://dev.blues.io/notecard/notecard-walkthrough/essential-requests/#configuring-synchronization-modes).

If you do not want to push data every 6 h, open `/etc/rc.local` and remove the respective line.

If you only want to send data from the Ami-System once, run
```bash
python3 ami-trap-raspi-cellular-send.py
```

If you want to send data from the Ami-System once and receive data from the server once, run
```bash
python3 ami-trap-raspi-cellular-send_and_receive.py
```

You can add these to the `afterStartup.sh` and `beforeShutdown.sh` WittyPi scripts, for example.

Please note that this is (currently) not a stand-alone Ami-System setup.
It only adds cellular connecivity to an existing setup.

### Troubleshooting

If installation does not work, then you may need to make the script executable first:
```bash
sudo chmod +x install.sh
```

If installation does not work and a `bad interpreter` error occurs, try to remove `CR` characters from the file first:
```bash
sudo sed -i -e 's/\r$//' install.sh
```

If no data is pushed automatically, check your `/etc/rc.local` file. It should conatain a line that invokes the cellular service and all preceding lines should be terminated with an `&`.

### Manual setup

Install Python dependencies:
```bash
sudo python3 -m pip install python_periphery-2.4.1-py2.py3-none-any.whl
sudo python3 -m pip install filelock-3.12.2-py3-none-any.whl
sudo python3 -m pip install note_python-1.5.0-py3-none-any.whl
```

Set the cloud project to which data is published:
```bash
sudo python3 ami-trap-raspi-cellular-config.py
```

## File structure

* `_version.py`: Just contains the version number of the software as a string that can be imported as variable `__version__` into other Python scripts.
* `ami-trap-raspi-cellular-config.py`: One-time configuration script.
* `ami-trap-raspi-cellular.py`: Entrypoint for the cellular connectivity service. Should be run at start-up with root privileges if sending and receiving data is required regularly.
* `ami-trap-raspi-cellular-send.py`: Alternative entrypoint for cellular connectivity. Run to send data once.
* `ami-trap-raspi-cellular-sned_and_receive.py`: Alternative entrypoint for cellular connectivity. Run to send and receive data once.
* `amitrap_cellular.py`: Collection of cellular connectivity routines for the Ami-System.
* `amitrap.py`: A class for interacting with the Raspberry-Pi or Rock-Pi based Ami-System.
* `python_periphery-2.4.1-py2.py3-none-any.whl`: Python package `python-periphery`, which is required. Downloaded from [here](https://pypi.org/project/python-periphery).
* `filelock-3.12.2-py3-none-any.whl`: Python package `filelock`, which is required.
* `note_python-1.5.0-py3-none-any.whl`: Python package `note-python`, which is required.Downloaded from [here](https://pypi.org/project/note-python).
* `install.sh`: Install bash script.

## Remotely sending and receiving data

### Web app (work in progress)

You can use https://jonasbchrt.github.io/ami-trap-app-cellular-js/ to send and receive data.
Enter the passkey at the top (ask [@JonasBchrt](https://github.com/JonasBchrt) if unsure) and click on *Show dashboard* to get some information about all AMIs that were online during the past seven days.

### Blues notehub

Log in to the [blues notehub](https://notehub.io) and got to the relevant project. Ask [@JonasBchrt](https://github.com/JonasBchrt) if unsure or you do not have access.

Below an overview of the notehub interface:

* **Devices**: See a list of all cellular-equipped Ami-Systems, the projects they belong to (AMBER, AgZero+, ...), the last time they were online, and the tower they last connected to. Use the *Usage* tab to see consumed and remaining data volume. Each Ami-System comes with 500 MB in total. Use the *Events* button to see the most recent messages from a selected Ami-System. Use the *Note* button to send commands to the Ami-System. (See [command interface](#command-interface).)

* **Fleets**: See all Ami-Systems belonging to a specific project (AMBER, AgZero+, ...). Otherwise, identically to the *Devices* tab.

* **Events**: See a list of all messages from all Ami-Systems in the past seven days. Filter the *file* attribute to show only *data.qo* to see only status messages.

* **Firmware**: Upload firmware for firmware updates over-the-air. Apply the update in the *Devices* tab. I ([@JonasBchrt](https://github.com/JonasBchrt)) decided that the firmware must be a `.zip` file with a script named `install.sh` in its top-level directory. All installation steps must be done by this script. Please throughly test any firmware before sending it out, including a complete install over-the-air on a dummy system. In addition, please keep the file size small.

### Command interface

The following JSON *Notes* are recognised by the Ami-System:

* `{"type": "camera", "data": your_camera_config_json}`: Set the camera configuration to the JSON provided using the same convention as the Ami-System Bluetooth app. If successful, the `output` string `"Camera configuration updated."` is returned.

* `{"type": "command", "data": "your_shell_command"}`: Evaluate the provided shell command(s) and returns the output as `output` string. (Hint: Shell commands allow you to do a lot of things. Wanna know what the WittyPi is doing? `printf '13' | /home/pi/wittypi/wittyPi.sh` does the job. But it's also easy to break things...)

* `{"type": "reboot"}`: Reboot the Rapsberry Pi.

* `{"type": "shutdown"}`: Shutdown the Rapsberry Pi.

* `{"type": "time"}`: Get the current time and timezone from the cellular internet and sets the OS time. (And the WittyPi RTC time, if possible.)

* `{"type": "bluetooth", "data": true}`: Enable Bluetooth.

* `{"type": "bluetooth", "data": false}`: Disable Bluetooth.

## Function listing for `amitrap_cellular.py`

### `cellular_configure(i2c_path="/dev/i2c-1")`

    Configure cellular connectivity via Notecard and Notehub.
    
    Only needs to run once for each Notecard.
    (Except if you want to change the configuration.)
    Sets the synchronization mode and interval.
    Assigns the Notecard to a Notehub project to define where the data goes on the server.

### `cellular_send(output=None, i2c_path="/dev/i2c-1")`
    
    Send status data from Ami-Trap to Notehub.

### `cellular_receive(i2c_path="/dev/i2c-1")`
    
    Receive data from Notehub and return output string.

### `cellular_send_picture(i2c_path="/dev/i2c-1")`
    
    Send most recent picture from Ami-Trap to Notehub.
    
    Compress image such that it fits into 8 KB.
    (According to https://discuss.blues.com/t/encode-and-send-a-small-image/475
    8 KB are safe.)

## Notes

Tested on AMBER 2023, AgZero+ 2023, and WittyPi 2024 images.

Find more details [here](https://github.com/JonasBchrt/ami-trap-raspi-cellular/blob/main/README.md).

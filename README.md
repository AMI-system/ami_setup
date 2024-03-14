# ami_setup (cellular)

Publish information from an Ami-System with a cellular connection to the cloud.

*Author: Jonas Beuchert (UKCEH)*

*Date: March 2024*

## Hardware setup

* Get a [Blues Notecard](https://blues.com/products/notecard/) and a [Blues Notecarrier Pi](https://blues.com/products/notecarrier/notecarrier-pi/).
* Remove the screw from the Notecarrier.
* Insert the Notecard into the slot on the Notecarrier.
* Secure it with the screw.
* Connect the antenna to the `MAIN` socket on the Notecard.
* Ensure that all swicthes on the back of the Notecarrier are in the `off` position.
* Stack the Notecarrier on the Raspberry Pi or Rock Pi pin header.

## Software setup

 Clone/copy this repository to your Ami-System.

 Open the file `amitrap_cellular.py` and replace the string `todo:replace-with-your-product-uid` with the desired product UID.
 Ask [@JonasBchrt](https://github.com/JonasBchrt) if unsure.

Run:
```bash
sudo ./install.sh
```

After installation, reboot:

```bash
sudo reboot
```

[🪳Troubleshooting](#troubleshooting)

If there is a cellular connection available, then the information from the Ami-Trap should now be pushed to the cloud every 120 min.
You can change this interval in `ami-trap-raspi-cellular.py` in `__main__` using the `interval_minutes` parameter.
The synchronisation mode of the Notecard can be configured in the `cellular_configure` function in `amitrap_cellular.py`.
You can find the available modes [here](https://dev.blues.io/notecard/notecard-walkthrough/essential-requests/#configuring-synchronization-modes).

If you do not want to push data every 120 min, open `/etc/rc.local` and remove the respective line.

If you only want to send data once, run
```bash
python3 ami-trap-raspi-cellular-send.py
```

If you want to send and receive data once, run
```bash
python3 ami-trap-raspi-cellular-send_and_receive.py
```

You can add these to the `afterStartup.sh` and `beforeShutdown.sh` scripts, for example.

Please note that this is (currently) not a stand-alone Ami-System setup.
It only adds cellular connecivity to an existing setup.

## Troubleshooting

If installation does not work, then you may need to make the script executable first:
```bash
sudo chmod +x install.sh
```

If installation does not work and a `bad interpreter` error occurs, try to remove `CR` characters from the file first:
```bash
sudo sed -i -e 's/\r$//' install.sh
```

If no data is pushed automatically, check your `/etc/rc.local` file. It should conatain a line that invokes the cellular service and all preceding lines should be terminated with an `&`.

## File structure

* `_version.py`: Just contains the version number of the software as a string that can be imported as variable `__version__` into other Python scripts.
* `ami-trap-raspi-cellular-config.py`: One-time configuration script.
* `ami-trap-raspi-cellular.py`: Entrypoint for the cellular connectivity service. Should be run at start-up with root privileges.
* `amitrap_cellular.py`: Collection of cellular connectivity routines for the Ami-System.
* `amitrap.py`: A class for interacting with the Raspberry-Pi or Rock-Pi based Ami-System.
* `python_periphery-2.4.1-py2.py3-none-any.whl`: Python package `python-periphery`, which is required. Downloaded from [here](https://pypi.org/project/python-periphery).
* `filelock-3.12.2-py3-none-any.whl`: Python package `filelock`, which is required.
* `note_python-1.5.0-py3-none-any.whl`: Python package `note-python`, which is required.Downloaded from [here](https://pypi.org/project/note-python).
* `install.sh`: Install bash script.

## Function lisiting for `amitrap_cellular.py`

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

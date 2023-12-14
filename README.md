# ami_setup (Bluetooth for Rock Pi)

*Author: Jonas Beuchert (UKCEH)*

*Date: December 2023*

To setup Bluetooth connectivity for your Rock-Pi-based Ami-Trap, clone/copy this repository and run:

```bash
sudo ./install.sh
```

If this doesn't work, you may need to make the script executable first:
```bash
sudo chmod +x install.sh
```

Then, reboot:

```bash
sudo reboot
```

Please note that this is (currently) not a stand-alone Ami setup.
It only adds Bluetooth connecivity to an existing setup.

Find more details [here](https://github.com/JonasBchrt/ami-trap-raspi-cellular/blob/main/README.md).

File structure:
* `_version.py`: Just contains the version number of the software as a string that can be imported as variable `__version__` into other Python scripts.
* `ami-trap-rockpi-bluetooth.py`: Entrypoint for the Bluetooth service. Should be run at start-up with root privileges.
* `amitrap_bluetooth.py`: Collection of Bluetooth routines for the Ami-trap.
* `amitrap.py`: A class for interacting with the Raspberry-Pi or Rock-Pi based Ami-Trap.
* `install.sh`: Install bash script.

Tested on the image `RockImg070823` with `bluez_peripheral` 0.1.7 and `dbus_next` 0.2.3.

# ami_setup (Bluetooth)

*Author: Jonas Beuchert (UKCEH)*

*Date: December 2023*

To setup Bluetooth connectivity for your Ami-Trap, clone/copy this repository to your Ami-Trap and run:

```bash
sudo ./install.sh
```

If this doesn't work, you may need to make the script executable first:
```bash
sudo chmod +x install.sh
```

After installation, reboot:

```bash
sudo reboot
```

Please note that this is (currently) not a stand-alone Ami setup.
It only adds Bluetooth connecivity to an existing setup.

Find more details [here](https://github.com/JonasBchrt/ami-trap-raspi-cellular/blob/main/README.md).

File structure:
* `_version.py`: Just contains the version number of the software as a string that can be importet as variable `__version__` into other Python scripts.
* `ami-trap-raspi-bluetooth.py`: Entrypoint for the Bluetooth service. Should be run at start-up with root privileges.
* `amitrap_bluetooth.py`: Collection of Bluetooth routines for the Ami-trap.
* `amitrap.py`: A class for interacting with the Raspberry-Pi or Rock-Pi based Ami-Trap.
* `bluez_peripheral-0.1.7-py3-none-any.whl`: Python package `bluez-peripheral`, which is required. Downloaded from [here](https://pypi.org/project/bluez-peripheral).
* `install.sh`: Install bash script.

Tested on the image `rasp-pi-amber-20231013`.

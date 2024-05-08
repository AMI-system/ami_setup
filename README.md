# ami_setup (Bluetooth)

*Author: Jonas Beuchert (UKCEH)*

*Date: December 2023*

To setup Bluetooth connectivity for your Ami-System, clone/copy this repository to your Ami-System and run:

```bash
sudo ./full-install.sh
```

If this doesn't work, you may need to make the script executable first:
```bash
sudo chmod +x full-install.sh
```

After installation, reboot:

```bash
sudo reboot
```

Now, you should be able to connect to your Ami-System via [the app](https://jonasbchrt.github.io/ami-trap-app-bluetooth/).

Find more details [here](https://github.com/JonasBchrt/ami-trap-raspi-cellular/blob/main/README.md).

Please note that this is (currently) not a stand-alone Ami-System setup.
It only adds Bluetooth connecivity to an existing setup.

For adding Bluetooth to a Rock-Pi-based system, see [here](https://github.com/AMI-trap/ami_setup/tree/bluetooth-rockpi).

File structure:
* `_version.py`: Just contains the version number of the software as a string that can be importet as variable `__version__` into other Python scripts.
* `ami-trap-raspi-bluetooth.py`: Entrypoint for the Bluetooth service. Should be run at start-up with root privileges.
* `amitrap_bluetooth.py`: Collection of Bluetooth routines for the Ami-System.
* `amitrap.py`: A class for interacting with the Raspberry-Pi or Rock-Pi based Ami-System.
* `bluez_peripheral-0.1.7-py3-none-any.whl`: Python package `bluez-peripheral`, which is required. Downloaded from [here](https://pypi.org/project/bluez-peripheral).
* `dbus_next-0.2.3-py3-none-any.whl`: Python package `python-dbus-next`, which is required. Downloaded from [here](https://pypi.org/project/dbus-next).
* `full-install.sh`: Install bash script.
* `install.sh`: Update bash script.

Tested on the image `rasp-pi-amber-20231013`.

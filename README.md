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

 Clone/copy this repository to your Ami-System and run:

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

If there is a cellular connection available, then the information from the Ami-Trap should now be pushed to the cloud every 120 min.
You can change this interval in `ami-trap-raspi-cellular.py` in `__main__` using the `interval_minutes` parameter.
The synchronisation mode of the Notecard can be configured in the `cellular_configure` function in `amitrap_cellular.py`.
You can find the available modes [here](https://dev.blues.io/notecard/notecard-walkthrough/essential-requests/#configuring-synchronization-modes).

Please note that this is (currently) not a stand-alone Ami-System setup.
It only adds cellular connecivity to an existing setup.

## File structure

* `_version.py`: Just contains the version number of the software as a string that can be imported as variable `__version__` into other Python scripts.
* `ami-trap-raspi-cellular-config.py`: One-time configuration script.
* `ami-trap-raspi-cellular.py`: Entrypoint for the cellular connectivity service. Should be run at start-up with root privileges.
* `amitrap_cellular.py`: Collection of cellular connectivity routines for the Ami-System.
* `amitrap.py`: A class for interacting with the Raspberry-Pi or Rock-Pi based Ami-System.
* `note_python-1.5.0-py3-none-any.whl`: Python package `note-python`, which is required. Downloaded from [here](https://pypi.org/project/note-python).
* `install.sh`: Install bash script.

## Notes

Tested on the image `???`.

Find more details [here](https://github.com/JonasBchrt/ami-trap-raspi-cellular/blob/main/README.md).

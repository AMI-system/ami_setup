import os
import re
import glob
import time
import importlib
# import datetime
import subprocess
import json
from _version import __version__

class AmiTrap:
    """
    A class for interacting with the Raspberry-Pi based Ami-Trap.

    Date: November 2023
    Author: Jonas Beuchert (UKCEH)

    Attributes:
        camera_path (str): The path to the Raspberry Pi camera.
        camera_config_path (str): The path to the camera configuration file.
        picture_path (str): The path to the directory where pictures are stored.
        picture_format (str): The format of the pictures.
        boot_config_path (str): The path to the Raspberry Pi boot configuration file.
        is_rockpi (bool): Whether the device is a Rock Pi or a Raspberry Pi.
    """

    def __init__(self,
                 camera_path="/dev/video0",
                 camera_config_path="/home/pi/scripts/setCamera.sh",
                 picture_path="/media/pi/PiImages",
                 picture_format="*.jp*g",
                 boot_config_path="/boot/config.txt",
                 is_rockpi=False
                 ):
        """
        Initializes the Amitrap class.

        Args:
            camera_path (str, optional): The path to the Raspberry Pi camera. Defaults to "/dev/video0".
            camera_config_path (str, optional): The path to the camera configuration file. Defaults to "/home/pi/scripts/setCamera.sh".
            picture_path (str, optional): The path to the directory where pictures are stored. Defaults to "/media/pi/PiImages".
            picture_format (str, optional): The naming convention of the pictures. Defaults to "*.jp*g".
            boot_config_path (str, optional): The path to the Raspberry Pi boot configuration file. Defaults to "/boot/config.txt".
            is_rockpi (bool, optional): Whether the device is a Rock Pi. Defaults to False, i.e., a Raspberry Pi.
        """
        self.camera_path = camera_path
        self.camera_config_path = camera_config_path
        self.picture_path = picture_path
        self.picture_format = picture_format
        self.boot_config_path = boot_config_path
        self._shell = None
        self.is_rockpi = is_rockpi

    def get_software_version(self):
        return __version__

    def get_camera_info(self):
        """
        Gets information about the Raspberry Pi camera.

        Returns:
            dict: A dictionary containing information about the camera, including whether it is connected and the current configuration.
        """
        camera_info = {}
        camera_info["connected"] = self._is_camera_connected()
        camera_info["config"] = self._read_camera_config()
        return camera_info

    def _is_camera_connected(self):
        """
        Checks if the Raspberry Pi camera is connected.

        Returns:
            bool: True if the camera is connected, False otherwise.
        """
        return os.path.exists(self.camera_path)

    def _read_camera_config(self):
        """
        Reads the configuration file for the Raspberry Pi camera.

        Returns:
            dict: A dictionary containing the camera configuration.
        """
        try:
            with open(self.camera_config_path, "r") as f:
                content = f.read()
                matches = re.findall(r'([a-z_]+)=([0-9]+)', content) 
                config = {}
                for word, number in matches: 
                    config[word] = number
                return config
        except FileNotFoundError:
            return {}
        
    def set_camera_config(self, config):
        """
        Sets the configuration for the Raspberry Pi camera.

        May require root privileges.

        Args:
            config (dict): A dictionary containing the camera configuration.
        """
        try:
            with open(self.camera_config_path, "r") as f:
                content = f.read()
            # Search for keys in file and replace numbers  
            for key, value in config.items():
                content = re.sub(rf"{key}=[0-9]+", f"{key}={value}", content)
            with open(self.camera_config_path, "w") as f:
                f.write(content)
        except FileNotFoundError:
            pass

    def get_time(self):
        """
        Gets the current time.

        Returns:
            float: The current time in seconds since the epoch.
        """
        return time.time()

    def get_timezone(self):
        """
        Gets the current timezone.

        Returns:
            str: The current timezone.
        """
        # return datetime.datetime.now().astimezone().tzname()
        # Reload time module to get the latest timezone information
        # importlib.reload(time)
        # return time.tzname[0] + "WTF0"
        # Use subprocess to get the timezone
        return subprocess.check_output("date +%Z", shell=True, universal_newlines=True).strip()

    def get_time_info(self):
        """
        Gets the current time and timezone.

        Returns:
            dict: A dictionary containing the current time and timezone.
                - "current_time" (float): The current time in seconds since the epoch.
                - "timezone" (str): The current timezone.
        """
        return {
            "os_time": self.get_time(),
            "timezone": self.get_timezone()
        }

    def get_memory_info(self):
        """
        Gets information about the memory usage, the stored pictures, and whether an SSD is connected.

        Returns:
            dict: A dictionary containing information about the memory usage.
        """
        memory_info = {}
        memory_info["ssd_connected"] = self._is_ssd_connected()
        if os.path.exists(self.picture_path):
            pictures = glob.glob(os.path.join(self.picture_path, self.picture_format))
            picture_count = len(pictures)
            memory_info["picture_count"] = picture_count
            if picture_count > 0:
                most_recent_file = max(pictures, key=os.path.getmtime)
                memory_info["last_picture_timestamp"] = os.path.getmtime(most_recent_file)
            stat = os.statvfs(self.picture_path)
            memory_info["free_memory"] = stat.f_frsize * stat.f_bavail
        else:
            memory_info["picture_count"] = 0
            memory_info["free_memory"] = 0
        return memory_info

    def _is_ssd_connected(self):
        """
        Checks if a drive is connected.

        Returns:
            bool: True if at least one drive is connected, False otherwise.
        """
        output = subprocess.check_output(['lsblk', '-o', 'NAME,TYPE']) 
        # Decode the output from bytes to string 
        output = output.decode('utf-8') 
        return "sda" in output

    def get_bluetooth_info(self):
        """
        Gets information about the Bluetooth settings.

        Returns:
            dict: A dictionary containing information about the Bluetooth settings, including whether Bluetooth is powered on and enabled.
        """
        bluetooth_info = {}
        bluetooth_info["powered"] = self._is_bluetooth_powered()
        bluetooth_info["enabled"] = self._is_bluetooth_enabled()
        return bluetooth_info

    def _is_bluetooth_powered(self):
        """
        Checks if Bluetooth is powered on.

        Returns:
            bool: True if Bluetooth is powered on, False otherwise.
        """
        try:
            output = subprocess.check_output(['bluetoothctl', 'show'], universal_newlines=True, timeout=0.5)
        except subprocess.TimeoutExpired:
            return False
        return "Powered: yes" in output

    def _is_bluetooth_enabled(self):
        """
        Checks if Bluetooth is enabled.

        Returns:
            bool: True if Bluetooth is enabled, False otherwise.
        """
        try:
            with open(self.boot_config_path) as f:
                boot_file_content = "".join(f.readlines()).replace(" ", "")
            return not "dtoverlay=disable-bt" in boot_file_content or "#dtoverlay=disable-bt" in boot_file_content
        except FileNotFoundError:
            return None
    
    def enable_bluetooth(self):
        """
        Enables Bluetooth. Only takes effect after reboot.

        May require root privileges.
        """
        try:
            with open(self.boot_config_path, "r") as f:
                content = f.read()
                content = content.replace("dtoverlay=disable-bt", "#dtoverlay=disable-bt")
                with open(self.boot_config_path, "w") as f:
                    f.write(content)
        except FileNotFoundError:
            pass

    def disable_bluetooth(self):
        """
        Disables Bluetooth. Only takes effect after reboot.

        May require root privileges.
        """
        try:
            with open(self.boot_config_path, "r") as f:
                content = f.read()
                content = re.sub(r"[\s*#*\s*]*dtoverlay=disable-bt\s*", "\n\ndtoverlay=disable-bt\n", content)
                with open(self.boot_config_path, "w") as f:
                    f.write(content)
        except FileNotFoundError:
            pass

    def evaluate_command(self, command, timeout=10.0):
        """
        Evaluates a command in a shell.

        May require root privileges.

        Args:
            command (str): The command to be evaluated.
            timeout (float, optional): The timeout in seconds. Defaults to 10.0.

        Returns:
            str: The output of the command.
        """
        return subprocess.check_output(command, shell=True, universal_newlines=True, timeout=timeout)
    
    def reboot(self):
        """
        Reboots the Raspberry Pi.

        May require root privileges.
        """
        os.system("reboot")

    def shutdown(self):
        """
        Shuts down the Raspberry Pi.

        May require root privileges.
        """
        os.system("shutdown -h now")

    def set_time(self, time=None, zone=None):
        """
        Sets the time of the Raspberry Pi.

        May require root privileges.

        Args:
            time (float): The time in seconds since the epoch.
            zone (str): The time zone.
        """

        if time is not None:
            bash_cmd = f"sudo date -s '@'{time}"
            print(bash_cmd)
            print()
            subprocess.run(bash_cmd, shell=True, check=True)

        if zone is not None:
            bash_cmd = f"sudo timedatectl set-timezone {zone}"
            print(bash_cmd)
            print()
            subprocess.run(bash_cmd, shell=True, check=True)

    def get_serial_number(self):
        """
        Gets the serial number of the Raspberry Pi / Rock Pi.

        Returns:
            str: The serial number of the Raspberry Pi.
        """
        cpuserial = "0000000000000000"
        try:
            with open("/proc/cpuinfo", "r") as f:
                for line in f:
                    if line[0:6]=="Serial":
                        cpuserial = line[10:26]
        except:
            cpuserial = "ERROR000000000"
        
        return cpuserial
    
    def get_hardware_version(self):
        """
        Gets the hardware version of the Raspberry Pi / Rock Pi.

        Returns:
            str: The hardware version stored in /proc/device-tree/model.
        """
        try:
            with open("/proc/device-tree/model", "r") as f:
                return f.read()
        except:
            return "ERROR"
        
    def get_is_rockpi(self):
        """
        Checks if the device is a Rock Pi.

        Returns:
            bool: True if the device is a Rock Pi, False otherwise.
        """
        return "rock pi" in self.get_hardware_version().lower()
    
    def get_is_raspberrypi(self):
        """
        Checks if the device is a Raspberry Pi.

        Returns:
            bool: True if the device is a Raspberry Pi, False otherwise.
        """
        return "raspberry pi" in self.get_hardware_version().lower()
    
    def get_chunk_of_most_recent_picture(self, chunk_idx=0, chunk_size=512):
        """
        Gets a chunk of the most recent picture.

        Args:
            chunk_idx (int, optional): The index of the chunk. Defaults to 0.
            chunk_size (int, optional): The size of the chunk [bytes]. Defaults to 512 bytes.

        Returns:
            bytes: The chunk of the picture.
        """
        pictures = glob.glob(os.path.join(self.picture_path, self.picture_format))
        if len(pictures) == 0:
            return b""
        most_recent_file = max(pictures, key=os.path.getmtime)
        with open(most_recent_file, "rb") as f:
            f.seek(chunk_idx * chunk_size)
            return f.read(chunk_size)

    def set_wifi(self, network, password):
        """
        Sets the WiFi network and password.

        May require root privileges.

        Args:
            network (str): The WiFi network name.
            password (str): The WiFi network password.
        """
        if not self.is_rockpi:
            bash_cmd = f"sudo wpa_passphrase \"{network}\" \"{password}\" | sudo tee -a /etc/wpa_supplicant/wpa_supplicant.conf"
        else:
            bash_cmd = f"nmcli dev wifi rescan"
        print(bash_cmd)
        print()
        subprocess.run(bash_cmd, shell=True, check=True)
        if not self.is_rockpi:
            # Re-fresh configs
            bash_cmd = "sudo wpa_cli -i wlan0 reconfigure"
        else:
            bash_cmd = f"nmcli dev wifi connect \"{network}\" password \"{password}\""
        print(bash_cmd)
        print()
        subprocess.run(bash_cmd, shell=True, check=True)
    
    def _crc16(self, buffer):
        crc = 0x0
        for byte in buffer:
            code = (crc >> 8) & 0xFF
            code ^= byte & 0xFF
            code ^= code >> 4
            crc = (crc << 8) & 0xFFFF
            crc ^= code
            code = (code << 5) & 0xFFFF
            crc ^= code
            code = (code << 7) & 0xFFFF
            crc ^= code
        return crc

    def check_file_crc16(self, desired_checksum, path="/tmp/firmware.zip"):
        """
        Checks the CRC16 checksum of a  file.

        Args:
            path (str): The path to the file.
            desired_checksum (int): The desired CRC16 checksum.

        Returns:
            bool: True if the checksum matches, False otherwise.
        """
        # Read firmware file
        with open(path, "rb") as f:
            firmware = f.read()
        # Calculate checksum
        checksum = self._crc16(firmware)
        # Print comparison:
        print(f"Calculated checksum: {checksum}")
        print(f"Desired checksum: {desired_checksum}")
        print()
        # Compare checksums
        return checksum == desired_checksum

    def update_firmware(self, path="/tmp/firmware.zip"):
        """
        Updates the firmware of the Ami-Trap.

        May require root privileges.

        Args:
            path (str): The path to the firmware file.
        """
        temp_path = "/tmp/ami-trap-firmware"
        # Create temp directory if it doesn't exist
        bash_cmd = f"sudo mkdir -p {temp_path}"
        # Extract zip file to temp
        bash_cmd = f"unzip -o {path} -d {temp_path}"
        print(bash_cmd)
        print()
        subprocess.run(bash_cmd, shell=True, check=True)
        # # Read source_paths and destination_paths from config.json
        # with open(os.path.join(temp_path, "config.json"), "r") as f:
        #     config = json.load(f)
        # source_paths = config["source_paths"]
        # destination_paths = config["destination_paths"]
        # # Move files to destination_paths
        # for source_path, destination_path in zip(source_paths, destination_paths):
        #     bash_cmd = f"sudo mv {os.path.join(temp_path, source_path)} {destination_path}"
        #     print(bash_cmd)
        #     print()
        #     subprocess.run(bash_cmd, shell=True, check=True)
        # Execute install.sh script
        bash_cmd = f"sudo bash {os.path.join(temp_path, 'install.sh')}"
        print(bash_cmd)
        print()
        subprocess.run(bash_cmd, shell=True, check=True)
        # Remove temp directory
        bash_cmd = f"sudo rm -rf {temp_path}"

    def download_firmware(self, url="https://jonasbchrt.github.io/ami-trap-app-bluetooth/firmware.zip"):
        """
        Downloads the firmware of the Ami-Trap.

        Args:
            url (str): The URL of the firmware zip file.
        """
        temp_path = "/tmp"
        # Download firmware file
        bash_cmd = f"wget -O {temp_path}/firmware.zip {url}"
        print(bash_cmd)
        print()
        subprocess.run(bash_cmd, shell=True, check=True)

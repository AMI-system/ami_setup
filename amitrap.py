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
        wittypi_path (str): The path to the WittyPi utilities.
        audio_path (str): The path to the directory where audio files are stored.
        audio_format (str): The format of the audio files.
        ultrasound_path (str): The path to the directory where ultrasound files are stored.
        ultrasound_format (str): The format of the ultrasound files.
        storage_path (str): The path to the directory where data is stored (e.g., pictures, audio files, ultrasound files).
    """

    def __init__(self,
                 camera_path="/dev/video0",
                 camera_config_path="/home/pi/scripts/setCamera.sh",
                 picture_path="/media/pi/PiImages/images",
                 picture_format="*.jp*g",
                 boot_config_path="/boot/config.txt",
                 is_rockpi=False,
                 wittypi_path="/home/pi/wittypi",
                 audio_path="/media/pi/PiImages/audio",
                 audio_format="*.wav",
                 ultrasound_path="/media/pi/PiImages/ultrasonic",
                 ultrasound_format="*.wav",
                 storage_path="/media/pi/PiImages"
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
            wittypi_path (str, optional): The path to the WittyPi utilities. Defaults to "/home/pi/wittypi".
            audio_path (str, optional): The path to the directory where audio files are stored. Defaults to "/media/pi/PiImages/audio".
            audio_format (str, optional): The naming convention of the audio files. Defaults to "*.wav".
            ultrasound_path (str, optional): The path to the directory where ultrasound files are stored. Defaults to "/media/pi/PiImages/ultrasound".
            ultrasound_format (str, optional): The naming convention of the ultrasound files. Defaults to "*.wav".
            storage_path (str, optional): The path to the directory where data is stored (e.g., pictures, audio files, ultrasound files). Defaults to "/media/pi/PiImages".
        """
        self.camera_path = camera_path
        self.camera_config_path = camera_config_path
        self.picture_path = picture_path
        self.picture_format = picture_format
        self.boot_config_path = boot_config_path
        self._shell = None
        self.is_rockpi = is_rockpi
        self.wittypi_path = wittypi_path
        self.audio_path = audio_path
        self.audio_format = audio_format
        self.ultrasound_path = ultrasound_path
        self.ultrasound_format = ultrasound_format
        self.storage_path = storage_path

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
        camera_info["id"] = self.get_camera_id()
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
        
        Returns:
            bool: True if the configuration was set successfully, False otherwise.
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
            return False
        try:
            # Try to execute the script
            bash_cmd = f"sudo bash {self.camera_config_path}"
            print(bash_cmd)
            subprocess.run(bash_cmd, shell=True, check=True)
            print()
        except Exception:
            pass
        # Try to save setting in config.json
        try:
            with open("/home/pi/config.json", "r") as f:
                config_json = json.load(f)
            config_json["camera_settings"] = config
            with open("/home/pi/config.json", "w") as f:
                json.dump(config_json, f, indent=4)
        except FileNotFoundError:
            pass
        return True

    def get_camera_id(self):
        """
        Gets the ID of the camera.

        Returns:
            str: The ID of the camera or an empty string if the camera is not connected.
        """
        # Look for file in the folder /dev/v4l/by-id/ of the pattern "usb-046d_Logitech_BRIO_*-video-index0" and get the * part
        try:
            camera_id = glob.glob("/dev/v4l/by-id/usb-046d_Logitech_BRIO_*-video-index0")[0].split("_")[-1].split("-")[0]
        except Exception:
            camera_id = ""
        return camera_id

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
        return subprocess.check_output("date +%z", shell=True, universal_newlines=True).strip()

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
            try:
                pictures = glob.glob(os.path.join(self.picture_path, "**", self.picture_format), recursive=True)
                picture_count = len(pictures)
                memory_info["picture_count"] = picture_count
                if picture_count > 0:
                    most_recent_file = max(pictures, key=os.path.getmtime)
                    memory_info["last_picture_timestamp"] = os.path.getmtime(most_recent_file)
                    memory_info["last_picture_size"] = os.path.getsize(most_recent_file)
                else:
                    memory_info["last_picture_timestamp"] = None
                    memory_info["last_picture_size"] = None
                pictures_last_24h = [f for f in pictures if os.path.getmtime(f) > time.time() - 24 * 3600]
                picture_count_last_24h = len(pictures_last_24h)
                memory_info["picture_count_last_24h"] = picture_count_last_24h
                # Count pictures from last 24 h below 200 KB
                memory_info["picture_count_last_24h_below_200kb"] = len([f for f in pictures_last_24h if os.path.getsize(f) < 200 * 1024])
            except:
                memory_info["picture_count"] = 0
                memory_info["last_picture_timestamp"] = None
                memory_info["last_picture_size"] = None
                memory_info["picture_count_last_24h"] = 0
                memory_info["picture_count_last_24h_below_200kb"] = 0
        else:
            memory_info["picture_count"] = 0
            memory_info["last_picture_timestamp"] = None
            memory_info["last_picture_size"] = None
            memory_info["picture_count_last_24h"] = 0
            memory_info["picture_count_last_24h_below_200kb"] = 0
        if os.path.exists(self.storage_path):
            stat = os.statvfs(self.storage_path)
            memory_info["free_memory"] = stat.f_frsize * stat.f_bavail
        else:
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
        try:
            return subprocess.check_output(command, shell=True, universal_newlines=True, timeout=timeout, stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError as e:
            return str(e.output)
                
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

        if time is not None:
            try:
                # Source WittyPi utilities and set RTC time
                bash_cmd = f"exec printf '1\n13\n' | {self.wittypi_path}/wittyPi.sh"
                print(bash_cmd)
                print()
                subprocess.run(bash_cmd, check=True, shell=True, timeout=2)
            except Exception as e:
                print("Could not set RTC time. Is there an issue with the WittyPi?")
                print()

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
    
    def get_most_recent_picture_path(self):
        """
        Gets the path to the most recent picture.

        Returns:
            str: The path to the most recent picture.
        """
        pictures = glob.glob(os.path.join(self.picture_path, "**", self.picture_format), recursive=True)
        if len(pictures) == 0:
            return ""
        return max(pictures, key=os.path.getmtime)
    
    def get_chunk_of_most_recent_picture(self, chunk_idx=0, chunk_size=512):
        """
        Gets a chunk of the most recent picture.

        Args:
            chunk_idx (int, optional): The index of the chunk. Defaults to 0.
            chunk_size (int, optional): The size of the chunk [bytes]. Defaults to 512 bytes.

        Returns:
            bytes: The chunk of the picture.
        """
        pictures = glob.glob(os.path.join(self.picture_path, "**", self.picture_format), recursive=True)
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
        # if not self.is_rockpi:
        #     bash_cmd = f"sudo wpa_passphrase \"{network}\" \"{password}\" | sudo tee -a /etc/wpa_supplicant/wpa_supplicant.conf"
        # else:
        bash_cmd = f"nmcli dev wifi rescan"
        print(bash_cmd)
        print()
        # subprocess.run(bash_cmd, shell=True, check=True)
        try:
            subprocess.check_output(bash_cmd, shell=True, universal_newlines=True, timeout=11, stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError as e:
            print(e.output)
            print()
        # if not self.is_rockpi:
        #     # Re-fresh configs
        #     bash_cmd = "sudo wpa_cli -i wlan0 reconfigure"
        # else:
        bash_cmd = f"nmcli dev wifi connect \"{network}\" password \"{password}\""
        print(bash_cmd)
        print()
        try:
            subprocess.check_output(bash_cmd, shell=True, universal_newlines=True, timeout=11, stderr=subprocess.STDOUT)
            return True
        except subprocess.CalledProcessError as e:
            print(e.output)
            print()
            return False

    def scan_wifi(self):
        """
        Scans for WiFi networks and returns unique network names.

        Returns:
            list: A list of unique WiFi network names.
        """
        if not self.is_rockpi:
            bash_cmd = "sudo iwlist wlan0 scan | grep ESSID | sed -e 's/.*ESSID:\"//' -e 's/\"$//'"
        else:
            bash_cmd = "nmcli dev wifi list"
        # print(bash_cmd)
        # print()
        output = subprocess.check_output(bash_cmd, shell=True, universal_newlines=True)
        if not self.is_rockpi:
            return list(set(filter(None, output.split("\n"))))
        else:
            # Loop over lines. Ignore first line. Ignore the first 27 chars from each line, get the next 13 chars and strip white space. Then, find unique ones.
            return list(set(filter(None, [line[27:40].strip() for line in output.split("\n")[1:]])))

    def get_wifi_name(self):
        """
        Gets the WiFi status.

        Returns:
            str: The name of the WiFi network if connected, empty string otherwise.
        """
        try:
            if not self.is_rockpi:
                bash_cmd = "iwgetid -r"
            else:
                bash_cmd = "nmcli dev status"
            # print(bash_cmd)
            # print()
            output = subprocess.check_output(bash_cmd, shell=True, universal_newlines=True)
            if not self.is_rockpi:
                return output.strip()
            else:
                # Find the line that starts with "wlan0". Check if " connected" is in the line. If so, return the next word.
                for line in output.split("\n"):
                    if line.startswith("wlan0"):
                        if " connected" in line:
                            return line.split()[-1]
        except subprocess.CalledProcessError as e:
            print(e)
            print()
        return ""
    
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

    def set_metadata(self, metadata, path="/home/pi/config.json"):
        """
        Updates the metadata of the Ami-Trap in the config.json file.
        
        If the file doesn't exist, it is created.
        
        Args:
            metadata (dict): A dictionary containing the metadata.
        """
        # Read config.json, if it exists
        try:
            with open(path, "r") as f:
                config = json.load(f)
        except FileNotFoundError:
            config = {}
        # Go through all fields in metadata and update config
        for top_level_key, top_level_value in metadata.items():
            # Chdck if key exists already in conig.json
            if top_level_key in config:
                # If it's a dictionary, update only the keys that are present in the metadata
                if isinstance(top_level_value, dict):
                    for low_level_key, low_level_value in top_level_value.items():
                        config[top_level_key][low_level_key] = low_level_value
                else:
                    # If it's not a dictionary, update the value
                    config[top_level_key] = top_level_value
            else:
                # If it doesn't exist, create it
                config[top_level_key] = top_level_value
        # Write config to config.json. Format.
        with open(path, "w") as f:
            json.dump(config, f, indent=4)

    def get_wittypi_schedule(self):
        """
        Gets the schedule of the WittyPi.

        Returns:
            dict: A list containing the schedule of the WittyPi.
        """
        try:
            with open(f"{self.wittypi_path}/schedule.wpi", "r") as f:
                lines = []
                # Read file line-by-line. Ignore lines that are empty or contain white space or start with # (potentailly after whiote space). Remove white space from start and end of line. Discard everything from # onwards.
                for line in f.readlines():
                    line = line.split("#")[0].strip()
                    if line:
                        lines.append(line)
                return lines
        except FileNotFoundError:
            return []
        
    def get_microphone_info(self):
        """
        Gets information about the microphone and audio and ultrasound files.

        Returns:
            dict: A dictionary containing status information.
        """
        microphone_info = {}
        microphone_info["connected"] = self._is_microphone_connected()
        if os.path.exists(self.audio_path):
            try:
                audio_files = glob.glob(os.path.join(self.audio_path, "**", self.audio_format), recursive=True)
                microphone_info["audio_count"] = len(audio_files)
                if len(audio_files) > 0:
                    most_recent_audio_file = max(audio_files, key=os.path.getmtime)
                    microphone_info["last_audio_timestamp"] = os.path.getmtime(most_recent_audio_file)
                    microphone_info["last_audio_size"] = os.path.getsize(most_recent_audio_file)
                else:
                    microphone_info["last_audio_timestamp"] = None
                    microphone_info["last_audio_size"] = None
                audio_files_last_24h = [f for f in audio_files if os.path.getmtime(f) > time.time() - 24 * 3600]
                microphone_info["audio_count_last_24h"] = len(audio_files_last_24h)
                # Count audio files from last 24 h below 200 KB
                microphone_info["audio_count_last_24h_below_1kb"] = len([f for f in audio_files_last_24h if os.path.getsize(f) < 1 * 1024])
            except:
                microphone_info["audio_count"] = 0
                microphone_info["last_audio_timestamp"] = None
                microphone_info["last_audio_size"] = None
                microphone_info["audio_count_last_24h"] = 0
                microphone_info["audio_count_last_24h_below_1kb"] = 0
        else:
            microphone_info["audio_count"] = 0
            microphone_info["last_audio_timestamp"] = None
            microphone_info["last_audio_size"] = None
            microphone_info["audio_count_last_24h"] = 0
            microphone_info["audio_count_last_24h_below_1kb"] = 0
        if os.path.exists(self.ultrasound_path):
            try:
                ultrasound_files = glob.glob(os.path.join(self.ultrasound_path, "**", self.ultrasound_format), recursive=True)
                microphone_info["ultrasound_count"] = len(ultrasound_files)
                if len(ultrasound_files) > 0:
                    most_recent_ultrasound_file = max(ultrasound_files, key=os.path.getmtime)
                    microphone_info["last_ultrasound_timestamp"] = os.path.getmtime(most_recent_ultrasound_file)
                    microphone_info["last_ultrasound_size"] = os.path.getsize(most_recent_ultrasound_file)
                else:
                    microphone_info["last_ultrasound_timestamp"] = None
                    microphone_info["last_ultrasound_size"] = None
                ultrasound_files_last_24h = [f for f in ultrasound_files if os.path.getmtime(f) > time.time() - 24 * 3600]
                microphone_info["ultrasound_count_last_24h"] = len(ultrasound_files_last_24h)
                # Count ultrasound files from last 24 h below 1 KB
                microphone_info["ultrasound_count_last_24h_below_1kb"] = len([f for f in ultrasound_files_last_24h if os.path.getsize(f) < 1 * 1024])
            except:
                microphone_info["ultrasound_count"] = 0
                microphone_info["last_ultrasound_timestamp"] = None
                microphone_info["last_ultrasound_size"] = None
                microphone_info["ultrasound_count_last_24h"] = 0
                microphone_info["ultrasound_count_last_24h_below_1kb"] = 0
        else:
            microphone_info["ultrasound_count"] = 0
            microphone_info["last_ultrasound_timestamp"] = None
            microphone_info["last_ultrasound_size"] = None
            microphone_info["ultrasound_count_last_24h"] = 0
            microphone_info["ultrasound_count_last_24h_below_1kb"] = 0
    
        microphone_info["frequencies"] = self._get_microphone_frequencies()

        return microphone_info
    
    def _is_microphone_connected(self):
        """
        Checks if the microphone is connected.

        Returns:
            bool: True if the microphone is connected, False otherwise.
        """
        # Run arecord -L and check if it returns a plughw and hw device called AudioMoth USB microphone
        found_hw = False
        found_plughw = False
        try:
            output = subprocess.check_output(['arecord', '-L'], universal_newlines=True)
            # Find line that starts with "hw:" and extract next line. Check if "AudioMoth USB microphone" is in the next line.
            for line in output.split("\n"):
                if line.startswith("hw:"):
                    found_hw = "AudioMoth USB Microphone" in output.split("\n")[output.split("\n").index(line) + 1] or found_hw
                if line.startswith("plughw:"):
                    found_plughw = "AudioMoth USB Microphone" in output.split("\n")[output.split("\n").index(line) + 1] or found_plughw
        except subprocess.CalledProcessError:
            return False
        return found_hw and found_plughw
    
    def _get_microphone_frequencies(self):
        """
        Gets the frequencies of the microphone.

        Returns:
            list: A list of frequencies.
        """
        hw_frequency = 0
        plughw_frequency = 0
        try:
            output = subprocess.check_output(['arecord', '-L'], universal_newlines=True)
            # Find line that starts with "hw:" and extract next line. Check if "AudioMoth USB microphone" is in the next line. If so, extract the frequencies.
            for line in output.split("\n"):
                if line.startswith("hw:"):
                    if "AudioMoth USB Microphone" in output.split("\n")[output.split("\n").index(line) + 1]:
                        # Find the first number in the line
                        hw_frequency = int(re.search(r'\d+', output.split("\n")[output.split("\n").index(line) + 1]).group())
                if line.startswith("plughw:"):
                    if "AudioMoth USB Microphone" in output.split("\n")[output.split("\n").index(line) + 1]:
                        # Find the first number in the line
                        plughw_frequency = int(re.search(r'\d+', output.split("\n")[output.split("\n").index(line) + 1]).group())
        except subprocess.CalledProcessError:
            return [0, 0]
        return [hw_frequency, plughw_frequency]

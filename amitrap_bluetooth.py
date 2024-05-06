"""
Collection of Bluetooth routines for the AMI-trap.

Date: November 2023
Author: Jonas Beuchert

This module defines the Bluetooth service for the AMI-trap. It provides
characteristics for retrieving status information, configuration,
and files from the AMI-trap, as well as for sending commands and files.

Core routines:
    - `power_on_bluetooth`: Turn on Bluetooth
    - `bluetooth_loop`: Main loop for the Bluetooth service
    - `power_off_bluetooth`: Turn off Bluetooth

Uses the bluez-peripheral library to implement a Bluetooth low-energy (BLE)
peripheral device and the AmiTrap class to interface with the AMI-trap.

"""

from bluez_peripheral.gatt.service import Service
from bluez_peripheral.gatt.characteristic import (
    characteristic,
    CharacteristicFlags as CharFlags,
)
from bluez_peripheral.util import get_message_bus, Adapter
from bluez_peripheral.advert import Advertisement
from bluez_peripheral.agent import NoIoAgent
import json
import os
from amitrap import AmiTrap
import json
from PIL import Image
import io

# BLE UUIDs that I defined myself
# Overall AMI-TRAP service UUID
AMI_TRAP_SERVICE_UUID = "12345678-1234-5678-1234-56789abcdef0"
# Get general status and system configuration of AMI-TRAP, excluding camera configuration
AMI_TRAP_GET_STATUS_CHARACTERISTIC_UUID = "09876543-2109-8765-4321-fedcba987653"
# Get camera configuration of AMI-TRAP
AMI_TRAP_GET_CAMERA_CONFIG_CHARACTERISTIC_UUID = "09876543-2109-8765-4321-fedcba987654"
# Send command to AMI-TRAP using JSON API
AMI_TRAP_SET_CMD_CHARACTERISTIC_UUID = "09876543-2109-8765-4321-fedcba987655"
# Get output of command sent to AMI-TRAP
AMI_TRAP_GET_OUTPUT_CHARACTERISTIC_UUID = "09876543-2109-8765-4321-fedcba987656"
# Get most recent picture from AMI-TRAP
AMI_TRAP_GET_PICTURE_CHARACTERISTIC_UUID = "09876543-2109-8765-4321-fedcba987657"
# Send file to AMI-TRAP
AMI_TRAP_SET_FILE_CHARACTERISTIC_UUID = "09876543-2109-8765-4321-fedcba987658"
# Get file from AMI-TRAP
AMI_TRAP_GET_FILE_CHARACTERISTIC_UUID = "09876543-2109-8765-4321-fedcba987659"

# Name of the BLE device (prefix)
AMI_TRAP_NAME = "AMI"


class AmiTrapService(Service):
    def __init__(self, is_rockpi=False):
        # Base 16 service UUID, This should be a primary service.
        super().__init__(AMI_TRAP_SERVICE_UUID, True)

        if not is_rockpi:
            self._ami = AmiTrap()
        else:
            self._ami = AmiTrap(camera_config_path="/home/rock/setCamera.sh",
                                camera_path="/dev/video5",
                                is_rockpi=True)

        self._output = ""

        self._picture_chunk_idx = 0

        self._file = None

        self._file_chunk_idx = 0

    def _check_string_length(self, string):
        """Check if string is too long for one 512 bytes packet."""
        if len(string) > 512:
            print(f"Data too large for one 512 bytes packet: {len(string)} bytes. Skipping.")
            print()
            return ""
        else:
            return string

    # Characteristics and Descriptors can have multiple flags set at once.
    # @characteristic(AMI_TRAP_CHARACTERISTIC_UUID, CharFlags.NOTIFY | CharFlags.READ)
    @characteristic(AMI_TRAP_GET_STATUS_CHARACTERISTIC_UUID, CharFlags.READ)
    def get_status(self, value=None, options=None):
        """
        Get the general status and system configuration of the AMI-trap.

        Returns:
            bytes: The status and configuration information in JSON format.
        """
        # This function is called when the characteristic is read.

        time_info = self._ami.get_time_info()

        # Takes 17 ms
        memory_info = self._ami.get_memory_info()

        # Takes 30-35 ms
        bluetooth_info = self._ami.get_bluetooth_info()

        # Assemble status info dict from info about time, memory, and bluetooth
        data = {
            "time": time_info,
            "memory": memory_info,
            "bluetooth": bluetooth_info,
            # "hardware": "Raspberry Pi" if not self._ami.is_rockpi else "Rock Pi",
            "hardware": self._ami.get_hardware_version(),
            "id": self._ami.get_serial_number(),
            "version": self._ami.get_software_version(),
            # "temperature": None, # TODO: Add temperature info once available
            "wifi": self._ami.get_wifi_name(),
        }

        # Convert dict to JSON string
        json_data = json.dumps(data, indent=4)

        # Check if JSON string is too large for one BLE packet (512 bytes)
        json_data = self._check_string_length(json_data)

        # Characteristics need to return bytes. So, turn JSON string into bytes.
        bytes_data = bytes(json_data, "utf-8")
        print(f"Transfer {len(bytes_data)} bytes.")
        print()
        return bytes_data

    @characteristic(AMI_TRAP_GET_CAMERA_CONFIG_CHARACTERISTIC_UUID, CharFlags.READ)
    def get_camera_config(self, value=None, options=None):
        """
        Get the camera configuration of the AMI-trap.

        Returns:
            bytes: The camera configuration information in JSON format.
        """
        # This function is called when the characteristic is read.

        camera_info = self._ami.get_camera_info()

        time_info = self._ami.get_time()

        data = {
            "os_time": time_info,
            "camera": camera_info,
        }

        json_data = json.dumps(data, indent=4)

        # Check if JSON string is too large for one BLE packet (512 bytes)
        json_data = self._check_string_length(json_data)

        # Characteristics need to return bytes.
        bytes_data = bytes(json_data, "utf-8")
        print(f"Transfer {len(bytes_data)} bytes.")
        print()
        return bytes_data

    @characteristic(AMI_TRAP_GET_OUTPUT_CHARACTERISTIC_UUID, CharFlags.READ)
    def get_output(self, value=None, options=None):
        """
        Get the output of the last command sent to the AMI-trap.

        Returns:
            bytes: The command output as string.
        """
        # This function is called when the characteristic is read.

        # Characteristics need to return bytes.
        bytes_data = bytes(self._output, "utf-8")
        self._output = "{}"
        print(f"Transfer {len(bytes_data)} bytes.")
        print()
        return bytes_data

    # This is a write only characteristic.
    @characteristic(AMI_TRAP_SET_CMD_CHARACTERISTIC_UUID, CharFlags.WRITE)
    def set_command(self, options):
        # This function is a placeholder.
        # In Python 3.9+ you don't need this function (See PEP 614)
        pass

    # In Python 3.9+:
    # @characteristic("BEF1", CharFlags.WRITE).setter
    # Define a characteristic writing function like so.
    @set_command.setter
    def set_command(self, value, options):
        """
        Execute command on the AMI-trap.

        Args:
            value (bytes): The command data in JSON format.

        """
        # Your characteristics will need to handle bytes.
        # print(value)
        print(f"Received {len(value)} bytes.")
        print()
        # Turn into JSON
        json_data = json.loads(value)
        print(json_data)
        print()

        command_recognized = False

        try:
            if "type" in json_data:
                if json_data["type"] == "camera" and "data" in json_data:
                    self._ami.set_camera_config(json_data["data"])
                    self._output = json.dumps({"success": "Camera configuration updated."})
                    command_recognized = True
                elif json_data["type"] == "command" and "data" in json_data:
                    output = self._ami.evaluate_command(json_data["data"])
                    print(output)
                    print()
                    # Add data to be sent out (command output)
                    self._output = output
                    command_recognized = True
                elif json_data["type"] == "reboot":
                    self._ami.reboot()
                    self._output = "Rebooting."
                    command_recognized = True
                elif json_data["type"] == "shutdown":
                    self._ami.shutdown()
                    self._output = "Shutting down."
                    command_recognized = True
                elif json_data["type"] == "time" and "data" in json_data:
                    print(f"Setting local time-of-day to {json_data['data']}.")
                    print()
                    self._ami.set_time(time=json_data["data"])
                    self._output = json.dumps({"success": "Time set."})
                    command_recognized = True
                elif json_data["type"] == "timezone" and "data" in json_data:
                    print(f"Setting local timezone to {json_data['data']}.")
                    print()
                    self._ami.set_time(zone=json_data["data"])
                    self._output = json.dumps({"success": "Timezone set."})
                    command_recognized = True
                elif json_data["type"] == "bluetooth" and "data" in json_data:
                    if json_data["data"]:
                        self._ami.enable_bluetooth()
                        self._output = "Bluetooth enabled. Takes effect after reboot."
                    else:
                        self._ami.disable_bluetooth()
                        self._output = "Bluetooth disabled. Takes effect after reboot."
                    command_recognized = True
                elif (
                    json_data["type"] == "wifi"
                    and "network" in json_data
                    and "password" in json_data
                ):
                    self._ami.set_wifi(json_data["network"], json_data["password"])
                    self._output = json.dumps({"success": "Wifi configuration updated."})
                    command_recognized = True
                elif json_data["type"] == "wifi-scan":
                    self._output = json.dumps({"wifi-networks": []})
                    wifi_networks = self._ami.scan_wifi()
                    for i in range(len(wifi_networks)):
                        output_json = {
                            "wifi-networks": wifi_networks[:i + 1]
                        }
                        output = json.dumps(output_json)
                        if len(output) > 512:
                            print("Truncated WiFi output due to 512 bytes limit.")
                            print()
                            break
                        self._output = output
                    command_recognized = True
                # # firmwareStart
                # elif json_data["type"] == "firmwareStart" and "data" in json_data:
                #     self._file = bytearray()
                #     self._receiving_file = True
                #     self._file_path = "/tmp/firmware.zip"
                #     self._output = "Firmware update bia BLE started."
                #     command_recognized = True
                # # firmwareEnd
                # elif json_data["type"] == "firmwareEnd" and "data" in json_data:
                #     self._receiving_file = False
                #     if self._ami.check_file_crc16(json_data["data"]):
                #         # Concatenate all chunks in one bytearray and save as /tmp/firmware.zip
                #         with open("/tmp/firmware.zip", "wb") as f:
                #             f.write(self._file)
                #         self._ami.update_firmware()
                #         self._output = "Firmware update via BLE finished."
                #     else:
                #         self._output = "Firmware update via BLE failed. Try again."
                #     command_recognized = True
                # firmwareOnline
                elif json_data["type"] == "firmwareOnline":
                    self._ami.download_firmware()
                    self._ami.update_firmware()
                    self._ami.reboot()
                    # self._output = "Firmware update via WiFi/Ethernet."
                    command_recognized = True
                elif json_data["type"] == "firmwareOffline":
                    self._ami.update_firmware()
                    self._ami.reboot()
                    # self._output = "Firmware update from local file."
                    command_recognized = True
                elif json_data["type"] == "fileStart" and "path" in json_data:
                    self._file = bytearray()
                    # self._receiving_file = True
                    self._file_path = json_data["path"]
                    self._output = "File transfer started."
                    command_recognized = True
                elif json_data["type"] == "fileEnd" and "crc16" in json_data:
                    # self._receiving_file = False
                    with open(self._file_path, "wb") as f:
                        f.write(self._file)
                    if self._ami.check_file_crc16(json_data["crc16"], self._file_path):
                        self._output = json.dumps({"success": "File transfer finished."})
                    else:
                        # Delete file
                        os.remove(self._file_path)
                        self._output = json.dumps({"error": "File transfer failed. Try again."})
                    command_recognized = True
                elif json_data["type"] == "readFile" and "path" in json_data:
                    try:
                        with open(json_data["path"], "rb") as f:
                            self._file = bytearray(f.read())
                    except FileNotFoundError as e:
                        self._file = None
                        self._output = json.dumps({"error": str(e)[:500]})
                    self._file_chunk_idx = 0
                    # self._output = "File transfer."
                    command_recognized = True
                elif json_data["type"] == "getSmallPicture":
                    try:
                        # Get path to most recent picture
                        picture_path = self._ami.get_most_recent_picture_path()
                        # Open picture
                        picture = Image.open(picture_path)
                        small_picture = picture.resize((256, 135), Image.Resampling.LANCZOS)
                        self._file = io.BytesIO()
                        small_picture.save(self._file, format="JPEG")
                        self._file = self._file.getvalue()
                    except Exception as e:
                        self._file = None
                        print(e)
                        self._output = json.dumps({"error": str(e)[:500]})
                    self._file_chunk_idx = 0
                    command_recognized = True
                elif json_data["type"] == "metadata" and "data" in json_data:
                    try:
                        self._ami.set_metadata(json_data["data"])
                        self._output = json.dumps({"success": "Metadata updated."})
                    except:
                        self._output = json.dumps({"error": "Metadata update failed."})
                    command_recognized = True
            if not command_recognized:
                print("Command not recognized:")
                print(json_data)
                print()
                self._output = json.dumps({"error": "Command not recognized."})

        except Exception as e:
            # Output error message
            self._output = json.dumps({"error": str(e)[:500]})

    # This is a write only characteristic.
    @characteristic(AMI_TRAP_SET_FILE_CHARACTERISTIC_UUID, CharFlags.WRITE)
    def set_file(self, options):
        # This function is a placeholder.
        # In Python 3.9+ you don't need this function (See PEP 614)
        pass

    # In Python 3.9+:
    # @characteristic("BEF1", CharFlags.WRITE).setter
    # Define a characteristic writing function like so.
    @set_file.setter
    def set_file(self, value, options):
        """Receive a 512-byte chunk of a file that is being sent to the AMI-trap."""
        # Your characteristics will need to handle bytes.
        # print(value)
        print(f"Received {len(value)} bytes.")
        print()
        # if self._receiving_file:
        self._file.extend(value)
        print(f"File size: {len(self._file)} bytes.")
        print()
        # else:
        #     print("File transfer not started.")
        #     print()

    # Characteristics and Descriptors can have multiple flags set at once.
    @characteristic(AMI_TRAP_GET_PICTURE_CHARACTERISTIC_UUID, CharFlags.READ)
    def get_picture(self, value=None, options=None):
        """Get a 508-byte chunk of the most recent picture taken by the AMI-trap."""
        # This function is called when the characteristic is read.

        bytes_data = self._picture_chunk_idx.to_bytes(
            4, "big"
        ) + self._ami.get_chunk_of_most_recent_picture(
            chunk_idx=self._picture_chunk_idx, chunk_size=512 - 4
        )  # Subtract the size of an integer (4 bytes)

        if len(bytes_data) < 512:
            print(
                f"Picture read. {self._picture_chunk_idx} chunks in total. Resetting chunk index to 0."
            )
            self._picture_chunk_idx = 0
        else:
            self._picture_chunk_idx += 1
        print(f"Transferring {len(bytes_data)} bytes.")
        print()

        return bytes_data

    @characteristic(AMI_TRAP_GET_FILE_CHARACTERISTIC_UUID, CharFlags.READ)
    def get_file(self, value=None, options=None):
        """Get a 512-byte chunk of the file that was requested via the set_file characteristic."""
        if self._file is None:
            print("No file to transfer.")
            print()
            return bytes(0)
        chunk_size = 512
        file_length = len(self._file)
        start_idx = self._file_chunk_idx * chunk_size
        end_idx = min(start_idx + chunk_size, file_length)
        bytes_data = self._file[start_idx:end_idx]
        self._file_chunk_idx += 1
        print(f"Transferring {len(bytes_data)} bytes of {file_length} bytes.")
        print()

        return bytes_data


async def bluetooth_loop(duration_seconds=65535, is_rockpi=False):
    """Main loop for the Bluetooth service.

    Regsiters the Bluetooth service and starts an advert.
    
    Args:
        duration_seconds (int, optional): Duration of the Bluetooth advert in seconds. Defaults to 65535."""
    # Alternatively you can request this bus directly from dbus_next.
    bus = await get_message_bus()

    service = AmiTrapService(is_rockpi=is_rockpi)
    await service.register(bus)

    # An agent is required to handle pairing
    agent = NoIoAgent()
    # This script needs superuser for this to work.
    await agent.register(bus)

    adapter = await Adapter.get_first(bus)

    # Start an advert that will last for `duration_seconds` seconds.
    name = AMI_TRAP_NAME + "-" + service._ami.get_serial_number()
    print(name)
    print()
    advert = Advertisement(name, [AMI_TRAP_SERVICE_UUID], 0x000F, duration_seconds)
    await advert.register(bus, adapter)

    await bus.wait_for_disconnect()


async def power_on_bluetooth():
    """Power on Bluetooth adapter."""
    bus = await get_message_bus()

    adapter = await Adapter.get_first(bus)

    await adapter.set_powered(True)

    print("Bluetooth powered on.")
    print()


async def power_off_bluetooth():
    """Power off Bluetooth adapter."""
    bus = await get_message_bus()

    adapter = await Adapter.get_first(bus)

    await adapter.set_powered(False)

    print("Bluetooth powered off.")
    print()

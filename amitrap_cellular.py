import notecard
from notecard import card, hub, note, file
try:
    from notecard import binary_helpers
except:
    print("Failed to import binary_helpers. Make sure you have the latest version of note-python installed.")
    print("sudo python3 -m pip install git+https://github.com/blues/note-python")
    print()
# Use python-periphery on a Linux desktop or Raspberry Pi
from periphery import I2C
from time import sleep
import json
from amitrap import AmiTrap
from PIL import Image
import io


async def cellular_configure(i2c_path="/dev/i2c-1"):
    """Configure cellular connectivity via Notecard and Notehub.
    
    Only needs to run once for each Notecard.
    (Except if you want to change the configuration.)
    Sets the synchronization mode and interval.
    Assigns the Notecard to a Notehub project to define where the data goes on the server.
    
    Date: November 2023
    Author: Jonas Beuchert
    
    Args:
        i2c_path (str, optional): Path to I2C device. Defaults to "/dev/i2c-1".
            On a Raspberry Pi, the following GPIOs can be used for I2C:
            - GPIO2 (pin 3) as SDA for /dev/i2c-1
            - GPIO3 (pin 5) as SCL for /dev/i2c-1
            - Others, e.g., via bit-banging
            On a Rock Pi, the following GPIOs can be used for I2C:
            - GPIO2_A7 (pin 3) as SDA for /dev/i2c-7
            - GPIO2_B0 (pin 5) as SCL for /dev/i2c-7
            - GPIO2_A0 (pin 27) as SDA for /dev/i2c-2
            - GPIO2_A1 (pin 28) as SCL for /dev/i2c-2
            - Others, e.g., via bit-banging
    """

    # Notehub (cloud) project unique identifier
    productUID = "todo:replace-with-your-product-uid"

    # Synchronization mode
    # Must be one of 'periodic', 'continous', 'minimum', 'off', or 'dfu'
    sync_mode = 'minimum'
    outbound_interval_minutes = 3
    inbound_interval_minutes = 60

    # Connect to Notecard via I2C
    nCard = _connect_to_notecard(i2c_path)

    # Get and print cellular module (Notecard) information
    print(card.version(nCard))
    print()
    # Get and print data usage information
    print(nCard.Transaction({"req": "card.usage.get"}))
    print()
    # Configure cellular module (Notecard)
    hub.set(nCard,
            product=productUID,
            mode=sync_mode,
            outbound=outbound_interval_minutes,
            inbound=inbound_interval_minutes)
    # Print configuration
    print(hub.get(nCard))
    print()

    # Sync with cloud (Notehub)
    if _sync_and_print_status(nCard):
        print("Cellular connectivity configured for Ami-Trap and synchronized with Notehub.")
        print()
        return
    print("Cellular connectivity configured for Ami-Trap, but not yet synchronized with Notehub.")
    print()


def _connect_to_notecard(i2c_path="/dev/i2c-1", mode="minimum"):
    """Connect to Notecard via I2C.
    
    Args:
        i2c_path (str, optional): Path to I2C device. Defaults to "/dev/i2c-1".
            On a Raspberry Pi, the following GPIOs can be used for I2C:
            - GPIO2 (pin 3) as SDA for /dev/i2c-1
            - GPIO3 (pin 5) as SCL for /dev/i2c-1
            - Others, e.g., via bit-banging
            On a Rock Pi, the following GPIOs can be used for I2C:
            - GPIO2_A7 (pin 3) as SDA for /dev/i2c-7
            - GPIO2_B0 (pin 5) as SCL for /dev/i2c-7
            - GPIO2_A0 (pin 27) as SDA for /dev/i2c-2
            - GPIO2_A1 (pin 28) as SCL for /dev/i2c-2
            - Others, e.g., via bit-banging
    
    Returns:
        notecard: Notecard object.
    """
    # Configure I2C (connection between Notecard and RasPi)
    port = I2C(i2c_path)
    # Connect to Notecard via I2C
    nCard = notecard.OpenI2C(port, 0, 0)
    # Check sync mode
    sync_mode = hub.get(nCard)["mode"]
    # Set sync mode if different
    if sync_mode != mode:
        hub.set(nCard,
                mode=mode)
    return nCard


def _gather_status_data(ami, nCard):
    """Gather status data from Ami-Trap and send to Notecard.
    
    Args:
        ami (AmiTrap): AmiTrap object.
        nCard (notecard): Notecard object.
    """
    camera_info = ami.get_camera_info()
        
    time_info = ami.get_time_info()

    memory_info = ami.get_memory_info()

    bluetooth_info = ami.get_bluetooth_info()
        
    data = {"os_time":time_info,
            "camera":camera_info,
            "memory":memory_info,
            "bluetooth":bluetooth_info,
            "temperature":card.temp(nCard)["value"]
            }
    
    print(json.dumps(data, indent=4))
    print()

    # Add data to be sent out (configuration + temperature)
    print(note.add(nCard,
                   body=data))
    print()


def _sync_and_print_status(nCard, timeout=600):
    """Sync with cloud (Notehub) and print status for a given time.
    
    Args:
        nCard (notecard): Notecard object.
        timeout (int, optional): Timeout in seconds. Defaults to 600.

    Returns:
        bool: True if sync is complete, False if not.
    """
    # Sync with cloud (Notehub)
    print(hub.sync(nCard))
    print()
    # Print status for a given time or until sync is complete
    for i in range(timeout):
        status = hub.syncStatus(nCard)
        print(status)
        print()
        if "completed" in status:
            return True
        sleep(1)
    # If sync is not complete after timeout
    return False


async def cellular_send(i2c_path="/dev/i2c-1"):
    """Send status data from Ami-Trap to Notehub.

    Date: November 2023
    Author: Jonas Beuchert
    
    Args:
        i2c_path (str, optional): Path to I2C device. Defaults to "/dev/i2c-1".
            On a Raspberry Pi, the following GPIOs can be used for I2C:
            - GPIO2 (pin 3) as SDA for /dev/i2c-1
            - GPIO3 (pin 5) as SCL for /dev/i2c-1
            - Others, e.g., via bit-banging
            On a Rock Pi, the following GPIOs can be used for I2C:
            - GPIO2_A7 (pin 3) as SDA for /dev/i2c-7
            - GPIO2_B0 (pin 5) as SCL for /dev/i2c-7
            - GPIO2_A0 (pin 27) as SDA for /dev/i2c-2
            - GPIO2_A1 (pin 28) as SCL for /dev/i2c-2
            - Others, e.g., via bit-banging
    """

    # Connect to Notecard via I2C
    nCard = _connect_to_notecard(i2c_path)

    ami = AmiTrap()

    _gather_status_data(ami, nCard)

    if _sync_and_print_status(nCard):
        print("Sent data from Ami-Trap to Notehub.")
        print()
        return
    print("Failed to send data from Ami-Trap to Notehub.")


def _process_incoming_changes(ami, nCard):
    """Process incoming changes from Notehub.

    Args:
        ami (AmiTrap): AmiTrap object.
        nCard (notecard): Notecard object.
    Returns:
        str: Output string with info or None if nothing received.
    """
    output = None
    # Check for changes in Notecard files
    changes = file.changes(nCard)
    print(changes)
    print()
    # Check if there is at least one change in inbound file
    if "info" in changes and "data.qi" in changes["info"] and "total" in changes["info"]["data.qi"] and changes["info"]["data.qi"]["total"] > 0:
        changes_count = changes['info']['data.qi']['total']
        print(f"{changes_count} inbound change(s).")
        print()
        for change_idx in range(changes_count):
            # Print change and delete
            change = note.get(nCard, delete=True)
            print(change)
            print()
            print(change["body"])
            print()
            command_recognized = False
            if "type" in change["body"]:
                if change["body"]["type"] == "camera" and "data" in change["body"]:
                    ami.set_camera_config(change["body"]["data"])
                    command_recognized = True
                    output = "Camera configuration updated."
                elif change["body"]["type"] == "command" and "data" in change["body"]:
                    output = ami.evaluate_command(change["body"]["data"])
                    print(output)
                    print()
                    # # Add data to be sent out (command output)
                    # note.add(nCard,
                    #         body={"type":"output","data":output})
                    # # Sync data with cloud
                    # hub.sync(nCard)
                    # # # Print status until sync completed
                    # # while True:
                    # #     status = hub.syncStatus(nCard)
                    # #     print(status)
                    # #     print()
                    # #     if "completed" in status:
                    # #         break
                    # #     sleep(1)
                    command_recognized = True
                elif change["body"]["type"] == "reboot":
                    ami.reboot()
                    command_recognized = True
                elif change["body"]["type"] == "shutdown":
                    ami.shutdown()
                    command_recognized = True
                elif change["body"]["type"] == "time":
                    print("Wait for Notecard to acquire time-of-day")
                    timeout = 60
                    got_time = False
                    for iterations in range(timeout):
                        response = card.time(nCard)
                        time = response["time"]
                        zone = response["zone"].split(",")[1]
                        if zone != "Unknown":
                            got_time = True
                            break
                        sleep(1)
                    if not got_time:
                        print("Failed to set local time-of-day via card.time.")
                    else:
                        print(f"Setting local time-of-day to {time} {zone}.")
                        ami.set_time(time, zone)
                    command_recognized = True
                elif change["body"]["type"] == "bluetooth" and "data" in change["body"]:
                    if change["body"]["data"]:
                        ami.enable_bluetooth()
                        output = "Bluetooth enabled. Takes effect after reboot."
                    else:
                        ami.disable_bluetooth()
                        output = "Bluetooth disabled. Takes effect after reboot."
                    command_recognized = True
                elif change["body"]["type"] == "continuous" and "data" in change["body"]:
                    if change["body"]["data"]:
                        hub.set(nCard,
                                mode="continuous")
                        print("Sync mode set to continuous.")
                        print()
                        output = "Sync mode set to continuous."
                    else:
                        hub.set(nCard,
                                mode="minimum")
                        print("Sync mode set to minimum.")
                        print()
                        output = "Sync mode set to minimum."
                    command_recognized = True
            if not command_recognized:
                print("Command not recognized:")
                print(change["body"])
                print()
                output = "Command not recognized."
                # # Write new config file
                # with open(config_file_name, "w") as f:
                #     json.dump(change["body"], f, indent=4)
                # print(f"Wrote new dummy configuration to {config_file_name}.")
                # print()

            # Send output to Notehub
            print(note.add(nCard,
                           file="output.qo",
                           body={"output":output})
                           )
            print()
    else:
        print("No inbound changes.")
        print()

    return output


async def cellular_receive(i2c_path="/dev/i2c-1"):
    """Receive data from Notehub and return output string.
    
    Date: November 2023
    Author: Jonas Beuchert
    
    Args:
        i2c_path (str, optional): Path to I2C device. Defaults to "/dev/i2c-1".
            On a Raspberry Pi, the following GPIOs can be used for I2C:
            - GPIO2 (pin 3) as SDA for /dev/i2c-1
            - GPIO3 (pin 5) as SCL for /dev/i2c-1
            - Others, e.g., via bit-banging
            On a Rock Pi, the following GPIOs can be used for I2C:
            - GPIO2_A7 (pin 3) as SDA for /dev/i2c-7
            - GPIO2_B0 (pin 5) as SCL for /dev/i2c-7
            - GPIO2_A0 (pin 27) as SDA for /dev/i2c-2
            - GPIO2_A1 (pin 28) as SCL for /dev/i2c-2
            - Others, e.g., via bit-banging

    Returns:
        Output string with info or None if nothing received.
    """

    output = None

    # Connect to Notecard via I2C
    nCard = _connect_to_notecard(i2c_path)

    if _sync_and_print_status(nCard):

        ami = AmiTrap()

        return _process_incoming_changes(ami, nCard)

async def cellular_send_picture(i2c_path="/dev/i2c-1"):
    """Send most recent picture from Ami-Trap to Notehub.
    
    Compress image such that it fits into 8 KB.
    (According to https://discuss.blues.com/t/encode-and-send-a-small-image/475
    8 KB are safe.)
    
    Date: December 2023
    Author: Jonas Beuchert
    """
    DEBUG = True

    # Connect to Notecard via I2C
    nCard = _connect_to_notecard(i2c_path)

    ami = AmiTrap()
    # Get most recent picture
    picture_path = ami.get_most_recent_picture_path()
    # Read picture, convert to grey scale, and compress such that it fits into 8 KB
    image = Image.open(picture_path).convert("L")
    image.thumbnail((128, 128))  # 128x128 can be 16 KB without compressions
    # JPEG compress image and turn into bytes array. Print size in bytes
    image_bytes = io.BytesIO()
    image.save(image_bytes, format="JPEG", quality=85)
    image_bytes = image_bytes.getvalue()
    print(f"Picture size: {len(image_bytes)} bytes")
    print()

    if DEBUG:
        # Save image to /tmp/
        image.save("/tmp/image.jpg", format="JPEG", quality=85)

    # Reset binary data store on Notecard
    binary_helpers.binary_store_reset(card=nCard)
    # Send picture to Notecard
    binary_helpers.binary_store_transmit(card=nCard, data=image_bytes, offset=0)
    # Change mode to continous
    prev_sync_mode = hub.get(nCard)["mode"]
    hub.set(nCard,
            mode="continuous")
    if not _sync_and_print_status(nCard):
        print("Failed to send picture from Ami-Trap to Notehub.")
        print()
        return
    # Send picture from Notecard to Notehub
    try:
        print(note.add(nCard,
                    file="binary.qo",
                    binary=True,
                    live=True))
    except Exception as e:
        print("note.add doesn't work with binary files. Use Transaction instead.")
        print(e)
        print()
        print(nCard.Transaction({"req": "note.add",
                                 "file": "binary.qo",
                                 "binary": True,
                                 "live": True}))
    # Sync data with cloud
    if not _sync_and_print_status(nCard):
        print("Failed to send picture from Ami-Trap to Notehub.")
        print()
        return

    print("Sent picture from Ami-Trap to Notehub.")
    print()

    # Change mode back to previous mode
    hub.set(nCard,
            mode=prev_sync_mode)

    # Print current mode
    print(hub.get(nCard))
    print()

def _check_for_firmware_update(ami, nCard):
    """Check for firmware update.
    
    Args:
        ami (AmiTrap): AmiTrap object.
        nCard (notecard): Notecard object.
    """
    import binascii

    req = {"req": "dfu.status"}
    rsp = nCard.Transaction(req)
    print(rsp)
    print()

    if "mode" in rsp and rsp["mode"] == "downloading":
        print("Firmware download in progress.")
        print()
        # Set sync mode to cont. until 5 min timeout or until mode is ready
        print("Setting mode to continuous until download is complete.")
        print()
        req = {"req": "hub.set"}
        req["mode"] = "continuous"
        print(nCard.Transaction(req))
        print()
        timeout = 300
        while "mode" in rsp and rsp["mode"] == "downloading" and timeout > 0:
            sleep(1)
            timeout -= 1
            rsp = nCard.Transaction({"req":"dfu.status"})
            print(rsp)
            print()

    if "mode" in rsp and rsp["mode"] == "ready":
        try:
            print("Firmware update available.")
            print()
            length = rsp["body"]["length"]
            print("Starting firmware update...")
            print()
            req = {"req": "hub.set"}
            req["mode"] = "dfu"
            rsp = nCard.Transaction(req)
            print(rsp)
            print()
            print("Waiting for DFU mode...")
            print()
            rsp = nCard.Transaction({"req":"dfu.get","length":0})
            print(rsp)
            print()
            timeout = 61
            while "err" in rsp and timeout > 0:
                sleep(1)
                timeout -= 1
                rsp = nCard.Transaction({"req":"dfu.get","length":0})
                print(rsp)
                print()
            if timeout == 0:
                print("Failed to enter DFU mode.")
                print()
                raise Exception("Failed to enter DFU mode.")
            print("Firmware update started.")
            print()
            offset = 0
            size = 4096
            num_retries = 5
            while True:
                if offset + size > length:
                    size = length - offset

                if size <= 0:
                    break

                content = b''
                requestException = None
                for _ in range(num_retries):
                    requestException = None
                    try:
                        rsp = nCard.Transaction({"req":"dfu.get","offset":offset,"length":size})
                        if "payload" not in rsp:
                            raise Exception(f"No content available at {offset} with length {size}.")
                        content = binascii.a2b_base64(rsp["payload"])
                        break
                    except Exception as e:
                        requestException = e

            if requestException is not None:
                raise Exception(
                    f"Failed to read content after {num_retries} retries") from requestException

            offset += size

            # Save content as zip file in "/tmp/". Unzip and run install.sh.
            with open("/tmp/firmware.zip", "wb") as f:
                f.write(content)
            print(f"Downloaded {size} bytes.")
            print()
            # Unzip and run install.sh
            ami.update_firmware()
        
            print("Firmware update completed.")
            print()
            req = {"req": "dfu.status"}
            req["stop"] = True
            req["status"] = "Firmware update completed."
            rsp = card.Transaction(req)

        except Exception as e:
            print(f"An error occurred: {e}")
            print()
            req = {"req": "dfu.status"}
            req["stop"] = True
            req["status"] = "Firmware update failed."
            rsp = card.Transaction(req)

    else:

        print("No firmware update available.")
        print()

    # If mode is continuous, set it back to minimum
    if hub.get(nCard)["mode"] == "continuous":
        hub.set(nCard,
                mode="minimum")
        print("Sync mode set to minimum.")
        print()

async def cellular_send_and_receive(i2c_path="/dev/i2c-1"):
    """Send status data from Ami-Trap to Notehub. Receive data from Notehub and send output string back.

    Date: November 2023
    Author: Jonas Beuchert
    
    Args:
        i2c_path (str, optional): Path to I2C device. Defaults to "/dev/i2c-1".
            On a Raspberry Pi, the following GPIOs can be used for I2C:
            - GPIO2 (pin 3) as SDA for /dev/i2c-1
            - GPIO3 (pin 5) as SCL for /dev/i2c-1
            - Others, e.g., via bit-banging
            On a Rock Pi, the following GPIOs can be used for I2C:
            - GPIO2_A7 (pin 3) as SDA for /dev/i2c-7
            - GPIO2_B0 (pin 5) as SCL for /dev/i2c-7
            - GPIO2_A0 (pin 27) as SDA for /dev/i2c-2
            - GPIO2_A1 (pin 28) as SCL for /dev/i2c-2
            - Others, e.g., via bit-banging
    """

    # Connect to Notecard via I2C
    nCard = _connect_to_notecard(i2c_path)

    ami = AmiTrap()

    loop = False

    while True:

        _gather_status_data(ami, nCard)

        if not _sync_and_print_status(nCard):
            print("Failed to send data from Ami-Trap to Notehub.")
            print()
            return
        
        print("Sent data from Ami-Trap to Notehub.")
        print()

        output = _process_incoming_changes(ami, nCard)

        _check_for_firmware_update(ami, nCard)

        if output is None and not loop:
            return

        if not _sync_and_print_status(nCard):
            print("Failed to send output from Ami-Trap to Notehub.")
            print()
            return
        print("Sent output from Ami-Trap to Notehub.")
        print()

        if output == "Sync mode set to continuous.":
            loop = True
        elif output == "Sync mode set to minimum.":
            loop = False

        if not loop:
            return

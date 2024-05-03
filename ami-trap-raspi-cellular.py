from amitrap_cellular import cellular_send_and_receive
import asyncio
from amitrap import AmiTrap


async def main(interval_minutes=15, port="/dev/i2c-1"):
    print()

    while True:
        print("Run Ami-Trap cellular program (send and receive).")
        print(f"Sending data every {interval_minutes} minutes.")
        print()

        try:

            while True:
            
                # Call cellular_send() asynchronously
                asyncio.create_task(cellular_send_and_receive(i2c_path=port))

                # Sleep for the specified interval
                await asyncio.sleep(interval_minutes * 60)

        except Exception as e:
            print(f"An error occurred: {e}")
            print("Restarting program...")
            print()
            continue


if __name__ == "__main__":

    print()

    if AmiTrap().get_is_raspberrypi():
        port = "/dev/i2c-1"
        print("Raspberry Pi detected.")
        print("Using I2C port 1.")
        print()
    elif AmiTrap().get_is_rockpi():
        port = "/dev/i2c-7"
        print("Rock Pi detected.")
        print("Using I2C port 7.")
        print()
    else:
        print("No Raspberry Pi or Rock Pi detected.")
        print("Exiting program...")
        print()
        exit()

    asyncio.run(main(interval_minutes=60*6, port=port))

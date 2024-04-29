

"""
File: ami-trap-raspi-cellular-send-amber.py
Date: March 2024
Autor: Jonas Beuchert
Description: This script runs the Ami-Trap cellular program to send data at regular intervals. 
             It detects the type of device (Raspberry Pi or Rock Pi) and uses the appropriate I2C port.
"""

from amitrap_cellular import cellular_send_amber, monitor_amber_files
import asyncio


async def cellular_loop(interval_minutes=15):

    print()

    while True:
        print("Run Ami-Trap cellular program (send).")
        print(f"Sending data every {interval_minutes} minutes.")
        print()

        try:

            while True:
            
                # Call cellular_send() asynchronously
                asyncio.create_task(cellular_send_amber())

                # Sleep for the specified interval
                await asyncio.sleep(interval_minutes * 60)

        except Exception as e:
            print(f"An error occurred: {e}")
            print("Restarting program...")
            print()
            continue


async def file_monitoring_loop(interval_seconds=10):

    print()

    while True:
        print("Run Ami-Trap file monitoring program.")
        print(f"Checking for new files every {interval_seconds} seconds.")
        print()

        try:

            while True:
            
                # Call cellular_send() asynchronously
                asyncio.create_task(monitor_amber_files(path="~/Desktop/model_data_bookworm/results"))

                # Sleep for the specified interval
                await asyncio.sleep(interval_seconds)

        except Exception as e:
            print(f"An error occurred: {e}")
            print("Restarting program...")
            print()
            continue


if __name__ == "__main__":

    print()

    asyncio.run(cellular_loop(interval_minutes=30))

    asyncio.run(file_monitoring_loop(interval_seconds=10))

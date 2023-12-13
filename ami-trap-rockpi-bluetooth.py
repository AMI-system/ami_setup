import asyncio
from amitrap_bluetooth import bluetooth_loop, power_on_bluetooth, power_off_bluetooth


async def run_bluetooth_robustly():
    """Run Bluetooth loop. Restart if an exception occurs.

    Date: November 2023
    Author: Jonas Beuchert

    Bluetooth must be turned on before calling this function.
    Bluetooth can be turned off after calling this function."""

    while True:
        try:
            # Run Bluetooth loop
            await bluetooth_loop(is_rockpi=True)

        except Exception as e:
            print(f"An error occurred: {e}")
            print("Restarting program...")
            print()
            continue


async def no_button_main(duration_minutes=None):
    """Run Bluetooth continuously or for a specified duration.

    Date: November 2023
    Author: Jonas Beuchert

    Powers on Bluetooth.
    Advertises Bluetooth service for pairing.
    Powers off Bluetooth.

    Args:
        duration_minutes (int, optional): Duration in minutes. Defaults to None."""

    if duration_minutes is None:
        print("Run Bluetooth continuously.")
        print()

        # Power on Bluetooth
        await power_on_bluetooth()

        # Run Bluetooth, restart if an exception occurs
        await run_bluetooth_robustly()

    else:
        print(f"Run Bluetooth for {duration_minutes} minute(s).")
        print()

        # Power on Bluetooth
        await power_on_bluetooth()

        # Run Blutooth asynchronously, restart if an exception occurs
        task = asyncio.create_task(run_bluetooth_robustly())

        # Wait for the specified duration
        await asyncio.sleep(duration_minutes * 60)

        # Cancel Bluetooth task
        task.cancel()

        # Power off Bluetooth
        await power_off_bluetooth()


if __name__ == "__main__":

    print()

    # Not possible to disable Bluetooth with a button/switch on the device
    # So, just run the program continuously

    asyncio.run(no_button_main())

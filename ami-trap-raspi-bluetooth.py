import asyncio
from amitrap_bluetooth import bluetooth_loop, power_on_bluetooth, power_off_bluetooth
import RPi.GPIO as GPIO


async def run_bluetooth_robustly():
    """Run Bluetooth loop. Restart if an exception occurs.

    Date: November 2023
    Author: Jonas Beuchert

    Bluetooth must be turned on before calling this function.
    Bluetooth can be turned off after calling this function."""

    while True:
        try:
            # Run Bluetooth loop
            await bluetooth_loop()

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


async def button_main(GPIO_PIN=17):
    """Run Bluetooth when button/switch is pressed.

    Date: November 2023
    Author: Jonas Beuchert
    

    Powers on Bluetooth when GPIO pin is pulled low.
    Advertises Bluetooth service for pairing.
    Powers off Bluetooth when GPIO pin is pulled high.
    
    Args:
        GPIO_PIN (int, optional): GPIO pin number (BCM) of the switch/button. Defaults to 17 (GPIO17)."""

    # Set the GPIO mode to BCM
    GPIO.setmode(GPIO.BCM)

    # Set the GPIO pin as input with pull-up resistor
    GPIO.setup(GPIO_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    while True:
        print("Run Bluetooth when button is pressed.")
        print()

        try:
            # Power off Bluetooth
            await power_off_bluetooth()

            bluetooth_on = False

            while True:
                if GPIO.input(GPIO_PIN) == GPIO.LOW and not bluetooth_on:
                    await power_on_bluetooth()

                    task = asyncio.create_task(bluetooth_loop())

                    bluetooth_on = True

                elif GPIO.input(GPIO_PIN) == GPIO.HIGH and bluetooth_on:
                    task.cancel()

                    await power_off_bluetooth()

                    bluetooth_on = False

                # Delay for a short period before checking again (1 second)
                await asyncio.sleep(1)

        except Exception as e:
            print(f"An error occurred: {e}")
            print("Restarting program...")
            print()
            continue


if __name__ == "__main__":
    # Can Bluetooth be enabled/disabled with a button/switch on the device?
    HAS_BUTTON = False

    print()

    if not HAS_BUTTON:
        # Not possible to disable Bluetooth with a button/switch on the device
        # So, just run the program continuously

        asyncio.run(no_button_main())

    else:
        # Possible to disable Bluetooth with a button/switch on the device
        # So, run the program when the button/switch is pressed

        asyncio.run(button_main())

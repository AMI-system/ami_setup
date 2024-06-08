"""
test_wpi_script_generator_ags.py

This script is used to test the functionality of the WittyPi script generator.

Author: Jonas Beuchert (UKCEH)
Date: 8 June 2024
"""
# 50 times, do:
# Generate a random date string between 10th June 00:00 BST and 16th June 23:59:59 BST
# The date string should be in the format "DD JUN 2024 HH:MM:SS".
# Then, run a command sudo date -s "2024-06-DD HH:MM:SS" to set the system time to the generated date.
# Then, write the time to the Witty Pi RTC using printf '1\n13' | /home/pi/wittypi/wittyPi.sh.
# Then, run the Witty Pi script generator like sudo python3 /home/pi/wittypi/wpi_script_generator_ags.py.

import random
import subprocess
import time

# Define the start and end date for the random date generation
start_date = time.mktime(time.strptime("10 Jun 2024 00:00:00", "%d %b %Y %H:%M:%S"))
end_date = time.mktime(time.strptime("16 Jun 2024 23:59:59", "%d %b %Y %H:%M:%S"))

# Run the Witty Pi script generator 50 times
for i in range(50):
    # Generate a random date string with minute and second set to zero
    random_date = time.strftime("%d JUN 2024 %H:00:00", time.localtime(random.randint(start_date, end_date)))
    print(f"Setting system time to {random_date}...")

    # Set the system time
    subprocess.run(f"sudo date -s '{random_date}'", shell=True)

    # Write the time to the Witty Pi RTC
    subprocess.run("printf '1\n13' | /home/pi/wittypi/wittyPi.sh", shell=True)
    # Run the Witty Pi script generator
    output = subprocess.check_output("sudo python3 /home/pi/scripts/wpi_script_generator_ags.py", shell=True, universal_newlines=True)

    # The output should contain "Schedule next shutdown at 2024-06-DD HH", DD and HH are the next time after the current time from the following table:
    # 11th June 4am
    # 12th June 11am
    # 13th June 3am
    # 14th June 11am
    # 15th June 3am
    # 16th June 11am
    # 18th June 4am

    target_string = "Schedule next shutdown at: 2024-06-"
    # Select next date based on which one is next after random_date from the table and append to the target string
    if random_date < "11 JUN 2024 04:59:59":
        target_string += "11 04"
    elif random_date < "12 JUN 2024 12:59:59":
        target_string += "12 12"
    elif random_date < "13 JUN 2024 04:59:59":
        target_string += "13 04"
    elif random_date < "14 JUN 2024 12:59:59":
        target_string += "14 12"
    elif random_date < "15 JUN 2024 04:59:59":
        target_string += "15 04"
    elif random_date < "16 JUN 2024 12:59:59":
        target_string += "16 12"
    else:
        target_string += "18 04"
    
    print()
    print("###########################################################")
    print(f"Test {i+1}/50")
    print(f"Test date: {random_date}")
    print(f"Target string: {target_string}")
    print("Output:")
    print(output)
    
    if target_string in output:
        print("Test passed.")
    else:
        print("Test failed.")
        break

    print("###########################################################")
    print()

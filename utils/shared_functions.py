#!/usr/bin/env python3
#-*- coding: utf-8 -*-

from datetime import datetime, timedelta
from timezonefinder import TimezoneFinder
import json
import pytz
import subprocess
import re


def get_current_time(lat, lng):
    """
    Get the current local time for a given latitude and longitude.

    This function determines the timezone based on the provided geographical
    coordinates (latitude and longitude), then retrieves and returns the
    current local time in that timezone.

    Parameters:
    lat (float): The latitude of the location.
    lng (float): The longitude of the location.

    Returns:
    str: The current local time in ISO 8601 format, or an error message if
    the timezone could not be determined.

    Raises:
    pytz.UnknownTimeZoneError: If the timezone name is not recognized.

    Examples:
    >>> get_current_time(40.7128, -74.0060)  # New York City coordinates
    '2024-05-14T12:34:56-04:00'
    >>> get_current_time(51.5074, -0.1278)  # London coordinates
    '2024-05-14T17:34:56+01:00'
    """

    # Get the timezone name from coordinates
    tf = TimezoneFinder()
    timezone_str = tf.timezone_at(lat=lat, lng=lng)
    if timezone_str is None:
        return "Timezone could not be determined"

    # Convert to timezone-aware datetime object
    timezone = pytz.timezone(timezone_str)
    current_time = datetime.now(timezone)

    # Format the datetime in ISO 8601 format
    return current_time


def get_survey_start_end_datetimes(current_time, start_time_str, end_time_str):
    """
    Obtain the start and end datetime for a survey period.

    This function converts start and end time strings to datetime objects 
    based on the current date and timezone of the `current_time`. It ensures 
    that the end datetime is always after the start datetime, adjusting for 
    cases where the survey period spans midnight.

    Parameters:
    current_time (datetime): The current datetime object, timezone-aware.
    start_time_str (str): The survey start time as a string in "HH:MM:SS" format.
    end_time_str (str): The survey end time as a string in "HH:MM:SS" format.

    Returns:
    tuple: A tuple containing the start and end datetimes in ISO 8601 format.

    Raises:
    ValueError: If the current time is outside the survey start and end hours.

    Examples:
    >>> current_time = datetime(2024, 5, 14, 15, 30, tzinfo=pytz.UTC)
    >>> get_survey_start_end_datetimes(current_time, "14:00:00", "16:00:00")
    ('2024-05-14T14:00:00+0000', '2024-05-14T16:00:00+0000')
    >>> current_time = datetime(2024, 5, 14, 1, 30, tzinfo=pytz.UTC)
    >>> get_survey_start_end_datetimes(current_time, "23:00:00", "02:00:00")
    ('2024-05-13T23:00:00+0000', '2024-05-14T02:00:00+0000')
    """

    # Convert start and end time strings to time objects
    start_time = datetime.strptime(start_time_str, "%H:%M:%S").time()
    end_time = datetime.strptime(end_time_str, "%H:%M:%S").time()

    # Extract date from specified datetime
    current_date = current_time.date()

    # Initialize start and end datetime
    start_datetime = datetime.combine(current_date, start_time, current_time.tzinfo)
    end_datetime = datetime.combine(current_date, end_time, current_time.tzinfo)

    # Adjust end datetime if it falls on the next day
    if start_datetime <= current_time <= end_datetime:
        # Case 1: Current time is between start and end times
        pass
    elif start_datetime <= current_time and current_time >= end_datetime:
        # Case 2: Current time is after the start time and end time is on the next day
        end_datetime += timedelta(days=1)
    elif start_datetime >= current_time and current_time <= end_datetime:
        # Case 3: Current time is before the start time and start time is on the previous day
        start_datetime -= timedelta(days=1)
    else:
        # Current time is outside the valid survey period
        raise ValueError("This script cannot be run outside of the survey start and end hours.")

    return start_datetime, end_datetime


def remove_comments(data):
    """
    Recursively remove 'COMMENT' entries from a nested dictionary.

    This function traverses a nested dictionary and removes any key-value 
    pairs where the key is 'COMMENT'. It processes dictionaries recursively.

    Parameters:
    data (dict): The nested dictionary from which 'COMMENT' entries will be removed.

    Returns:
    None: The function modifies the input dictionary in place and does not return anything.

    Examples:
    >>> data = {
    ...     'name': 'John',
    ...     'age': 30,
    ...     'COMMENT': 'This is a comment',
    ...     'address': {
    ...         'city': 'New York',
    ...         'COMMENT': 'Another comment'
    ...     }
    ... }
    >>> remove_comments(data)
    >>> print(data)
    {'name': 'John', 'age': 30, 'address': {'city': 'New York'}}
    """

    if isinstance(data, dict):
        # Check if 'COMMENT' key exists and delete it
        if "COMMENT" in data:
            del data["COMMENT"]
        # Recursively process each value in the dictionary
        for key, value in list(data.items()):
            remove_comments(value)
    elif isinstance(data, list):
        # Recursively process each item in the list
        for item in data:
            remove_comments(item)


# Update camera and motion configuration and store metadata
def update_motion_config(script_path, config_data):
    with open(script_path, 'r') as script_file:
        script_lines = script_file.readlines()

    # For each line in the motion.config file
    for i, line in enumerate(script_lines):
        # Ignore lines starting with #
        if line.strip().startswith('#'):
            continue

        # List every motion configuration parameter and addionally specify the camera ID (videodevice) and exif_text (field for metadata storage)
        field_search = "exif_text"

        # Search for the occurence of the field name, followed by one or more whitespaces
        pattern = fr'({field_search} )(\S+)'
        match = re.search(pattern, line)

        if match:
            # Obtain the field name
            field,_ = line.split(' ', 1)

            # Stops the capture of field name mentions within the exif_text string
            # The exif_text field also includes a semicolon before the field name
            if field == field_search or field == f";{field_search}":
                # Ignore fields that will vary between surveying components
                fields_ignore = ["ultrasonic_operation", "ultrasonic_settings", "audio_operation", "audio_settings"]
                metadata =  dict((field, config_data[field]) for field in config_data if field not in fields_ignore)

                # Replace the whole line to remove the semicolon
                new_line = line.replace(line, f"exif_text \'{json.dumps(metadata)}\'\n")
                print(f"Updated exif metadata configuration") 
                script_lines[i] = new_line
                break
            else:
                continue

    # Write the updated script content back to the file
    with open(script_path, 'w') as script_file:
        script_file.writelines(script_lines)


def get_sunset_sunrise_times(latitude, longitude, date):
    """
    Get the sunset and sunrise times for a given location and date.

    This function uses the Helicron command-line tool to retrieve the sunset and sunrise
    times for the specified latitude, longitude, and date. It returns the times as
    naive datetime objects.

    Parameters:
    latitude (float): The latitude of the location.
    longitude (float): The longitude of the location.
    date (datetime): The date for which to get the sunset and sunrise times.

    Returns:
    tuple: A tuple containing two datetime objects:
        - sunset (datetime): The time of sunset on the specified date.
        - sunrise (datetime): The time of sunrise on the specified date.

    Raises:
    RuntimeError: If the Helicron command fails.

    Examples:
    >>> from datetime import datetime
    >>> get_sunset_sunrise_times(52.752845, -3.253449, datetime(2024, 5, 14))
    (datetime.datetime(2024, 5, 14, 20, 45, tzinfo=None), datetime.datetime(2024, 5, 14, 5, 15, tzinfo=None))
    """

    # Construct the Helicron command
    # heliocron -date 2020-02-25 --latitude 52.752845 --longitude -3.253449 report --json
    command = ["/home/pi/scripts/heliocron", 
               "--date", date.strftime("%Y-%m-%d"), 
               "--latitude", str(latitude), 
               "--longitude", str(longitude), 
               "report", "--json"]

    # Run the command
    result = subprocess.run(command, capture_output=True, text=True)
    # print(result)

    # Check if the command was successful
    if result.returncode == 0:
        # Split the output by newlines and return civil dawn and civil dusk times
        stdout = json.loads(result.stdout)
        #print(stdout)
        sunset = datetime.strptime(stdout['sunset'], '%Y-%m-%dT%H:%M:%S%z')
        sunrise = datetime.strptime(stdout['sunrise'], '%Y-%m-%dT%H:%M:%S%z')
        return sunset.replace(tzinfo=None), sunrise.replace(tzinfo=None)
    else:
        # Handle error
        raise RuntimeError(f"Error executing Helicron command: {result.stderr}")


def read_json_config(json_path):
    """
    Load the configuration parameters from a JSON file.

    This function reads a JSON file from the specified path and returns its
    contents as a dictionary.

    Parameters:
    json_path (str): The path to the JSON configuration file.

    Returns:
    dict: A dictionary containing the configuration parameters.

    Raises:
    FileNotFoundError: If the specified JSON file does not exist.
    json.JSONDecodeError: If the file is not a valid JSON.

    Examples:
    >>> config = read_json_config('/path/to/config.json')
    >>> print(config)
    {'param1': 'value1', 'param2': 'value2'}
    """

    with open(json_path, 'r') as json_file:
        return json.load(json_file)


def get_previous_sunday():
    """
    Get the date of the previous Sunday.

    This function calculates the date of the most recent Sunday. If today
    is Sunday, it returns today's date.

    Returns:
    datetime: A datetime object representing the previous Sunday's date.

    Examples:
    >>> get_previous_sunday()
    datetime.datetime(2024, 5, 12, 0, 0)
    """

    # Get today's date
    today = datetime.now()

    # Get the day of the week (0 = Monday, 6 = Sunday)
    day_of_week = today.weekday()

    if day_of_week == 6:  # If today is Sunday
        return today
    else:
        # Calculate the date for the previous Sunday
        previous_sunday = today - timedelta(days=day_of_week + 1)
        return previous_sunday


def time_difference(start_date, end_date):
    """
    Calculate the time difference between two dates.

    This function calculates the difference between two datetime objects
    and returns the difference in days, hours, and minutes.

    Parameters:
    start_date (datetime): The start datetime.
    end_date (datetime): The end datetime.

    Returns:
    tuple: A tuple containing three elements:
        - days (int): The number of days in the time difference.
        - hours (int): The number of hours in the time difference.
        - minutes (int): The number of minutes in the time difference.

    Examples:
    >>> from datetime import datetime
    >>> start_date = datetime(2024, 5, 12, 8, 0, 0)
    >>> end_date = datetime(2024, 5, 14, 10, 30, 0)
    >>> time_difference(start_date, end_date)
    (2, 2, 30)
    """
    time_delta = end_date - start_date

    # Get the total seconds in the time difference
    total_seconds = time_delta.total_seconds()

    # Convert time delta to days, hours, and minutes
    days = int(total_seconds) // (24 * 3600)
    hours = (int(total_seconds) % (24 * 3600)) // 3600
    minutes = int(total_seconds % 3600) // 60

    return days, hours, minutes

def custom_format_datetime(dt):
    """
    Convert a datetime object to the custom format 'YYYY_MM_DD__HH_MM_SS_{plus|minus}_HHMM'.
    
    Args:
        dt (datetime): The datetime object to be formatted.
    
    Returns:
        str: The datetime string in the custom format. 
             For example: '2023_05_09__23_45_00_minus_0001'.
    
    Example:
        >>> from datetime import datetime, timezone, timedelta
        >>> dt = datetime(2023, 5, 9, 23, 45, 0, tzinfo=timezone(timedelta(hours=-1)))
        >>> custom_format_datetime(dt)
        '2023_05_09__23_45_00_minus_0100'
    """
    # Extract the formatted date and time parts
    formatted_date_time = dt.strftime('%Y_%m_%d__%H_%M_%S')
    
    # Handle the timezone part
    timezone_offset = dt.strftime('%z')  # Get the timezone part in ±HHMM format
    if timezone_offset.startswith('+'):
        formatted_timezone = timezone_offset.replace('+', '_plus_')
    else:
        formatted_timezone = timezone_offset.replace('-', '_minus_')
    
    # Combine the formatted parts
    custom_formatted_string = f"{formatted_date_time}{formatted_timezone}"
    
    return custom_formatted_string
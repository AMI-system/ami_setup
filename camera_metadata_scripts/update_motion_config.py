#Script to set configiration set in config.json 
import json
import re

# Load the config paramters from the JSON file
def read_json_config(json_path):
    with open(json_path, 'r') as json_file:
        return json.load(json_file)

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

# Replace with the actual path to your motion configuration file as needed
motion_script_path = 'motion_scripts/motion.conf' # /etc/motion/motion.conf

# Path to config.json file
json_config_path = "config.json" # /home/pi/config.json

# Read the JSON configuration file
json_config = read_json_config(json_config_path)

# Update motion settings in the shell script file
update_motion_config(motion_script_path, json_config)
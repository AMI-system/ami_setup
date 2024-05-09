#Script to set configiration set in config.json 
import json
import re

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
motion_script_path = "/etc/motion/motion.conf"

# Read the config file
config_path = Path('/home/pi/config.json')
with config_path.open() as fp:
    config = json.load(fp)











#Save metadata as dictionary using same heirarchical structure as the config dictionary
metadata = {
     
     "motion_event_data":{
     
      "event_ids": {
         "parent_event_id": parent_event_id,
         "event_id": eventID
      },

    "date_fields": {
        "event_date": current_time,
        "recording_period_start_time": None,
        "recording_period_end_time": None
        },

    "file_characteristics":{
         "file_path": full_path,
         "file_type": audio_type
        }
   }

   }


# Update motion settings in the shell script file
update_motion_config(motion_script_path, config)
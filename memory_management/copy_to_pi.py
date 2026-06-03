'''
File:   copy_to_pi.py

Spec:   This script is used to copy WISPR data (stored as .dat files) 
        from the WISPR3 to an SSD storage device interfaced to the Raspberry Pi.
        This script finds both storage devices and copies the data. In general, this 
        script is mostly a wrapper for the 'rsync' command, which is 
        used to do the actual copying. 

I/O:    This program accepts the data source and desitnation directories as function inputs.
        However, default values are provided for both. 

Usage:  <copy_to_pi.py>
'''

import subprocess 
import yaml
from pathlib import Path

def get_default_paths_from_config(config_path="config.yaml"):
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
        path_to_wispr3_data = config.get('WISPR3_DATA_DIR')
        path_to_ssd = config.get('SSD_DIR')
    return path_to_wispr3_data, path_to_ssd

def soft_search_WISPR(where_to_look):
    '''
    This function looks for a WISPR3 directory in a user specified location.
    This function allows for non-exact matches. Be careful!
    Inputs:
        Where_to_look: The directory to look for the WISPR3 data directory.
        Ex. If the files are in <path/to/WISPR3_storage/files> (omit 'files' part of this string')
        Use: <path/to/WISPR3_MicroSD> 
        The "path/to" and "WISPR3_MicroSD" will be split

    Outputs: 
        <path/to/WISPR3_MicroSD> (NO TRAILING SLASH)
    '''
    # 1. Convert the input into a Path object.
    orignal_full_path = Path(where_to_look).resolve() 

    #2. Strip the path into the parent_dir and target_dir.
    parent_dir = orignal_full_path.parent
    target_dir = orignal_full_path.name
    target_dir_upper = target_dir.upper() # Convert to uppercase for case-insensitive matching.

    # 3. Check that the parent directory exists. If not, raise an error.
    if not parent_dir.is_dir():
        raise FileNotFoundError(f"Parent directory {parent_dir} not found.")
    
    print(f"Looking in {parent_dir} for WISPR3 MicroSD card named something like {target_dir}...")

    # 4. List the directories in the parent directory.
    for item in parent_dir.iterdir():
        if item.is_dir():
            current_dir_upper = item.name.upper()
            
            # 5. Look for a directory that contains 'WISPR' or the target_dir in the name. 
            if "WISPR" in current_dir_upper or target_dir_upper in current_dir_upper:
                # 6. Return the path without the trailing slash.
                discovered_path = str(item) # Path lib natively comits the trailing slash when cast to a string. 
                print(f"soft_search_WISPR found: {discovered_path}")
    
                return discovered_path # :D 
            
    # 7. If no directory is found, raise an error.
    raise FileNotFoundError(f"No directory containing 'WISPR' or '{target_dir}' found in {parent_dir}.")

def soft_search_SSD(where_to_look):
    '''
    This function looks for an SSD directory instead of a WISPR3 directory.
    '''
    # 1. Convert the input into a Path object.
    orignal_full_path = Path(where_to_look).resolve() 

    #2. Strip the path into the parent_dir and target_dir.
    parent_dir = orignal_full_path.parent
    target_dir = orignal_full_path.name
    target_dir_upper = target_dir.upper() # Convert to uppercase for case-insensitive matching.

    # 3. Check that the parent directory exists. If not, raise an error.
    if not parent_dir.is_dir():
        raise FileNotFoundError(f"Parent directory {parent_dir} not found.")
    
    print(f"Looking in {parent_dir} for SSD card named something like {target_dir}...")

    # 4. List the directories in the parent directory.
    for item in parent_dir.iterdir():
        if item.is_dir():
            current_dir_upper = item.name.upper()
            
            # 5. Look for a directory that contains 'SSD' or the target_dir in the name. 
            # TODO: what should this actually be? 
            if "SSD" in current_dir_upper or target_dir_upper in current_dir_upper:
                # 6. Return the path without the trailing slash.
                discovered_path = str(item) # Path lib natively comits the trailing slash when cast to a string. 
                print(f"soft_search_SSD found: {discovered_path}")
    
                return discovered_path # :D 
            
    # 7. If no directory is found, raise an error.
    raise FileNotFoundError(f"No directory containing 'SSD' or '{target_dir}' found in {parent_dir}.")


def copy_to_pi():
    '''
    This function copies WISPR data from the WISPR3 to the SSD storage device
    using rsync. 

    Inputs:
        path_to_wispr3_data: The path to the WISPR3 data directory. 
        path_to_ssd: The path to the SSD storage device. 

    Outputs:
        Status. 
    '''
    # Get the default paths from the config file.
    path_to_wispr3_data, path_to_ssd = get_default_paths_from_config()
    # Debug 
    print(f"Path to WISPR3 data: {path_to_wispr3_data}")
    print(f"Path to SSD: {path_to_ssd}")

    # Check that the paths are valid and make modifications if necessary.
    path_to_wispr3_data = soft_search_WISPR(path_to_wispr3_data) 
    path_to_ssd = soft_search_SSD(path_to_ssd)
    # Debug
    print(f"Adjusted path to WISPR3 data: {path_to_wispr3_data}")
    print(f"Adjusted path to SSD: {path_to_ssd}")

    # Construct the rsync command as a list of arguments
    # Store everything inside "WISPR_data" on the SSD. 
    rsync_command = [
        "rsync", 
        "-ahv", 
        "--update", 
        path_to_wispr3_data, 
        f"{path_to_ssd}/WISPR_data/"
    ]

    # Execute the rsync command. 
    try:
        # Run RSYNC. 
        subprocess.run(rsync_command, check=True) 
        print(f"\nSuccessfully copied WISPR data from {path_to_wispr3_data} to {path_to_ssd}/WISPR_data/")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\nError copying WISPR data: {e}")
        return False


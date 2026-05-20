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

###################################################################
# CONFIGURATION DEFAULTS
path_to_wispr3_data = "/media/pi/WISPR3_DATA" # TODO: make this correct
path_to_ssd = "/media/pi/SSD" # TODO: make this correct 
###################################################################

def copy_to_pi(path_to_wispr3_data=path_to_wispr3_data, path_to_ssd=path_to_ssd):
    '''
    This function copies WISPR data from the WISPR3 to the SSD storage device
    using rsync. 

    Inputs:
        path_to_wispr3_data: The path to the WISPR3 data directory. 
        path_to_ssd: The path to the SSD storage device. 

    Outputs:
        Status. 
    '''
    # Construct the rsync command
    rsync_command = f"rsync -ah --update {path_to_wispr3_data} {path_to_ssd}" # Careful with the trailing slashes here.

    # Execute the rsync command
    subprocess.run(rsync_command)

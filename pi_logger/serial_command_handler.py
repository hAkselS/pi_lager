'''
File:   serial_command_handler.py

Spec:   This script listens for serial commands from the Seaglider and 
        dispatches functions and scripts accordingly. There are two
        primary commands: 'start' and 'download'. When start is received,
        this script will launch main.py. This script also has a method to 
        stop main.py if download is received while main.py is still running.
        When download is received, this script will call prep_download() which
        summarizes and packetizes the results from the most recent dive and 
        sends them to the Seaglider through serial (or ymodem TBD).

I/O:    This program listens on a serial port (default: /dev/ttyXXX) for commands from the Seaglider.
        This program outputs the results of the most recent dive to the Seaglider through serial (or ymodem TBD).
        Allowed commands are:
            1. start 
                - Receives: 'start,a,12345678,2026-08-19T20:59:20Z'
                            '\r'
                - (Yes, a new line then a \return)
                - Launches main.py and analyzes directive stored in param. 
                - Params must be a number between 0 and 15,999,999 (TODO: needs testing)
            2. download 
                - Prepares data for download and sends a packet to Seaglider. 

ID: sch

Usage:  <python3 pi_logger/serial_command_handler.py>
'''

import subprocess
import time
import sys
import os
import signal
import serial
from datetime import datetime, timezone

#####################################################################
# CONFIGURATION DEFAULTS
# TODO: MOVE THESE TO CONFIG.YAML
SERIAL_PORT = '/dev/ttys001'  # Probably /dev/ttyAMA0 or similar on Pi
BAUD_RATE = 9600
TERMINATOR = '\r' # How pi_logger recognizes a complete line # TODO: test on glider!!!
DELIMITER = ',' # Used to separate 'start,dive/climb,param,datetime' 

MAIN_SCRIPT_PATH = 'pi_logger/main.py'  # Path to main.py relative to this script
#####################################################################


#####################################################################
# GLOBAL STATE FLAGS & STATUS VARIABLES
download_received_early = False
download_called_prematurely = False

# Process management state
main_process = None
start_command_received = False
#####################################################################


# ==============================================================================
# --- Handler Functions ---
# ==============================================================================
def set_pi_datetime(date_string):
    # Parse ISO format (replace 'Z' with explicit UTC offset for older Python versions)
    dt = datetime.fromisoformat(date_string.replace("Z", "+00:00"))

    # Format as 'YYYY-MM-DD HH:MM:SS' in UTC
    formatted_time = dt.astimezone(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")

    # Use a subprocess to set the datetim
    # TODO: TEST ME ON THE RASPBERRY PI
    # subprocess.run(["sudo", "date", "-u", "-s", formatted_time], check=True)
    
    new_time = datetime.now(timezone.utc)
    print(f"\nsch: set_pi_datetime has been called with string -> [{date_string}]\n" \
    f"     new datetime -> [{new_time}]")


def set_mission_params(param_string):
    print(f"sch: set_mission_params has been called with string -> [{param_string}]")
    # Implement later
    pass

def set_dive_climb(dive_letter):
    print(f"sch: set_dive_climb has been called with letter -> [{dive_letter}]")
    # TODO: save dive climb status to

def start_main_dot_py():
    print(f"sch: start_mission has been called")


# def prep_download():
#     """
#     Called before or when the 'download' command is received.
#     Gathers all information to be transfered to the glider to radio transmission to shore
#     into once text file and finishes.
#     """
#     global download_received_early, download_called_prematurely
#     print("sch: Executing prep_download()...")
#     print(f"  └─ Flag (download_received_early): {download_received_early}")
#     print(f"  └─ Flag (download_called_prematurely): {download_called_prematurely}")
#     # TODO: Implement download preparation logic here




# ==============================================================================
# --- Process Control Helpers ---
# ==============================================================================
# TODO: uncomment when ready
# def stop_main_process():
#     """
#     Politely attempts to shut down main.py using SIGTERM for 10 seconds.
#     If main.py does not terminate in time, forcefully kills it with SIGKILL.
#     """
#     global main_process
#     if main_process is None or main_process.poll() is not None:
#         return  # Process is not running

#     print("sch: Politely requesting main.py to stop (SIGTERM)...")
#     main_process.terminate()

#     try:
#         # Wait up to 10 seconds for graceful exit
#         main_process.wait(timeout=10)
#         print("sch: main.py stopped cleanly.")
#     except subprocess.TimeoutExpired:
#         print("sch: main.py timed out after 10s. Forcefully terminating (SIGKILL)...")
#         main_process.kill()
#         main_process.wait()  # Ensure process resources are cleaned up
#         print("sch: main.py forcefully terminated.")

# def shutdown_pi():
#     """
#     Called after prep_download() completes.
#     """
#     print("sch: Executing shutdown_pi()...")
#     # TODO: Implement system shutdown logic here (e.g., os.system("sudo shutdown -h now"))



# ==============================================================================
# --- Main Serial Listener Loop ---
# ==============================================================================
def run_serial_handler():
    global start_command_received, main_process
    global download_received_early, download_called_prematurely

    print(f"sch: Starting serial listener on {SERIAL_PORT} @ {BAUD_RATE} baud...\n")

    try:
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
    except Exception as e:
        print(f"[Error] Failed to open serial port {SERIAL_PORT}: {e}")
        sys.exit(1)

    buffer = ""

    while True:
        # Check if main.py exited on its own (for status awareness)
        # TODO: reinstate this when ready
        # if main_process is not None and main_process.poll() is not None:
        #     # Process finished naturally
        #     # TODO: alter flags for more aksel style design 
        #     # TODO: when main finishes, run packetize results
        #     pass

        # Read available bytes from serial
        if ser.in_waiting > 0:
            data = ser.read(ser.in_waiting).decode('utf-8', errors='ignore')
            buffer += data # Buffer is necessary so nothing is lost if a second packet comes in

            # Handle START ('start') scenario
            if 'start' in buffer:
                parsed_start_cmd = buffer.strip().split(",")
                print(f"sch: start case: parsed_start_cmd -> [{parsed_start_cmd}]")
                pi_start, pi_dive, pi_params, pi_date = parsed_start_cmd

                # Set date time 
                set_pi_datetime(pi_date)

                # Set param values (does nothing right now)
                set_mission_params(pi_params)

                # Store dive/climb status
                set_dive_climb(pi_dive)

                # Start main.py
                start_main_dot_py()

                # Reset the buffer
                buffer = ''

            # Handle DOWNLOAD ('download') scenario
            elif 'download' in buffer:
                parsed_download_cmd = buffer.strip()
                print(f"sch: download case: parsed_download_cmd -> [{parsed_download_cmd}]")

                #TODO: handle download 

                # Reset the buffer
                buffer = ''

            else:
                continue


if __name__ == '__main__':
    run_serial_handler()

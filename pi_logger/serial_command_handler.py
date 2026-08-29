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
                - (Yes, a new line then a \r (return))
                - Launches main.py and analyzes directive stored in param. 
                - Params must be a number between 0 and 15,999,999 (TODO: needs testing)
            2. download 
                - Prepares data for download and sends a packet to Seaglider. 

ID:     sch

Usage:  <python3 pi_logger/serial_command_handler.py>
'''

import subprocess
import time
import sys
import os
import signal
import serial
from datetime import datetime, timezone
import yaml

# ==============================================================================
# --- Configuration Defaults ---
CONFIG_PATH = 'config/config.yaml'
MAIN_SCRIPT_PATH = 'pi_logger/main.py'  # Path to main.py relative to this script
PACKETIZE_SCRIPT_PATH = 'packet_handling/packetize_dive_results.py' # TODO: call this as a function, don't use sub process popen
# DOWNLOAD_SCRIPT_PATH = '' # TODO: call this as a function, don't use sub process popen 

# ------------------------------------------------------------------------------
# --- YAML Configuration Defaults ---
try:
    with open(CONFIG_PATH, "r") as config_file:
        config = yaml.safe_load(config_file) or {}
except (FileNotFoundError, PermissionError):
    print("ERROR: sch: YAML failed to open for initial configs")
    config = {}  # File couldn't be opened, fall back to empty dict

# Now the .get() defaults WILL save you:
SERIAL_PORT = config.get("SERIAL_PORT", '/dev/ttys001')
BAUD_RATE = config.get("BAUD_RATE", 9600)
TERMINATOR = config.get("TERMINATOR", "\r")
DELIMITER = config.get("DELIMITER", ",")
PROMPT = config.get("PROMPT", "P>")

# ==============================================================================


# ==============================================================================
# GLOBAL STATE FLAGS & STATUS VARIABLES
main_process = None
main_finished = False 

packetize_process = None
download_packet_created = False
# download_finished = False
# ==============================================================================


# ==============================================================================
# --- Handler Functions ---
# ==============================================================================
def set_pi_datetime(date_string):
    # Parse ISO format (replace 'Z' with explicit UTC offset for older Python versions)
    dt = datetime.fromisoformat(date_string.replace("Z", "+00:00"))

    # Format as 'YYYY-MM-DD HH:MM:SS' in UTC
    formatted_time = dt.astimezone(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")

    # Save date into config.yaml (for now) 
    # TODO: think of a better place to store this
    with open(CONFIG_PATH, "r") as config_file:
        config = yaml.safe_load(config_file) or {}
    
        config["DATE_TIME"] = formatted_time
    
        with open(CONFIG_PATH, "w") as config_file:
            yaml.safe_dump(config, config_file, sort_keys=False)

    # Use a subprocess to set the datetime
    # TODO: TEST ME ON THE RASPBERRY PI
    print("ERROR: sch: sudo date -u -s formatted time IS COMMENTED OUT")
    # subprocess.run(["sudo", "date", "-u", "-s", formatted_time], check=True)
    
    new_time = datetime.now(timezone.utc)
    print(f"\nsch: set_pi_datetime has been called with string -> [{date_string}]\n" \
    f"     new datetime -> [{new_time}]")


def set_mission_params(param_string):
    print(f"sch: set_mission_params has been called with string -> [{param_string}]")
    # Implement later
    print("ERROR: sch: set mission params passing, not implemented yet")
    pass

def set_dive_climb(dive_letter):
    print(f"sch: set_dive_climb has been called with letter -> [{dive_letter}]")
    # Check for valid dive letter
    if dive_letter not in ("a","b",):
        print("ERROR: sch: Dive letter must be 'a' or 'b'")
        return 

    # Open config then write dive letter
    with open(CONFIG_PATH, "r") as config_file:
        config = yaml.safe_load(config_file) or {}

    config["DIVE_CLIMB"] = dive_letter

    with open(CONFIG_PATH, "w") as config_file:
        yaml.safe_dump(config, config_file, sort_keys=False)

    print(f"sch: set_dive_climb: updated DIVE_CLIMB to [{dive_letter}]")


def start_main_dot_py():
    global main_process
    print(f"sch: start_mission has been called\n")
    main_process = subprocess.Popen(["python3", MAIN_SCRIPT_PATH])

def send_fkw_results_and_prompt():
    # TODO: rebuild something more robust
    ''' A temporary function designed to send the latest FKW_detector results
    over serial to the seaglider when the 'download' command comes in. '''
    print(f"sch: send_fkw_results_and_prompt has been called")



# def call_packetize_results():
#     """
#     Called before or when the 'download' command is received.
#     Gathers all information to be transfered to the glider to radio transmission to shore
#     into once text file and finishes.
#     """
#     global download_process
#     print(f"sch: call packetize_results has been called")
#     # TODO: DO NOT USE SUBPROCESS HERE, CALL AN IMPORTED FUNCTION INSTEAD 


# ==============================================================================
# --- Process Control Helpers ---
# ==============================================================================
def is_main_running():
    """Helper function to cleanly check if main.py is currently active."""
    global main_process
    return main_process is not None and main_process.poll() is None

def stop_main_process():
    """
    Politely attempts to shut down pi_logger/main.py using SIGTERM for 10 seconds.
    If main.py does not terminate in time, forcefully kills it with SIGKILL.
    """
    global main_process
    if main_process is None or main_process.poll() is not None:
        print("sch: stop_main_process exiting b/c main is not running.")
        return  # Process is not running

    print("sch: Politely requesting main.py to stop (SIGTERM)...")
    main_process.terminate()

    try:
        # Wait up to 5 seconds for graceful exit
        main_process.wait(timeout=5)
        print("sch: main.py stopped cleanly.")
    except subprocess.TimeoutExpired:
        print("sch: main.py timed out after 5s. Forcefully terminating (SIGKILL)...")
        main_process.kill()
        main_process.wait()  # Ensure process resources are cleaned up
        print("sch: main.py forcefully terminated.")

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
    global main_process, main_finished

    print(f"sch: Starting serial listener on {SERIAL_PORT} @ {BAUD_RATE} baud...\n")

    try:
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
    except Exception as e:
        print(f"[Error] Failed to open serial port {SERIAL_PORT}: {e}")
        sys.exit(1)

    buffer = ""

    while True:
        # Maintain state for main.py
        if is_main_running():
            # print("sch: main is running!")
            pass
        elif main_process is not None:
            # main_process exists, but poll() returned an exit code (just finished)
            exit_code = main_process.poll()
            print(f"\nsch: main finished with exit code {exit_code}")
            main_process = None  # Clear process reference
            main_finished = True # Process complete (remembers that main has finished till process termination)
        else:
            # print("sch: main is not running")
            pass

        # Read available bytes from serial
        if ser.in_waiting > 0:
            data = ser.read(ser.in_waiting).decode('utf-8', errors='ignore')
            buffer += data
            buffer = buffer.strip()

            # ===========================================
            # -- Handle START ('start') scenario --
            # ===========================================
            if 'start' in buffer:
                # Guard against spawning a second instance
                if is_main_running():
                    print("ERROR: sch: start called while main is already running")
                    buffer = ''
                    continue

                print(f"sch: start case: raw command string (buffer) -> {buffer}")
                parsed_start_cmd = buffer.split(",")
                print(f"sch: start case: parsed_start_cmd -> {parsed_start_cmd}\n")
                # Check incoming start command 
                if (len(parsed_start_cmd) != 4 
                    or not parsed_start_cmd[1].isalpha() 
                    or len(parsed_start_cmd[1]) != 1 
                    or not parsed_start_cmd[2].isdigit() 
                    or not parsed_start_cmd[3].replace('Z', '').replace('-', '').replace(':', '').replace('T', '').isalnum()): 
                    print("ERROR: sch: invalid start buffer command... Continuing\n")
                    buffer = '' # Clear buffer and hope for a good fresh command
                    continue

                pi_start, pi_dive, pi_params, pi_date = [item.strip() for item in parsed_start_cmd]

                
                set_pi_datetime(pi_date)
                set_mission_params(pi_params)
                set_dive_climb(pi_dive)

                start_main_dot_py()
                buffer = ''

            # ===========================================
            # -- Handle DOWNLOAD ('download') scenario --
            # ===========================================
            elif 'download' in buffer:
                parsed_download_cmd = buffer.strip()
                print(f"sch: download case: parsed_download_cmd -> {parsed_download_cmd}")

                # If download arrives while main is active, stop main before packetizing
                if is_main_running():
                    print("sch: Download command received while main is running. Stopping main...")
                    stop_main_process()
                    
                # Packetize the results, then send them overserial
                else:
                    # call_packetize_results()
                    # TODO: call send download
                    pass

                buffer = ''

            else:
                continue


if __name__ == '__main__':
    run_serial_handler()

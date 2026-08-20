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
# --- Worker functions ---
# ==============================================================================
# def handle_start_param(param: str):
#     """
#     Called when the 'start' command is received.
#     :param param: The parameter string passed after the delimiter (e.g., '15999999')
#     """
#     print(f"sch: Handling parameters: {param}")
#     # TODO: Implement parameter logic here


def prep_download():
    """
    Called before or when the 'download' command is received.
    Gathers all information to be transfered to the glider to radio transmission to shore
    into once text file and finishes.
    """
    global download_received_early, download_called_prematurely
    print("sch: Executing prep_download()...")
    print(f"  └─ Flag (download_received_early): {download_received_early}")
    print(f"  └─ Flag (download_called_prematurely): {download_called_prematurely}")
    # TODO: Implement download preparation logic here


# def shutdown_pi():
#     """
#     Called after prep_download() completes.
#     """
#     print("sch: Executing shutdown_pi()...")
#     # TODO: Implement system shutdown logic here (e.g., os.system("sudo shutdown -h now"))


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


# ==============================================================================
# --- Main Serial Listener Loop ---
# ==============================================================================
def run_serial_handler():
    global start_command_received, main_process
    global download_received_early, download_called_prematurely

    print(f"sch: Starting serial listener on {SERIAL_PORT} @ {BAUD_RATE} baud...")

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
            buffer += data # Buffer is necessary so if more data is received nothing is whiped out

            print(f"sch: received data = [{data}], \n buffer =[{buffer}]\n")

            # Handle START ('start') scenario
            if 'start' in buffer:
                print(f"sch: start case: buffer is {buffer}")

                # TODO: handle start

                # Reset the buffer
                buffer = ''

            elif 'download' in buffer:
                print(f"sch: download case: buffer is {buffer}")

                #TODO: handle download 

                # Reset the buffer
                buffer = ''

            else:
                continue
            

                print(f"sch: Received line = [{line}]")

            #     # Split payload by configured delimiter
            #     parts = line.split(DELIMITER, 1)
            #     cmd = parts[0].strip().lower()
            #     arg = parts[1].strip() if len(parts) > 1 else ""

                # --------------------------------------------------------------
                # Command 1: START
                # --------------------------------------------------------------
                # if cmd == 'start':
                #     start_command_received = True
                    
                #     # 1. Process params
                #     handle_start_param(arg)

                #     # 2. Launch main.py in the background
                #     if main_process is None or main_process.poll() is not None:
                #         print(f"sch: Launching {MAIN_SCRIPT_PATH} background process...")
                #         main_process = subprocess.Popen([sys.executable, MAIN_SCRIPT_PATH])
                #     else:
                #         print("sch: Notice: main.py is already running.")

                # --------------------------------------------------------------
                # Command 2: DOWNLOAD
                # --------------------------------------------------------------
                # elif cmd == 'download':
                #     is_running = (main_process is not None and main_process.poll() is None)

                #     if is_running:
                #         # Case A: Download called while main.py is actively running
                #         download_received_early = True
                #         print("[Flag Set] download_received_early = True")
                #         stop_main_process()

                #     elif not start_command_received or main_process is None:
                #         # Case B: Start was never called or main was never launched
                #         download_called_prematurely = True
                #         print("[Flag Set] download_called_prematurely = True")

                #     # 1. Execute download preparation
                #     prep_download()

                #     # 2. Trigger final shutdown
                #     shutdown_pi()
                    
                #     # Exit listener loop
                #     ser.close()
                #     return


if __name__ == '__main__':
    run_serial_handler()

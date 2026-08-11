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
import time
import sys
import os
import signal
import serial

# ==============================================================================
# --- Configuration ---
# ==============================================================================
SERIAL_PORT = '/dev/ttyUSB0'  # Probably /dev/ttyAMA0 or similar on Pi
BAUD_RATE = 9600
TERMINATOR = '\r\n'
DELIMITER = ',' # Used to separate 'start,15999999' 

# Script configuration
MAIN_SCRIPT_PATH = 'pi_logger/main.py'  # Path to main.py relative to this script

# ==============================================================================
# --- Global State Flags & Tracking Variables ---
# ==============================================================================
download_received_early = False
download_called_prematurely = False

# Process management state
main_process = None
start_command_received = False


# ==============================================================================
# --- Placeholder Functions ---
# ==============================================================================
def handle_params(param: str):
    """
    Called when the 'start' command is received.
    :param param: The parameter string passed after the delimiter (e.g., '15999999')
    """
    print(f"[Handler] Handling parameters: {param}")
    # TODO: Implement parameter logic here


def prep_download():
    """
    Called when the 'download' command is received.
    Can inspect the global flags: download_received_early & download_called_prematurely
    """
    global download_received_early, download_called_prematurely
    print("[Handler] Executing prep_download()...")
    print(f"  └─ Flag (download_received_early): {download_received_early}")
    print(f"  └─ Flag (download_called_prematurely): {download_called_prematurely}")
    # TODO: Implement download preparation logic here


def shutdown_pi():
    """
    Called after prep_download() completes.
    """
    print("[Handler] Executing shutdown_pi()...")
    # TODO: Implement system shutdown logic here (e.g., os.system("sudo shutdown -h now"))


# ==============================================================================
# --- Process Control Helpers ---
# ==============================================================================
def stop_main_process():
    """
    Politely attempts to shut down main.py using SIGTERM for 10 seconds.
    If main.py does not terminate in time, forcefully kills it with SIGKILL.
    """
    global main_process
    if main_process is None or main_process.poll() is not None:
        return  # Process is not running

    print("[Handler] Politely requesting main.py to stop (SIGTERM)...")
    main_process.terminate()

    try:
        # Wait up to 10 seconds for graceful exit
        main_process.wait(timeout=10)
        print("[Handler] main.py stopped cleanly.")
    except subprocess.TimeoutExpired:
        print("[Handler] main.py timed out after 10s. Forcefully terminating (SIGKILL)...")
        main_process.kill()
        main_process.wait()  # Ensure process resources are cleaned up
        print("[Handler] main.py forcefully terminated.")


# ==============================================================================
# --- Main Serial Listener Loop ---
# ==============================================================================
def run_serial_handler():
    global start_command_received, main_process
    global download_received_early, download_called_prematurely

    print(f"[Handler] Starting serial listener on {SERIAL_PORT} @ {BAUD_RATE} baud...")

    try:
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
    except Exception as e:
        print(f"[Error] Failed to open serial port {SERIAL_PORT}: {e}")
        sys.exit(1)

    buffer = ""

    while True:
        # Check if main.py exited on its own (for status awareness)
        if main_process is not None and main_process.poll() is not None:
            # Process finished naturally
            # TODO: check to see if this is necessary
            pass

        # Read available bytes from serial
        if ser.in_waiting > 0:
            data = ser.read(ser.in_waiting).decode('utf-8', errors='ignore')
            buffer += data

            # Check if complete message with terminator arrived
            # TODO: ensure the line terminator is correct here
            while TERMINATOR in buffer:
                line, buffer = buffer.split(TERMINATOR, 1)
                line = line.strip()

                if not line:
                    continue

                print(f"[Serial Received] -> {line}")

                # Split payload by configured delimiter
                parts = line.split(DELIMITER, 1)
                cmd = parts[0].strip().lower()
                arg = parts[1].strip() if len(parts) > 1 else ""

                # --------------------------------------------------------------
                # Command 1: START
                # --------------------------------------------------------------
                if cmd == 'start':
                    start_command_received = True
                    
                    # 1. Process params
                    handle_params(arg)

                    # 2. Launch main.py in the background
                    if main_process is None or main_process.poll() is not None:
                        print(f"[Handler] Launching {MAIN_SCRIPT_PATH} background process...")
                        main_process = subprocess.Popen([sys.executable, MAIN_SCRIPT_PATH])
                    else:
                        print("[Handler] Notice: main.py is already running.")

                # --------------------------------------------------------------
                # Command 2: DOWNLOAD
                # --------------------------------------------------------------
                elif cmd == 'download':
                    is_running = (main_process is not None and main_process.poll() is None)

                    if is_running:
                        # Case A: Download called while main.py is actively running
                        download_received_early = True
                        print("[Flag Set] download_received_early = True")
                        stop_main_process()

                    elif not start_command_received or main_process is None:
                        # Case B: Start was never called or main was never launched
                        download_called_prematurely = True
                        print("[Flag Set] download_called_prematurely = True")

                    # 1. Execute download preparation
                    prep_download()

                    # 2. Trigger final shutdown
                    shutdown_pi()
                    
                    # Exit listener loop
                    ser.close()
                    return


if __name__ == '__main__':
    run_serial_handler()

# TODO: remove Aksel Notes 
# Program comes online. 

# Program waits for directive 

# Program writes to config.yaml in pi lager and FKW (both must been in the ~/ directory)

# Program starts pi lager / main.py (with the ability to cancel)

# Program waits for download command

# Program starts download command 

# When download finishes, serial command handlers asks RPi to shutdown

# End 
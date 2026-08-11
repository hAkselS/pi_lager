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


# TODO: generated code to get started with
# Create an interupt handler if serial command handler wants to stop main 
# (if the 'download' command was received before main is finished)
import signal
import sys
import time

def handle_shutdown_signal(signum, frame):
    print("\n[main.py] Received polite stop request. Cleaning up...")
    # Do cleanup here (save files, close serial connections, etc.)
    sys.exit(0)

# Register the signal handler for polite termination
signal.signal(signal.SIGTERM, handle_shutdown_signal)

print("[main.py] Script started...")
try:
    for i in range(10):
        print(f"[main.py] Working... step {i}")
        time.sleep(1)
except Exception as e:
    print(f"[main.py] Interrupted: {e}")
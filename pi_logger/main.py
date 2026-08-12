'''
File:   main.py

Spec:   This script is the primary orchestrator of the processes that make up pi logger.
        Main.py will read the config.yaml and utilize the parameters to launch the appropriate processes.
        Main.py then launches copy_memory_to_pi.py to move fresh data from the WISPR to the Pi.
        Once copy_memory_to_pi.py is complete, main.py will launch the FKW_detector. When the detector is finished,
        main.py will send a success message to serial_command_handler.py and exit. 

I/O:    This script reads the config.yaml.
        This scrip accepts an interupt signal from serial_command_handler.py. 

Usage:  <python3pi_logger/main.py>
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
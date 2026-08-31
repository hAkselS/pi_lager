'''
File:   main.py

Spec:   This script is the primary orchestrator of the processes that make up pi logger.
        Main.py will read the config.yaml and utilize the parameters to launch the appropriate processes.
        Main.py then launches copy_memory_to_pi.py to move fresh data from the WISPR to the Pi.
        Once copy_memory_to_pi.py is complete, main.py will launch the FKW_detector. When the detector is finished,
        main.py will send a success message to serial_command_handler.py and exit. 
        Note: No main because this should always run in order. 

I/O:    This script reads the config.yaml.
        This scrip accepts an interupt signal from serial_command_handler.py. 

ID:     mdp (main dot py)

Usage:  <python3 pi_logger/main.py>
'''

import signal
import sys
import time
import os
import subprocess 

# Add project root so copy_to_pi can be imported 
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(project_root)
import memory_management.copy_to_pi as copy_to_pi

# ==============================================================================
# --- Configuration Defaults ---
# ==============================================================================
CONFIG_PATH = "config/config.yaml"
PATH_TO_FKW_RUN_DETECTOR_SCRIPT = "~/FKW_detector/sys_control/run_detector.sh" # Outside of this repo, assumes FKW_detector is in ~/

# Global handle for tracking the active subprocess
fkw_process = None
# ==============================================================================

# ==============================================================================
# --- Process Group Cleanup & Signal Handlers ---
# ==============================================================================
def cleanup_subprocesses():
    """Kills the active subprocess and all of its spawned child processes."""
    global fkw_process
    if fkw_process and fkw_process.poll() is None:  # Check if still running
        print("\n[mdp] Terminating detector process group...")
        try:
            # Send SIGTERM to the ENTIRE process group (using negative PGID)
            pgid = os.getpgid(fkw_process.pid)
            os.killpg(pgid, signal.SIGTERM)
            
            # Allow up to 3 seconds for graceful shutdown
            try:
                fkw_process.wait(timeout=3)
            except subprocess.TimeoutExpired:
                print("[mdp] Detector hung, forcing SIGKILL...")
                os.killpg(pgid, signal.SIGKILL)
                
        except ProcessLookupError:
            pass  # Process group already terminated

def handle_shutdown_signal(signum, frame):
    """Handler for SIGTERM (from serial handler) and SIGINT (Ctrl+C)."""
    print(f"\n[mdp] Received shutdown signal ({signum}). Cleaning up...")
    cleanup_subprocesses()
    sys.exit(0)

# Register signal handlers for both polite termination (SIGTERM) and Ctrl+C (SIGINT)
signal.signal(signal.SIGTERM, handle_shutdown_signal)
signal.signal(signal.SIGINT, handle_shutdown_signal)

# ==============================================================================
# --- Main Execution Flow ---
# ==============================================================================
try:
    # --- Start copy_to_pi.py ---
    # TODO: add conditional statement to skip this based on yaml
    try:
        print("mdp: starting copy_to_pi")
        # print("ERROR: mdp: copy_to_pi commented out")
        copy_to_pi.copy_to_pi()
    except Exception as e:
        sys.exit(f"mdp: copy_to_pi execution failed - {e}")

    # --- Start FKW_detector ---
    try:
        expanded_fkw_path = os.path.expanduser(PATH_TO_FKW_RUN_DETECTOR_SCRIPT)

        # start_new_session=True attaches all child sub-processes to a single Process Group ID
        print("mdp: starting FKW_detector")
        # print("ERROR: mdp: subprocess commented out")
        fkw_process = subprocess.Popen(["bash", expanded_fkw_path], start_new_session=True)
        
        # Wait for the detector shell script to finish execution
        return_code = fkw_process.wait()
        
        if return_code != 0:
            print(f"mdp: FKW_detector exited with error code {return_code}")
        else:
            print("\nmdp: FKW_detector completed successfully.")

    except FileNotFoundError:
        print(f"mdp: script not found at {expanded_fkw_path}")
    except Exception as e:
        print(f"mdp: failed to execute shell script - {e}")

finally:
    # Guarantees process cleanup on normal exit, unhandled exceptions, or sys.exit()
    cleanup_subprocesses()
    
import serial # pip install pyserial 
import shlex
import time

# --- Configuration ---
SERIAL_PORT = '/dev/ttyUSB0'
BAUD_RATE = 9600
TERMINATOR = '\r\n'

# --- Command Handler Functions ---
# Each function receives 'arg' as a string or None

def handle_status(arg):
    return "STATUS: OK"

def handle_copy_memory(arg):
    # Logic for wispr memory copy goes here
    return f"Copying memory to destination: {arg}" if arg else "Copying memory..."

def handle_report_memory(arg):
    return "Memory Report: 85% Free"

def handle_shutdown(arg):
    # You might want to trigger os.system('sudo shutdown now') here
    return "System is shutting down..."

def handle_echo(arg):
    return f"ECHO: {arg}"

def handle_hello(arg):
    return "Hello back! I am a Raspberry Pi."

# --- Command Registry ---
# Mapping the trigger string to a specific ID and function
COMMAND_MAP = {
    "requests_status":    {"id": "001", "func": handle_status},
    "copy_wispr_memory":  {"id": "002", "func": handle_copy_memory},
    "report_memory":      {"id": "003", "func": handle_report_memory},
    "shutdown":           {"id": "004", "func": handle_shutdown},
    "echo":               {"id": "005", "func": handle_echo},
    "hello_world":        {"id": "006", "func": handle_hello},
}

def main():
    try:
        # Initialize Serial
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=0.1)
        time.sleep(2) # Give the port time to settle
       
        # Initial Ready Pulse
        print("System Ready. Sending Startup Signal...")
        ser.write(f"I'm ready{TERMINATOR}".encode())
        ser.write(f"I'm ready{TERMINATOR}".encode())

        while True:
            if ser.in_waiting > 0:
                # Read until the newline terminator
                raw_data = ser.readline().decode('utf-8', errors='ignore').strip()
               
                if not raw_data:
                    continue

                # Handle quoting requirement: remove outer quotes if they exist
                # shlex.split handles cases like: "command:parameter with spaces"
                try:
                    processed_input = shlex.split(raw_data)[0]
                except Exception:
                    processed_input = raw_data.strip('"')

                # Split command and parameter
                if ":" in processed_input:
                    cmd_key, arg = processed_input.split(":", 1)
                else:
                    cmd_key, arg = processed_input, None

                # Dispatch Logic
                if cmd_key in COMMAND_MAP:
                    entry = COMMAND_MAP[cmd_key]
                    cmd_id = entry["id"]
                   
                    # 1. Immediate ACK with ID
                    ser.write(f"ACK_{cmd_id}{TERMINATOR}".encode())
                   
                    # 2. Execute Function
                    response = entry["func"](arg)
                   
                    # 3. Send Function Response
                    if response:
                        ser.write(f"{response}{TERMINATOR}".encode())
                else:
                    # Optional: handle unknown commands
                    ser.write(f"ACK_ERR: Unknown Command{TERMINATOR}".encode())

            # Non-blocking pause (prevents 100% CPU usage)
            time.sleep(0.01)

    except serial.SerialException as e:
        print(f"Serial Error: {e}")
    except KeyboardInterrupt:
        print("\nScript stopped by user.")
    finally:
        if 'ser' in locals() and ser.is_open:
            ser.close()

if __name__ == "__main__":
    main()
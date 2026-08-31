'''
File:   serial_command_generator.py

Spec:   Open a serial port and send hand typed commands through it.
        Used to send test commands to serial_command_handler.py.
        * Not to be used in real deployments! * 

Usage:  python3 test_scripts/serial_command_generator.py
'''

import os
import pty
import select

def main():
    # 1. Create a pseudo-terminal pair (built-in Python module)
    master, slave = pty.openpty()
    slave_port_name = os.ttyname(slave)

    print("=" * 60)
    print(f"Virtual Serial Port Created!")
    print(f"Set your handler script's SERIAL_PORT to: {slave_port_name}")
    print("=" * 60)
    print("Type your commands below (or 'exit' to quit):\n")

    try:
        while True:
            cmd = input("Send command > ")
            if cmd.strip() == "exit": # Aksel removed '.lower()' 
                break

            # Write data to the master end; your listener reads from slave_port_name
            payload = (cmd + "\n").encode("utf-8")
            os.write(master, payload)
            print(f" -> Sent: {repr(payload)}")


            # Read reply
            rlist, _, _ = select.select([master], [], [], .05)
            if master in rlist: 
                response = os.read(master, 4096)
                print(f"\n<- Received the following response:")
                print(f"{repr(response.decode('utf-8', errors='ignore'))}")

    except KeyboardInterrupt:
        print("\nClosing port.")
    finally:
        os.close(master)
        os.close(slave)

if __name__ == "__main__":
    main()
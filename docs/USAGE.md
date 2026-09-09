# Usage

## Normal Mission Usage:
During normal mission operation, no user input is needed to start the pi_lager as it should run automatically. 

## During Testing:
### Python Start:
Running the pi_lager directly with python ensures that all pi_lager's print statements show directly in the terminal. This is nice for debugging potential errors. Make sure to navigate into ```~/pi_lager``` and start the virtual environment with ```source venv/bin/activate``` before starting the pi_lager. In ~/pi_lager with the virtual environment running, use ```python BENCHTEST=1 pi_logger/serial_command_handler.py``` to start pi_lager. BENCHTEST=1 ensures Raspberry Pi specific commands, such as setting the time, do not run on your local machine. Feel free to remove BENCHTEST=1 if you are running on a Pi and want a full and complete integration test. 

### Shell Start: 
To be continued

# Pi Lager Config
### Location of audio data created by the WISPR
#### Make sure to specify the full path, either using /home/camera/look_here... or ~/look_here
WISPR3_DATA_DIR: /media/camera/WISPR

### Location to copy and store WISPR data
#### Make sure to specify the full path, either using /home/camera/look_here... or ~/look_here
SSD_DIR: /home/camera

### Serial port information used by the pi_logger/serial_command_handler.py
#### THESE FUNCTIONS CONFIGURATIONS DO NOT WORK YET (but wil be added later)!!!!
SERIAL_PORT: '/dev/ttyUSB0'  # Probably /dev/ttyAMA0 or similar on Pi
BAUD_RATE: 9600
TERMINATOR: '\r\n'
DELIMITER: ',' # Used to separate various parameters in the start command 

### Is the glider diving or climbing? ('a':dive)('b':climb)
DIVE_CLIMB: 'a'
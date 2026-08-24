# Pi Lager Config
### Location of audio data created by the WISPR
WISPR3_DATA_DIR: /media/camera/WISPR

### Location to copy and store WISPR data
SSD_DIR: /home/camera

### Serial port information used by the pi_logger/serial_command_handler.py
#### THESE FUNCTIONS CONFIGURATIONS DO NOT WORK YET!!!!
SERIAL_PORT: '/dev/ttyUSB0'  # Probably /dev/ttyAMA0 or similar on Pi
BAUD_RATE: 9600
TERMINATOR: '\r\n'
DELIMITER: ',' # Used to separate various parameters in the start command 

### Is the glider diving or climbing? ('a':dive)('b':climb)
DIVE_CLIMB: 'a'
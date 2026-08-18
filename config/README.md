# Pi Lager Config
### Where the Raspberry Pi can find new data
WISPR3_DATA_DIR: /media/camera/WISPR

### Where the Raspberry Pi copy data to
SSD_DIR: /home/camera

### Serial port information used by the pi_logger/serial_command_handler.py
SERIAL_PORT: '/dev/ttyUSB0'  # Probably /dev/ttyAMA0 or similar on Pi
BAUD_RATE: 9600
TERMINATOR: '\r\n'
DELIMITER: ',' # Used to separate various parameters in the start command 

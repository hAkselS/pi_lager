# Repository Summary
## What This Repo Does:
Pi lager is a dedicated middle man between the False Killer Whale Detector and the Seaglider. Pi lager facilitates serial communication with the Seaglider by persistently listening over /dev/ttyAMA0 for commands sent from the glider. This repository is designed to start on boot and run on a Raspberry Pi 5, older verions of the Pi will not work. The Seaglider considers a Raspberry Pi 5 running pi lager and false killer whale detector and logger device. 

## How it Works:
A shell script called, start_pi_lager.sh start pi_logger/serial_command_handler.py and dumps any print statement outputs into a log file. Once running, the serial command handler listens for any serial commands. Currently the command handler can only respond effectively to two commands, start and download. The serial command handler expects start to come first, then download. Ideally, the download command is received after all tasks spawned by the start command finished, but edge case handling is implemented in this repository to handle edge cases efficiently. 

When the start command is received, the serial command handler fires off pi_logger/main.py. Main.py first copies any new files from the WISPR3 over to the Raspberry Pi's local memory using rsync. With all the audio data, stored as .dat files, is successfully transfered to the Raspberry Pi, main.py fires up the false killer whale detector by creating a subprocess to start FKW_detector's own main.py. When the false killer whale detector finishes its work, nothing happens in pi lager until the download command is received from the glider.

When the serial command handler receives "download" from the glider, it looks into ~/FKW_detector/data_products/packets for the most recent file. This file is then read and sent over serial to the glider for transmission to the basestation. Error handling is in place to ensure that any processes still running (besides serial command handler) are stopped when the download command is received. 

Future development includes creating a packetizer that will create a packet consisting of the false killer whale results packet, but also some metadata about the most recent dive. This expanded packet might include how long the pi ran for, how many images were analyzed, how long did the false killer whale detector run for, and more.

## What to Watch Out for:
    - Users must download FKW_detector and pi_lager into the ~/ directory on their Raspberry Pi.
    - Users must set the directories where they expect to discover the data, transfer the data, and analyze the data in both FKW_detector/config/config.yaml and pi_lager/config/config.yaml.


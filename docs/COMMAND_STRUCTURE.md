# Command Structure

## Start
The start command is structured like so: ```start,a,12345678,2026-08-19T20:59:20Z```. Pi lager will not accept commands that are not of this form. The word 'start' tells pi lager to start parsing arguements. the a indicates if pi lager is running during a dive or a climb (a is dive, b is climb). 1234567 is a parameter that allows users to set the max number of images to analyze, allowed run time for the device and more, but this feature has not been implemented yet. Lastly, is the datetime string in UTC. Upon receiving the start command the pi sets its datetime to whatever it receives from the glider.

## Download:
The download command is structured like so: ```download```. There is nothing special about this, when pi lager sees the command it will send the most recent false killer whale detections packet over serial and then wait for further instruction. 

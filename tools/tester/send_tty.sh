#!/bin/sh
#
# Send a packet to the specified serial port
# and wait for, and output the response, it is assumed
# that the response will end with an EOL character.
#
# usage: send_tty.sh <data-to-send> <port>
#
# [backgound]  Wait for, and read a line from the serial port into RESP,
# max 128 characters, timeout=10s, then output $RESP
#
#(read -n240 -t7 -a RESP < /dev/ttyUSB0; echo "${RESP[*]}")&
command tail -f /dev/ttyUSB0 & 
# Hack - use read to pause for 200ms to give previous
# command a chance to get started..
read -p "" -t0.2
#sleep 1
 
# Send command
echo "Settings" > /dev/ttyUSB0
read
kill $!
exit
# Wait for background read to complete

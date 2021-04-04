#! /bin/bash
# Skript to test a openandhome-sensor 
#
webserv=$1 
keyword=$2
ssid=$3
ssid_pass=$4

#Kill Processes on exit
trap "exit" INT TERM ERR
trap "kill 0" EXIT

function show_text {
    echo ""
    echo "*********************************"
    echo $1
    echo "*********************************"
    echo ""
}
function check_webside {

if curl -s "$1" | grep -i "$2" >> /dev/null
then
    # if the keyword is in the content

    show_text "keyword $2 found at $1 "

else
    echo ""
    echo "*********************************"
    echo -e "\e[31mError!!! keyword $2 missing at $1\e[0m"
    echo "*********************************"
    echo ""
fi

 }

 function send_ap {
     
     echo ""
     echo "Sending SSID:$1 with pass: $2"
     echo ""
     echo "WifiSSID $1" >  /dev/ttyUSB0; 
     echo "WifiKey $2" > /dev/ttyUSB0; 
     echo "Save" > /dev/ttyUSB0; 
     sleep 1; 
     echo "reboot" > /dev/ttyUSB0 
     show_text "Kontrollieren Sie bitte die Einstellungen und die Verbindung. Drücken Sie dann Return um zu beenden."
     sleep 1;
     tail -f /dev/ttyUSB0
     sleep 1;
     echo "Settings" > /dev/ttyUSB0 
     sleep 1
     echo "WifiDisconnect" > /dev/ttyUSB0 
     sleep 2
     echo "WifiConnect" > /dev/ttyUSB0
     read
     killall tail
     
 }

 function reset_ap {
     echo "Reset the AP"
     echo "WifiSSID ssid" >  /dev/ttyUSB0; sleep 1;
     echo "WifiKey wpakey" > /dev/ttyUSB0; sleep 1;
     echo "WifiSSID2 ssid" >  /dev/ttyUSB0; sleep 1;
     echo "WifiKey2 wpakey" > /dev/ttyUSB0;sleep 1; 
     echo "Save" > /dev/ttyUSB0; sleep 1;
     echo "reboot" > /dev/ttyUSB0
     sleep 1;
     echo "Settings" > /dev/ttyUSB0
     read  INPUT <  /dev/ttyUSB0
     echo $INPUT
 }



send_ap $ssid $ssid_pass
#reset_ap
#https://www.ridgesolutions.ie/index.php/2019/03/08/bash-send-data-to-serial-rs232-port-and-wait-for-response/
#https://unix.stackexchange.com/questions/117037/how-to-send-data-to-a-serial-port-and-see-any-answer
#https://stackoverflow.com/questions/13823706/capture-multiline-output-as-array-in-bash
#check_webside $webserv $keyword

#! /bin/bash 

echo "Dieses Skript schiebt die aktuelle Configuration auf den Sonoff"
if [[ -z $1 ]]; then
echo "Bitte die IP und den Namen übergeben. Beispiel: ./set_config.sh 192.168.4.1 POW1 setwifi/setfw"
exit
fi 
if [[ -z $2 ]]; then
echo "Bitte die IP und den Namen übergeben. Beispiel: ./set_config.sh 192.168.2.111 POW1"
exit
fi 




if [[ $3 == "setwifi" ]]; then
 echo "Wir sind in der initialen Konfiguration. Setzen die Wifi-Parameter und brechen dann ab."
 echo "Setze Wifi-Parameter"
 sleep 1
 wget -O/dev/null http://$1/cm?cmnd=Password%20Install@Network
 sleep 1
 wget -O/dev/null http://$1/cm?cmnd=Password1%20Install@Network
 sleep 1
 wget -O/dev/null http://$1/cm?cmnd=Password2%20Install@Network
 sleep 1
 wget -O/dev/null http://$1/cm?cmnd=SSId%20installnetwork
 sleep 1
 wget -O/dev/null http://$1/cm?cmnd=SSId1%20installnetwork
 sleep 1
 wget -O/dev/null http://$1/cm?cmnd=SSId2%20installnetwork
 sleep 1
 exit
fi

if [[ $3 == "setfw" ]]; then
echo "Mache ein Firmwareupdate [STRG-C] um abzubrechen"
sleep 4
wget -O/dev/null http://$1/cm?cmnd=Upgrade%201
exit
fi

echo "Lade globale Einstellungen"
. ../set_config_global.sh
echo
echo

#echo "Schalte MQTT an"
#sleep 1
#wget -O/dev/null http://$1/cm?cmnd=SetOption3%201
sleep 1
wget -O/dev/null http://$1/cm?cmnd=restart%201
echo "Bin Fertig"

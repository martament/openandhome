#! /bin/bash
echo "Dieses Skript schiebt die aktuelle Configuration auf den Sonoff"
if [[ -z $1 ]]; then
echo "Bitte die IP und den Namen übergeben. Beispiel: ./set_config.sh 192.168.4.1 POW1 setwifi"
exit
fi 
if [[ -z $2 ]]; then
echo "Bitte die IP und den Namen übergeben. Beispiel: ./set_config.sh 192.168.2.111 POW1"
exit
fi 

echo
if [[ $3 == "setwifi" ]]; then
 echo "Wir sind in der initialen Konfiguration. Setzen die Wifi-Parameter und brechen dann ab."
 echo "Setze Wifi-Parameter"
 wget -O/dev/null http://$1/cm?cmnd=Password%205641952001359038
 wget -O/dev/null http://$1/cm?cmnd=Password1%205641952001359038
 wget -O/dev/null http://$1/cm?cmnd=Password2%20m2sxZeUZ
 wget -O/dev/null http://$1/cm?cmnd=SSId2%20openandhome
 wget -O/dev/null http://$1/cm?cmnd=SSId%20wlan%40heinrichs
 wget -O/dev/null http://$1/cm?cmnd=SSId1%20wlan%40heinrichs
 exit
fi 
echo "Lade globale Einstellungen"
. ../set_config_global.sh
echo
wget -O/dev/null http://$1/cm?cmnd=restart%201

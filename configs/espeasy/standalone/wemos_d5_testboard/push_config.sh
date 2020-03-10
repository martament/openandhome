#! /bin/bash
echo "Dieses Skript schiebt die aktuelle Configuration auf den ESP"
echo "Bitte die IP übergeben"
echo
echo "Sende Config"
curl -v -F Upload=@config.dat http://$1/upload
echo 
echo "Bitte daran denken noch die Adresse des Sensors unter device auszuwählen"
echo "reboot" >  /dev/ttyUSB0

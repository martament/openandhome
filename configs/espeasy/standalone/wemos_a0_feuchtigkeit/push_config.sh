#! /bin/bash
echo "Dieses Skript schiebt die aktuelle Configuration auf den ESP"
echo "Bitte die IP übergeben"
echo
echo "Sende Icon und Openandhome-Dashboard"
curl -v -F Upload=@openandhome.esp http://$1/upload
curl -v -F Upload=@water.png http://$1/upload
echo "Sende Config und rules"
curl -v -F Upload=@config.dat http://$1/upload
curl -v -F Upload=@rules1.txt http://$1/upload
echo 
echo "Fertig mit dem Upload der Daten"

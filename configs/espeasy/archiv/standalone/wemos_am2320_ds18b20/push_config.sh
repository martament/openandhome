#! /bin/bash
echo "Dieses Skript schiebt die aktuelle Configuration auf den ESP"
echo "Bitte die IP übergeben"
echo "Erstelle aktuelle Version des Dashboards"
cat ../resources/header.txt table.txt ../resources/footer.txt > openandhome.esp
echo
echo "Sende Icon und Openandhome-Dashboard"
curl -v -F Upload=@openandhome.esp http://$1/upload
curl -v -F Upload=@../resources/temperature.png http://$1/upload
curl -v -F Upload=@../resources/humidity.png http://$1/upload
curl -v -F Upload=@../resources/openandhome_32.png http://$1/upload
echo "Sende Config"
curl -v -F Upload=@../resources/config.dat http://$1/upload
echo 
echo "Bitte daran denken noch die Adresse des Sensors unter device auszuwählen"

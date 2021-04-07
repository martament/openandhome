#! /bin/bash
echo "Dieses Skript schiebt die aktuelle Configuration auf den ESP"
echo "Bitte die IP übergeben"
echo
old_pwd=`pwd`
cd ../resources
echo "Erstelle aktuelle Version des Dashboards"
cat header.txt "$old_pwd/table.txt" footer.txt > "$old_pwd/openandhome.esp"
echo "Sende Icon und Openandhome-Dashboard"
#http://$1/filelist?delete=openandhome.esp
curl -v -F Upload=@"$old_pwd/openandhome.esp" http://$1/upload
curl -v -F Upload=@temperature.png http://$1/upload
curl -v -F Upload=@temperature1.png http://$1/upload
curl -v -F Upload=@distance.png http://$1/upload
curl -v -F Upload=@humidity.png http://$1/upload
curl -v -F Upload=@openandhome_32.png http://$1/upload
curl -v -F Upload=@openandhome.css http://$1/upload
echo "Sende Config"
curl -v -F Upload=@config.dat http://$1/upload
cd "$old_pwd"
echo 
echo "Bitte daran denken noch die Adresse des Sensors unter device auszuwählen"
echo "reboot" >  /dev/ttyUSB0

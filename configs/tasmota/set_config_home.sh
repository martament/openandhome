#! /bin/bash
echo "Lade set_config_home.sh"
echo "Dieses Skript beinhaltet den Teil der Konfiguration der Sonoff, welcher auf alle Varianten für Daheim zu flashen ist."

if [[ -z $1 ]]; then
echo "Bitte die IP übergeben. Beispiel: ./set_config_home.sh 192.168.4.1 POW1"
exit
fi 
if [[ -z $2 ]]; then
echo "Bitte die IP und den Namen übergeben. Beispiel: ./set_config_home.sh 192.168.2.111 POW1"
exit
fi 

echo
echo "Setze MQTT-Parameter"
wget -O/dev/null http://$1/cm?cmnd=MqttClient%20$2
sleep 8
wget -O/dev/null http://$1/cm?cmnd=MqttUser%20openhabian
sleep 8
wget -O/dev/null http://$1/cm?cmnd=MqttHost%20192.168.178.62
sleep 8
wget -O/dev/null http://$1/cm?cmnd=MqttPassword%20openandhome%40Raspi
sleep 8
echo "Setze Netzwerk-Parameter"
wget -O/dev/null http://$1/cm?cmnd=Hostname%20Sonoff-$2
sleep 8
wget -O/dev/null http://$1/cm?cmnd=DeviceName%20$2
sleep 8
wget -O/dev/null http://$1/cm?cmnd=FriendlyName%20$2
sleep 5
#Client durchstarten um 20 nach 12
wget -O/dev/null http://$1/cm?cmnd=rule1%20on%20Time%23Minute=345%20do%20restart%201%20endon
sleep 5
wget -O/dev/null http://$1/cm?cmnd=rule1%20off
sleep 5
#SetOption41 115 Gratious ARP jede 115 sekunden
#Verhindert dauthenticate bei alten Routern
#https://tasmota.github.io/docs/Commands/
wget -O/dev/null http://$1/cm?cmnd=SetOption41%20115
sleep 5
wget -O/dev/null http://$1/cm?cmnd=FullTopic%20%25prefix%25%2F%25topic%25%2F$2%2F
sleep 5
#SetOption53 	Display hostname and IP address in GUI
wget -O/dev/null http://$1/cm?cmnd=SetOption53%201
echo "Fertig mit set_config_home.sh"

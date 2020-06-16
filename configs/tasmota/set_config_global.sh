#! /bin/bash
echo "Lade set_config_global.sh"
echo "Dieses Skript beinhaltet den Teil der Konfiguration der Sonoff, welcher auf alle Varianten zu flashen ist."

if [[ -z $1 ]]; then
echo "Bitte die IP und den Namen übergeben. Beispiel: ./set_config_global.sh 192.168.4.1 POW1"
exit
fi 
if [[ -z $2 ]]; then
echo "Bitte die IP und den Namen übergeben. Beispiel: ./set_config_global.sh 192.168.2.111 POW1"
exit
fi 
#Wir prüfen den Typ des Modules und setzen diesen nach dem Namen
l_name=${2:0:3}
case $l_name in 
    "POW")
        echo "Setze Typ auf POW"
        l_module=6;;
    "S20")
        echo "Setze Typ auf S20"
        l_module=8;;
    "Bas")
        echo "Setze Typ auf Basic"
        l_module=1;;
    "Dua")
        echo "Setze Typ auf Dual"
        l_module=5;;
esac
#Setze den Modultypen
wget -O/dev/null http://$1/cm?cmnd=Module%20$l_module
sleep 10
echo
echo "Setze MQTT-Parameter"
wget -O/dev/null http://$1/cm?cmnd=MqttClient%20$2
sleep 8
wget -O/dev/null http://$1/cm?cmnd=MqttUser%20openhabian
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
wget -O/dev/null http://$1/cm?cmnd=rule1%20on
sleep 5
wget -O/dev/null http://$1/cm?cmnd=FullTopic%20%25prefix%25%2F%25topic%25%2F$2%2F
sleep 5
#SetOption53 	Display hostname and IP address in GUI
wget -O/dev/null http://$1/cm?cmnd=SetOption53%201
echo "Fertig mit set_config_global.sh"

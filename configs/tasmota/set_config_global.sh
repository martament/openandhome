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

echo
echo "Setze MQTT-Parameter"

sleep 1
wget -O/dev/null http://$1/cm?cmnd=SetOption3%200
sleep 1

wget -O/dev/null http://$1/cm?cmnd=PowerRetain%20On
sleep 1
wget -O/dev/null http://$1/cm?cmnd=ButtonRetain%20On
sleep 1
wget -O/dev/null http://$1/cm?cmnd=ButtonRetain%20Off
sleep 1
wget -O/dev/null http://$1/cm?cmnd=SensorRetain%20Off
#Switch Retain nur on, wenn es ein Door-sensor ist. Sonst off
wget -O/dev/null http://$1/cm?cmnd=SwitchRetain%20Off
sleep 1
wget -O/dev/null http://$1/cm?cmnd=PowerOnState%203
sleep 1
wget -O/dev/null http://$1/cm?cmnd=MqttClient%20$2
sleep 1
wget -O/dev/null http://$1/cm?cmnd=MqttUser%20openhabian
sleep 1
wget -O/dev/null http://$1/cm?cmnd=StateText1%20OFF
sleep 1
wget -O/dev/null http://$1/cm?cmnd=StateText2%20ON
sleep 1
wget -O/dev/null http://$1/cm?cmnd=StateText3%20TOGGLE
sleep 1
wget -O/dev/null http://$1/cm?cmnd=StateText4%20HOLD
sleep 1
wget -O/dev/null http://$1/cm?cmnd=TelePeriod%20600
sleep 1
wget -O/dev/null http://$1/cm?cmnd=GroupTopic%20sonoffs
sleep 1
wget -O/dev/null http://$1/cm?cmnd=Topic%20schaltsteckdosen
sleep 1
wget -O/dev/null http://$1/cm?cmnd=FullTopic%20%25prefix%25%2F%25topic%25%2F$2%2F
echo "Setze MQTT-Host"
wget -O/dev/null http://$1/cm?cmnd=MqttHost%20openhabianpi
sleep 1
wget -O/dev/null http://$1/cm?cmnd=MqttPassword%20XXXXX
sleep 1
echo "Setze Netzwerk-Parameter"
wget -O/dev/null http://$1/cm?cmnd=Hostname%20Sonoff-$2
sleep 1
wget -O/dev/null http://$1/cm?cmnd=IPAddress1%200.0.0.0
sleep 1
wget -O/dev/null http://$1/cm?cmnd=IPAddress2%20192.168.178.1
sleep 1
wget -O/dev/null http://$1/cm?cmnd=IPAddress3%20255.255.255.0
sleep 1
wget -O/dev/null http://$1/cm?cmnd=IPAddress4%20192.168.178.1
sleep 1
wget -O/dev/null http://$1/cm?cmnd=NtpServer1%20192.168.178.1
sleep 1
wget -O/dev/null http://$1/cm?cmnd=NtpServer2%20de.pool.ntp.org
sleep 1
wget -O/dev/null http://$1/cm?cmnd=NtpServer3%200.de.pool.ntp.org
echo "Setzte sonstige Parameter"
wget -O/dev/null http://$1/cm?cmnd=SerialLog%200
sleep 1
wget -O/dev/null http://$1/cm?cmnd=SysLog%200
sleep 1
wget -O/dev/null http://$1/cm?cmnd=WebLog%202
sleep 1
wget -O/dev/null http://$1/cm?cmnd=LedState%200
sleep 1
wget -O/dev/null http://$1/cm?cmnd=FriendlyName%20$2
sleep 1
#Client durchstarten um 20 nach 12
wget -O/dev/null http://$1/cm?cmnd=rule1%20on%20Time%23Minute=345%20do%20restart%201%20endon
sleep 1
wget -O/dev/null http://$1/cm?cmnd=rule1%20on
sleep 1
echo "Setzte sonstige Parameter"
wget -O/dev/null http://$1/cm?cmnd=LogHost%20openhabianpi
sleep 1
wget -O/dev/null http://$1/cm?cmnd=OTAUrl%20https://github.com/martament/openandhome/blob/master/build/Tasmota/releases/sonoff-openandhome.bin
echo "Fertig mit set_config_global.sh"

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
wget -O/dev/null http://$1/cm?cmnd=PowerRetain%201
wget -O/dev/null http://$1/cm?cmnd=ButtonRetain%201
wget -O/dev/null http://$1/cm?cmnd=SensorRetain%201
wget -O/dev/null http://$1/cm?cmnd=SwitchRetain%201
wget -O/dev/null http://$1/cm?cmnd=MqttClient%20$2
wget -O/dev/null http://$1/cm?cmnd=MqttUser%20openhabian
wget -O/dev/null http://$1/cm?cmnd=StateText1%20OFF
wget -O/dev/null http://$1/cm?cmnd=StateText2%20ON
wget -O/dev/null http://$1/cm?cmnd=StateText3%20TOGGLE
wget -O/dev/null http://$1/cm?cmnd=StateText4%20HOLD
wget -O/dev/null http://$1/cm?cmnd=TelePeriod%20600
wget -O/dev/null http://$1/cm?cmnd=GroupTopic%20sonoffs
wget -O/dev/null http://$1/cm?cmnd=Topic%20schaltsteckdosen
wget -O/dev/null http://$1/cm?cmnd=FullTopic%20%25prefix%25%2F%25topic%25%2F$2%2F
echo "Setze MQTT-Host"
wget -O/dev/null http://$1/cm?cmnd=MqttHost%20openhabianpi
wget -O/dev/null http://$1/cm?cmnd=MqttPassword%20openandhome@Raspi
echo "Setze Netzwerk-Parameter"
wget -O/dev/null http://$1/cm?cmnd=Hostname%20Schaltsteckdose$2
wget -O/dev/null http://$1/cm?cmnd=IPAddress1%200.0.0.0
wget -O/dev/null http://$1/cm?cmnd=IPAddress2%20192.168.178.1
wget -O/dev/null http://$1/cm?cmnd=IPAddress3%20255.255.255.0
wget -O/dev/null http://$1/cm?cmnd=IPAddress4%20192.168.178.1
wget -O/dev/null http://$1/cm?cmnd=NtpServer1%20192.168.178.1
wget -O/dev/null http://$1/cm?cmnd=NtpServer2%20de.pool.ntp.org
wget -O/dev/null http://$1/cm?cmnd=NtpServer3%200.de.pool.ntp.org
echo "Setzte sonstige Parameter"
wget -O/dev/null http://$1/cm?cmnd=SerialLog%200
wget -O/dev/null http://$1/cm?cmnd=SysLog%200
wget -O/dev/null http://$1/cm?cmnd=WebLog%202
wget -O/dev/null http://$1/cm?cmnd=LedState%200
wget -O/dev/null http://$1/cm?cmnd=FriendlyName%20$2
#Client durchstarten um 20 nach 12
wget -O/dev/null http://$1/cm?cmnd=rule1%20on%20Time%23Minute=345%20do%20restart%201%20endon
wget -O/dev/null http://$1/cm?cmnd=rule1%20on
echo "Setzte sonstige Parameter"
wget -O/dev/null http://$1/cm?cmnd=LogHost%20openhabianpi
wget -O/dev/null http://$1/cm?cmnd=OTAUrl%20http://openhabianpi/firmware/sonoff-openandhome.bin
echo "Fertig mit set_config_global.sh"

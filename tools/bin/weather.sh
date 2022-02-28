#! /bin/bash
#
#Das Skript wird unter /usr/local/bin/weather.sh auf dem openandhome-server abgelegt
#Je nach Bedarf wird es über einen Cronjob z.B. alle 15 Minuten ausgeführt:
#
#0/15 * * * * /usr/local/bin/weather.sh
#
#Wir holen von api.weather.com die Wetterdaten
url="http://api.weather.com/v2/pws/observations/current?stationId=ILLSFELD3&format=json&units=m&apiKey=TODO_YOUR_API_KEY_HERE"
#Wir filtern über jq aus dem Json von api.weather.com die Temperatur
temp=`curl -s $url | jq '.observations[0].metric.temp'`
#Wir schicken die Daten über Mosquitto an Openandhome zur Darstellung in Grafana
mosquitto_pub -t 'openandhome/Aussen/Dach/Temperatur' -u openhabian -P TODO_PASSWORD -m $temp
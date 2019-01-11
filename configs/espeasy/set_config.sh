#! /bin/bash
echo "Dieses Skript schiebt die aktuelle Configuration auf den ESPEasy"
echo
echo "Leider stellt der ESP-Easy kein so komfortable CMD-Schnittstelle zur Verfügung wie der SONOFF. Daher sind mehrere Manuelle Schritte notwendig."
echo
echo "Bitte zuerst den AP setzen mittels: esp_sendap"
echo "Dann die entsprechende Config laden"

echo "Folgende Befehlskürzel stehen zur Verfügung: "
alias | grep esp_

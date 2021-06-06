#! /bin/bash
echo Mache das Git-Update
echo
##echo "Sichere unsere Dateien nach myfiles"
cp -v Sonoff-Tasmota/tasmota/user_config_override.h myfiles
cd Sonoff-Tasmota
git reset --hard
git pull
echo "Wir verwenden den folgenden Branch"
git config --get remote.origin.url
git branch
cd ..
cp -v myfiles/user_config_override.h Sonoff-Tasmota/tasmota/
#cp -v myfiles/platformio.ini Sonoff-Tasmota/

#! /bin/bash
echo Setze den Branch zurück auf die Version von arendst
echo Das loescht alle lokalen und remote Aenderungen
echo
read
echo "Sichere unsere Dateien nach myfiles"
cp -v Tasmota/sonoff/platformio.ini myfiles
cd Tasmota
#git remote add upstream  https://github.com/arendst/Sonoff-Tasmota.git
#git remote add origin https://github.com/martament/Sonoff-Tasmota.git
git fetch upstream
git checkout master
git reset --hard upstream/master
git push origin master --force
echo "Wir verwenden den folgenden Branch"
git config --get remote.origin.url
git branch
cd ..

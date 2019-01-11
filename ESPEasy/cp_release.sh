#!/bin/bash
set -e
if [[ $1 == "20" ]]
then
 my_pfad="ESPEasy_20"
else
 my_pfad="ESPEasy_mega"
fi

echo "Creating release from $my_pfad"


############## update Release_notes.txt
NOTES="releases/Release_notes.txt"
echo "-------------------------------------------------" > "$NOTES.new"
echo "Neues Release wurde erzeugt" >> "$NOTES.new"
echo "Release ist für $my_pfad"
echo "-------------------------------------------------" >> "$NOTES.new"
echo -e "\nRelease date: `date`\n" >> "$NOTES.new"


echo >> "$NOTES.new"
cat "$NOTES" >> "$NOTES.new"
mv "$NOTES.new" "$NOTES"
cd $my_pfad
pwd
if [ -f ".pioenvs/dev_ESP8266_4096/firmware.bin" ]
then
	mv .pioenvs/dev_ESP8266_4096/firmware.bin ../releases/`date '+%Y%m%d%H%M%S'`_$my_pfad_dev_ESP8266_4096.bin
else
	echo ".pioenvs/dev_ESP8266_4096/firmware.bin nicht gefunden"
fi

if [ -f ".pioenvs/normal_ESP8266_4096/firmware.bin" ]
then
 if [ $1 == "20" ]
 then
  cp .pioenvs/normal_ESP8266_4096/firmware.bin ../releases/ESP8266_4096_openandhome.bin
 else
  cp .pioenvs/normal_ESP8266_4096/firmware.bin ../releases/mega_ESP8266_4096_openandhome.bin
 fi
mv .pioenvs/normal_ESP8266_4096/firmware.bin ../releases/`date '+%Y%m%d%H%M%S'`_$my_pfad_normal_ESP8266_4096.bin
else
	echo ".pioenvs/normal_ESP8266_4096/firmware.bin nicht gefunden"
fi

cd ../releases
ls -lrtah ./
echo
echo "Das aktuelle Release kann mittels flashesp geflashed werden"
echo

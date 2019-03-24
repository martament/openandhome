#!/bin/bash
set -e

my_pfad="ESPEasy_mega"


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
if [ -f ".pioenvs/dev_ESP8266_4M/firmware.bin" ]
then
	mv .pioenvs/dev_ESP8266_4M/firmware.bin ../releases/`date '+%Y%m%d%H%M%S'`_dev_ESP8266_4096.bin
else
	echo "No Devel-Firmware"	
	echo ".pioenvs/dev_ESP8266_4M/firmware.bin not found"
	echo "No Devel-Firmware"
fi

if [ -f ".pioenvs/normal_ESP8266_4M/firmware.bin" ]
then
  cp .pioenvs/normal_ESP8266_4M/firmware.bin ../releases/ESP8266_4096_openandhome.bin
  mv .pioenvs/normal_ESP8266_4M/firmware.bin ../releases/`date '+%Y%m%d%H%M%S'`_normal_ESP8266_4096.bin
else
	echo "No Normal-Firmware"	
	echo ".pioenvs/normal_ESP8266_4M/firmware.bin not found"
	echo "No Normal-Firmware"	
fi

cd ../releases
ls -lrtah ./
echo
echo "The current Normal-Release can be flashed via flashesp"
echo

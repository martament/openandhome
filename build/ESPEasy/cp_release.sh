#!/bin/bash
set -e

my_pfad="ESPEasy"



pwd
cd $my_pfad

#Search for firmware...
buildfile=`find . -type f -name '*ESP8266*bin'| xargs ls | tail -n 1`

if [ -f $buildfile ]
then

	############## update Release_notes.txt
	echo "*********************************************************"
	echo "Creating release from $my_pfad"
	NOTES="../releases/Release_notes.txt"
	echo "-------------------------------------------------" > "$NOTES.new"
	echo "Neues Release wurde erzeugt" >> "$NOTES.new"
	echo "Release ist für $my_pfad"
	echo "-------------------------------------------------" >> "$NOTES.new"
	echo -e "\nRelease date: `date`\n" >> "$NOTES.new"
	############## update Release_notes.txt
	#Move files
  	echo "found $buildfile moving it...."
  	cp -av $buildfile ../releases/openandhome_devel.bin | tee >> "$NOTES.new"
 	mv -v $buildfile ../releases/ | tee >> "$NOTES.new"
	echo >> "$NOTES.new"
	cat "$NOTES" >> "$NOTES.new"
	mv "$NOTES.new" "$NOTES"
	echo "*********************************************************"
else
	echo "*********************************************************"
	echo "No firmware ESP8266 found"
	echo "*********************************************************"
fi

#Search for firmware esp32...
NOTES="../releases/Release_notes.txt"
echo "Search for ESP32 OTA-File"
buildfile=`find . -type f -name '*ESP32*ETH.bin'| xargs ls | tail -n 1`

if [ -f $buildfile ]
then

  	echo "found $buildfile moving it...."
 	mv -v $buildfile ../releases/ | tee >> "$NOTES.new"
	cat "$NOTES" >> "$NOTES.new"
	mv "$NOTES.new" "$NOTES"
	echo "*********************************************************"
else
	echo "*********************************************************"
	echo "No firmware OTA for  ESP32 found"
	echo "*********************************************************"
fi




echo "Search for Factory-Build"
buildfile=`find . -type f -name '*ESP32*factory.bin'| xargs ls | tail -n 1`

if [ -f $buildfile ]
then

	echo "Creating release from $my_pfad"
	NOTES="../releases/Release_notes.txt"
	echo "-------------------------------------------------" > "$NOTES.new"
	echo "Neues Release32 wurde erzeugt" >> "$NOTES.new"
	echo "Release32 ist für $my_pfad"
	echo "-------------------------------------------------" >> "$NOTES.new"
	echo -e "\nRelease date: `date`\n" >> "$NOTES.new"
	############## update Release_notes.txt
	#Move files
  	echo "found $buildfile moving it...."
  	cp -av $buildfile ../releases/openandhome_devel32.bin | tee >> "$NOTES.new"
 	mv -v $buildfile ../releases/ | tee >> "$NOTES.new"
	echo >> "$NOTES.new"
	cat "$NOTES" >> "$NOTES.new"
	mv "$NOTES.new" "$NOTES"
	echo "*********************************************************"
else
	echo "*********************************************************"
	echo "No firmware for Factory  ESP32 found"
	echo "*********************************************************"
fi


cd ../releases
ls -lrtah ./
echo
echo "The current Custom-Release can be flashed via flash_espstable"
echo

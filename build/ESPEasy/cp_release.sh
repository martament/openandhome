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
 	mv -v $buildfile ../releases/`date '+%Y%m%d%H%M%S'`_normal_ESP8266_4M1M.bin | tee >> "$NOTES.new"
	echo >> "$NOTES.new"
	cat "$NOTES" >> "$NOTES.new"
	mv "$NOTES.new" "$NOTES"
	echo "*********************************************************"
else
	echo "*********************************************************"
	echo "No firmware found"
	echo "*********************************************************"
fi

cd ../releases
ls -lrtah ./
echo
echo "The current Normal-Release can be flashed via flash_espstable"
echo

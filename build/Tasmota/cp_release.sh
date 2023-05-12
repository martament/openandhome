#!/bin/bash
set -e
#NEW="$1"


#[ "$NEW" != "" ] || exit 1

echo "Creating release"


############## update Release_notes.txt
NOTES="releases/Release_notes.txt"
echo "-------------------------------------------------" > "$NOTES.new"
echo "Neues Release wurde erzeugt" >> "$NOTES.new"
echo "-------------------------------------------------" >> "$NOTES.new"
echo -e "\nRelease date: `date`\n" >> "$NOTES.new"


echo >> "$NOTES.new"
cat "$NOTES" >> "$NOTES.new"
mv "$NOTES.new" "$NOTES"

if [ -f "Tasmota/.pio/build/tasmota-lite/firmware.bin" ]
then
	cp Tasmota/.pio/build/tasmota-lite/firmware.bin releases/tasmota-openandhome.bin
	mv Tasmota/.pio/build/tasmota-lite/firmware.bin releases/`date '+%Y%m%d%H%M%S'`_tasmota-de.bin
else
	echo "Tasmota/.pio/build/tasmota-lite/firmware.bin nicht gefunden"
fi
if [ -f "Tasmota/.pio/build/tasmota-4M/firmware.bin" ]
then
	cp Tasmota/.pio/build/tasmota-4M/firmware.bin releases/tasmota-openandhome-4M.bin
	mv Tasmota/.pio/build/tasmota-4M/firmware.bin releases/`date '+%Y%m%d%H%M%S'`_tasmota-de-4M.bin
else
	echo "Tasmota/.pio/build/tasmota-4M/firmware.bin nicht gefunden"
fi

ls -lrtah releases

ls -lrtah releases
cd releases
echo
echo "Das aktuelle Release kann mittels flashsonoff geflashed werden"
echo

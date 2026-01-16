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

if [ -f "Tasmota/.pio/build/tasmota-minimal/firmware.bin" ]
then
	cp Tasmota/.pio/build/tasmota-minimal/firmware.bin releases/tasmota-openandhome_minimal.bin
	mv Tasmota/.pio/build/tasmota-minimal/firmware.bin releases/`date '+%Y%m%d%H%M%S'`_tasmota-minimal.bin
else
	echo "Tasmota/.pio/build/tasmota-lite/firmware.bin nicht gefunden"
fi
if [ -f "Tasmota/.pio/build/tasmota-lite/firmware.bin" ]
then
	cp Tasmota/.pio/build/tasmota-lite/firmware.bin releases/tasmota-openandhome.bin
	mv Tasmota/.pio/build/tasmota-lite/firmware.bin releases/`date '+%Y%m%d%H%M%S'`_tasmota-lite.bin
else
	echo "Tasmota/.pio/build/tasmota-lite/firmware.bin nicht gefunden"
fi
if [ -f "Tasmota/.pio/build/tasmota-DE/firmware.bin" ]
then
	cp Tasmota/.pio/build/tasmota-DE/firmware.bin releases/tasmota-openandhome-de-4M.bin
	mv Tasmota/.pio/build/tasmota-DE/firmware.bin releases/`date '+%Y%m%d%H%M%S'`_tasmota-de-4M.bin
else
	echo "Tasmota/.pio/build/tasmota-DE/firmware.bin nicht gefunden"
fi


ls -lrtah releases

ls -lrtah releases
cd releases
echo
echo "Das aktuelle Release kann mittels flashsonoff geflashed werden"
echo

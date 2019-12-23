#!/bin/bash
set -e
echo "Setting environment"
. ../../../configs/env_build.rc
cd Sonoff-Tasmota
#Upgrading und updating
platformio upgrade
platformio update
platformio run --target clean --environment tasmota-DE
echo "*********************************************"
echo "Normal/Standard-Build of Sonoff"
echo "*********************************************"
platformio run --environment tasmota-DE

echo "*********************************************"
echo "Normal/Standard-Build "
echo "*********************************************"


#Go back
cd ..

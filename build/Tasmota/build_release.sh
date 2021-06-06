#!/bin/bash
set -e
echo "Setting environment"
. ../../../configs/env_build.rc
cd Sonoff-Tasmota
#Upgrading und updating
#platformio upgrade
#platformio update
git pull
export PLATFORMIO_BUILD_FLAGS='-DUSE_CONFIG_OVERRIDE'
platformio run --target clean 
echo "*********************************************"
echo "Normal/Standard-Build of Sonoff"
echo "*********************************************"
platformio run --environment tasmota-lite
#platformio run --environment tasmota

echo "*********************************************"
echo "Normal/Standard-Build "
echo "*********************************************"


#Go back
cd ..

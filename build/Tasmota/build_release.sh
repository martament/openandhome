#!/bin/bash
set -e
echo "Setting environment"
. ../../../configs/env_build.rc
cd Sonoff-Tasmota
platformio run --target clean --environment sonoff-DE
echo "*********************************************"
echo "Normal/Standard-Build of Sonoff"
echo "*********************************************"
platformio run --environment sonoff-DE

echo "*********************************************"
echo "Normal/Standard-Build "
echo "*********************************************"


#Go back
cd ..

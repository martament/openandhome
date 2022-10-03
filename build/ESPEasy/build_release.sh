#!/bin/bash
set -e
echo "Setting environment"
. ../../../configs/env_build.rc
cd ESPEasy
pio pkg update
pio upgrade
platformio run --target clean
echo "*********************************************"
echo "Normal-Build"
echo "*********************************************"
platformio run --environment normal_ESP8266_4M1M
#echo "*********************************************"
#echo "Devel-Build"
#echo "*********************************************"
#platformio run --environment normal_ESP8266_4M1M --environment dev_ESP8266_4M1M

echo "*********************************************"
echo "ready with Build"
echo "*********************************************"


#Go back
cd ..

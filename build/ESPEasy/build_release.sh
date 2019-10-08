#!/bin/bash
set -e
echo "Setting environment"
. ../../../configs/env_build.rc
cd ESPEasy
platformio run --target clean
echo "*********************************************"
echo "Normal/Standard-Build and Devel-Build"
echo "*********************************************"
platformio run --environment normal_ESP8266_4M1M
#platformio run --environment normal_ESP8266_4M1M --environment dev_ESP8266_4M1M

echo "*********************************************"
echo "Normal/Standard-Build and Devel-Build"
echo "*********************************************"


#Go back
cd ..

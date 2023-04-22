#!/bin/bash
set -e
echo "Setting environment"
. ../../../configs/env_build.rc
cd ESPEasy
#pio pkg update
pio upgrade
platformio run --target clean
echo "*********************************************"
echo "Normal-Build - Standardbox ESP8266"
echo "*********************************************"
platformio run --environment custom_ESP8266_4M1M
echo
echo
#https://docs.platformio.org/en/stable/boards/espressif32/esp32-poe.html
#platformio run --environment esp32-poe
echo "*********************************************"
echo "Custom-Build - Professionalbox ESP32"
echo "*********************************************"
platformio run --environment custom_ESP32_4M316k_ETH
#platformio run --environment normal_ESP32_4M316k_ETH
#echo "*********************************************"
#echo "Devel-Build"
#echo "*********************************************"
#platformio run --environment normal_ESP8266_4M1M --environment dev_ESP8266_4M1M

echo "*********************************************"
echo "ready with Build"
echo "*********************************************"


#Go back
cd ..

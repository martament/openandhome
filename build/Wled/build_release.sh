#!/bin/bash
set -e
echo "Setting environment"
. ../../../configs/env_build.rc
cd WLED
#git fetch
#git pull
platformio run --target clean
echo "*********************************************"
echo "Builde WLED"
echo "*********************************************"
#platformio run --environment d1_mini
platformio run --environment esp8266_1m_custom
#platformio run --environment normal_ESP8266_4M1M --environment dev_ESP8266_4M1M
mv .pio/build/esp8266_1m_custom/firmware.bin ../release/`date '+%Y%m%d%H%M%S'`_wled.bin
echo "*********************************************"
echo "fertig"
echo "*********************************************"


#Go back
cd ..

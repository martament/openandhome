#!/bin/bash
set -e
echo "Resetting environment"
. ../../../configs/env_build.rc
cd ESPEasy
pio pkg update
pio upgrade
platformio run --target clean
pio system prune --force
pio pkg install


#Go back
cd ..

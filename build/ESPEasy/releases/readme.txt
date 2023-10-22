Here you can find the latest version of our openandhome software for your device. 

Flashing is at your own risk.
Make a backup of your settings !!!!!!

https://openandhome.de/index.php/ufaqs/kann-man-die-firmware-selbst-flashen-2/
https://openandhome.de/index.php/ufaqs/ich-moechte-die-konfiguration-aendern-ist-dies-moeglich/


openandhome_stable.bin => This is the tested Software. This Version is delivered with our Sensors


openandhome_devel.bin => This is the bleeding edge of our development for the normal Sensorbox (WLAN)


openandhome_devel32_factory.bin => This is the bleeding edge of our development for the professional Sensorbox (LAN/POE) => flash via searial interface
openandhome_devel32_ota.bin => This is the bleeding edge of our development for the professional Sensorbox (LAN/POE) => flash via web interface

Since ESP32 does have its flash partitioned in several blocks, we have 2 bin files of each ESP32 build:
- XXX_ESP32_4M316k.bin
- XXX_ESP32_4M316k.factory.bin

The binary with ".factory" in the name must be flashed on a new node, via the serial interface of the board.
This flash must be started at address 0.

The binary without ".factory" can be used for OTA updates. (OTA for ESP32 is added in May 2020)


You can upload the firmware at the Interface with TOOLS/UPDATE FIRMWARE or direct by calling your Sensor http://$IP/upload

Syslog is only working with our Devel-Version. Tools/Advanced/Syslog Log Level has to be "none" at the stable one. 
With syslog enabled sensor will be out of order after a reboot if the Version is older than 1.1.2022

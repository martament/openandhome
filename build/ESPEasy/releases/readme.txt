Here you can find the latest version of our openandhome software for your device. 

Flashing is at your own risk.
Make a backup of your settings !!!!!!

https://openandhome.de/index.php/ufaqs/kann-man-die-firmware-selbst-flashen-2/
https://openandhome.de/index.php/ufaqs/ich-moechte-die-konfiguration-aendern-ist-dies-moeglich/


openandhome_stable.bin => This is the tested Software. This Version is delivered with our Sensors


openandhome_devel.bin => This is the bleeding edge of our development for the normal Sensorbox (WLAN)
openandhome_devl32.bin => This is the bleeding edge of our development for the professional Sensorbox (LAN/POE)

You can upload the firmware at the Interface with TOOLS/UPDATE FIRMWARE or direct by calling your Sensor http://$IP/upload

Syslog is only working with our Devel-Version. Tools/Advanced/Syslog Log Level has to be "none" at the stable one. 
With syslog enabled sensor will be out of order after a reboot if the Version is older than 1.1.2022

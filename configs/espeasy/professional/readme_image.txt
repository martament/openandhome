# Firmware-Image Professional (ESP32 4MB, Ethernet, LittleFS)
# Automatisch erzeugt von tools/bin/espeasy_download.py - nicht von Hand aendern.

Quelle:        https://github.com/letscontrolit/ESPEasy/releases/tag/mega-20260720
Release-Tag:   mega-20260720 (veroeffentlicht 2026-07-20)
Asset:         ESPEasy_mega_20260720_ESP32_binaries.zip
Asset-SHA256:  d696306e02cbbd46dedfa81d1fcc21f520c40c030b9d3a0b57ae0078a2c9d0e7
Heruntergeladen: 2026-11-12

Dateien (SHA256):
  075bc946a49137d30b8a15b4c5627c334eab2e30f34a1ac70a000d39bf742fbe  ESP_Easy_mega_20260720_collection_A_ESP32_4M316k.bin
  5074c21a74bff3ca3eb8f4274923ef13b64dc629bfc6048aef7848a605466a2d  ESP_Easy_mega_20260720_collection_A_ESP32_4M316k.factory.bin

Flashen:
  - factory.bin -> 0x000000 (Neu-Aufspielen), .bin -> 0x10000 (Update)
  - Filesystem LittleFS @0x3B1000, Groesse 0x4F000 (esp32_partition_app1810k_spiffs316k.csv)
  - config.dat/Dashboard per Web-Upload (Werkstatt-Tool bzw. OH-Flasher)

Test (24h, Syslog 192.168.9.4) und Freigabe: siehe plans/espeasy-fertig-images.md, Abschnitt 6.
Getestet am: (offen)

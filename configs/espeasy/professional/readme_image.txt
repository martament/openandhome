# Firmware-Image Typ 2026 (ESP32 4MB, Ethernet, LittleFS)
# Automatisch erzeugt von tools/bin/espeasy_download.py - nicht von Hand aendern.

Quelle:        https://github.com/letscontrolit/ESPEasy/releases/tag/mega-20261119
Release-Tag:   mega-20261119 (veroeffentlicht 2026-11-19)
Asset:         ESPEasy_mega_20261119_ESP32_binaries.zip
Asset-SHA256:  6365710c737a84d8f7465a2ab68a44a9f781f07351a47d1849ced7f5d26a1b96
Heruntergeladen: 2026-11-20

Dateien (SHA256):
  7165bd55b6b6ef8401a3fc567720a16e9c0cae5d0ea8b3a0070c6553e41d375c  ESP_Easy_mega_20261119_collection_A_ESP32_4M316k.bin
  61ebf50445a940b490b9a0f5c3c8b643b913af62327274cbdd8df3d0b4004903  ESP_Easy_mega_20261119_collection_A_ESP32_4M316k.factory.bin

Flashen:
  - factory.bin -> 0x000000 (Neu-Aufspielen), .bin -> 0x10000 (Update)
  - Filesystem LittleFS @0x3B1000, Groesse 0x4F000 (esp32_partition_app1810k_spiffs316k.csv)
  - config.dat/Dashboard per Web-Upload (Werkstatt-Tool bzw. OH-Flasher)

Test (24h, Syslog 192.168.9.4) und Freigabe: siehe plans/espeasy-fertig-images.md, Abschnitt 6.
Getestet am: (offen)

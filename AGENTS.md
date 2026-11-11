# AGENTS.md — openandhome

Leitfaden für KI-Agents und Entwickler. Dieses Dokument beschreibt, wie das Projekt
aufgebaut ist, welche Regeln gelten und wo die relevanten Dateien liegen.

Aktueller Plan zur Ablösung des Eigenbuilds:
[`plans/espeasy-fertig-images.md`](plans/espeasy-fertig-images.md)

## 1. Was ist das Projekt?

openandhome ist ein IoT-Sensorprojekt (Temperatur-/Feuchte-/Distanzsensoren,
„Sensorbox"). Die Firmware basiert auf:

- **ESPEasy** (Hauptplatform, ESP8266 + ESP32) — <https://github.com/letscontrolit/ESPEasy>
- **Tasmota** (nur historisch, Sonoff/Wemos) — <https://github.com/arendst/Sonoff-Tasmota>
- **WLED** (nur historisch)

Der Shop und die Dokumentation liegen unter <https://www.openandhome.de>.

## 2. Leitregeln (WICHTIG)

1. **Keine eigenen Firmware-Builds mehr.** ESPEasy-Images werden als fertige
   Release-Binaries von der ESPEasy-Website geladen (siehe
   [`configs/espeasy/professional/3_hut21/readme.txt`](configs/espeasy/professional/3_hut21/readme.txt)).
   Der alte Eigenbuild über PlatformIO ([`build/ESPEasy/build_release.sh`](build/ESPEasy/build_release.sh))
   und [`build/ESPEasy/myfiles/Custom.hESPEasy`](build/ESPEasy/myfiles/Custom.hESPEasy) ist **nicht mehr der
   aktuelle Weg** — die Custom.h dient nur noch als Analysequelle dafür, welche
   Optionen auf ein Fertig-Image angewendet werden müssen.
2. **LittleFS statt SPIFFS.** Neuere ESPEasy-Builds verwenden LittleFS. Alte
   `spiffs1M.bin`/`spiffs316k.bin`-Images sind mit neuen Firmware-Ständen
   u. U. inkompatibel. Filesystem-Inhalte (Dashboard, Icons, CSS) werden bevorzugt
   per Web-Upload gesetzt ([`configs/espeasy/standalone/resources/push_config.sh`](configs/espeasy/standalone/resources/push_config.sh)).
3. **Flashen unter Linux per `esptool`**, entweder über die in der `.bashrc`
   hinterlegten Aliase oder über [`tools/ohtoolbox/bin/linux_ohtoolbox.sh`](tools/ohtoolbox/bin/linux_ohtoolbox.sh)
   (Menü-Tool: WLAN setzen, Settings lesen, Debug-Log, Reboot).
4. **Windows-Kundenservice** läuft über [`tools/oh-flasher/`](tools/oh-flasher/Readme.md)
   (PowerShell + portable Python + esptool) — hier liegen die Firmware-Presets
   für 1–6 Sensoren unter `tools/oh-flasher/firmware/`.
5. **Keine Firmware-Binaries als Text bearbeiten**, keine `.bin`-Dateien
   committen, die nicht aus einem Download stammen (Herleitung/Provenienz in
   README oder readme.txt des Ordners dokumentieren).
6. **Branch-Modell Stable/Devel.** `devel` ist der Arbeitsstand: hier werden
   neue Fertig-Images **heruntergeladen**, Configs/Dashboard angepasst und
   getestet. `main` ist Stable: nur getestete Kombinationen (Image +
   `config.dat` + Dashboard + readme mit Herkunft/Testdatum), Merge aus `devel`
   erst nach bestandenem Test. **Downloads ausschließlich auf `devel`.**
7. **Configs über `config.dat`, nicht über Flasher-Presets.** Stable-Releases
   bestehen aus Image + `config.dat` + Dashboard-Dateien — je Variante
   (Anzahl Fühler, verbaute Zusatzhardware wie Display/Wassersensor).
   **WLAN-Zugangsdaten und Syslog-IP gehören NIE in eine `config.dat`** —
   sie werden immer per Befehl gesetzt und gelöscht (`WifiSSID`/`WifiKey`/
   `Save`/`reboot` bzw. Syslog-Kommando, siehe Testverfahren unten).
   Für den Test wird die Syslog-IP `192.168.9.4` nachgerüstet.
8. **24h-Testverfahren:** Testboxen laufen ca. 24 Stunden mit Syslog-Logging
   auf `192.168.9.4`. Danach startet der Nutzer **manuell** das Teardown:
   Syslog aus, bei WLAN-Boxen SSIDs löschen (wie `esp_resetap`), damit beim
   Kunden der AP geöffnet wird. Details im Plan, Abschnitt 4.

## 3. Verzeichnisstruktur

| Pfad | Inhalt |
|---|---|
| [`build/ESPEasy/`](build/ESPEasy/) | Alte Build-Pipeline (PlatformIO), Git-Update-Skripte, Patches, Custom.h |
| [`build/ESPEasy/myfiles/Custom.hESPEasy`](build/ESPEasy/myfiles/Custom.hESPEasy) | **Maßgebliche** Compile-/Default-Optionen des alten Eigenbuilds |
| [`build/ESPEasy/myfiles/*.patch`](build/ESPEasy/myfiles/) | 7 Patches (AP-Mode als Daily-Driver, ApDontForceSetup, SettingsStruct) |
| [`build/Tasmota/`](build/Tasmota/) | Alte Tasmota-Builds und Releases (historisch) |
| [`configs/espeasy/professional/`](configs/espeasy/professional/) | **Professional (ESP32)**: config.dat, Dashboard, fertiges collection_A-Image, Partition-CSV |
| [`configs/espeasy/standalone/`](configs/espeasy/standalone/) | **Standalone (ESP8266 4M1M)**: pro Sensorvariante `config.dat`, `table.txt`, `spiffs1M.bin` |
| [`configs/espeasy/resources/`](configs/espeasy/resources/) | Gemeinsame Dashboard-Bausteine: `header.txt`, `footer.txt`, Icons, `config.dat` |
| [`configs/espeasy/set/`](configs/espeasy/set/) | Fertige Konfig-Sets (1/3/4 Fühler, Getreide) |
| [`tools/oh-flasher/`](tools/oh-flasher/Readme.md) | Windows-Flasher für Endkunden |
| [`tools/ohtoolbox/`](tools/ohtoolbox/bin/linux_ohtoolbox.sh) | Linux-Multitool (WLAN, Settings, Debug) |
| [`docs/`](docs/) | PDF-Bedienungsanleitungen |
| [`plans/`](plans/) | Planungs-/Konzeptdokumente |

## 4. Geräteklassen und Flash-Layouts

### Professional (ESP32, 4 MB, **mit Ethernet/ETH**)

- Image: `ESP_Easy_mega_*_collection_A_ESP32_4M316k.bin` (+ `.factory.bin`)
- Achtung: der alte Eigenbuild hieß `custom_ESP32_4M316k_ETH` — beim Download
  prüfen, ob das Fertig-Image Ethernet unterstützt (offener Punkt O-2 im Plan).
- Partitionierung: [`configs/espeasy/professional/esp32_partition_app1810k_spiffs316k.csv`](configs/espeasy/professional/esp32_partition_app1810k_spiffs316k.csv)
  (`app0` @0x10000, `app1` @0x1E0000, `eeprom` @0x3B0000, `spiffs` @0x3B1000 Größe 0x4F000)
- Aliase: `esp32_flash_writefull` (0x000000), `esp32_flash_write` (0x3B1000, spiffs316k.bin),
  `esp32_flash_read`/`esp32_flash_readfull`, `esp_resetflash` (erase-flash)

### Standalone (ESP8266, 4 MB, 1 MB FS)

- Image: `openandhome_stable.bin` / `openandhome_devel.bin` (früher selbst gebaut)
- Filesystem: `spiffs1M.bin` @0x300000
- Aliase: `esp_flashstable_min`, `esp_flash_write` (0x300000), `esp_flash_read` (0x300000, 0x100000),
  `esp_blank` (blank_4MB.bin), `esp_resetflash`

### Serielle Konfiguration (immer nach dem Flashen)

- WLAN-Zugangsdaten: `esp_sendap`, `esp_sendaphome`, `esp_sendaptest`, `esp_resetap`
- Dauerhaft: `ResetFlashWriteCounter`, `Save`, `reboot`
- Monitoring: `esp_monitor` (→ `pio device monitor --port /dev/ttyUSB0 --baud 115200`)

## 5. Dashboard / Web-UI

Das Dashboard wird aus [`configs/espeasy/resources/header.txt`](configs/espeasy/resources/header.txt)
+ `<variante>/table.txt` + [`configs/espeasy/resources/footer.txt`](configs/espeasy/resources/footer.txt)
zu `openandhome.esp` zusammengebaut und per `push_config.sh` (curl-Upload) auf den
Sensor gespielt. Danach `config.dat` hochladen und `reboot`.

## 6. Testen der Sensorboxen (Devel)

1. Image + `config.dat` der Variante flashen, dann **WLAN per Befehl** setzen
   (`WifiSSID`/`WifiKey`/`Save`/`reboot`, Aliase `esp_sendap*`) und
   **Syslog per Befehl** auf `192.168.9.4` nachrüsten (Kommando in Schritt T1
   des Plans verifizieren, sonst Web-UI).
2. Ca. 24 h betreiben, Logs am Syslog-Server auswerten (Boot-Zyklen,
   WLAN/ETH, MQTT, NTP, Sensorwerte, Regeln, Speicherverschleiß).
3. **Teardown manuell:** Syslog-Logging abschalten (Kommando bzw. erneutes
   Spielen der Stable-`config.dat`), danach bei WLAN-Boxen:
   `WifiSSID ssid` → `WifiKey wpakey` → `WifiSSID2 ssid` → `WifiKey2 wpakey`
   → `Save` → `reboot` (entspricht `esp_resetap`).
4. Verifikation: kein Syslog-Traffic, SSIDs gelöscht, AP öffnet sich,
   Ergebnis in `readme.txt` des Testordners → Merge-Freigabe.

Helfer: [`tools/ohtoolbox/bin/linux_ohtoolbox.sh`](tools/ohtoolbox/bin/linux_ohtoolbox.sh)
(WLAN setzen, Settings lesen, Debug-Log, Reboot).

**DS18B20:** die Device-Adresse (1-Wire-MAC) muss sonst im Reiter Devices
manuell gewählt werden — Automatisierung (Verhalten bei leerer Adresse testen,
sonst HTTP-Skript) ist Schritt S1 im Plan.

## 7. Regeln für Änderungen

- Neue Konfigurationsvarianten immer als eigener Ordner unter
  `configs/espeasy/standalone/<variante>/` oder `configs/espeasy/professional/<variante>/`
  mit `table.txt`, `readme.txt` (Herkunft des Images, Version, Besonderheiten).
- Jedes mitgelieferte Image mit Herkunft, ESPEasy-Version und Collection
  dokumentieren (Vorbild: [`configs/espeasy/professional/3_hut21/readme.txt`](configs/espeasy/professional/3_hut21/readme.txt)).
- Nicht mehr benötigte Build-Reste (`build/ESPEasy/*`) nur löschen, wenn der
  Nutzer es explizit freigibt — sie sind die Referenz für die Custom.h-Analyse.
- Sensible Daten (WLAN-Passwörter) stehen teils in Aliassen/Dateien; bei neuen
  Dateien keine Klartresswerte ablegen, sondern Platzhalter verwenden.
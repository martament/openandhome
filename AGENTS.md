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
   Release-Binaries von GitHub geladen ([`tools/bin/espeasy_download.py`](tools/bin/espeasy_download.py)).
   Der alte Eigenbuild über PlatformIO ([`build/ESPEasy/build_release.sh`](build/ESPEasy/build_release.sh))
   und [`build/ESPEasy/myfiles/Custom.hESPEasy`](build/ESPEasy/myfiles/Custom.hESPEasy) ist **nicht mehr der
   aktuelle Weg** — die Custom.h dient nur noch als Analysequelle dafür, welche
   Optionen auf ein Fertig-Image angewendet werden müssen.
2. **Filesystem: ESP32 = LittleFS, ESP8266 = SPIFFS.** Die ESP32-Release-Images
   verwenden LittleFS; alte `spiffs316k.bin` sind damit inkompatibel. Die
   ESP8266-4M1M-Release-Images verwenden weiterhin SPIFFS (ein LittleFS-Image
   gibt es upstream nur als `custom_312_ESP8266_4M2M_LittleFS`, siehe Plan
   Abschnitt 5 C). Filesystem-Inhalte (Dashboard, Icons, CSS, `config.dat`)
   werden für beide per Web-Upload gesetzt (Werkstatt-Tool bzw. Flasher).
3. **Werkstatt (intern, Linux):** [`tools/ohwerkstatt/`](tools/ohwerkstatt/README.md) — Aufsetzen,
   24h-Test, Testende, Kundenpaket. Flashen per `esptool`.
4. **Endanwender:** [`tools/ohtoolbox/`](tools/ohtoolbox/README.md) ist das **Standardwerkzeug**
   (Linux/Windows, USB: WLAN mit Prüfung, Name, NTP, Resets, Debug).
   [`tools/oh-flasher/`](tools/oh-flasher/Readme.md) ist nur die **Notlösung** (portables Python +
   esptool: Sensoren neu erkennen, neu aufsetzen, Firmware); er lädt Firmware, Basis-config und
   Regeln laut [`manifest.json`](tools/oh-flasher/manifest.json) aus dem Repo (Branch `master`).
   Funktionen für Kunden gehören in die Toolbox; was die Weboberfläche braucht (Autoerkennung), in den Flasher.
5. **Keine Firmware-Binaries als Text bearbeiten**, keine `.bin`-Dateien
   committen, die nicht aus einem Download stammen (Herleitung/Provenienz in
   README oder readme.txt des Ordners dokumentieren).
6. **Branch-Modell Stable/Devel.** `devel` ist der Arbeitsstand: hier werden
   neue Fertig-Images **heruntergeladen**, Configs/Dashboard angepasst und
   getestet. **`master` ist Stable** (wird nicht in `main` umbenannt, weil
   Dashboard-Footer und Readmes auf `…/master/…` verlinken): nur getestete
   Kombinationen (Image + `config.dat` + Dashboard + readme mit Release-Tag,
   SHA256, Testdatum), Merge aus `devel` erst nach bestandenem Test.
   **Downloads ausschließlich auf `devel`.**
7. **Configs über `config.dat`, nicht über Flasher-Presets.** Stable-Releases
   bestehen aus Image + `config.dat` + Dashboard-Dateien — je Variante
   (Anzahl Fühler, verbaute Zusatzhardware wie Display/Wassersensor).
   **WLAN-Zugangsdaten und Syslog-IP gehören NIE in eine Release-Datei.**
   WLAN steht in ESPEasy in `security.dat` und wird per Befehl gesetzt/gelöscht
   (`WifiSSID`/`WifiKey`/`Save`/`reboot`). Die Syslog-IP steht in `config.dat`,
   bleibt dort im Stable leer und wird im Test per HTTP an `/advanced` gesetzt
   (ESPEasy hat kein Syslog-Kommando). Test-Syslog-IP: `192.168.9.4`.
8. **Keine `security.dat` committen** (auch nicht in Backup-Tars), außer sie
   enthält nachweislich nur Defaults (`ssid`/`wpakey`/`configesp`).
9. **24h-Testverfahren:** Testboxen laufen ca. 24 Stunden mit Syslog-Logging
   auf `192.168.9.4`. Danach startet der Nutzer **manuell** das Teardown:
   Syslog aus, bei WLAN-Boxen SSIDs löschen (wie `esp_resetap`), damit beim
   Kunden der AP geöffnet wird. Details im Plan, Abschnitt 4.

## 3. Verzeichnisstruktur

| Pfad | Inhalt |
|---|---|
| [`build/ESPEasy/myfiles/Custom.hESPEasy`](build/ESPEasy/myfiles/Custom.hESPEasy) | **Maßgebliche** Compile-/Default-Optionen des alten Eigenbuilds |
| [`build/ESPEasy/myfiles/*.patch`](build/ESPEasy/myfiles/) | 7 Patches (AP-Mode als Daily-Driver, ApDontForceSetup, SettingsStruct) |
| [`build/Tasmota/`](build/Tasmota/) | Alte Tasmota-Builds und Releases — Umstellung siehe [`plans/tasmota-fertig-images.md`](plans/tasmota-fertig-images.md) |
| [`configs/espeasy/professional/`](configs/espeasy/professional/) | **Professional (ESP32)**: collection_A-Image + `readme_image.txt`, Partition-CSV, Varianten-Ordner (alt) |
| [`configs/espeasy/standalone/`](configs/espeasy/standalone/) | **Standalone (ESP8266 4M1M)**: collection_A-Image + `readme_image.txt`, Varianten-Ordner (alt) |
| [`configs/espeasy/standalone/basis/config.dat`](configs/espeasy/standalone/basis/config.dat) | **Basis-config.dat** mit allen Tasks (Autoerkennung schaltet passende ein) |
| [`configs/espeasy/standalone/resources/`](configs/espeasy/standalone/resources/) | Dashboard-Bausteine für beide Klassen: `header.txt`, `footer.txt`, Icons, CSS |
| [`tools/oh-flasher/`](tools/oh-flasher/Readme.md) | Windows-Flasher für Endkunden |
| [`tools/ohtoolbox/`](tools/ohtoolbox/bin/linux_ohtoolbox.sh) | Toolbox für Endkunden (WLAN, Settings, Debug) |
| [`tools/ohwerkstatt/`](tools/ohwerkstatt/README.md) | Werkstatt-Tool (intern, Linux): Aufsetzen, 24h-Test, Testende |
| [`tools/bin/`](tools/bin/) | Python-Helfer: Download, Autoerkennung, Syslog, config.dat-Prüfung, Testablauf |
| [`docs/`](docs/) | PDF-Bedienungsanleitungen |
| [`plans/`](plans/) | Planungs-/Konzeptdokumente |

## 4. Geräteklassen und Flash-Layouts

### Professional (ESP32, 4 MB, **mit Ethernet/ETH**)

- **Board: Olimex ESP32-POE — USB und PoE nie gleichzeitig** (keine galvanische Trennung).
- **Standalone und Professional sind verschiedene Boxen** (Gehäuse, Board, Fühler). Anleitungen, Basis-configs und technische Daten nie zwischen den Klassen übernehmen; Anleitungen erzeugt [`tools/docs/anleitung.py`](tools/docs/anleitung.py) mit `--variante standalone|professional` (box-spezifische Inhalte getrennt).
- HTU21D (Kombifühler) bleibt in der Basis-config; die Autoerkennung schaltet ihn nur ein, wenn er am I2C-Bus antwortet (0x40).
- Ethernet per USB: `NetworkImportConfig,3,{"nwpluginID":3,…,"MDC":23,"MDIO":18,"pwr":12,"clock":3}`.
- Basis: [`configs/espeasy/professional/basis/config.dat`](configs/espeasy/professional/basis/config.dat)
  (alle Sensoren, MQTT + Zabbix aus). Zabbix ist Sonderanfertigung (optional).
- 1-Wire an GPIO 4 und 2, Wassersensor GPIO 34, I2C 13/16.
- Zeitserver (Professional **und** Standalone, auch AM2320-Basis): `de.pool.ntp.org`; `basis/rules1.txt` fällt ohne Zeit nach 90 s auf das Gateway, nach weiteren 90 s auf 192.168.178.1 zurück (nur zur Laufzeit). Werkstatt und Kunden-Flasher (Manifest-Eintrag `regeln`) laden `rules1.txt` mit der Basis hoch; Endanwender ändern den NTP-Server über die Weboberfläche (`/advanced`) oder die ohtoolbox (Menü n).

- Image: `ESP_Easy_mega_*_collection_A_ESP32_4M316k.bin` (+ `.factory.bin`)
- Ethernet ist enthalten (`FEATURE_ETHERNET=1` über `esp32_common_LittleFS_ETH`);
  der alte Eigenbuild hieß `custom_ESP32_4M316k_ETH`. ETH-Settings stehen in
  der Professional-`config.dat`.
- Partitionierung: [`configs/espeasy/professional/esp32_partition_app1810k_spiffs316k.csv`](configs/espeasy/professional/esp32_partition_app1810k_spiffs316k.csv)
  (`app0` @0x10000, `app1` @0x1E0000, `eeprom` @0x3B0000, `spiffs` @0x3B1000 Größe 0x4F000)
- Aliase: `esp32_flash_writefull` (0x000000), `esp32_flash_write` (0x3B1000, spiffs316k.bin),
  `esp32_flash_read`/`esp32_flash_readfull`, `esp_resetflash` (erase-flash)

### Standalone (ESP8266, 4 MB, 1 MB FS)

- Image neu: `ESP_Easy_mega_*_collection_A_ESP8266_4M1M.bin` — **nicht**
  `custom_312_ESP8266_4M1M` (Release-Build ohne eure Custom.h, es fehlen u. a.
  P013, P014, P051). Kein Zabbix (C017) und kein Email (N001) auf ESP8266.
- Image alt: `openandhome_stable.bin` / `openandhome_devel.bin` (selbst gebaut)
- Filesystem: **SPIFFS**, `spiffs1M.bin` @0x300000
- Aliase: `esp_flashstable_min`, `esp_flash_write` (0x300000), `esp_flash_read` (0x300000, 0x100000),
  `esp_blank` (blank_4MB.bin), `esp_resetflash`

### Serielle Konfiguration (immer nach dem Flashen)

- WLAN-Zugangsdaten: `esp_sendap`, `esp_sendaphome`, `esp_sendaptest`, `esp_resetap`
- Dauerhaft: `ResetFlashWriteCounter`, `Save`, `reboot`
- Monitoring: `esp_monitor` (→ `pio device monitor --port /dev/ttyUSB0 --baud 115200`)

## 5. Dashboard / Web-UI

Das Dashboard `openandhome.esp` erzeugt [`tools/bin/espeasy_testbox.py`](tools/bin/espeasy_testbox.py)
(Werkstatt-Menü 5) aus den **aktiven Tasks** der Box: [`header.txt`](configs/espeasy/standalone/resources/header.txt)
+ generierte Tabelle + [`footer.txt`](configs/espeasy/standalone/resources/footer.txt), Upload samt Icons/CSS
per HTTP. Es gibt keine festen Varianten mehr (die alten Variantenordner sind entfernt).

## 6. Testen der Sensorboxen (Devel)

1. Image + `config.dat` der Variante flashen, dann eindeutigen Namen setzen
   (`Name,<box>`, `Unit,<n>`, `Save`), **WLAN per Befehl** setzen
   (`WifiSSID`/`WifiKey`/`Save`/`reboot`, Aliase `esp_sendap*`) und
   **Syslog per HTTP** an `/advanced` auf `192.168.9.4` nachrüsten
   (kein Syslog-Kommando in ESPEasy; Formular komplett zurückschicken).
2. Ca. 24 h betreiben, Logs am Syslog-Server auswerten (Boot-Zyklen,
   WLAN/ETH, MQTT, NTP, Sensorwerte, Regeln, Speicherverschleiß).
3. **Teardown manuell:** Syslog-Logging per HTTP `/advanced` abschalten (nicht
   die Stable-`config.dat` neu spielen — das überschreibt Name und
   DS18B20-Adressen), danach bei WLAN-Boxen:
   `WifiSSID ssid` → `WifiKey wpakey` → `WifiSSID2 ssid` → `WifiKey2 wpakey`
   → `Save` → `reboot` (entspricht `esp_resetap`).
4. Verifikation: kein Syslog-Traffic, SSIDs gelöscht, AP öffnet sich,
   Ergebnis in `readme.txt` des Testordners → Merge-Freigabe.

Helfer:
- [`tools/ohwerkstatt/oh_werkstatt.sh`](tools/ohwerkstatt/oh_werkstatt.sh) — **intern, nur Linux**:
  Box aufsetzen + 24h-Test starten, Test prüfen, Test beenden, Einzelschritte.
  Standardweg USB (`/dev/ttyUSB*`, Benutzer braucht Gruppe `dialout`).
  Namen: im Test `Testbox<Unit>`, bei Auslieferung `Sensorbox1`/Unit 0.
  Web-Zugriff: „Allow IP range" 192.168.0.0–192.168.255.255 (liegt in `security.dat`).
- [`tools/ohtoolbox/bin/linux_ohtoolbox.sh`](tools/ohtoolbox/bin/linux_ohtoolbox.sh) — **für Endkunden**
  (WLAN setzen, Settings lesen, Debug-Log, Reboot). Nur Funktionen aufnehmen,
  die Kunden brauchen; Werkstatt-Funktionen gehören in `ohwerkstatt`.
- [`tools/bin/espeasy_configcheck.py`](tools/bin/espeasy_configcheck.py) — prüft `config.dat`/Backup-Tars
  (Syslog aus? `security.dat` nur Defaults?) vor jedem Commit.

**DS18B20:** die Device-Adresse (1-Wire-MAC) muss sonst im Reiter Devices
manuell gewählt werden. Bei 1 Fühler pro GPIO hilft die P004-Option
„Auto Select Sensor"; bei mehreren Fühlern Adressen seriell mit `owscan`
lesen und per HTTP-Skript an `/devices` setzen (Plan Abschnitt 8, D-2).

## 7. Regeln für Änderungen

- Keine Variantenordner: Neue Sensoren werden als (deaktivierter) Task in der
  Basis-config ergänzt (`configs/espeasy/<klasse>/basis/`); die Autoerkennung schaltet
  sie je Box ein. Nach Änderungen Kundenpaket/Manifest neu erzeugen (Werkstatt `k`).
- Jedes mitgelieferte Image mit Release-Tag, Asset-Name, SHA256 und Testdatum
  dokumentieren (`readme_image.txt`, siehe Plan, Abschnitt 3).
- Fertig-Images nur mit [`tools/bin/espeasy_download.py`](tools/bin/espeasy_download.py)
  laden (nur auf `devel`). Das Skript prüft SHA256, hält pro Geräteklasse ein
  Image und schreibt `readme_image.txt` (Release-Tag, Asset, SHA256,
  Flash-Adressen) — diese Datei nicht von Hand ändern; Testdatum nach dem
  24h-Test eintragen.
- Nicht mehr benötigte Build-Reste (`build/ESPEasy/*`) nur löschen, wenn der
  Nutzer es explizit freigibt — sie sind die Referenz für die Custom.h-Analyse.
- Sensible Daten (WLAN-Passwörter) stehen teils in Aliassen/Dateien; bei neuen
  Dateien keine Klartresswerte ablegen, sondern Platzhalter verwenden.
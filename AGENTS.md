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
   Der alte Eigenbuild über PlatformIO (entfernt, siehe Git-Historie)
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
   24h-Test, Testende; Menü `k` erzeugt Manifest und `ohtoolbox.zip`. Flashen per `esptool`.
4. **Endanwender:** ein Paket [`tools/ohtoolbox/`](tools/ohtoolbox/README.md) (portables Python,
   Windows/Linux) mit **Toolbox** (Standard: WLAN, Name, NTP, Sensoren erkennen, Grundkonfiguration,
   Resets, Debug) und **OH-Flasher** (Firmware-Update, Neu-Aufspielen als Notfall). Beide nutzen
   dieselben Module wie die Werkstatt. **Eine Quelle:** [`tools/bin/oh_klassen.py`](tools/bin/oh_klassen.py)
   (Images, Basis-configs, Regeln, Hardware je Klasse); daraus wird
   [`manifest.json`](tools/ohtoolbox/manifest.json) erzeugt (`python3 tools/bin/oh_klassen.py`).
   Nach jeder Änderung an Images/Basis-configs Manifest neu erzeugen und committen - die CI
   ([`.github/workflows/ohtoolbox.yml`](.github/workflows/ohtoolbox.yml)) prüft das und baut auf
   `master` automatisch ein Release `ohtoolbox-JJJJ.MM.TT-N` mit Release-Notes.
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
   Kunden der AP geöffnet wird. Ablauf: Werkstatt-Menü 1–3 (Abschnitt 6).

## 3. Verzeichnisstruktur

| Pfad | Inhalt |
|---|---|
| [`build/ESPEasy/myfiles/Custom.hESPEasy`](build/ESPEasy/myfiles/Custom.hESPEasy) | **Maßgebliche** Compile-/Default-Optionen des alten Eigenbuilds |
| [`build/ESPEasy/myfiles/*.patch`](build/ESPEasy/myfiles/) | 7 Patches (AP-Mode als Daily-Driver, ApDontForceSetup, SettingsStruct) |
| [`build/Tasmota/`](build/Tasmota/) | Alte Tasmota-Builds und Releases — Umstellung siehe [`plans/tasmota-fertig-images.md`](plans/tasmota-fertig-images.md) |
| [`configs/espeasy/professional/`](configs/espeasy/professional/) | **Professional (ESP32)**: collection_A (factory + App-Update), `readme_image.txt`, Partition-CSV, `basis/` (config.dat, rules1.txt) |
| [`configs/espeasy/standalone/`](configs/espeasy/standalone/) | **Standalone (ESP8266 4M1M)**: climate_B (Standard) und collection_H (AM2320), `readme_image.txt`, `basis/` und `basis_am2320/` (config.dat, rules1.txt) |
| [`tools/bin/oh_klassen.py`](tools/bin/oh_klassen.py) | **Eine Quelle** für Images, Basis-configs, Regeln und Hardware je Klasse; erzeugt das Manifest |
| [`configs/espeasy/standalone/resources/`](configs/espeasy/standalone/resources/) | Dashboard-Bausteine für beide Klassen: `header.txt`, `footer.txt`, Icons, CSS |
| [`tools/ohtoolbox/`](tools/ohtoolbox/README.md) | Endanwender-Paket: Toolbox (Standard) und OH-Flasher (Update/Notfall) |
| [`tools/ohwerkstatt/`](tools/ohwerkstatt/README.md) | Werkstatt-Tool (intern, Linux): Aufsetzen, 24h-Test, Testende |
| [`tools/bin/`](tools/bin/) | Python-Module: Download, Autoerkennung, Syslog, config.dat-Prüfung, Testablauf (Werkstatt), `oh_kunde.py` (Toolbox/Flasher) |
| [`tools/docs/`](tools/docs/) | Anleitungs-Generator `anleitung.py` und Word-Vorlage |
| [`docs/`](docs/) | Bedienungsanleitungen 2026 (Word), je eine für Standalone und Professional |
| [`.github/workflows/ohtoolbox.yml`](.github/workflows/ohtoolbox.yml) | CI: Manifest prüfen, auf `master` Release `ohtoolbox-…` mit Release-Notes |
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

- Image: `ESP_Easy_mega_*_collection_A_ESP32_4M316k.factory.bin` (Neu-Aufspielen @0x0) und
  `…_4M316k.bin` (Update: App @0x10000 + otadata 0xE000/0x2000 löschen; NVS/Ethernet bleiben).
  Ethernet ist enthalten (`FEATURE_ETHERNET=1`); die Ethernet-Hardware liegt im NVS (per USB gesetzt).
- Partitionierung: [`configs/espeasy/professional/esp32_partition_app1810k_spiffs316k.csv`](configs/espeasy/professional/esp32_partition_app1810k_spiffs316k.csv)
  (`app0` @0x10000, `app1` @0x1E0000, `eeprom` @0x3B0000, `spiffs` @0x3B1000 Größe 0x4F000)
- `/download` liefert bei ESP32 ein TAR (config.dat, security.dat, …).

### Standalone (ESP8266, 4 MB, 1 MB FS)

- Board: WeMos D1 mini (ESP8266), WLAN, USB-Versorgung.
- Image: `ESP_Easy_mega_*_climate_B_ESP8266_4M1M.bin` (Standard, kleinstes passendes Image,
  ~13 KB freier RAM); bei AM2320 (I2C 0x5C) `…_collection_H_…` mit `basis_am2320/` – Werkzeuge
  wählen das automatisch. **Nicht** `custom_312` (es fehlen P013/P014/P051). Kein Zabbix/Email.
- Flash @0x0; Update = dasselbe Image @0x0 (Dateisystem bleibt). Filesystem **SPIFFS** @0x300000.
- Basis: 1-Wire GPIO 0 (Fuehler1–4), HTU21D, OLED, HC-SR04; MQTT aus.

### Serielle Konsole (beide Klassen)

- WLAN: `WifiSSID,"…"`, `WifiKey,"…"`, `Save`, `Reboot`; löschen mit `ssid`/`wpakey` (wie `esp_resetap`).
- Weitere: `Name`, `Unit`, `NTPHost`, `I2CScanner`, `OWScan,<gpio>`, `TaskEnable/TaskDisable,<n>`,
  `TaskClear,<n>` (nur seriell erlaubt), `logentry,%sysbuild_filename%` (Image-Name).
- Port mit DTR/RTS **an** öffnen (sonst Reset bei ESP32); ESP32-Ausgabe enthält ANSI-Farbcodes.
- Die alten `.bashrc`-Aliase (`esp_flashstable*`, `esp32_flash_write`, `spiffs*.bin`) sind überholt.

## 5. Dashboard / Web-UI

Das Dashboard `openandhome.esp` erzeugt [`tools/bin/espeasy_testbox.py`](tools/bin/espeasy_testbox.py)
(Werkstatt-Menü 5) aus den **aktiven Tasks** der Box: [`header.txt`](configs/espeasy/standalone/resources/header.txt)
+ generierte Tabelle + [`footer.txt`](configs/espeasy/standalone/resources/footer.txt), Upload samt Icons/CSS
per HTTP. Es gibt keine festen Varianten mehr (die alten Variantenordner sind entfernt).
Beschriftung: DS18B20 mit Standardnamen `FuehlerN` → „Fühler N“; umbenannte Fühler (Task-Name,
z. B. `Heizungsvorlauf`) erscheinen mit ihrem Namen, andere Sensoren als „Wert (Task)“. Kunden
benennen unter Devices um und erneuern dann mit Toolbox **s** Dashboard und Display.

## 6. Testen der Sensorboxen (Devel)

Mit [`tools/ohwerkstatt/oh_werkstatt.sh`](tools/ohwerkstatt/README.md):

1. **Menü 1 – aufsetzen:** Chip erkennen, flashen (Sicherung vorher optional über Menü b), bei
   Professional Ethernet per USB, WLAN mit Prüfung (aus `~/.config/openandhome/wlan.txt`, sonst Abfrage), Zugriffsbereich, Basis-config + Regeln,
   Testname `Testbox<n>`, Sensoren erkennen, Dashboard, Werteprüfung, Syslog `192.168.9.4` an.
2. **Menü 2 – prüfen** (jederzeit, auch ohne USB per IP): Messwerte plausibel, Dashboard vollständig.
3. **Menü 3 – beenden** nach ~24 h: Abschlussprüfung, Syslog aus (nach Neustart geprüft), Name `Sensorbox1`/Unit 0,
   WLAN immer löschen (ohne Nachfrage) und prüfen, ob nach dem Neustart der AP startet. Protokoll unter `~/openandhome-testprotokolle/`.

Helfer:
- [`tools/ohwerkstatt/oh_werkstatt.sh`](tools/ohwerkstatt/oh_werkstatt.sh) — **intern, nur Linux**:
  Box aufsetzen + 24h-Test starten, Test prüfen, Test beenden, Einzelschritte.
  Standardweg USB (`/dev/ttyUSB*`, Benutzer braucht Gruppe `dialout`).
  Namen: im Test `Testbox<Unit>`, bei Auslieferung `Sensorbox1`/Unit 0.
  Web-Zugriff: „Allow IP range" 192.168.0.0–192.168.255.255 (liegt in `security.dat`).
- [`tools/ohtoolbox/`](tools/ohtoolbox/README.md) — **für Endkunden** (Toolbox und OH-Flasher, siehe Regel 4).
- [`tools/bin/espeasy_configcheck.py`](tools/bin/espeasy_configcheck.py) — prüft `config.dat`/Backup-Tars
  (Syslog aus? `security.dat` nur Defaults?) vor jedem Commit.

**DS18B20:** die Device-Adresse (1-Wire-MAC) muss sonst im Reiter Devices
manuell gewählt werden. Bei 1 Fühler pro GPIO hilft die P004-Option
„Auto Select Sensor"; bei mehreren Fühlern Adressen seriell mit `owscan`
lesen und per HTTP-Skript an `/devices` setzen (Plan Abschnitt 8, D-2).

## 7. Regeln für Änderungen

- Keine Variantenordner: Neue Sensoren werden als (deaktivierter) Task in der
  Basis-config ergänzt (`configs/espeasy/<klasse>/basis/`); die Autoerkennung schaltet
  sie je Box ein. Nach Änderungen das Manifest neu erzeugen (`python3 tools/bin/oh_klassen.py` bzw. Werkstatt `k`) und committen.
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
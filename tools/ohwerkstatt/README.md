# openandhome Werkstatt-Tool (intern, nur Linux)

Menü für Test und Auslieferung der Sensorboxen. **Nicht an Kunden ausliefern** —
dafür gibt es [`tools/ohtoolbox/`](../ohtoolbox/README.md).

```
tools/ohwerkstatt/oh_werkstatt.sh
```

Voraussetzungen: Python 3 mit `pyserial`, Box per USB (`/dev/ttyUSB*`), Benutzer
in Gruppe `dialout` (`sudo usermod -aG dialout $USER`, danach neu anmelden).
Grundkonfiguration läuft über USB; nur Syslog, `config.dat`-Upload,
Device-Einstellungen, Zugriffsbereich und Dashboard gehen über HTTP.

| Punkt | Funktion |
|---|---|
| 1 | **Box aufsetzen und 24h-Test starten:** Chip erkennen → Flashen (Image der Klasse laut [`oh_klassen.py`](../bin/oh_klassen.py)) → Professional: Ethernet per USB → WLAN mit Prüfung (aus `~/.config/openandhome/wlan.txt`: Zeile 1 SSID, Zeile 2 Passwort, `chmod 600`; fehlt die Datei, wird gefragt) → Web-Zugriff 192.168.0.0–192.168.255.255 → Basis-`config.dat` + `rules1.txt` (bei AM2320 automatisch collection_H/`basis_am2320`) → Testname `Sensorbox<Unit>` (Vorgabe) → Sensoren erkennen → Zabbix-Abfrage (Professional) → Dashboard → Werte- und Dashboard-Prüfung → Syslog an (UDP-Port 514). Der Zugriffsbereich schaltet auch „Append Unit Number to hostname“ aus (Hostname = Name) |
| 2 | Test prüfen: Messwerte plausibel? Dashboard vollständig ersetzt? |
| 3 | **Test beenden:** Abschlussprüfung → Syslog aus → Name `Sensorbox1`/Unit 0 → Zugriffsbereich → Neustart, prüfen ob Syslog wirklich aus ist → WLAN löschen wie `esp_resetap` (immer, ohne Nachfrage), Neustart und prüfen, ob der AP startet (Boot-Log per USB oder WLAN-Scan per `nmcli`) |
| 4 | Sensoren erkennen (I2C, DS18B20), Tasks einschalten, OLED-Zeilen setzen |
| 5 | Dashboard aus den aktiven Tasks erzeugen und hochladen (umbenannte Fühler erscheinen mit ihrem Task-Namen) |
| 6 | Gerätename/Unit setzen |
| 7 | 1-Wire-Scan (`OWScan,<GPIO>`) |
| 8 | Syslog an/aus/Status |
| 9 | `config.dat` / Backup-Tar prüfen |
| b | Box sichern (optional, vor dem Aufsetzen): kompletter Flash + `config.dat`/TAR nach `~/openandhome-backups/`; entfällt bei leerem Flash |
| k | Manifest aus [`oh_klassen.py`](../bin/oh_klassen.py) erzeugen und `ohtoolbox.zip` bauen (keine Box nötig) |
| t | Toolbox (Kundensicht) mit lokalen Dateien starten |
| f | OH-Flasher (Kundensicht) mit lokalen Dateien starten |
| i | Fertig-Images laden (nur Branch `devel`) |
| m | Serieller Monitor |

Testprotokolle: `~/openandhome-testprotokolle/<Testname>_<Start>.txt`
(Start, Firmware, Prüfungen Start/Ende, Ergebnis `BESTANDEN` /
`VORZEITIG BEENDET` (< 24 h) / `NICHT BESTANDEN`).

Netzwerk-Sonderfälle (automatisch behandelt):
- Web-Zugriff gesperrt (403, anderes Subnetz) → `ClearAccessBlock` per USB.
- Box landet in einem anderen WLAN/Netz und ist nicht erreichbar → bis zu
  3× Reboot per USB, danach Anzeige von IP/SSID und Eingabe einer anderen IP.

Die Python-Helfer lassen sich auch einzeln aufrufen:
[`espeasy_testbox.py`](../bin/espeasy_testbox.py),
[`espeasy_autoconfig.py`](../bin/espeasy_autoconfig.py),
[`espeasy_syslog.py`](../bin/espeasy_syslog.py),
[`espeasy_configcheck.py`](../bin/espeasy_configcheck.py),
[`espeasy_download.py`](../bin/espeasy_download.py).

Kunden-ZIP: baut die CI auf `master` automatisch (Release mit Release-Notes); lokal
`python3 tools/ohtoolbox/paket_bauen.py` → `tools/ohtoolbox/dist/ohtoolbox.zip`.


## Professional (Olimex ESP32-POE)

- **USB und PoE nie gleichzeitig anschließen** — das Board ist nicht galvanisch
  getrennt (Olimex-Hinweis; unsere Boxen haben die Variante **ohne** ISO).
- Menü 1 erkennt den ESP32 automatisch;
  Ethernet wird per USB eingerichtet, die Konfiguration läuft über WLAN am USB.
- Zabbix nur auf Nachfrage (Sonderanfertigung) bzw. `--zabbix <server>`.
- 24h-Test am PoE: erst USB ab, dann PoE an. Menü 2/3 funktionieren auch ohne
  USB (IP eingeben); Testende löscht die Werkstatt-WLAN-Daten immer.

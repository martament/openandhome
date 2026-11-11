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
| 1 | **Box aufsetzen und 24h-Test starten:** Chip erkennen → Sicherung (Flash + `config.dat`, `~/openandhome-backups/`) → Flashen (aktuelles `collection_A`-Image) → WLAN (USB) → Basis-`config.dat` (`configs/espeasy/<klasse>/basis/`) → Testname `Testbox<Unit>`, Web-Zugriff 192.168.0.0–192.168.255.255 → Sensoren erkennen → Dashboard → Werte- und Dashboard-Prüfung → Syslog an |
| 2 | Test prüfen: Messwerte plausibel? Dashboard vollständig ersetzt? |
| 3 | **Test beenden:** Abschlussprüfung → Syslog aus → Name `Sensorbox1`/Unit 0 → Zugriffsbereich → optional WLAN löschen wie `esp_resetap` |
| 4 | Sensoren erkennen (I2C, DS18B20), Tasks einschalten, OLED-Zeilen setzen |
| 5 | Dashboard aus den aktiven Tasks erzeugen und hochladen |
| 6 | Gerätename/Unit setzen |
| 7 | 1-Wire-Scan (`OWScan,<GPIO>`) |
| 8 | Syslog an/aus/Status |
| 9 | `config.dat` / Backup-Tar prüfen |
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

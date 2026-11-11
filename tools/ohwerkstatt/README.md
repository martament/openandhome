# openandhome Werkstatt-Tool (intern, nur Linux)

Menü für Test und Auslieferung der Sensorboxen. **Nicht an Kunden ausliefern** —
dafür gibt es [`tools/ohtoolbox/`](../ohtoolbox/README.md).

```
tools/ohwerkstatt/oh_werkstatt.sh
```

Voraussetzungen: Python 3, Box per USB (`/dev/ttyUSB*`), Benutzer in Gruppe
`dialout` (`sudo usermod -aG dialout $USER`, danach neu anmelden).

| Punkt | Funktion | Weg |
|---|---|---|
| 1 | Gerätename/Unit setzen (`Name`, `Unit`, `Save`) | USB |
| 2 | 1-Wire-Scan (`OWScan,<GPIO>`), Ergebnis auch in `ow-scan.txt` | USB |
| 3–5 | Syslog an (192.168.9.4, Level Info) / aus / Status | HTTP `/advanced`, IP per USB |
| 6 | Teardown: Syslog aus, Admin-Passwort löschen, bei WLAN-Boxen SSIDs löschen, Save, Reboot | HTTP + USB |
| 7 | `config.dat` / Backup-Tar prüfen | lokal |
| 8 | Fertig-Images laden (nur Branch `devel`) | GitHub |
| 9 | Serieller Monitor (`oh-monitor.txt`) | USB |
| a | Sensoren erkennen (I2C, DS18B20) und passende Tasks einschalten, OLED-Zeilen setzen; HC-SR04/Wassersensor per Abfrage | USB + HTTP |

Nach einem Neuflash: Ablauf in Plan Abschnitt 8.2 (u. a. `ClearAccessBlock`,
wenn der PC in einem anderen Subnetz als die Box liegt).

Ablauf des 24h-Tests: [`plans/espeasy-fertig-images.md`](../../plans/espeasy-fertig-images.md), Abschnitt 6.
WLAN für den Test setzen: ohtoolbox, Punkt 1.

Die Python-Helfer lassen sich auch einzeln aufrufen:
[`espeasy_syslog.py`](../bin/espeasy_syslog.py),
[`espeasy_autoconfig.py`](../bin/espeasy_autoconfig.py),
[`espeasy_configcheck.py`](../bin/espeasy_configcheck.py),
[`espeasy_download.py`](../bin/espeasy_download.py).

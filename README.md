# openandhome

<a href="https://www.openandhome.de"><img src="https://raw.githubusercontent.com/martament/openandhome/master/images/logo.gif"></a>

Dateien für die openandhome-Sensorboxen (**Standalone** mit WLAN und **Professional** mit
Netzwerkkabel/PoE). Die Boxen laufen mit [ESPEasy](https://github.com/letscontrolit/ESPEasy) –
mit den offiziellen Release-Images, ohne Eigenbuild.

## Für Kunden

- **Toolbox und OH-Flasher** (Windows/Linux): WLAN, Name, Zeitserver, Sensoren erkennen,
  Grundkonfiguration, Firmware-Update und Neu-Aufspielen:
  **https://github.com/martament/openandhome/releases/latest** (dort `ohtoolbox.zip` herunterladen) –
  Beschreibung in [`tools/ohtoolbox/README.md`](tools/ohtoolbox/README.md).
- **Bedienungsanleitungen:** [`docs/`](docs/)

Shop und Support: https://www.openandhome.de

## Inhalt des Repos

| Pfad | Inhalt |
|---|---|
| [`configs/espeasy/`](configs/espeasy/) | Freigegebene Images und Grundkonfigurationen je Box |
| [`tools/ohtoolbox/`](tools/ohtoolbox/) | Kunden-Paket (Toolbox + OH-Flasher) |
| [`tools/ohwerkstatt/`](tools/ohwerkstatt/README.md) | Werkstatt-Tool (intern): Aufsetzen, 24h-Test, Auslieferung |
| [`tools/bin/`](tools/bin/) | Gemeinsame Python-Module |
| [`docs/`](docs/) | Bedienungsanleitungen |
| [`AGENTS.md`](AGENTS.md) | Regeln und Aufbau für Entwickler |

# Rolle: credentials

Erzeugt und liest die Zugangsdaten des Servers.

## Zweck

- Liest `/etc/openandhome/credentials.yml` (0600 root); fehlende Schlüssel werden zufällig
  erzeugt (20 Zeichen, ohne leicht verwechselbare Zeichen), vorhandene bleiben unverändert.
- Stellt sie anderen Rollen als `credentials_values` bereit.

## Variablen

| Variable | Standard | Beschreibung |
|---|---|---|
| `credentials_file` | `/etc/openandhome/credentials.yml` | Ablage auf dem Server |
| `credentials_keys` | MQTT, InfluxDB, Grafana | Liste der Schlüssel (siehe `defaults/main.yml`) |
| `credentials_length` | `20` | Passwortlänge |

## Verwendung

Läuft in [`../../site.yml`](../../site.yml) immer zuerst (Tag `always`).

## Stolperfallen

Die Datei gehört nie ins Repo. Ein Schlüssel wird nur durch Löschen aus der Datei neu
erzeugt; danach `site.yml` laufen lassen (die Rollen gleichen Passwörter an).

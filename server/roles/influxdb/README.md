# Rolle: influxdb

InfluxDB 2 als Datenspeicher, nur lokal erreichbar.

## Zweck

- Installiert `influxdb2` und `influxdb2-cli`, lauscht nur auf `127.0.0.1:8086`, keine Telemetrie.
- Ersteinrichtung per API (Org `openandhome`, Benutzer `admin`, Operator-Token aus den Zugangsdaten).
- Buckets mit Aufbewahrung aus `oh_influx_buckets`; je Bucket eine InfluxQL-Datenbank
  gleichen Namens (DBRP).
- v1-Benutzer `telegraf` (schreiben) und `grafana` (lesen) für alle Buckets.

## Variablen

| Variable | Standard | Beschreibung |
|---|---|---|
| `influxdb_url` | `http://127.0.0.1:8086` | API-Adresse |
| `influxdb_bind_address` | `127.0.0.1:8086` | Lauschadresse |

Buckets und Aufbewahrung in [`../../group_vars/all/main.yml`](../../group_vars/all/main.yml).

## Verwendung

Teil von [`../../site.yml`](../../site.yml) (Tag `influxdb`).

## Stolperfallen

Kürzere Aufbewahrung löscht ältere Daten beim nächsten Lauf.

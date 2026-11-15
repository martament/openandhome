# Rolle: telegraf

Nimmt Messwerte (MQTT) und Logs (Syslog) der Sensorboxen an und schreibt sie in die InfluxDB.

## Zweck

- Installiert Telegraf mit der Konfiguration aus [`../../stack/telegraf/telegraf.conf`](../../stack/telegraf/telegraf.conf).
- Zugangsdaten über `/etc/openandhome/telegraf.env` (systemd-Drop-in), Port 514 per
  `CAP_NET_BIND_SERVICE` ohne root.

## Verwendung

Teil von [`../../site.yml`](../../site.yml) (Tag `telegraf`).

## Stolperfallen

ESPEasy-Syslog hat keinen Zeitstempel; deshalb `socket_listener` + Starlark statt
`inputs.syslog` (siehe [`../../AGENTS.md`](../../AGENTS.md)).

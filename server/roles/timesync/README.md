# Rolle: timesync

chrony als Zeitquelle und NTP-Server für die Sensorboxen im LAN.

## Zweck

- Ersetzt systemd-timesyncd durch chrony; Internet-Pool, dazu der DHCP-Server (Router).
- Erlaubt Zeitabfragen aus privaten Netzen.
- Mit RTC (`/dev/rtc0`, DS3231) liefert der Server auch ohne Internet Zeit
  (`local stratum 10`). Ohne RTC nicht – dafür `fake-hwclock`.

## Variablen

| Variable | Standard | Beschreibung |
|---|---|---|
| `timesync_pools` | `[de.pool.ntp.org]` | Zeitquellen im Internet |

## Verwendung

Teil von [`../../site.yml`](../../site.yml) (Tag `timesync`).

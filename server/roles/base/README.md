# Rolle: base

Grundeinrichtung des Pi für den Dauerbetrieb.

## Zweck

- Prüft die SD-Karte: Größe (`oh_min_disk_hard_gb`) und synchrone Schreibleistung (`oh_min_card_iops`).
- Trägt die Paketquellen von InfluxData und Grafana ein (deb822). Die Schlüssel werden auf dem
  Werkstatt-PC geladen und gegen feste Fingerabdrücke geprüft.
- Systemupdate, Neustart bei Bedarf, apt behält keine `.deb`-Dateien.
- Auslagerung nur zram (`/var/swap` weg), Journal nur im RAM (100 MB).
- SD-Karte schonen: Kernel-Writeback und ext4-Journal (`commit=`) nur alle `oh_write_interval_s`
  (300 s); bei Stromausfall gehen bis zu ~10 Minuten Daten verloren.
- SSH nur per Key, kein root; Firewall (nftables) nur aus privaten Netzen: SSH, MQTT,
  Grafana, NTP, Syslog, mDNS. Automatische Sicherheitsupdates.

## Variablen

| Variable | Standard | Beschreibung |
|---|---|---|
| `base_packages` | python3-debian, nftables, … | Grundpakete |
| `base_apt_repos` | influxdata, grafana | Quellen mit Schlüssel-URL und Fingerabdruck |
| `base_journal_max_use` | `100M` | Journal-Größe |

Ports, Netze und Kartengrenzen in [`../../group_vars/all/main.yml`](../../group_vars/all/main.yml).

## Verwendung

Teil von [`../../site.yml`](../../site.yml) (Tag `base`).

## Stolperfallen

Der Grafana-Schlüssel läuft am 2027-08-22 ab – dann neuen Fingerabdruck eintragen.

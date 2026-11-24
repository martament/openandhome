# AGENTS.md — server/

Ansible für den openandhome-Server (Raspberry Pi 4 B, Raspberry Pi OS Lite arm64, apt).
Maßgeblich ist [`../plans/server-ansible.md`](../plans/server-ansible.md); Projektregeln in
[`../AGENTS.md`](../AGENTS.md). Doku/Kommentare Deutsch, Bezeichner Englisch.

## Regeln

- **Umfang nur Sensorboxen.** Kein Tasmota/zigbee2mqtt/Wetter, keine Bezüge zur privaten
  Heiminstallation (Docker-Stack im privaten Ansible-Repo).
- **Kein festes Image, kein Klon.** `image_download` folgt immer der Weiterleitung
  `raspios_lite_arm64_latest`; Release und SHA256 landen in `openandhome-build.txt`
  (im Image und neben dem Image) und später im Testprotokoll.
- **Image-Anpassung ohne root:** nur Dateien der FAT-Boot-Partition, per `mtools`
  (`mcopy -i <img>@@<offset>`). Erste Einrichtung macht cloud-init (NoCloud aus
  `/boot/firmware`, Modul `rpi:` für I2C). SSH wird über die leere Datei `ssh`
  eingeschaltet (`sshswitch.service`), nicht über cloud-init.
- `image.yml` ist ein **Build**: jeder Lauf entpackt ein frisches Image (`changed` ist dort
  erwartet). Für `site.yml` gilt dagegen: zweiter Lauf `changed=0`.
- **`sd_write`:** nur `/dev/sdX` oder `/dev/mmcblkN`, wechselbar/USB/MMC, ≤ 256 GB, keine
  Systemeinhängepunkte, Bestätigung durch Eintippen. Nur umount/dd/cmp mit `become`.
  Diese Prüfungen nie abschwächen.
- **Keine Passwörter im Repo.** Zugangsdaten werden je Server zufällig erzeugt (Phase 2)
  und nur ins Übergabeprotokoll geschrieben. WLAN gibt es auf dem Server nicht.
- Variablen mit Rollenpräfix (`image_download_`, `image_customize_`, `sd_write_`); gemeinsame
  Werte mit `oh_` in `group_vars/all/main.yml`. Downloads mit `use_netrc: false`.
- `ansible-lint` muss im Profil `production` bestehen.

## Befunde zum Image (2026-10-06-raspios-trixie-arm64-lite)

- Boot-Partition FAT (Partition 1, Start 16384), Root ext4. `cmdline.txt` enthält `resize`.
- cloud-init 25.2 (`99_raspberry-pi.cfg`): Datasource NoCloud `file:///boot/firmware`,
  Standardbenutzer `pi` (gesperrt) – entfällt, weil `users:` kein `default` enthält.
  Netzwerk über netplan → NetworkManager. Zeit standardmäßig `systemd-timesyncd`.
- Vorinstalliert u. a.: avahi-daemon, network-manager, nftables, openssh-server, python3 3.13.
- cloud-init meldet auf dem Pi `extended_status: degraded done` wegen
  `Could not find module named cc_netplan_nm_patch` – das Modul steht in der
  mitgelieferten `cloud.cfg` von Raspberry Pi OS, nicht in unseren Dateien; harmlos.
- Das Image legt `/var/swap` (2,1 GB) an, aktiv ist aber nur zram – `base` räumt auf.
- Erster echter Lauf (2026-11-15): Pi 4 Model B Rev 1.1, 4 GB; Ping per `.local` ok.
  Dort kein DS3231 bestückt (`rtc-ds1307 1-0068: probe … error -5`).

## Befunde Phase 2 (2026-11-15)

- **SD-Karte entscheidet über alles.** Testkarte SA08G (2014, 8 GB): 2 synchrone
  4-KB-Schreibvorgänge/s, 3,1 MB/s sequentiell → Grafana-Paket 13 min entpacken,
  Grafana-Migrationen > 10 min, danach Karte voll. Daher Prüfungen in `base`
  (`oh_min_disk_hard_gb`, `oh_min_card_iops`). Belegung mit allen Diensten ca. 6,2 GB.
- Grafana 13 kopiert beim Installieren die gebündelten Plugins nach
  `/var/lib/grafana/plugins-bundled` (ca. 530 MB zusätzlich zu 1,4 GB in `/usr/share/grafana`).
- apt behält `.deb`-Dateien (ca. 0,7 GB) – `base` schaltet das ab.
- `inputs.syslog` (auch mit `best_effort`) verwirft bei ESPEasy-Zeilen ohne Zeitstempel
  (`<PRI>Box EspEasy: Text`) den Text. Ersatz: `inputs.socket_listener` + Starlark
  (`stack/telegraf/telegraf.conf`), erkennt `Box EspEasy:` und `Box_EspEasy:`.
- InfluxDB 2 ohne DBRP `telegraf/autogen`: Datenbank = Bucket (`openandhome`,
  `sensorbox_logs`, `system`), v1-Benutzer `telegraf` (schreiben) und `grafana` (lesen).
- MQTT-Benutzer `sensorbox` hat `readwrite openandhome/#` (ESPEasy abonniert
  `openandhome/%sysname%/#` für Befehle).
- Ansible auf dem Pi braucht etwas freien Platz in `~/.ansible/tmp`; bei voller Karte
  scheitert jeder Lauf mit „Failed to create temporary directory“.
- `grafana cli` bricht mit `panic: error getting work directory: stat .: permission denied`
  ab, wenn das Arbeitsverzeichnis für `grafana` nicht lesbar ist → immer mit
  `chdir: /usr/share/grafana` und `runuser -u grafana` aufrufen (auch später in `oh_config`).
- Die Kartenmessung schwankt auf dem fertigen Server stark (leere Karte 149/s, mit laufenden
  Diensten 24–29/s). Harte Grenze daher nur vor der ersten Installation, danach Hinweis.
- Erster vollständiger Lauf auf 64-GB-Karte (Pi 4, 2026-11-15): `failed=0`, zweiter Lauf
  `changed=0`; Grafana-Rollen, Rechte (viewer 403 / editor 200 beim Speichern), Datenquellen,
  MQTT, Syslog und Admin-Rücksetzen per `site.yml` geprüft. Belegung 6,5 GB.

## Befunde Dashboards und echte Sensorbox (2026-11-15)

- Wertnamen der Basis-configs: `Temperatur`, `Luftfeuchtigkeit`, `Distance` (HCSR04), `State`,
  `uptime`, `freeheap`, `rssi`, `load` – Dashboards erkennen zusätzlich die englischen Namen.
- **System-Werte beider Klassen gleich** (Basis-configs seit 2026-11-15): `uptime` Minuten,
  `freeheap` Bytes, `rssi` dBm, `load` %, alle 300 s, 0 Nachkommastellen, keine Formeln.
  Ältere ESP8266-Boxen (Kunden) senden noch `freeheap` in KB (`%value%/1024`) und `rssi` als
  `100+%value%`; das Dashboard „Sensorboxen – System“ rechnet sie um (`UMRECHNUNG` in
  `dashboards.py`: zweite Abfrage je Wert für `< 1024` bzw. `> 0`). `rssi` = 0 (Typ 2026 über
  Ethernet, WLAN aus) wird nicht angezeigt.
- config.dat direkt ändern: Settings-MD5 liegt bei ESP32 an 0xBBC (Struktur 3064 Byte), bei ESP8266
  an 0x514 (Struktur 1352 Byte); MD5 über die Struktur ohne die 16 MD5-Bytes. Die Firmware prüft sie
  nur fürs Log. Task-Blöcke (Name, Formeln ab +42, Wertnamen ab +206, je 41 Byte) liegen bei ESP32 ab
  0x8000, bei ESP8266 ab 0x1000, je Task 2048 Byte weiter, und haben keine Prüfsumme.
  Stellen vorher an einer Box per `/download` gegenprüfen.
- **Optionale Panels ausblenden geht nur im v2-Format** (dynamische Dashboards,
  `dashboardNewLayouts` ist in Grafana 13 an): `AutoGridLayout` + `conditionalRendering`
  (`ConditionalRenderingData`). Im klassischen Raster gibt es das nicht; `repeat` über eine
  leere Variable zeigt in Grafana 13 trotzdem ein leeres Panel. `dashboards.py` erzeugt
  `messwerte.json` deshalb mit `als_v2()`; die Datei-Provisionierung liest v2 problemlos.
- ESPEasy sendet LWT auf `openandhome/<Box>/status/LWT` (`Connected`/`Connection Lost`) –
  passt auf `openandhome/+/+/+`; Telegraf (`auto_float` + Starlark) legt es in
  `openandhome_status` ab und verwirft Text/NaN in `openandhome`.
- Prüfung im Browser: `grafana_sicht.py` (headless Chromium per CDP, im Scratchpad dieser
  Sitzung) – sichtbar ist ein Panel nur mit `getBoundingClientRect().height > 0`, ausgeblendete
  stehen weiter im DOM.

## Befunde SD-Karte schonen (2026-11-20)

- **Gesammelt schreiben, alle 5 Minuten** (`oh_write_interval_s: 300`, Vorgabe Nutzer:
  seltenes Schreiben ist wichtiger als Datenverlust bei Stromausfall, bis ~10 min in Kauf
  genommen): Telegraf `interval`/`flush_interval` 300 s (fest in `stack/telegraf/telegraf.conf`),
  Kernel `vm.dirty_expire/writeback_centisecs` 30000, ext4 `commit=300` (fstab + remount),
  Grafana SQLite `GF_DATABASE_WAL=true` und Log nur ins Journal, Mosquitto ohne Persistenz und
  Log ins Journal; das Journal liegt im RAM (`Storage=volatile`, Raspberry Pi OS ohnehin).
- **Nie `storage-wal-fsync-delay` in InfluxDB:** jeder Schreibzugriff wartet dann auf das
  verzögerte fsync – Telegraf bricht nach 5 s ab („context deadline exceeded“), `/api/v2/delete`
  hängt > 400 s. Die Rolle `influxdb` entfernt die Zeile.
- Telegraf `max_undelivered_messages = 20000` (Standard 1000 hielte das MQTT-Lesen bis zum
  nächsten Schreiben an). Der Funktionstest lässt Telegraf per `systemctl reload` (SIGHUP
  schreibt den Puffer) sofort schreiben, sonst warteten T2–T4 bis zu 5 Minuten.
- Messung ohne sendende Box (Leerlauf): vorher ~440 Schreibvorgänge/~3,4 MB in 9 min, nachher
  113/~1 MB. Rest fast nur Grafana: `server_lock` (interne Jobs, minütlich), nicht abschaltbar.
  Messen: `/proc/diskstats` (Feld 8 = Schreibvorgänge) und `/proc/<pid>/io` (`write_bytes`).
- Grafana-Panels verbinden Lücken bis 1 h (`spanNulls`), 5-Minuten-Daten sehen daher normal aus.
  Neue Werte erscheinen in Grafana erst nach bis zu 5 Minuten.

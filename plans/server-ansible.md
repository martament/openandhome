# Plan: openandhome-Server per Ansible (Raspberry Pi) + Kunden-Konfigprogramm

**Status:** Entwurf v2 — nur Planung, noch keine Umsetzung.
v2 berücksichtigt die Vorgaben: Pi 4 B als Hauptgerät, apt statt Docker auf dem Pi,
DHCP, ein Server je Kunde, nur Sensorboxen, kein Klon/Golden Image, Kunden-Konfigprogramm
mit drei Betriebsarten.

**Ziel:** Unter [`server/`](../server/) liegt ein Ansible-Playbook, das bei jedem Lauf das
**aktuelle** Raspberry-Pi-OS-Image lädt, für openandhome anpasst, auf eine SD-Karte schreibt,
den Server per SSH installiert und am Ende **automatisch auf Funktion testet**. Der Server
empfängt Messwerte und Logs der Sensorboxen und zeigt sie in Grafana an (Rollen Viewer/Editor).
Ein Konfigprogramm für den Kunden verbindet die Sensorboxen mit dem Server (oder mit einem
eigenen Docker-Server bzw. der eigenen Lösung des Kunden).

---

## 0. Sofort-Befund (vor der Umsetzung erledigen)

In der alten Server-Doku `openandhome-server/openandhome-server1.odt` und in
`openandhome-server/configs/telegraf/openandhome_wiener.conf` stehen Klartext-Passwörter
(root/pi/Mosquitto `openhabian`, Grafana-admin, Telegraf-Influx-Passwort) sowie
WLAN-Zugangsdaten eines Kunden.

- **Diese Werte gelten als kompromittiert.** Sie werden im neuen Aufbau nicht übernommen,
  bestehende Kundenserver/-netze mit diesen Daten sollten geändert werden.
- Der alte Ordner `openandhome-server/` liegt nicht in Git und bleibt nur Analysequelle.
  Nichts daraus wird ungeprüft in dieses Repo kopiert.

---

## 1. Bestandsaufnahme (Analyse des alten Images)

| Thema | Altes Image `openandhome-server1` | Bewertung |
|---|---|---|
| Betriebssystem | Raspbian 12 bookworm, **32 Bit (armhf)**, ursprünglich 2020, hochgezogen | ersetzen durch frisches 64-Bit-Image |
| Benutzer | `pi` (Passwort aus der Doku) | ersetzen durch `ohadmin` (nur SSH-Key) |
| Dienste | apt-Pakete: Mosquitto 2.0.11, **InfluxDB 1.8.10** (EOL), Telegraf 1.31, **Grafana Enterprise** 11.1 | apt beibehalten; InfluxDB 2, Grafana OSS |
| Netzwerk | dhcpcd **und** NetworkManager parallel, ModemManager | nur NetworkManager (Image-Standard), ModemManager weg |
| Zeit | ntp **und** ntpsec parallel, DS3231-RTC per Overlay | chrony + DS3231, Server ist NTP-Server im LAN |
| Hardware | `dtoverlay=i2c-rtc,ds3231`, `disable-wifi`, `disable-bt` | übernehmen |
| Mosquitto | kein anonymer Zugriff, Passwortdatei | übernehmen, neue Benutzer/Passwörter je Server |
| Telegraf | MQTT `openandhome/#`, `sensoren/#`, Tasmota, zigbee2mqtt, Wetter; Regex-Zerlegung in `sensorbox`/`device`/`valuename` | nur `openandhome/#`; `topic_parsing` statt Regex, **gleiche Tag-Namen** |
| Grafana | anonymer Zugriff an, Benutzer `viewer`/`editor` nur in der Doku | anonym aus, Rollen per Ansible |
| Dashboards | `Sensoren`, `Sensoren - System`, `System Monitoring-rpi` (InfluxQL, Measurement `openandhome`); `Agrarset_*` (altes `mqtt_consumer`-Schema) | erste drei übernehmen und bereinigen, `Agrarset_*` entfallen |
| Daten | InfluxDB leer | keine Migration nötig |
| Sonstiges | VS-Code-Repo, triggerhappy, rsync-Dienst, NFS-Client | entfallen |

ESPEasy-Thema der Sensorboxen (aus der Doku):
`openandhome/%sysname%/%tskname%/%valname%` (Publish), `openandhome/%sysname%/#` (Subscribe).

**Umfang:** ausschließlich Sensorboxen. Tasmota, zigbee2mqtt, Wetter und die private
Heiminstallation (Docker-Stack im privaten Ansible-Repo) gehören **nicht** dazu.

---

## 2. Entscheidungen

| # | Entscheidung | Begründung |
|---|---|---|
| E1 | **Hauptgerät Raspberry Pi 4 Model B**, Raspberry Pi OS **Lite 64 Bit (arm64)**, jeweils aktuelles Release (derzeit trixie) | InfluxDB 2 gibt es nur für 64 Bit; Pi 4 hat genug RAM |
| E2 | **Pi 3 Model B v1.2 nur „best effort“**: gleiches Image (arm64 läuft dort), aber nicht Teil des Pflichttests. Scheitert der Funktionstest am RAM (1 GB), wird die Unterstützung gestrichen | Vorgabe: im Zweifel weglassen |
| E3 | **Installation per apt**, kein Docker auf dem Pi | Vorgabe; weniger RAM, gewohnte Abläufe |
| E4 | **DHCP**; Erreichbarkeit per Hostname `openandhome-server1` (Router-DNS, z. B. FRITZ!Box) und `openandhome-server1.local` (mDNS/avahi). Sensorboxen bekommen vom Konfigprogramm **den Namen, falls er auflösbar ist, sonst die IP** (Abschnitt 6.4) | Vorgabe DHCP; ESPEasy löst kein mDNS auf |
| E5 | **Ein Server je Kunde.** Zugangsdaten werden **je Server neu erzeugt** und nur im Übergabeprotokoll ausgegeben, nie im Repo | Regel 7 in AGENTS.md sinngemäß |
| E6 | **Kein Klon/Golden Image.** Jeder Server: aktuelles Image laden → anpassen → installieren → automatischer Funktionstest. Image-Release, SHA256 und Paketversionen landen im Protokoll | Vorgabe |
| E7 | **InfluxDB 2**, Abfragen per InfluxQL; Datenbank = Bucket (`openandhome`, `sensorbox_logs`, `system`). Die alten Dashboards werden neu erzeugt (`stack/grafana/dashboards.py`), daher keine Zuordnung `telegraf/autogen` | alte Dashboards nutzen in Grafana 13 entfernte Paneltypen |
| E8 | **Grafana OSS** (Paket `grafana`, nicht `grafana-enterprise`), Benutzer `admin`, `editor` (Rolle Editor), `viewer` (Rolle Viewer), anonymer Zugriff aus | Vorgabe Rollen; Enterprise ohne Lizenz unnötig |
| E9 | **Logs der Sensorboxen über Telegraf `inputs.syslog`** (UDP 514, RFC 3164) in einen eigenen Influx-Bucket, Anzeige in Grafana (Logs-Panel). Kein Loki auf dem Pi | spart RAM; Grafana zeigt Metriken und Logs |
| E10 | **Eine Quelle für die Stack-Konfiguration** (Abschnitt 4): dieselben Dateien dienen der apt-Installation (Ansible) und dem Docker-Stack (Konfigprogramm, Betriebsart b) | kein Auseinanderlaufen von Pi- und Docker-Variante |
| E11 | **Kundeneinstellungen über eine Textdatei auf der Boot-Partition** (`openandhome.txt`, FAT, unter Windows lesbar), angewendet von einem Dienst auf dem Server. Das Konfigprogramm nutzt **denselben Weg** | Vorgabe: Textdatei oder Konfigprogramm, ein Mechanismus |
| E12 | **Konfigprogramm = Erweiterung der ohtoolbox** (neues Menü „Server“), keine dritte Anwendung | Regel 4: ein Paket, dieselben Module |
| E13 | Entwicklung auf `devel`, Merge nach `master` erst nach bestandenem Funktionstest | Branch-Modell, Regel 6 |

---

## 3. Verzeichnisstruktur `server/`

```
server/
├── README.md                 # Bedienung (Menschen)
├── AGENTS.md                 # Detailregeln (KI-Agents)
├── ansible.cfg
├── inventory.yml             # localhost (Image/SD) + openandhome-server1 (DHCP, per Name)
├── group_vars/all/main.yml   # Image-Quelle, Ports, Aufbewahrung, Benutzer, Hostname
├── group_vars/all/vault.yml.example   # nur Platzhalter; echte vault.yml nie committen
├── image.yml                 # Phase 1 (lokal): herunterladen, anpassen, SD schreiben
├── site.yml                  # Phase 2 (per SSH): Server installieren
├── test.yml                  # Phase 3: automatischer Funktionstest + Protokoll
├── server.yml                # alles nacheinander (image → warten auf SSH → site → test)
├── stack/                    # EINE Quelle der Dienst-Konfiguration (E10, Abschnitt 4)
│   ├── mosquitto/openandhome.conf
│   ├── telegraf/openandhome.conf
│   ├── grafana/provisioning/{datasources,dashboards,alerting}/…
│   ├── grafana/dashboards/*.json
│   └── docker/compose.yml    # nur für Betriebsart b (Kunden-Docker-Server)
└── roles/
    ├── image_download        # aktuelles Lite-arm64-Image + SHA256 prüfen, Cache
    ├── image_customize       # Loop-Mount, cloud-init, config.txt, openandhome.txt-Vorlage
    ├── sd_write              # Schreiben nur auf ausdrücklich angegebenes Gerät
    ├── base                  # Pakete, Härtung, Firewall, SD-schonendes Logging, avahi
    ├── timesync              # chrony + DS3231, NTP-Server fürs LAN
    ├── mosquitto
    ├── influxdb
    ├── telegraf
    ├── grafana
    ├── oh_config             # Dienst, der openandhome.txt anwendet (E11)
    └── server_test           # Funktionstest (test.yml)
```

Konventionen (angelehnt an das private Ansible-Repo, aber eigenständig): Variablen mit
Rollenpräfix, `no_log: true` bei Secrets, zweiter Lauf `changed=0`, nur-lesende Befehle
`changed_when: false`, APT-Quellen im deb822-Format mit `Signed-By`, je Rolle `README.md`.

---

## 4. Eine Quelle für die Stack-Konfiguration (E10)

Die Dateien unter `server/stack/` enthalten **keine Passwörter**, sondern Umgebungsvariablen:

- Telegraf und Grafana-Provisioning lösen `${VAR}` bzw. `$__env{VAR}` selbst auf.
- **apt/Pi:** Ansible legt `/etc/openandhome/stack.env` (0600) an und bindet sie per
  systemd-Drop-in (`EnvironmentFile=`) bei telegraf und grafana-server ein.
- **Docker (Betriebsart b):** dieselben Dateien werden eingehängt, Werte kommen aus `.env`.
- Mosquitto kennt keine Variablen: Konfig ist statisch, die Passwortdatei wird erzeugt
  (Pi: `mosquitto_passwd`; Konfigprogramm: Hash in Python oder `docker run … mosquitto_passwd`).

Inhalt der Konfiguration:

| Dienst | Konfiguration |
|---|---|
| Mosquitto | Listener 1883 (LAN), `allow_anonymous false`, Benutzer `sensorbox` (nur Schreiben auf `openandhome/#`) und `telegraf` (nur Lesen), ACL-Datei, Persistenz an |
| Telegraf | `inputs.mqtt_consumer` auf `openandhome/+/+/+`, `topic_parsing` → Tags `sensorbox`, `device`, `valuename`, Measurement `openandhome`, Wert als float; `inputs.syslog` UDP 514 → Bucket `sensorbox_logs`; Systemmetriken des Servers (cpu, mem, disk, system, temp) → Bucket `system` |
| InfluxDB 2 | Org `openandhome`, Buckets `openandhome` (Aufbewahrung Standard 2 Jahre), `sensorbox_logs` (30 Tage), `system` (30 Tage); DBRP `telegraf/autogen` → `openandhome`; getrennte Tokens für Telegraf (schreiben) und Grafana (lesen) |
| Grafana | Datenquelle InfluxQL (Token per Header), Ordner „openandhome“ mit den Dashboards, Variable `$sensorbox`; Benutzer `admin`/`editor`/`viewer`; Dashboards **nur importieren, wenn sie fehlen** (Änderungen der Editoren bleiben); Alarmregel „Sensorbox sendet nicht“ (optional, nur aktiv, wenn SMTP gesetzt ist) |

Die Dashboards werden auf die Tags `sensorbox`/`device`/`valuename` und `$sensorbox`
umgestellt; fest eingetragene Boxnamen entfallen. Ein neues Dashboard „Sensorbox-Logs“
zeigt die Syslog-Meldungen je Box.

---

## 5. Ablauf Werkstatt: neuer Server je Kunde

### Phase 1 – Image (`image.yml`, lokal, mit `become` für Loop-Mount und dd)

1. **Herunterladen:** `https://downloads.raspberrypi.com/raspios_lite_arm64_latest`
   (Weiterleitung auf das aktuelle Release) + zugehörige `.sha256`; Prüfsumme prüfen;
   Cache in `~/.cache/openandhome/raspios/`. Release-Name und SHA256 werden gemerkt
   (für das Protokoll).
2. **Anpassen** (ohne Einhängen, per mtools direkt in der Boot-Partition der Image-Datei):
   - cloud-init (`user-data`, `network-config`, `meta-data` auf der Boot-Partition):
     Hostname `openandhome-server1`, Benutzer `ohadmin` mit Werkstatt-SSH-Key, ohne Passwort-Login,
     Locale `de_DE.UTF-8`, Zeitzone `Europe/Berlin`, Tastatur `de`, Ethernet per DHCP.
     *Prüfpunkt P1:* Falls das aktuelle Image kein cloud-init nutzt, Rückfall auf
     `userconf.txt` + `ssh`-Datei (Rolle erkennt das am Inhalt der Boot-Partition).
   - `config.txt`: `dtparam=i2c_arm=on`, `dtoverlay=i2c-rtc,ds3231`, `dtoverlay=disable-wifi`,
     `dtoverlay=disable-bt`.
   - Vorlage `openandhome.txt` auf der Boot-Partition (alle Felder leer, mit Erklärung).
3. **SD schreiben:** nur mit `-e sd_device=/dev/sdX`. Die Rolle bricht ab, wenn das Gerät
   nicht wechselbar ist, größer als 256 GB, eingehängt ist oder eine Systempartition enthält,
   und fragt einmal mit Anzeige von Größe/Modell nach.

### Phase 2 – Installation (`site.yml`, per SSH auf den Pi)

`base` → `timesync` → `mosquitto` → `influxdb` → `telegraf` → `grafana` → `oh_config`

- `base`: System aktualisieren, Pakete (avahi-daemon, chrony, i2c-tools, nftables,
  unattended-upgrades), ModemManager/triggerhappy entfernen, SSH nur per Key,
  Firewall (offen: 22, 1883, 3000, 123/udp, 514/udp, 5353/udp; alles nur LAN),
  Journal begrenzt (`SystemMaxUse`), `noatime`, Swap klein.
- `timesync`: chrony mit Internet-Pool, Router als Fallback, RTC per `rtcsync`;
  `allow` für private Netze, `local stratum 10` (Server liefert auch ohne Internet Zeit).
- Dienste nach Abschnitt 4; Zugangsdaten werden beim ersten Lauf **zufällig erzeugt**,
  auf dem Server in `/etc/openandhome/` (0600) abgelegt und in das Übergabeprotokoll
  übernommen. Folgeläufe lesen sie von dort (idempotent).

### Phase 3 – Funktionstest (`test.yml`, Pflicht vor Auslieferung)

Automatisch, Ergebnis als Protokoll unter `~/openandhome-serverprotokolle/<Datum>_<MAC>/`:

| # | Prüfung |
|---|---|
| T1 | Alle Dienste aktiv, auch **nach einem Neustart** (Test startet den Pi neu) |
| T2 | Simulierte Sensorbox: `mosquitto_pub -u sensorbox` auf `openandhome/Testbox/Fuehler1/Temperature` → Wert per InfluxQL mit Tags `sensorbox=Testbox`, `device=Fuehler1`, `valuename=Temperature` lesbar |
| T3 | Anonymes MQTT abgelehnt; Benutzer `sensorbox` darf nicht lesen |
| T4 | Syslog: UDP-Meldung im ESPEasy-Format (`<14>Testbox_EspEasy: …`) → im Bucket `sensorbox_logs` |
| T5 | Grafana: `viewer` sieht Dashboards und Daten, Speichern ergibt 403; `editor` darf speichern; ohne Anmeldung kein Zugriff |
| T6 | Dashboard-Abfrage über die Grafana-API liefert die Testwerte (Datenquelle funktioniert) |
| T7 | NTP: Server beantwortet Zeitanfragen; `hwclock -r` liest die RTC (Warnung statt Fehler ohne RTC) |
| T8 | `openandhome.txt`: Testwert eintragen → Dienst wendet an → Feld geleert |
| T9 | Zweiter `site.yml`-Lauf: `changed=0` |
| T10 | Optional mit echter Sensorbox (Werkstatt-Box per Konfigprogramm verbinden): Messwerte und Logs kommen an |
| T11 | Testdaten entfernen (Testbox-Serien, Test-Logs), damit der Kunde einen leeren Server bekommt |

Protokoll enthält: Image-Release + SHA256, Paketversionen (mosquitto, influxdb2, telegraf,
grafana), Ergebnis T1–T11, **Übergabeblatt** mit Hostname, Grafana-Zugängen
(admin/editor/viewer), MQTT-Zugang für Sensorboxen und Kennwort für das Konfigprogramm.
Das Übergabeblatt wird ausgedruckt/dem Kunden übergeben, nicht ins Repo gelegt.

**Freigabe:** Bestehen T1–T9 und T11 auf dem Pi 4 mit dem aktuellen Image, wird der
Stand von `devel` nach `master` übernommen (E13). Da das Image nicht festgeschrieben ist,
belegt das Protokoll, mit welchem Release getestet wurde.

### Werkstatt-Bedienung

```bash
cd server
ansible-playbook server.yml -e sd_device=/dev/sdX        # alles
ansible-playbook image.yml  -e sd_device=/dev/sdX        # nur Karte
ansible-playbook site.yml                                 # nur installieren/aktualisieren
ansible-playbook test.yml                                 # nur testen
```

Später optional als Menüpunkt im Werkstatt-Tool (`oh_werkstatt.sh`, „Server aufsetzen“).

---

## 6. Kunden-Konfigprogramm (ohtoolbox, Menü „Server“)

Die ohtoolbox (portables Python, Windows/Linux) erhält einen Bereich **„Sensorboxen im
Netzwerk / Server“**. Die Sensorboxen werden wie bisher per HTTP (oder USB) angesprochen;
neu ist die Netzwerksuche nach Boxen und nach dem Server.

### 6.0 Menüstruktur der Toolbox

**Grundsätze**

- **Je Ebene höchstens 5–6 Punkte**; was selten oder riskant ist, steht unter **w – Weitere**.
- **Nur zeigen, was passt:** ohne Box am USB kein USB-Menü; Professional ohne WLAN-Punkte
  (außer unter Weitere); im Server-Bereich nur die Punkte der gewählten Betriebsart;
  „Stack installieren“ nur, solange noch keiner installiert ist.
- **Betriebsart einmal wählen:** Beim ersten Aufruf fragt ein kurzer Assistent „Wohin sollen
  Ihre Sensorboxen ihre Daten senden?“. Die Antwort wird im Benutzerprofil gespeichert
  (`oh-toolbox.json`, Zugangsdaten 0600); danach geht es direkt ins passende Menü.
- **Statuszeile oben** in jedem Menü (Box bzw. Ziel, erreichbar ja/nein).
- **Tasten bleiben stabil:** die bisherigen Tasten (1–9, n, g, s, k) behalten ihre Bedeutung,
  damit README und Anleitung gültig bleiben; neu sind nur `w` (Weitere), `z` (zurück), `q` (Ende).
- Gefährliche Punkte (k, Stack neu installieren, Box trennen) mit Rückfrage.

**Start**

```
openandhome Toolbox
  1  Sensorbox am USB              (nur wenn eine Box erkannt wurde)
  2  Sensorboxen im Netzwerk / Server
  q  Ende
```

Startverhalten: Box am USB und keine Betriebsart gespeichert → direkt ins USB-Menü (wie
heute). Keine Box am USB → direkt in den Netzwerk-Bereich. Sonst das Startmenü.

**1 – Sensorbox am USB** (bestehende Funktionen, gruppiert)

```
Sensorbox1 · Standalone · 192.168.178.34
  1  WLAN einrichten               (nicht bei Professional mit LAN)
  g  Namen ändern
  s  Sensoren neu erkennen
  3  Einstellungen anzeigen
  w  Weitere …
  z  zurück
```

```
Weitere (Problemlösung)
  2  Neustart                      6  Reset DHCP
  4  Debugger                      7  Admin-Passwort zurücksetzen
  5  WLAN löschen                  8  Zugangspunkt starten
  n  Zeitserver                    9  IP-Filter zurücksetzen
  k  Grundkonfiguration wiederherstellen (mit Rückfrage)
  z  zurück
```

**2 – Sensorboxen im Netzwerk / Server**

Erster Aufruf – Assistent:

```
Wohin sollen Ihre Sensorboxen ihre Daten senden?
  1  An den openandhome-Server, den Sie von uns haben          → a
  2  Auf Ihren Docker-Server (wir installieren alles)          → b
  3  An Ihr eigenes System (MQTT-Broker/Syslog angeben)        → c
  4  Nirgendwohin – Sensorboxen arbeiten allein (Standalone)   → Boxen trennen
```

Danach je nach Betriebsart:

```
a) openandhome-Server                     b) Docker-Server
Ziel: openandhome-server1 (192.168.178.50) ✓   Ziel: nas.local · Stack ✓ läuft
  1  Sensorboxen verbinden                  1  Stack installieren   (nur bis installiert)
  2  Übersicht Sensorboxen                  1  Sensorboxen verbinden
  3  Grafana öffnen                         2  Übersicht Sensorboxen
  4  Servereinstellungen …                  3  Grafana öffnen
  w  Weitere …                              4  Servereinstellungen …
  z  zurück                                 w  Weitere …   z  zurück

c) Eigenes System
Ziel: mqtt.firma.lan:1883 · Syslog 192.168.1.10
  1  Sensorboxen verbinden
  2  Übersicht Sensorboxen
  3  Integrationshilfe speichern (Themenschema, Telegraf-Snippet, Dashboards)
  w  Weitere …
  z  zurück
```

```
Servereinstellungen (a, b)                Weitere (a, b, c)
  1  E-Mail-Benachrichtigung + Testmail     1  Sensorbox vom Ziel trennen
  2  Grafana-Passwörter                     2  Server neu suchen / Adresse ändern
  3  Aufbewahrungsdauer der Daten           3  Betriebsart wechseln (Assistent)
  4  Einstellungen anzeigen                 4  Diagnose (MQTT, Syslog, NTP; Datei für Support)
  z  zurück                                 5  Stack aktualisieren          (nur b)
                                            z  zurück
```

- **Sensorboxen verbinden** zeigt die gefundenen Boxen mit Status (verbunden / nicht
  verbunden / anderes Ziel) und fragt „alle“ oder Auswahl; danach Prüfung, ob Werte ankommen.
- **Übersicht** zeigt je Box: Name, IP, Image, Ziel, letzte Meldung beim Server (a, b).
- In a werden Servereinstellungen über `openandhome.txt` geschrieben (6.6), in b über die
  `.env` des Stacks (per SSH) – für den Anwender gleich.
- **Grafana-Passwörter:** Der Kunde darf alle drei ändern, auch `admin`. Vor dem Ändern
  des Admin-Passworts zeigt die Toolbox einen Hinweis und verlangt eine ausdrückliche
  Bestätigung (Eingabe `ja`):

  > Sie ändern das Administrator-Passwort von Grafana. Wir kennen das neue Passwort nicht.
  > Notieren Sie es sicher.
  > Haben Sie es vergessen, können Sie es selbst neu setzen: SD-Karte des Servers in einen
  > PC stecken, in `openandhome.txt` ein neues Passwort eintragen, Karte zurückstecken und
  > den Server starten (beim Docker-Server: Toolbox → Servereinstellungen).
  > Unser Support hilft in diesem Fall nur mit der **Neukonfiguration des Servers** – dabei
  > gehen alle gespeicherten Messwerte, Dashboards und Einstellungen verloren.

- **Selbsthilfe-Weg:** `oh-config.service` setzt das Admin-Passwort lokal mit
  `grafana cli admin reset-admin-password` (kein altes Passwort nötig). Damit dient
  `openandhome.txt` auch als Rücksetzweg. Er wird in README/Anleitung und im Kommentar der
  Datei erklärt. **Support-Weg ist ausschließlich die Neukonfiguration.**
- Beim Docker-Stack (b) setzt die Toolbox das Passwort über SSH ebenso per
  `grafana cli` im Container; Voraussetzung ist der SSH-Zugang zum Docker-Host.
- **Neukonfiguration** heißt: Server (a) bzw. Stack (b) neu aufsetzen, so wie in der Werkstatt
  bzw. über „Stack installieren“. Danach gelten die Zugänge eines neuen Übergabeblatts
  (a) bzw. die neu erzeugten Zugänge (b), und die Sensorboxen werden neu verbunden.
- Der OH-Flasher bleibt unverändert ein eigenes Programm (Update/Notfall).

### 6.1 Gemeinsame Bausteine

- **Boxen im Netz finden:** Subnetz-Scan auf Port 80 mit Prüfung `/json` (ESPEasy),
  Liste mit Name, IP, Image, aktivem Controller.
- **Box auf ein Ziel stellen** (ein Modul für a, b, c):
  - MQTT-Controller C005 (Controller 1 der Basis-config) einschalten, Host/Port,
    Benutzer/Passwort, Publish `openandhome/%sysname%/%tskname%/%valname%`,
    Subscribe `openandhome/%sysname%/#` (über `/controllers?index=1`).
  - Syslog-IP und -Port (über `/advanced`, wie `setze_syslog` in `espeasy_testbox.py`).
  - Optional NTP-Host = Server (Toolbox-Menü n gibt es schon).
  - Prüfen: Controller verbunden (`/json`), und – wo möglich – Wert kommt beim Ziel an.
- **Box vom Server lösen:** Controller aus, Syslog leer (Zurück zu Standalone).
- Name der Box muss eindeutig sein (`%sysname%`); das Programm warnt bei Dubletten.

### 6.2 Betriebsart a) Gelieferter openandhome-Server

1. Server finden (`openandhome-server1`, `.local`, sonst IP eingeben).
2. Zugang aus dem Übergabeblatt eingeben (einmalig, lokal gespeichert).
3. Boxen auswählen → auf Server stellen (Metriken + Syslog).
4. **Servereinstellungen** ändern: SMTP/Alarm-Empfänger, Grafana-Passwörter,
   Aufbewahrungsdauer. Das Programm schreibt dazu `openandhome.txt` per SSH
   (Benutzer `ohconfig`, der nur diese Datei schreiben und den Anwende-Dienst starten darf,
   per `ForceCommand`) – derselbe Weg wie die manuelle Bearbeitung der SD-Karte (E11).

### 6.3 Betriebsart b) Stack auf vorhandenem Docker-Server des Kunden

1. Kunde gibt Docker-Host (SSH-Zugang) an, oder lässt sich nur ein Verzeichnis erzeugen.
2. Das Programm erzeugt aus `server/stack/` (im ohtoolbox-Paket enthalten) einen Ordner
   `openandhome-stack/` mit `compose.yml`, Konfigs, `.env` (zufällige Passwörter) und
   Mosquitto-Passwortdatei.
3. Mit SSH-Zugang: hochladen, `docker compose up -d`, warten bis gesund, gleiche
   Prüfungen wie T2–T6 (verkürzt). Ohne SSH: Anleitung „Ordner kopieren und starten“.
4. Danach Boxen auf diesen Server stellen (wie a).

Images im Compose mit fester Hauptversion (`influxdb:2`, `grafana/grafana-oss:<major>`,
`telegraf:<major>`, `eclipse-mosquitto:2`), Healthchecks für jeden Dienst.

### 6.4 Betriebsart c) Eigene Lösung des Kunden

- Kunde gibt MQTT-Broker (Host, Port, Benutzer, Passwort) und Syslog-Ziel (IP, Port) an.
- Boxen werden darauf gestellt.
- Das Programm legt eine **Integrationshilfe** ab: Themenschema, Telegraf-Snippet
  (`server/stack/telegraf/openandhome.conf`), Dashboards als JSON zum Import, Hinweis zu
  Loki/Alloy (`syslog_format = "rfc3164"`) für Kunden mit Loki.

### 6.5 Name oder IP des Servers in der Box (DHCP, E4)

Das Programm trägt zuerst den Hostnamen ein und prüft nach ~30 s, ob der Controller
verbunden ist. Wenn nicht (Router löst den Namen nicht auf), trägt es die IP ein und
empfiehlt, im Router eine feste DHCP-Zuordnung für den Server einzurichten. Ändert sich
die IP später, stellt ein erneuter Lauf „Boxen auf Server stellen“ alle Boxen um.

### 6.6 `openandhome.txt` (Boot-Partition)

```
# openandhome Server-Einstellungen. Leere Felder bleiben unverändert.
# Passwortfelder werden nach dem Anwenden automatisch geleert.
smtp_host=
smtp_port=587
smtp_user=
smtp_passwort=
smtp_absender=
alarm_empfaenger=
# Admin-Passwort vergessen? Hier ein neues eintragen und den Server starten.
# Hinweis: Unser Support hilft dabei nur mit der Neukonfiguration des Servers
# (alle Messwerte, Dashboards und Einstellungen gehen verloren).
grafana_admin_passwort=
grafana_editor_passwort=
grafana_viewer_passwort=
aufbewahrung_tage=
```

Dienst `oh-config.service` liest die Datei beim Start und auf Anforderung (Pfad-Unit),
wendet die Werte an (Grafana-API, `grafana.ini`-Drop-in für SMTP, Influx-Bucket-Aufbewahrung),
leert Passwortfelder und schreibt `letzte_anwendung=<Datum> OK/FEHLER: …` zurück.

---

## 7. Auswirkungen auf das openandhome-Repo (außerhalb von `server/`)

| Bereich | Änderung |
|---|---|
| [`tools/bin/`](../tools/bin/) | neues Modul `oh_server.py` (Box-Suche, Box auf Ziel stellen, Stack erzeugen/deployen); nutzt `espeasy_testbox.py`-Funktionen (`setze_syslog`, HTTP-Zugriff) |
| [`tools/ohtoolbox/`](../tools/ohtoolbox/) | Menü „Server“ (a/b/c), Paket enthält `server/stack/`; Abhängigkeit für SSH (paramiko) ins portable Python |
| Basis-configs | MQTT-Controller bleibt aus (Standalone). *Prüfpunkt P2:* in beiden Basis-configs prüfen, ob Controller 1 schon C005 mit den Themen oben ist (laut Custom.h-Analyse ja) |
| [`AGENTS.md`](../AGENTS.md) | Abschnitt „Server“ ergänzen (Ziel, Regeln, Verweis auf `server/`) |
| Anleitungen | Kapitel „Sensorboxen mit Server verbinden“ (später, über `tools/docs/anleitung.py`) |

---

## 8. Offene Punkte / Prüfpunkte

| # | Punkt |
|---|---|
| P1 | **Erledigt** (2026-10-06-raspios-trixie-arm64-lite): cloud-init 25.2, NoCloud aus `/boot/firmware`, Modul `rpi:` für I2C. SSH über die leere Datei `ssh` (`sshswitch.service`). Anpassung braucht kein Loop-Mount und kein root (mtools auf der FAT-Partition); nur das SD-Schreiben braucht sudo |
| P2 | Controller 1 in den Basis-configs = C005 mit `openandhome/%sysname%/…`? |
| P3 | **Entschieden:** Wir gehen davon aus, dass bald ein ESPEasy-Release mit funktionierendem Syslog kommt (`mega-20260720` sendet keins). Keine eigene Log-Regel als Produktfunktion; die Testlog-Regel bleibt nur im Test. Server und Konfigprogramm setzen die normale Syslog-Einstellung (`/advanced`). Bis zum neuen Image kommen beim Kunden nur Metriken an – der Funktionstest prüft Syslog serverseitig (T4) |
| P4 | Pi 3 B v1.2: Funktionstest einmal probehalber; bei RAM-Problemen Unterstützung streichen (E2) |
| P5 | **Erledigt** (2026-11-15): arm64-Pakete influxdb2/influxdb2-cli 2.9.1, telegraf 1.40.3 (repos.influxdata.com), grafana 13.3.1 (apt.grafana.com); Schlüssel-Fingerabdrücke in `roles/base/defaults` |
| P6 | **Erledigt:** `inputs.syslog` verwirft den Text bei ESPEasy-Zeilen ohne Zeitstempel. Ersatz `inputs.socket_listener` + Starlark; getestet mit `<14>Box_EspEasy: …`, `<13>Box EspEasy: …` und Zeilen ohne Format |
| P7 | **SD-Karte:** mindestens 16 GB, empfohlen 32 GB, Klasse A1/A2. Prüfung in `base` (Größe, ≥ 100 synchrone 4-KB-Schreibvorgänge/s) |

---

## 9. Umsetzungsreihenfolge

1. `server/`-Grundgerüst, `image_download`, `image_customize`, `sd_write` → Pi 4 startet und ist per SSH erreichbar (P1 klären).
2. `base`, `timesync`, `mosquitto`, `influxdb`, `telegraf`, `grafana` mit `server/stack/`.
3. `server_test` (T1–T11) + Protokoll/Übergabeblatt → erster vollständiger Durchlauf auf `devel`.
4. `oh_config` + `openandhome.txt`.
5. ohtoolbox Menü „Server“: Betriebsart a.
6. Betriebsart c, danach b (Docker-Stack aus `server/stack/`).
7. Doku (AGENTS.md, READMEs, Anleitungskapitel), Merge nach `master` nach bestandenem Test.

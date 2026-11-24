# openandhome-Server (Ansible)

Richtet einen openandhome-Server auf einem **Raspberry Pi 4 Model B** ein. Er empfängt
Messwerte (MQTT) und Logs (Syslog) der Sensorboxen und zeigt sie in Grafana an.
Ein Server je Kunde. Plan und Entscheidungen: [`../plans/server-ansible.md`](../plans/server-ansible.md).

**Stand:** Phase 1 (Image + SD-Karte), Phase 2 (Installation, `site.yml`) und Phase 3
(Funktionstest, `test.yml`) sind umgesetzt. Offen: `oh_config` (`openandhome.txt`, T8).

**SD-Karte:** mindestens 16 GB, empfohlen 32 GB, **Klasse A1 oder A2**. Das System mit allen
Diensten belegt ca. 6,2 GB. Um die Karte zu schonen, schreibt der Server gesammelt etwa alle
5 Minuten (`oh_write_interval_s`); bei Stromausfall gehen bis zu ~10 Minuten Messwerte verloren,
neue Werte erscheinen in Grafana mit bis zu 5 Minuten Verzögerung.
`site.yml` bricht bei zu kleinen (< 14 GB Dateisystem) oder zu langsamen Karten
(< 100 synchrone 4-KB-Schreibvorgänge/s) mit einer Meldung ab.

## Voraussetzungen (Werkstatt-PC, Linux)

- `ansible-core` ≥ 2.16, `xz`, `sfdisk`, `mtools`, `cmp`; optional `cloud-init` (prüft die Vorlagen)
- SSH-Key `~/.ssh/id_ed25519.pub` (anpassbar: `oh_admin_ssh_pubkeys` in
  [`group_vars/all/main.yml`](group_vars/all/main.yml))
- mDNS-Auflösung (`.local`) oder die IP des Pi
- Platz: ca. 0,6 GB Cache + 3 GB je Image unter `~/.cache/openandhome/`

## Phase 1: Image bauen und SD-Karte schreiben

```bash
cd server
ansible-playbook image.yml                           # nur Image bauen
ansible-playbook image.yml -K -e sd_device=/dev/sdX  # bauen und auf SD-Karte schreiben
```

- Lädt **jedes Mal das aktuelle** Raspberry Pi OS Lite (64 Bit) und prüft den SHA256
  (bereits geladene Releases kommen aus dem Cache).
- Passt das Image an, ohne es einzuhängen (mtools, kein root): Hostname `openandhome-server1`,
  Benutzer `ohadmin` nur mit SSH-Key, Deutsch/Berlin, Ethernet per DHCP, I2C + DS3231-RTC,
  WLAN/Bluetooth aus, SSH an, Vorlage `openandhome.txt`, Herkunftsdatei `openandhome-build.txt`.
- Schreibt nur auf ein ausdrücklich genanntes, wechselbares Gerät nach Bestätigung
  (Gerätenamen eintippen) und vergleicht die Karte danach mit dem Image. `-K` fragt das
  sudo-Passwort ab (nur für umount/dd/cmp).

Danach Karte in den Pi stecken, Netzwerkkabel anschließen, starten. Nach ca. 2 Minuten:

```bash
ansible server -m ping                               # per openandhome-server1.local
ansible server -m ping -e oh_server_address=<IP>     # falls mDNS nicht geht
```

## Phase 2: Server installieren

```bash
ansible-playbook site.yml                    # alles (erster Lauf ca. 15–20 min)
ansible-playbook site.yml --tags grafana     # nur eine Rolle
```

Rollen: `credentials` (Zugangsdaten je Server, zufällig, in `/etc/openandhome/credentials.yml`),
`base` (Kartenprüfung, Paketquellen mit Schlüsselprüfung, Update, zram, Journal, SSH, Firewall,
Sicherheitsupdates), `timesync` (chrony, NTP-Server fürs LAN), `mosquitto`, `influxdb`,
`telegraf`, `grafana` (Benutzer `admin`, `editor`, `viewer`). Dienstkonfiguration aus
[`stack/`](stack/README.md).

Grafana: `http://openandhome-server1.local:3000` (Benutzer `admin`, `editor`, `viewer`).

## Phase 3: Funktionstest, Protokoll, Übergabeblatt

```bash
ansible-playbook test.yml                                   # alle Prüfungen (ca. 5 min)
ansible-playbook test.yml -e server_test_echte_box=Sensorbox1   # zusätzlich T10 mit echter Box
```

Prüft T1–T11 aus dem Plan (Dienste nach Neustart, MQTT, Zugriffsschutz, Syslog, Grafana-Rechte,
Dashboards, NTP, zweiter Lauf ohne Änderungen, echte Box) und entfernt die Testdaten. Ergebnis
unter `~/openandhome-serverprotokolle/<Datum>_<MAC>/`: `protokoll.txt` und `uebergabeblatt.txt`
(Zugangsdaten für den Kunden – ausdrucken, nicht ins Repo). Freigabe nach `master` nur mit
bestandenem Test. Details: [`roles/server_test`](roles/server_test/README.md).

Sensorboxen an den Server senden lassen: ohtoolbox Menü **v** bzw.
`python3 ../tools/bin/oh_server.py verbinden --server openandhome-server1`
(siehe [`../tools/ohtoolbox/README.md`](../tools/ohtoolbox/README.md)).

## Aufbau

| Pfad | Inhalt |
|---|---|
| [`image.yml`](image.yml) | Phase 1 |
| [`inventory.yml`](inventory.yml) | `werkstatt` (lokal), `server` (Pi per DHCP/mDNS) |
| [`group_vars/all/main.yml`](group_vars/all/main.yml) | Hostname, Admin, Keys, Locale, Cache |
| [`roles/image_download`](roles/image_download/README.md) | aktuelles Image + SHA256 |
| [`roles/image_customize`](roles/image_customize/README.md) | cloud-init, config.txt, openandhome-Dateien |
| [`roles/sd_write`](roles/sd_write/README.md) | SD-Karte schreiben mit Schutzprüfungen |
| [`site.yml`](site.yml) | Phase 2 |
| [`stack/`](stack/README.md) | Mosquitto-, Telegraf-, Grafana-Konfiguration und Dashboards (eine Quelle für Pi und Docker) |
| `roles/credentials`, `base`, `timesync`, `mosquitto`, `influxdb`, `telegraf`, `grafana` | Installation |
| [`test.yml`](test.yml), [`roles/server_test`](roles/server_test/README.md) | Phase 3 |

## Stolperfallen

- Unterstützt wird der **Pi 4 B**. Der Pi 3 B v1.2 startet dasselbe Image, ist aber nur
  „best effort“ (Plan E2).
- Jeder neue Server hat neue SSH-Host-Keys unter demselben Namen. Ansible nutzt deshalb
  eine eigene `known_hosts` (`~/.cache/openandhome/known_hosts_server`), die `sd_write`
  vor jedem neuen Server bereinigt.
- Eine `~/.netrc` wird für die Downloads bewusst nicht benutzt (`use_netrc: false`).
- Ubuntu ab 25.10 nutzt **sudo-rs**; dessen Passwortabfrage erkennt Ansible nicht
  („Timed out waiting for become … password prompt“). Das Inventory nimmt deshalb auf dem
  Werkstatt-PC das klassische `sudo.ws`, falls installiert.

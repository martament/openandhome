# openandhome-Server (Ansible)

Richtet einen openandhome-Server auf einem **Raspberry Pi 4 Model B** ein. Er empfängt
Messwerte (MQTT) und Logs (Syslog) der Sensorboxen und zeigt sie in Grafana an.
Ein Server je Kunde. Plan und Entscheidungen: [`../plans/server-ansible.md`](../plans/server-ansible.md).

**Stand:** Phase 1 (Image + SD-Karte) ist umgesetzt. Installation (`site.yml`) und
Funktionstest (`test.yml`) folgen.

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

## Aufbau

| Pfad | Inhalt |
|---|---|
| [`image.yml`](image.yml) | Phase 1 |
| [`inventory.yml`](inventory.yml) | `werkstatt` (lokal), `server` (Pi per DHCP/mDNS) |
| [`group_vars/all/main.yml`](group_vars/all/main.yml) | Hostname, Admin, Keys, Locale, Cache |
| [`roles/image_download`](roles/image_download/README.md) | aktuelles Image + SHA256 |
| [`roles/image_customize`](roles/image_customize/README.md) | cloud-init, config.txt, openandhome-Dateien |
| [`roles/sd_write`](roles/sd_write/README.md) | SD-Karte schreiben mit Schutzprüfungen |

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

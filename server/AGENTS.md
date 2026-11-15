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

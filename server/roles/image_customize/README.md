# Rolle: image_customize

Erzeugt aus dem geladenen Image ein angepasstes openandhome-Server-Image – ohne root.

## Zweck

- Entpackt ein frisches Image nach `~/.cache/openandhome/build/<release>/`.
- Schreibt per `mtools` in die Boot-Partition: cloud-init (`user-data`, `network-config`,
  `meta-data`), leere Datei `ssh`, ergänzte `config.txt`, `openandhome.txt` (Vorlage für
  Kundeneinstellungen) und `openandhome-build.txt` (Herkunft).
- Prüft die cloud-init-Dateien mit `cloud-init schema`, falls lokal installiert.

## Variablen

| Variable | Standard | Beschreibung |
|---|---|---|
| `image_customize_build_dir` | `{{ oh_cache_dir }}/build/<release>` | Ausgabeordner |
| `image_customize_config_txt` | i2c, ds3231, disable-wifi, disable-bt | Zeilen für `config.txt` `[all]` |
| `image_customize_admin_groups` | adm, sudo, i2c, … | Gruppen von `oh_admin_user` |

Gemeinsame Werte (`oh_hostname`, `oh_admin_user`, `oh_admin_ssh_pubkeys`, Locale) in
[`../../group_vars/all/main.yml`](../../group_vars/all/main.yml).

## Verwendung

Teil von [`../../image.yml`](../../image.yml) (Tag `customize`).

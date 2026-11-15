# Rolle: sd_write

Schreibt das angepasste Image auf eine SD-Karte.

## Zweck

- Prüft das Ziel: ganzes Gerät (`/dev/sdX`, `/dev/mmcblkN`), wechselbar/USB/MMC, nicht NVMe,
  ≤ `sd_write_max_size_gb`, groß genug, nicht als Systemlaufwerk eingehängt.
- Fragt nach (Gerätenamen eintippen), hängt Partitionen aus, schreibt mit `dd`, vergleicht mit `cmp`.
- Entfernt alte Host-Keys des Servers aus `oh_known_hosts`.

## Variablen

| Variable | Standard | Beschreibung |
|---|---|---|
| `sd_device` | – (Pflicht) | Zielgerät, z. B. `/dev/sdb` |
| `sd_write_max_size_gb` | `256` | größte erlaubte Karte |
| `sd_write_verify` | `true` | nach dem Schreiben vergleichen |
| `sd_write_confirm` | `""` | gleich `sd_device` setzen, um die Rückfrage zu überspringen |

## Verwendung

```bash
ansible-playbook image.yml -K -e sd_device=/dev/sdX
```

Die Rolle läuft nur, wenn `sd_device` gesetzt ist (Tag `sd`). `-K` fragt das sudo-Passwort ab.

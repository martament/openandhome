# Rolle: image_download

Lädt das **aktuelle** Raspberry Pi OS Lite (arm64) und prüft den SHA256.

## Zweck

- Folgt der Weiterleitung `raspios_lite_arm64_latest` und ermittelt das Release.
- Lädt `.img.xz` in den Cache (`~/.cache/openandhome/raspios/<release>/`), nur wenn es fehlt
  oder die Prüfsumme nicht passt.

## Variablen

| Variable | Standard | Beschreibung |
|---|---|---|
| `image_download_url` | `…/raspios_lite_arm64_latest` | Weiterleitung auf das aktuelle Release |
| `image_download_cache` | `{{ oh_cache_dir }}/raspios` | Cache-Ordner |

Ergebnis-Fakten: `image_download_release`, `image_download_xz`, `image_download_sha256`,
`image_download_file_url`.

## Verwendung

Teil von [`../../image.yml`](../../image.yml) (Tag `download`).

# Rolle: grafana

Grafana OSS mit Datenquellen, Dashboards und den Rollen Viewer/Editor.

## Zweck

- Installiert `grafana` (OSS). Einstellungen per `GF_*` in `/etc/openandhome/grafana.env`
  (anonymer Zugriff aus, keine Registrierung, keine Telemetrie, Startseite = Messwerte,
  SQLite im WAL-Modus, Log nur ins Journal).
- Datenquellen und Dashboards aus [`../../stack/grafana`](../../stack/grafana/); Editoren dürfen
  die Dashboards in der Oberfläche ändern.
- Setzt das Admin-Passwort und legt `editor` (Editor) und `viewer` (Viewer) an.

## Variablen

| Variable | Standard | Beschreibung |
|---|---|---|
| `grafana_url` | `http://127.0.0.1:3000` | API-Adresse |
| `grafana_dashboard_dir` | `/etc/grafana/dashboards/openandhome` | Dashboard-Dateien |
| `grafana_users` | editor, viewer | Benutzer mit Rolle |

## Verwendung

Teil von [`../../site.yml`](../../site.yml) (Tag `grafana`).

## Stolperfallen

Der erste Start legt die Datenbank an und dauert auf langsamen Karten mehrere Minuten.

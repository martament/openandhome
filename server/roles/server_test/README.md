# Rolle: server_test

Funktionstest des openandhome-Servers mit Protokoll und Übergabeblatt.

## Zweck

Prüfungen nach Plan (Abschnitt 5): T1 Dienste (nach Neustart), T2 MQTT → InfluxDB,
T3 MQTT-Zugriffsschutz, T4 Syslog, T5 Grafana-Rechte, T6 Dashboards/Datenquelle,
T7 NTP (+ RTC als Hinweis), T8 `openandhome.txt` (folgt mit `oh_config`), T9 zweiter Lauf
von `site.yml` mit `changed=0`, T10 echte Sensorbox (optional), Kartengröße (Hinweis),
T11 Testdaten entfernen.

Schreibt nach `~/openandhome-serverprotokolle/<Datum>_<MAC>/`:
`protokoll.txt` (Image, Paketversionen, Ergebnisse) und `uebergabeblatt.txt` (0600,
Zugangsdaten für den Kunden). Bricht erst nach Protokoll und Aufräumen ab, wenn eine
Pflichtprüfung fehlschlägt.

## Variablen

| Variable | Standard | Beschreibung |
|---|---|---|
| `server_test_box` | `Testbox` | Name der simulierten Sensorbox |
| `server_test_neustart` | `true` | T1 mit Neustart |
| `server_test_idempotenz` | `true` | T9 (`site.yml` erneut, ca. 1–2 min) |
| `server_test_echte_box` | `""` | Name einer echten Box für T10 |
| `server_test_protokolle` | `~/openandhome-serverprotokolle` | Ablage auf dem Werkstatt-PC |

## Verwendung

```bash
ansible-playbook test.yml
ansible-playbook test.yml -e server_test_echte_box=Sensorbox1
```

## Stolperfallen

Das Übergabeblatt enthält Passwörter im Klartext – nicht ins Repo, nur ausgedruckt an den Kunden.

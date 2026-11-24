# stack/ – eine Quelle der Dienst-Konfiguration

Dieselben Dateien dienen der apt-Installation auf dem Pi (`site.yml`) und später dem
Docker-Stack der Toolbox (Plan E10, Betriebsart b). **Keine Passwörter** – Werte kommen
aus Umgebungsvariablen (Pi: `/etc/openandhome/*.env` per systemd-Drop-in; Docker: `.env`).

| Variable | Verwendet von | Bedeutung |
|---|---|---|
| `OH_HOSTNAME` | Telegraf | Hostname für Server-Metriken |
| `OH_MQTT_URL` | Telegraf | z. B. `tcp://127.0.0.1:1883` |
| `OH_MQTT_TELEGRAF_PASSWORD` | Telegraf | MQTT-Benutzer `telegraf` |
| `OH_INFLUX_URL` | Telegraf, Grafana | z. B. `http://127.0.0.1:8086` |
| `OH_INFLUX_TELEGRAF_PASSWORD` | Telegraf | InfluxDB-v1-Benutzer `telegraf` (schreiben) |
| `OH_INFLUX_GRAFANA_PASSWORD` | Grafana | InfluxDB-v1-Benutzer `grafana` (lesen) |
| `OH_SYSLOG_PORT` | Telegraf | UDP-Port für Syslog der Sensorboxen (514) |

Datenfluss: Sensorbox → MQTT `openandhome/<Box>/<Task>/<Wert>` → Mosquitto → Telegraf
(Tags `sensorbox`, `device`, `valuename`) → InfluxDB-Bucket `openandhome`, Measurement
`openandhome` (nur gültige Zahlen). Online-Status (`openandhome/<Box>/status/LWT`) →
Measurement `openandhome_status` (Text `Connected`/`Connection Lost`).
Syslog (UDP, Rohzeile, per Starlark in `severity`, `sensorbox`, `message` zerlegt) → Bucket `sensorbox_logs`. Server-Metriken → Bucket `system`.

Die Dashboards in `grafana/dashboards/` erzeugt `grafana/dashboards.py` – nicht von Hand
ändern, sondern das Skript anpassen und neu ausführen (`python3 grafana/dashboards.py`).

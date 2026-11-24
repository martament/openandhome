# Rolle: mosquitto

MQTT-Broker für die Sensorboxen.

## Zweck

- Installiert Mosquitto (Debian) mit Konfiguration und ACL aus [`../../stack/mosquitto`](../../stack/mosquitto/).
- Kein anonymer Zugriff. Benutzer `sensorbox` (`readwrite openandhome/#`) und `telegraf` (nur lesen).
- Keine Persistenz, Log ins Journal (SD-Karte schonen; die Boxen melden ihren Status nach einem
  Neustart des Brokers selbst neu). Steht in `/etc/mosquitto/mosquitto.conf`.
- Die Passwortdatei wird nur neu erzeugt, wenn sich Passwörter geändert haben (Prüfsumme daneben).

## Variablen

| Variable | Standard | Beschreibung |
|---|---|---|
| `mosquitto_passwd_file` | `/etc/mosquitto/openandhome.passwd` | Passwortdatei |
| `mosquitto_acl_file` | `/etc/mosquitto/openandhome.acl` | ACL |

## Verwendung

Teil von [`../../site.yml`](../../site.yml) (Tag `mosquitto`).

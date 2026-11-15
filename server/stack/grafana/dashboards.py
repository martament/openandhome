#!/usr/bin/env python3
"""Erzeugt die openandhome-Dashboards (Grafana, InfluxQL) als JSON.

Aufruf: python3 server/stack/grafana/dashboards.py
Ausgabe: server/stack/grafana/dashboards/*.json (werden committet und per
Provisioning nach /etc/grafana/dashboards/openandhome geladen).

Datenmodell (stack/README.md): Measurement "openandhome", Feld "value",
Tags "sensorbox" (ESPEasy %sysname%), "device" (%tskname%), "valuename" (%valname%).
"""
import json
import os

AUS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dashboards")

DS_WERTE = {"type": "influxdb", "uid": "oh-messwerte"}
DS_LOGS = {"type": "influxdb", "uid": "oh-logs"}
DS_SERVER = {"type": "influxdb", "uid": "oh-server"}

BOX = '"sensorbox" =~ /^$sensorbox$/'


def variable(name, label, ds, query):
    return {
        "name": name, "label": label, "type": "query", "datasource": ds,
        "query": query, "definition": query, "refresh": 2, "sort": 1,
        "multi": True, "includeAll": True, "current": {"text": ["All"], "value": ["$__all"]},
    }


def ziel(ds, query, alias="", ref="A", fmt="time_series"):
    return {"datasource": ds, "refId": ref, "rawQuery": True, "query": query,
            "resultFormat": fmt, "alias": alias}


def zeitreihe(titel, ds, ziele, einheit="", pos=(0, 0, 12, 8), stufen=False, minmax=None, beschreibung=""):
    x, y, w, h = pos
    feld = {"unit": einheit, "custom": {"lineWidth": 2, "spanNulls": 3600000,
                                        "lineInterpolation": "stepAfter" if stufen else "smooth"}}
    if minmax:
        feld["min"], feld["max"] = minmax
    return {
        "type": "timeseries", "title": titel, "description": beschreibung, "datasource": ds,
        "gridPos": {"x": x, "y": y, "w": w, "h": h}, "targets": ziele,
        "fieldConfig": {"defaults": feld, "overrides": []},
        "options": {"legend": {"displayMode": "table", "placement": "bottom",
                               "calcs": ["lastNotNull", "min", "max"]},
                    "tooltip": {"mode": "multi", "sort": "desc"}},
    }


def kennzahl(titel, ds, query, einheit="", pos=(0, 0, 6, 4), schwellen=None):
    x, y, w, h = pos
    stufen = [{"color": "green", "value": None}] + [
        {"color": farbe, "value": wert} for wert, farbe in (schwellen or [])]
    return {
        "type": "stat", "title": titel, "datasource": ds,
        "gridPos": {"x": x, "y": y, "w": w, "h": h}, "targets": [ziel(ds, query)],
        "fieldConfig": {"defaults": {"unit": einheit, "thresholds": {"mode": "absolute", "steps": stufen}},
                        "overrides": []},
        "options": {"reduceOptions": {"calcs": ["lastNotNull"]}, "colorMode": "value", "graphMode": "area"},
    }


def dashboard(uid, titel, panels, variablen=(), zeit="now-24h", tags=("openandhome",)):
    return {
        "uid": uid, "title": titel, "tags": list(tags), "timezone": "browser",
        "schemaVersion": 39, "version": 1, "editable": True, "refresh": "1m",
        "time": {"from": zeit, "to": "now"}, "templating": {"list": list(variablen)},
        "panels": panels, "links": [{"type": "dashboards", "tags": ["openandhome"], "asDropdown": True,
                                     "title": "openandhome", "includeVars": True, "keepTime": True}],
    }


def wert(bedingung, gruppe='"sensorbox", "device"'):
    return (f'SELECT mean("value") FROM "openandhome" WHERE {bedingung} AND {BOX} AND $timeFilter '
            f'GROUP BY time($__interval), {gruppe} fill(null)')


def messwerte():
    v = variable("sensorbox", "Sensorbox", DS_WERTE, 'SHOW TAG VALUES FROM "openandhome" WITH KEY = "sensorbox"')
    alias = "$tag_sensorbox $tag_device"
    panels = [
        zeitreihe("Temperatur", DS_WERTE, [ziel(DS_WERTE, wert('"valuename" =~ /^Temperat/'), alias)],
                  "celsius", (0, 0, 24, 10)),
        zeitreihe("Luftfeuchte", DS_WERTE, [ziel(DS_WERTE, wert('"valuename" = \'Humidity\''), alias)],
                  "humidity", (0, 10, 12, 8)),
        zeitreihe("Abstand", DS_WERTE, [ziel(DS_WERTE, wert('"valuename" = \'Distance\''), alias)],
                  "suffix: cm", (12, 10, 12, 8)),
        zeitreihe("Wassersensor", DS_WERTE, [ziel(DS_WERTE, wert('"valuename" = \'State\''), alias)],
                  "", (0, 18, 24, 6), stufen=True, minmax=(0, 1),
                  beschreibung="1 = Wasser erkannt (je nach Verdrahtung)"),
    ]
    return dashboard("oh-messwerte", "Sensorboxen – Messwerte", panels, [v])


def boxsystem():
    v = variable("sensorbox", "Sensorbox", DS_WERTE, 'SHOW TAG VALUES FROM "openandhome" WITH KEY = "sensorbox"')
    alias = "$tag_sensorbox"
    panels = [
        zeitreihe("WLAN-Signal", DS_WERTE, [ziel(DS_WERTE, wert('"valuename" = \'rssi\'', '"sensorbox"'), alias)],
                  "dBm", (0, 0, 12, 8)),
        zeitreihe("Freier Speicher", DS_WERTE,
                  [ziel(DS_WERTE, wert('"valuename" = \'freeheap\'', '"sensorbox"'), alias)], "decbytes", (12, 0, 12, 8)),
        zeitreihe("Laufzeit seit Neustart", DS_WERTE,
                  [ziel(DS_WERTE, wert('"valuename" = \'Uptime\'', '"sensorbox"'), alias)], "m", (0, 8, 12, 8)),
        zeitreihe("Auslastung", DS_WERTE, [ziel(DS_WERTE, wert('"valuename" = \'load\'', '"sensorbox"'), alias)],
                  "percent", (12, 8, 12, 8)),
    ]
    return dashboard("oh-boxsystem", "Sensorboxen – System", panels, [v], zeit="now-7d")


def logs():
    v = variable("sensorbox", "Sensorbox", DS_LOGS, 'SHOW TAG VALUES FROM "syslog" WITH KEY = "sensorbox"')
    q = ('SELECT "message", "sensorbox", "severity" FROM "syslog" '
         'WHERE "sensorbox" =~ /^$sensorbox$/ AND $timeFilter ORDER BY time DESC LIMIT 1000')
    panel = {
        "type": "logs", "title": "Meldungen der Sensorboxen", "datasource": DS_LOGS,
        "gridPos": {"x": 0, "y": 0, "w": 24, "h": 22}, "targets": [ziel(DS_LOGS, q, fmt="table")],
        "options": {"showTime": True, "wrapLogMessage": True, "sortOrder": "Descending", "enableLogDetails": True},
    }
    return dashboard("oh-logs", "Sensorboxen – Logs", [panel], [v], zeit="now-6h")


def server():
    s = DS_SERVER
    panels = [
        kennzahl("CPU", s, 'SELECT 100 - last("usage_idle") FROM "cpu" WHERE "cpu" = \'cpu-total\' AND $timeFilter',
                 "percent", (0, 0, 4, 4), [(70, "orange"), (90, "red")]),
        kennzahl("Arbeitsspeicher", s, 'SELECT last("used_percent") FROM "mem" WHERE $timeFilter',
                 "percent", (4, 0, 4, 4), [(80, "orange"), (90, "red")]),
        kennzahl("SD-Karte belegt", s, 'SELECT last("used_percent") FROM "disk" WHERE "path" = \'/\' AND $timeFilter',
                 "percent", (8, 0, 4, 4), [(80, "orange"), (90, "red")]),
        kennzahl("Temperatur", s, 'SELECT max("temp") FROM "temp" WHERE $timeFilter GROUP BY time($__interval)',
                 "celsius", (12, 0, 4, 4), [(70, "orange"), (80, "red")]),
        kennzahl("Laufzeit", s, 'SELECT last("uptime") FROM "system" WHERE $timeFilter', "s", (16, 0, 4, 4)),
        kennzahl("Last (5 min)", s, 'SELECT last("load5") FROM "system" WHERE $timeFilter', "", (20, 0, 4, 4),
                 [(3, "orange"), (4, "red")]),
        zeitreihe("CPU und Arbeitsspeicher", s, [
            ziel(s, 'SELECT 100 - mean("usage_idle") FROM "cpu" WHERE "cpu" = \'cpu-total\' AND $timeFilter '
                    'GROUP BY time($__interval) fill(null)', "CPU", "A"),
            ziel(s, 'SELECT mean("used_percent") FROM "mem" WHERE $timeFilter GROUP BY time($__interval) fill(null)',
                 "Arbeitsspeicher", "B")], "percent", (0, 4, 12, 8), minmax=(0, 100)),
        zeitreihe("Temperatur", s, [ziel(s, 'SELECT mean("temp") FROM "temp" WHERE $timeFilter '
                                            'GROUP BY time($__interval), "sensor" fill(null)', "$tag_sensor")],
                  "celsius", (12, 4, 12, 8)),
        zeitreihe("SD-Karte", s, [ziel(s, 'SELECT mean("used") FROM "disk" WHERE "path" = \'/\' AND $timeFilter '
                                         'GROUP BY time($__interval) fill(null)', "belegt")],
                  "bytes", (0, 12, 24, 6)),
    ]
    return dashboard("oh-server", "openandhome-Server", panels, zeit="now-24h")


def main():
    os.makedirs(AUS, exist_ok=True)
    for name, d in (("messwerte", messwerte()), ("boxsystem", boxsystem()), ("logs", logs()), ("server", server())):
        pfad = os.path.join(AUS, f"{name}.json")
        with open(pfad, "w", encoding="utf-8") as f:
            json.dump(d, f, ensure_ascii=False, indent=2)
            f.write("\n")
        print(pfad)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Erzeugt die openandhome-Dashboards (Grafana, InfluxQL) als JSON.

Aufruf: python3 server/stack/grafana/dashboards.py
Ausgabe: server/stack/grafana/dashboards/*.json (werden committet und per
Provisioning nach /etc/grafana/dashboards/openandhome geladen).

Datenmodell (stack/README.md): Measurement "openandhome", Feld "value",
Wertnamen wie in den Basis-configs: Temperatur, Luftfeuchtigkeit, Distance, State,
uptime, freeheap, rssi, load (englische ESPEasy-Standardnamen werden mit erkannt).

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


# Optionale Sensoren: Panel nur anzeigen, wenn es Daten hat. Das geht nur mit dem
# v2-Format (dynamische Dashboards, AutoGrid-Layout, conditionalRendering).
# repeat ueber eine leere Variable zeigt in Grafana 13 trotzdem ein leeres Panel.
OPTIONAL = {  # Titel: (Wertnamen, Einheit, Stufen, Min/Max, Hinweis)
    "Luftfeuchte": ("(Luftfeuchtigkeit|Humidity)", "humidity", False, None, "Kombifühler (HTU21D/AM2320)"),
    "Abstand": ("(Distance|Abstand)", "suffix: cm", False, None, "Ultraschall-Abstandssensor HC-SR04"),
    "Wassersensor": ("(State)", "", True, (0, 1), "Wassersensor, 1 = Wasser erkannt (je nach Verdrahtung)"),
}

HINWEIS_OPTIONAL = ("Luftfeuchte, Abstand und Wassersensor erscheinen nur, wenn eine der gewählten "
                    "Sensorboxen diesen Messwert im gewählten Zeitraum gesendet hat.")


def messwerte():
    v = variable("sensorbox", "Sensorbox", DS_WERTE, 'SHOW TAG VALUES FROM "openandhome" WITH KEY = "sensorbox"')
    alias = "$tag_sensorbox $tag_device"
    panels = [zeitreihe("Temperatur", DS_WERTE, [ziel(DS_WERTE, wert('"valuename" =~ /^Temperat/'), alias)],
                        "celsius", (0, 0, 24, 10))]
    for titel, (muster, einheit, stufen, minmax, hinweis) in OPTIONAL.items():
        panels.append(zeitreihe(titel, DS_WERTE, [ziel(DS_WERTE, wert(f'"valuename" =~ /^{muster}$/'), alias)],
                                einheit, (0, 0, 24, 8), stufen=stufen, minmax=minmax,
                                beschreibung=f"{hinweis}. Nur sichtbar, wenn eine gewählte Box diesen Wert sendet."))
    d = dashboard("oh-messwerte", "Sensorboxen – Messwerte", panels, [v])
    d["description"] = HINWEIS_OPTIONAL
    return als_v2(d, bedingt=set(OPTIONAL))


def als_v2(d, bedingt=(), spalten=1):
    """Setzt ein Dashboard (v1-Aufbau dieses Skripts) in das v2-Format um.
    Panels in `bedingt` werden nur angezeigt, wenn ihre Abfrage Daten liefert."""
    elemente, items = {}, []
    for nr, p in enumerate(d["panels"], start=1):
        name = f"panel-{nr}"
        abfragen = [{"kind": "PanelQuery", "spec": {
            "refId": t["refId"], "hidden": False,
            "query": {"kind": "DataQuery", "group": "influxdb", "version": "v0",
                      "datasource": {"name": t["datasource"]["uid"]},
                      "spec": {k: t[k] for k in ("alias", "query", "rawQuery", "resultFormat")}}}}
            for t in p["targets"]]
        elemente[name] = {"kind": "Panel", "spec": {
            "id": nr, "title": p["title"], "description": p.get("description", ""), "links": [],
            "data": {"kind": "QueryGroup", "spec": {"queries": abfragen, "transformations": [], "queryOptions": {}}},
            "vizConfig": {"kind": "VizConfig", "group": p["type"], "version": "",
                          "spec": {"options": p.get("options", {}), "fieldConfig": p.get("fieldConfig", {})}}}}
        item = {"kind": "AutoGridLayoutItem", "spec": {"element": {"kind": "ElementReference", "name": name}}}
        if p["title"] in bedingt:
            item["spec"]["conditionalRendering"] = {"kind": "ConditionalRenderingGroup", "spec": {
                "visibility": "show", "condition": "and",
                "items": [{"kind": "ConditionalRenderingData", "spec": {"value": True}}]}}
        items.append(item)
    variablen = [{"kind": "QueryVariable", "spec": {
        "name": v["name"], "label": v.get("label", ""), "current": v["current"],
        "hide": "dontHide", "refresh": "onTimeRangeChanged", "skipUrlSync": False,
        "query": {"kind": "DataQuery", "group": "influxdb", "version": "v0",
                  "datasource": {"name": v["datasource"]["uid"]}, "spec": {"__legacyStringValue": v["query"]}},
        "regex": "", "sort": "alphabeticalAsc", "definition": v["query"], "options": [],
        "multi": v["multi"], "includeAll": v["includeAll"], "allowCustomValue": True}}
        for v in d["templating"]["list"]]
    return {
        "apiVersion": "dashboard.grafana.app/v2", "kind": "Dashboard", "metadata": {"name": d["uid"]},
        "spec": {
            "title": d["title"], "description": d.get("description", ""), "tags": d["tags"],
            "editable": True, "cursorSync": "Off", "liveNow": False, "preload": False,
            "annotations": [], "variables": variablen, "elements": elemente,
            "links": [dict(l, icon="", tooltip="", targetBlank=False) for l in d["links"]],
            "timeSettings": {"timezone": "browser", "from": d["time"]["from"], "to": d["time"]["to"],
                             "autoRefresh": d["refresh"], "hideTimepicker": False, "fiscalYearStartMonth": 0,
                             "autoRefreshIntervals": ["10s", "30s", "1m", "5m", "15m", "30m", "1h"]},
            "layout": {"kind": "AutoGridLayout", "spec": {
                "maxColumnCount": spalten, "columnWidthMode": "standard", "rowHeightMode": "standard",
                "fillScreen": False, "items": items}},
        },
    }


# freeheap/rssi (Task System, P026): Basis-configs beider Klassen senden Bytes und dBm.
# Aeltere ESP8266-Boxen (Basis vor 2026-11-15, Kundenboxen) senden KB ("%value%/1024")
# und 100 + dBm ("100+%value%") - die zweite Abfrage je Wert rechnet diese um.
# rssi = 0 heisst "kein WLAN" (Typ 2026 ueber Ethernet) und wird nicht angezeigt.
UMRECHNUNG = {  # Wertname: ((Bedingung, Rechnung) aktuell, (Bedingung, Rechnung) alte ESP8266-Boxen)
    "freeheap": (('"value" >= 1024', ""), ('"value" < 1024', " * 1024")),
    "rssi": (('"value" < 0', ""), ('"value" > 0', " - 100")),
}


def umgerechnet(name, alias):
    ziele = []
    for ref, (bedingung, rechnung) in zip("AB", UMRECHNUNG[name]):
        q = (f'SELECT mean("value"){rechnung} FROM "openandhome" WHERE "valuename" = \'{name}\' '
             f'AND {bedingung} AND {BOX} AND $timeFilter GROUP BY time($__interval), "sensorbox" fill(null)')
        ziele.append(ziel(DS_WERTE, q, alias, ref=ref))
    return ziele


def boxsystem():
    v = variable("sensorbox", "Sensorbox", DS_WERTE, 'SHOW TAG VALUES FROM "openandhome" WITH KEY = "sensorbox"')
    alias = "$tag_sensorbox"
    panels = [
        zeitreihe("WLAN-Signal", DS_WERTE, umgerechnet("rssi", alias), "dBm", (0, 0, 12, 8),
                  beschreibung="WLAN-Empfang in dBm (-50 sehr gut, -80 schwach). Boxen über Ethernet ohne WLAN erscheinen nicht. Ältere ESP8266-Boxen (100 + dBm) werden umgerechnet."),
        zeitreihe("Freier Speicher", DS_WERTE, umgerechnet("freeheap", alias), "bytes", (12, 0, 12, 8),
                  beschreibung="Freier Arbeitsspeicher in Bytes. Ältere ESP8266-Boxen (KB) werden umgerechnet."),
        zeitreihe("Laufzeit seit Neustart", DS_WERTE,
                  [ziel(DS_WERTE, wert('"valuename" =~ /^[Uu]ptime$/', '"sensorbox"'), alias)], "m", (0, 8, 12, 8)),
        zeitreihe("Auslastung", DS_WERTE, [ziel(DS_WERTE, wert('"valuename" = \'load\'', '"sensorbox"'), alias)],
                  "percent", (12, 8, 12, 8)),
    ]
    status_q = ('SELECT last("value") FROM "openandhome_status" WHERE ' + BOX +
                ' AND $timeFilter GROUP BY time($__interval), "sensorbox" fill(previous)')
    panels.insert(0, {
        "type": "state-timeline", "title": "Online-Status", "datasource": DS_WERTE,
        "description": "Meldung der Box an den MQTT-Broker (LWT): Connected = online",
        "gridPos": {"x": 0, "y": 0, "w": 24, "h": 5},
        "targets": [ziel(DS_WERTE, status_q, "$tag_sensorbox")],
        "fieldConfig": {"defaults": {"mappings": [{"type": "value", "options": {
            "Connected": {"text": "online", "color": "green", "index": 0},
            "Connection Lost": {"text": "offline", "color": "red", "index": 1}}}]}, "overrides": []},
        "options": {"showValue": "never", "mergeValues": True, "alignValue": "left"},
    })
    for p in panels[1:]:
        p["gridPos"]["y"] += 5
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
        zeitreihe("Netzlast (eth0)", s, [
            ziel(s, 'SELECT non_negative_derivative(mean("bytes_recv"), 1s) * 8 FROM "net" '
                    'WHERE "interface" = \'eth0\' AND $timeFilter GROUP BY time($__interval) fill(null)', "empfangen", "A"),
            ziel(s, 'SELECT non_negative_derivative(mean("bytes_sent"), 1s) * 8 FROM "net" '
                    'WHERE "interface" = \'eth0\' AND $timeFilter GROUP BY time($__interval) fill(null)', "gesendet", "B")],
                  "bps", (0, 18, 24, 8)),
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

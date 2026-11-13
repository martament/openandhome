#!/usr/bin/env python3
"""Erkennt angeschlossene Sensoren und schaltet die passenden Tasks ein (Plan 8.1).

Voraussetzung: Die Box hat eine Basis-config.dat, in der alle moeglichen Tasks
angelegt sind (nicht vorhandene deaktiviert). Das Skript
- scannt per USB den I2C-Bus (I2CScanner) und den 1-Wire-Bus (OWScan,<GPIO>),
- aktiviert I2C-Tasks (Display, HTU21D, AM2320, BMx280), deren Adresse gefunden wurde,
- aktiviert so viele DS18B20-Tasks wie Fuehler gefunden wurden und setzt ihre Adresse,
- traegt die aktiven Messwerte in die OLED-Zeilen ein,
- laesst nicht erkennbare Tasks (HC-SR04, Wassersensor ...) unveraendert,
  ausser sie werden mit --an/--aus genannt.
Ohne --anwenden wird nur angezeigt, was sich aendern wuerde.

Beispiele:
  tools/bin/espeasy_autoconfig.py
  tools/bin/espeasy_autoconfig.py --aus HCSR04 --anwenden
"""

import argparse
import json
import os
import re
import sys
import time

import serial

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from espeasy_syslog import Box, FormParser  # noqa: E402

PLUGIN_DS18B20 = 4
PLUGIN_SYSINFO = 26
# Plugin-Nr. -> moegliche I2C-Adressen
I2C_PLUGINS = {
    14: {0x40},          # SI70xx/HTU21D
    51: {0x5C},          # AM2320
    28: {0x76, 0x77},    # BMx280
    36: {0x3C, 0x3D},    # OLED SSD1306/SH1106 Framed
    23: {0x3C, 0x3D},    # OLED SSD1306
}
PLUGINS_OLED = {36, 23}
EINHEITEN = {"temperatur": "C", "luftfeuchtigkeit": "%", "distance": "cm", "druck": "hPa"}
OLED_ZEILEN = 12
P036_SCROLL_SOFORT = "32"   # OLED Framed 'Scroll': 1 Very Slow ... 32 Instant
P036_ZEIT_HHMM = "1"   # OLED Framed 'Header Time format': 0 HH:MM:SS, 1 HH:MM (24h)


# --- USB ---
def oeffne(port, timeout=0.2):
    """Oeffnet den Port mit DTR und RTS aktiv (pyserial-Standard).

    An der Olimex ESP32-POE getestet: DTR/RTS aus loest ueber die
    Auto-Reset-Schaltung einen Reset aus, beide an nicht."""
    s = serial.Serial()
    s.port, s.baudrate, s.timeout = port, 115200, timeout
    s.dtr = True
    s.rts = True
    s.open()
    return s


def seriell(port, kommando, wartezeit=3.0):
    """Sendet ein Kommando und liefert die Antwortzeilen (ohne Echo und Log-Praefix)."""
    with oeffne(port) as s:
        s.write(b"\n")          # Datenmuell im Eingabepuffer verwerfen
        time.sleep(0.3)
        s.reset_input_buffer()
        s.write(kommando.encode() + b"\n")
        ende, daten = time.time() + wartezeit, b""
        while time.time() < ende:
            daten += s.read(4096)
    zeilen = []
    for z in re.sub(r"\x1b\[[0-9;]*m", "", daten.decode("latin-1")).replace("\r", "").split("\n"):
        z = re.sub(r"^[\d:.]+\s*:\s*>?\s*", "", z).strip()   # "24.920 : >  ..." -> "..."
        if z and kommando.lower() not in z.lower():
            zeilen.append(z)
    return zeilen


def box_ip(port):
    for z in seriell(port, "Settings"):
        m = re.match(r"IP Address\s*:\s*([\d.]+)", z)
        if m and m.group(1) != "0.0.0.0":
            return m.group(1)
    sys.exit("FEHLER: IP der Box per USB nicht lesbar (WLAN verbunden?). --host angeben.")


# I2C-Geraete, die die Basis-config.dat (noch) nicht abdeckt -> Hinweis statt stiller Ignoranz
I2C_HINWEISE = {
    0x5C: "AM2320 - braucht Image collection_H und configs/espeasy/standalone/basis_am2320/config.dat "
          "(Werkstatt-Menue 1 und Flasher waehlen das automatisch).",
}


def i2c_hinweise(gefunden, bekannt):
    """Gibt Hinweise fuer gefundene I2C-Adressen aus, zu denen kein Task passt."""
    for adresse in sorted(set(gefunden) - set(bekannt)):
        text = I2C_HINWEISE.get(adresse, "unbekanntes Geraet - in der Basis-config.dat gibt es keinen passenden Task.")
        print(f"HINWEIS: I2C-Adresse 0x{adresse:02x}: {text}")


def i2c_scan(port):
    return {int(m.group(1), 16) for z in seriell(port, "I2CScanner")
            if (m := re.search(r"Found 0x([0-9a-fA-F]{2})", z))}


def hexnorm(text):
    return re.sub(r"[^0-9a-f]", "", text.lower())


OW_ADRESSE = re.compile(r"\b(?:[0-9a-fA-F]{2}[-: ]?){7}[0-9a-fA-F]{2}\b")


def ow_scan(port, gpio):
    # Adressen bestehen aus 8 Hex-Bytes, z. B. 28-ff-64-1e-...; Log-Zeilen ("... | WD : ...") ignorieren
    return [m.group(0) for z in seriell(port, f"OWScan,{gpio}", 4)
            if "|" not in z and (m := OW_ADRESSE.search(z))]


# --- HTTP ---
def lies_task(box, nr):
    html = box.get(f"/devices?index={nr}&page=1")
    parser = FormParser()
    parser.feed(html)
    return html, parser.felder


def dallas_option(html, adresse):
    """Optionswert im Feld dallas_addr0, dessen Text die gescannte Adresse enthaelt."""
    block = re.search(r"name='dallas_addr0'.*?</select>", html, re.S)
    if not block:
        return None
    ziel = hexnorm(adresse)[:16]
    for wert, text in re.findall(r"<option[^>]*value=['\"]?([^'\" >]+)[^>]*>([^<]*)", block.group(0)):
        if ziel and ziel in hexnorm(text):
            return wert
    return None


def autokonfiguration(box, port, an=(), aus=(), anwenden=False, ow_gpios=None, leise=False):
    """Scannt, zeigt die Aenderungen und schreibt sie bei anwenden=True.

    ow_gpios: 1-Wire-Busse, die gescannt werden (Professional: 4 und 2); Standard
    ist der GPIO des ersten DS18B20-Tasks. Fuehler1..N werden in Scan-Reihenfolge
    vergeben und bekommen GPIO und Adresse ihres Busses.
    leise=True: nur Warnungen ausgeben (Endanwender-Werkzeuge).
    Liefert die Namen der nicht erkennbaren Tasks (HC-SR04, Wassersensor ...)."""
    ausgabe = (lambda *a, **k: None) if leise else print
    tasks = json.loads(box.get("/json"))["Sensors"]
    ausgabe(f"Box {box.basis}: {len(tasks)} Tasks")

    formulare = {t["TaskNumber"]: lies_task(box, t["TaskNumber"]) for t in tasks}
    plugin = {nr: int(f["TDNUM"]) for nr, (_, f) in formulare.items() if f.get("TDNUM", "").isdigit()}

    i2c = i2c_scan(port)
    ausgabe("I2C gefunden:", ", ".join(f"0x{a:02x}" for a in sorted(i2c)) or "nichts")
    i2c_hinweise(i2c, {a for p in plugin.values() if p in I2C_PLUGINS for a in I2C_PLUGINS[p]})
    ds_tasks = sorted(nr for nr, p in plugin.items() if p == PLUGIN_DS18B20)
    fuehler = []
    if ds_tasks:
        for gpio in ow_gpios or [formulare[ds_tasks[0]][1].get("taskdevicepin1", "-1")]:
            gefunden = ow_scan(port, gpio)
            ausgabe(f"1-Wire an GPIO {gpio}: {len(gefunden)} Fuehler {gefunden}")
            fuehler += [(str(gpio), a) for a in gefunden]
        if len(fuehler) > len(ds_tasks):
            print(f"WARNUNG: {len(fuehler)} Fuehler, aber nur {len(ds_tasks)} DS18B20-Tasks in der config.dat")
        # Nach dem Scan neu lesen, damit das Adressfeld die gefundenen Fuehler anbietet
        formulare.update({nr: lies_task(box, nr) for nr in ds_tasks})

    # Soll-Zustand je Task bestimmen
    neu, nicht_erkennbar = {}, []
    for nr, (html, felder) in formulare.items():
        f, name, p = dict(felder), felder.get("TDN", ""), plugin.get(nr)
        if p in I2C_PLUGINS:
            treffer = sorted(I2C_PLUGINS[p] & i2c)
            aktiv = bool(treffer)
            if treffer:
                f["i2c_addr"] = str(treffer[0])
        elif p == PLUGIN_DS18B20:
            k = ds_tasks.index(nr)
            aktiv = k < len(fuehler)
            if aktiv:
                gpio, adresse = fuehler[k]
                if f.get("taskdevicepin1") != gpio:
                    f["taskdevicepin1"] = gpio
                    if not anwenden:
                        ausgabe(f"  '{name}': GPIO -> {gpio}, Adresse {adresse} (wird beim Anwenden gewaehlt)")
                        neu[nr] = dict(f, TDE="on")
                        continue
                    # Adressliste haengt am gespeicherten GPIO: erst Pin speichern, dann neu lesen
                    box.post(f"/devices?index={nr}&page=1", dict(f, edit="1"))
                    html, felder_neu = lies_task(box, nr)
                    f = dict(felder_neu)
                wert = dallas_option(html, adresse)
                if wert is None:
                    if anwenden:   # im Probelauf kann die Auswahlliste noch unvollstaendig sein
                        print(f"WARNUNG: Adresse {adresse} nicht im Auswahlfeld von '{name}' - bitte in der Weboberflaeche waehlen")
                else:
                    f["dallas_addr0"] = wert
        elif p in (PLUGIN_SYSINFO, *PLUGINS_OLED) or p is None:
            neu[nr] = f     # Systeminfo / Display ohne I2C-Treffer-Logik: unveraendert
            continue
        else:
            nicht_erkennbar.append(name)
            if name not in an and name not in aus:
                neu[nr] = f     # nicht erkennbar und nicht genannt: unveraendert
                continue
            aktiv = name in an
        if aktiv:
            f["TDE"] = "on"
        else:
            f.pop("TDE", None)
        neu[nr] = f

    # OLED-Zeilen aus den aktiven Messwerten erzeugen
    werte = []
    for t in tasks:
        nr = t["TaskNumber"]
        if plugin.get(nr) in PLUGINS_OLED or plugin.get(nr) == PLUGIN_SYSINFO or "TDE" not in neu[nr]:
            continue
        for i in range(1, 5):
            wert = neu[nr].get(f"TDVN{i}")
            if wert:
                werte.append(f"[{neu[nr]['TDN']}#{wert}] {EINHEITEN.get(wert.lower(), '')}".rstrip())
    for nr, f in neu.items():
        if plugin.get(nr) in PLUGINS_OLED and "TDE" in f:
            for i in range(1, OLED_ZEILEN + 1):
                f[f"pc_arg{i}"] = f"{i}: {werte[i - 1]}" if i <= len(werte) else ""
            if "scroll" in f:
                # Seitenwechsel ohne Rein-/Rausscrollen: Scrollen war instabil
                f["scroll"] = P036_SCROLL_SOFORT
            f.pop("ScrollLines", None)      # lange Zeilen nicht scrollen (Checkbox aus)
            if "timeFmt" in f:
                # Uhrzeit oben links HH:MM statt HH:MM:SS (Feld fehlt in ESP8266-Images mit LIMIT_BUILD_SIZE)
                f["timeFmt"] = P036_ZEIT_HHMM

    # Aenderungen anzeigen und schreiben
    aenderungen = 0
    for t in tasks:
        nr = t["TaskNumber"]
        alt, f = formulare[nr][1], neu[nr]
        diff = {k: (alt.get(k), f.get(k)) for k in set(alt) | set(f) if alt.get(k) != f.get(k)}
        status = "AN " if "TDE" in f else "aus"
        ausgabe(f"  [{status}] Task {nr:2} {f.get('TDN', ''):<14} {t['Type']}")
        for k, (a, b) in sorted(diff.items()):
            ausgabe(f"         {k}: {a!r} -> {b!r}")
        if diff:
            aenderungen += 1
            if anwenden:
                f["edit"] = "1"
                box.post(f"/devices?index={nr}&page=1", f)

    if not aenderungen:
        ausgabe("Keine Aenderungen noetig.")
    elif anwenden:
        ausgabe(f"{aenderungen} Task(s) geschrieben.")
    else:
        ausgabe(f"{aenderungen} Task(s) wuerden geaendert - mit --anwenden schreiben.")
    if nicht_erkennbar:
        ausgabe("Nicht erkennbar (per --an/--aus waehlen):", ", ".join(nicht_erkennbar))
    return nicht_erkennbar


def main():
    parser = argparse.ArgumentParser(description="Sensoren erkennen und Tasks passend einschalten.")
    parser.add_argument("--port", default="/dev/ttyUSB0")
    parser.add_argument("--host", help="IP der Box (Standard: per USB gelesen)")
    parser.add_argument("--passwort", help="Admin-Passwort der Box, falls gesetzt")
    parser.add_argument("--an", nargs="*", default=[], metavar="TASKNAME", help="nicht erkennbare Tasks einschalten")
    parser.add_argument("--aus", nargs="*", default=[], metavar="TASKNAME", help="nicht erkennbare Tasks ausschalten")
    parser.add_argument("--anwenden", action="store_true", help="Aenderungen wirklich schreiben")
    parser.add_argument("--ow-gpios", nargs="*", type=int, help="1-Wire-Busse (Standard: je Box-Klasse)")
    args = parser.parse_args()

    box = Box(args.host or box_ip(args.port), args.passwort)
    ow = args.ow_gpios
    if ow is None and "ESP32" in json.loads(box.get("/json"))["System"].get("Binary Filename", ""):
        from oh_klassen import KLASSEN
        ow = KLASSEN["ESP32"]["ow_gpios"]      # Professional: zwei 1-Wire-Busse
    autokonfiguration(box, args.port, args.an, args.aus, args.anwenden, ow_gpios=ow)


if __name__ == "__main__":
    main()

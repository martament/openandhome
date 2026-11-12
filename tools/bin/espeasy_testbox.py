#!/usr/bin/env python3
"""Testablauf fuer Sensorboxen (Plan Abschnitt 6 und 8.2).

  aufsetzen  Sicherung, Flashen, WLAN, Basis-config.dat, Name/Unit,
             Sensoren erkennen, Dashboard, Werte- und Dashboard-Pruefung,
             Syslog an -> 24h-Test laeuft
  pruefen    Werte und Dashboard pruefen (jederzeit waehrend des Tests)
  dashboard  Dashboard aus den aktiven Tasks erzeugen und hochladen
  beenden    Werte pruefen, Syslog aus, optional WLAN zuruecksetzen (wie esp_resetap)

Grundkonfiguration laeuft ueber USB; nur Syslog, config.dat-Upload, Device-
Einstellungen und Dashboard gehen ueber HTTP (dafuer gibt es keine Kommandos).
Protokolle: ~/openandhome-testprotokolle/<Name>_<Start>.txt

Beispiele:
  tools/bin/espeasy_testbox.py aufsetzen
  tools/bin/espeasy_testbox.py pruefen
  tools/bin/espeasy_testbox.py beenden --wlan-reset
"""

import argparse
import datetime
import getpass
import glob
import html
import json
import os
import re
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid

import serial

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from espeasy_autoconfig import PLUGIN_DS18B20, PLUGIN_SYSINFO, PLUGINS_OLED, autokonfiguration, oeffne  # noqa: E402
from espeasy_configcheck import lese_settings  # noqa: E402
from espeasy_syslog import Box, FormParser, setze_syslog  # noqa: E402

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
ESPTOOL_PFAD = os.path.join(ROOT, "tools/oh-flasher/bin/pythonportable/Lib/site-packages")
RESSOURCEN = os.path.join(ROOT, "configs/espeasy/standalone/resources")
DASHBOARD_DATEIEN = ["temperature.png", "temperature1.png", "humidity.png", "distance.png",
                     "openandhome_32.png", "openandhome.css"]
PROTOKOLLE = os.path.expanduser("~/openandhome-testprotokolle")
# Erlaubter Web-Zugriff (Config -> Client IP filtering: Allow IP range)
ZUGRIFF_VON, ZUGRIFF_BIS = "192.168.0.0", "192.168.255.255"
# Name bei Auslieferung (wie bisher); im Test heisst die Box Testbox<Unit>
AUSLIEFERUNG_NAME, AUSLIEFERUNG_UNIT = "Sensorbox1", "0"
BACKUPS = os.path.expanduser("~/openandhome-backups")

KLASSEN = {
    "ESP8266": {
        "name": "standalone",
        "image": "configs/espeasy/standalone/ESP_Easy_mega_*_climate_B_ESP8266_4M1M.bin",
        "flash": ["-fs", "4MB", "0x0"],
        "basis": "configs/espeasy/standalone/basis/config.dat",
        "wlan": True,
        # climate_B hat kein AM2320-Plugin (P051) -> bei erkanntem AM2320 collection_H
        "am2320": {
            "image": "configs/espeasy/standalone/ESP_Easy_mega_*_collection_H_ESP8266_4M1M.bin",
            "basis": "configs/espeasy/standalone/basis_am2320/config.dat",
        },
    },
    "ESP32": {
        "name": "professional",
        "image": "configs/espeasy/professional/ESP_Easy_mega_*_collection_A_ESP32_4M316k.factory.bin",
        "flash": ["0x0"],
        "basis": "configs/espeasy/professional/basis/config.dat",
        # Werkstatt laeuft per WLAN am USB (USB und PoE nie gleichzeitig, Olimex ESP32-POE
        # ist nicht galvanisch getrennt); beim Kunden Ethernet
        "wlan": True,
        "wlan_reset": True,
        # Olimex ESP32-POE: LAN8720 (0), MDC 23, MDIO 18, Power 12, 50 MHz APLL invertiert GPIO17 (3)
        "ethernet": '{"nwpluginID":3,"enabled":"true","route_prio":200,"Index":0,"phytype":0,'
                    '"phyaddr":0,"MDC":23,"MDIO":18,"pwr":12,"clock":3}',
        "ow_gpios": [4, 2],
        "zabbix_controller": 2,
    },
}

# Plausibilitaet je Messwertname: (min, max, verdaechtige Werte)
GRENZEN = {
    "temperatur": (-40.0, 85.0, {85.0, -127.0, 0.0}),
    "luftfeuchtigkeit": (1.0, 100.0, {0.0}),
    "distance": (0.1, 500.0, set()),
}
EINHEITEN = {"temperatur": "°C", "luftfeuchtigkeit": "%", "distance": "cm"}
ICONS = {"temperatur": "temperature.png", "luftfeuchtigkeit": "humidity.png", "distance": "distance.png"}


# --- Ein-/Ausgabe ---
def frage(text, standard=""):
    antwort = input(f"{text}{f' [{standard}]' if standard else ''}: ").strip()
    return antwort or standard


def ja(text, standard=True):
    antwort = frage(f"{text} (j/n)", "j" if standard else "n").lower()
    return antwort.startswith(("j", "y"))


def schritt(text):
    print(f"\n\033[36m=== {text}\033[0m")


class Protokoll:
    def __init__(self, pfad):
        self.pfad = pfad

    def schreibe(self, text):
        os.makedirs(os.path.dirname(self.pfad), exist_ok=True)
        with open(self.pfad, "a", encoding="utf-8") as f:
            f.write(text.rstrip() + "\n")

    @staticmethod
    def neuestes(name):
        dateien = sorted(glob.glob(os.path.join(PROTOKOLLE, f"{name}_*.txt")))
        return Protokoll(dateien[-1]) if dateien else None


# --- USB ---
def sende(port, *kommandos, wartezeit=1.5):
    """Sendet Kommandos (Leerzeile vorweg gegen Datenmuell) und liefert die Antwortzeilen."""
    with oeffne(port) as s:
        s.write(b"\n")
        time.sleep(0.3)
        s.reset_input_buffer()
        for k in kommandos:
            s.write(k.encode() + b"\n")
            time.sleep(0.4)
        ende, daten = time.time() + wartezeit, b""
        while time.time() < ende:
            daten += s.read(4096)
    return [re.sub(r"^[\d:.]+\s*:\s*>?\s*", "", z).strip()
            for z in re.sub(r"\x1b\[[0-9;]*m", "", daten.decode("latin-1")).replace("\r", "").split("\n") if z.strip()]


def usb_da(port):
    return bool(port) and os.path.exists(port)


def kommando(port, box, *kommandos):
    """Sendet Kommandos per USB, sonst per HTTP (/control?cmd=), z. B. Professional am PoE."""
    if usb_da(port):
        return sende(port, *kommandos)
    for k in kommandos:
        try:
            box.get("/control?cmd=" + urllib.parse.quote(k))
        except OSError:
            pass     # Reboot/WLAN-Wechsel trennt die Verbindung
    return []


def usb_ip(port):
    for z in sende(port, "Settings", wartezeit=2):
        m = re.match(r"IP Address\s*:\s*([\d.]+)", z)
        if m and m.group(1) != "0.0.0.0":
            return m.group(1)
    return None


def warte_ip(port, sekunden=90):
    print(f"Warte auf Netzwerk (max. {sekunden} s) ...", end="", flush=True)
    ende = time.time() + sekunden
    while time.time() < ende:
        try:
            ip = usb_ip(port)
        except serial.SerialException:
            ip = None
        if ip:
            print(f" {ip}")
            return ip
        print(".", end="", flush=True)
        time.sleep(3)
    sys.exit("\nFEHLER: Box bekommt keine IP (WLAN-Daten / Kabel pruefen).")


def erreichbar(port, ip):
    """Box-Objekt, wenn die geschuetzten Seiten erreichbar sind, sonst None.

    /json antwortet auch bei Subnetz-Sperre, daher wird /advanced geprueft; eine
    Sperre hebt ClearAccessBlock per USB auf (nur bis zum naechsten Reboot)."""
    box = Box(ip, None)
    for versuch in range(3):
        try:
            box.get("/advanced")
            return box
        except urllib.error.HTTPError as e:
            if e.code == 403 and port:
                print("Web-Zugriff gesperrt (anderes Subnetz) -> ClearAccessBlock per USB")
                sende(port, "ClearAccessBlock")
        except OSError:
            time.sleep(2)
    return None


def http_bereit(port, ip, neustarts=3):
    """Wartet, bis die Weboberflaeche erreichbar ist.

    Die Box kann in einem anderen WLAN/Netz landen (z. B. gleiche SSID in zwei
    Netzen, nach frischem Flash beobachtet). Dann per USB neu starten und neu
    verbinden; hilft das nicht, kann eine andere IP eingegeben werden."""
    for runde in range(neustarts + 1):
        box = erreichbar(port, ip)
        if box:
            return box
        if not port or runde == neustarts:
            break
        print(f"{ip} nicht erreichbar (anderes WLAN/Netz?) -> Reboot per USB ({runde + 1}/{neustarts})")
        sende(port, "Reboot")
        time.sleep(10)
        ip = warte_ip(port)
    print(f"\033[31mWeboberflaeche nicht erreichbar.\033[0m Box meldet per USB:")
    if port:
        for z in sende(port, "Settings", wartezeit=2):
            if re.match(r"(IP Address|WifiSSID)\s*:", z):
                print(f"  {z}")
    anders = frage("Andere IP eingeben (leer = abbrechen)")
    if anders:
        return http_bereit(port, anders, neustarts=0)
    sys.exit("Abgebrochen: Box im Netz nicht erreichbar.")


def setze_zugriff(box, von=ZUGRIFF_VON, bis=ZUGRIFF_BIS):
    """Erlaubt Web-Zugriffe dauerhaft aus dem IP-Bereich (Config-Seite, liegt in security.dat).

    Noetig, weil ein 'Save' nach ClearAccessBlock sonst 'Allow All' festschreibt
    und eine frisch geflashte Box nur das eigene Subnetz erlaubt."""
    felder = dict(lies_formular_config(box))
    felder.update({"ipblocklevel": "2", "iprangelow": von, "iprangehigh": bis})
    box.post("/config", felder)
    neu = lies_formular_config(box)
    if neu.get("ipblocklevel") != "2" or neu.get("iprangelow") != von or neu.get("iprangehigh") != bis:
        sys.exit(f"FEHLER: IP-Zugriff nicht gesetzt ({neu.get('ipblocklevel')}, {neu.get('iprangelow')}-{neu.get('iprangehigh')})")
    print(f"Web-Zugriff erlaubt fuer {von} - {bis}")


def lies_formular_config(box):
    parser = FormParser()
    parser.feed(box.get("/config"))
    return parser.felder


def am2320_erkannt(port):
    """Der AM2320 schlaeft und antwortet oft erst beim zweiten Zugriff - daher zweimal scannen."""
    from espeasy_autoconfig import i2c_scan
    return any(0x5C in i2c_scan(port) for _ in range(2))


def waehle_variante(port, klasse, image_aktuell, erzwingen=False):
    """Prueft auf AM2320; flasht bei Bedarf das passende Image nach (Einstellungen bleiben).

    Liefert den Pfad der zu verwendenden Basis-config.dat."""
    variante = klasse.get("am2320")
    if not variante or not (erzwingen or am2320_erkannt(port)):
        return os.path.join(ROOT, klasse["basis"])
    print("AM2320 erkannt (I2C 0x5C) -> Image mit AM2320-Plugin und AM2320-Basis-config.dat")
    bild = sorted(glob.glob(os.path.join(ROOT, variante["image"])))[-1]
    # Auch bei --ohne-flash: ohne passendes Image fehlt das AM2320-Plugin und der Task verschwindet
    if os.path.basename(bild).removesuffix(".bin") != image_aktuell:
        print(f"Flashe {os.path.basename(bild)} (nur Firmware, Einstellungen bleiben) ...")
        esptool(port, "write_flash", *klasse["flash"], bild)
        time.sleep(20)
    return os.path.join(ROOT, variante["basis"])


def flash_leer(port):
    """True, wenn Bootloader und App-Bereich nur 0xFF enthalten (neues Board)."""
    import tempfile
    with tempfile.TemporaryDirectory() as tmp:
        for adresse in ("0x1000", "0x10000"):
            pfad = os.path.join(tmp, "probe.bin")
            esptool(port, "read_flash", adresse, "0x40", pfad)
            with open(pfad, "rb") as f:
                if f.read() != b"\xff" * 0x40:
                    return False
    return True


def setze_zabbix(box, nr, server):
    """Zabbix-Controller (Sonderanfertigung) ein- oder ausschalten; Standard: aus."""
    p = f"/controllers?index={nr}"
    f = FormParser()
    f.feed(box.get(p))
    felder = dict(f.felder, edit="1")
    if felder.get("protocol") != "17":
        print(f"WARNUNG: Controller {nr} ist kein Zabbix-Controller - nichts geaendert.")
        return
    if server:
        felder.update(controllerenabled="on", controllerhostname=server)
    else:
        felder.pop("controllerenabled", None)
    box.post(p, felder)
    print(f"Zabbix-Controller: {'an, Server ' + server if server else 'aus'}")


# --- esptool ---
def esptool(port, *argumente):
    umgebung = dict(os.environ, PYTHONPATH=ESPTOOL_PFAD)
    ergebnis = subprocess.run([sys.executable, "-m", "esptool", "--port", port, "-b", "460800", *argumente],
                              capture_output=True, text=True, env=umgebung)
    if ergebnis.returncode != 0:
        sys.exit(f"FEHLER esptool {argumente[0]}:\n{ergebnis.stdout[-800:]}{ergebnis.stderr[-800:]}")
    return ergebnis.stdout


def chip_info(port):
    ausgabe = esptool(port, "chip_id")
    chip = "ESP32" if "ESP32" in re.search(r"Chip is (\S+)", ausgabe).group(1) else "ESP8266"
    mac = re.search(r"MAC: ([0-9a-f:]+)", ausgabe).group(1)
    return chip, mac


# --- HTTP ---
def lade_hoch(box, pfad, name=None):
    with open(pfad, "rb") as f:
        daten = f.read()
    grenze = uuid.uuid4().hex
    body = (f"--{grenze}\r\nContent-Disposition: form-data; name=\"file\"; filename=\"{name or os.path.basename(pfad)}\"\r\n"
            "Content-Type: application/octet-stream\r\n\r\n").encode() + daten + f"\r\n--{grenze}--\r\n".encode()
    req = urllib.request.Request(
        box.basis + "/upload", data=body, headers={"Content-Type": f"multipart/form-data; boundary={grenze}"})
    with box.oeffner.open(req, timeout=30) as antwort:
        if antwort.status != 200:
            sys.exit(f"FEHLER: Upload {pfad} -> HTTP {antwort.status}")


def aktive_messwerte(box, alle=False):
    """[(Taskname, Wertname, Wert, Plugin-Typ)] der aktiven (bzw. aller) Sensor-Tasks."""
    werte = []
    for t in json.loads(box.get("/json"))["Sensors"]:
        if (t["TaskEnabled"] != "true" and not alle) or "System Info" in t["Type"] or "Display" in t["Type"]:
            continue
        for v in t.get("TaskValues", []):
            werte.append((t["TaskName"], v["Name"], v["Value"], t["Type"]))
    return werte


# --- Dashboard ---
def erzeuge_dashboard(box, ressourcen=RESSOURCEN, alle=False):
    """alle=True: Zeilen fuer alle Sensor-Tasks (Kundenpaket ohne Netzwerk)."""
    zeilen, fuehler_nr = [], 0
    for task, wert, _, typ in aktive_messwerte(box, alle):
        art = wert.lower()
        if "1-Wire" in typ:
            fuehler_nr += 1
            label = f"Fühler {fuehler_nr}"
            icon = "temperature.png" if fuehler_nr % 2 else "temperature1.png"
        else:
            label = f"{wert} ({task})"
            icon = ICONS.get(art, "humidity.png")
        zeilen.append(f" <tr>\n  <td>{html.escape(label)}:</td>\n  <td><img src=\"{icon}\"></td>\n"
                      f"  <td>[{task}#{wert}] {EINHEITEN.get(art, '')}</td>\n </tr>")
    tabelle = "<table id=\"sensordata\" >\n" + "\n".join(zeilen) + "\n</table>\n"
    with open(os.path.join(ressourcen, "header.txt"), encoding="utf-8") as f:
        kopf = f.read()
    with open(os.path.join(ressourcen, "footer.txt"), encoding="utf-8") as f:
        fuss = f.read()
    return kopf + tabelle + fuss, len(zeilen)


def dashboard_hochladen(box, ablage=None, ressourcen=RESSOURCEN, alle=False):
    inhalt, anzahl = erzeuge_dashboard(box, ressourcen, alle)
    ablage = ablage or os.path.join(os.path.expanduser("~"), ".cache", "openandhome")
    os.makedirs(ablage, exist_ok=True)
    pfad = os.path.join(ablage, "openandhome.esp")
    with open(pfad, "w", encoding="utf-8") as f:
        f.write(inhalt)
    for datei in DASHBOARD_DATEIEN:
        lade_hoch(box, os.path.join(ressourcen, datei))
    lade_hoch(box, pfad)
    print(f"Dashboard mit {anzahl} Messwert(en) hochgeladen ({pfad}).")


# --- Pruefung ---
def pruefe(box, port=None):
    """Prueft Messwerte und Dashboard. Liefert (ok, Berichtszeilen)."""
    # Aktive Tasks sofort messen lassen statt auf das Intervall zu warten
    nummern = [t["TaskNumber"] for t in json.loads(box.get("/json"))["Sensors"] if t["TaskEnabled"] == "true"]
    kommando(port, box, *[f"TaskRun,{n}" for n in nummern])
    time.sleep(4)
    bericht, ok = [], True
    werte = aktive_messwerte(box)
    if not werte:
        bericht.append("FEHLER  keine aktiven Sensoren")
        ok = False
    for task, wert, zahl, _ in werte:
        unten, oben, verdaechtig = GRENZEN.get(wert.lower(), (None, None, set()))
        status = "OK"
        if unten is not None and not unten <= float(zahl) <= oben:
            status, ok = "FEHLER", False
        elif float(zahl) in verdaechtig:
            status = "WARNUNG"
        bericht.append(f"{status:<8}{task}#{wert} = {zahl} {EINHEITEN.get(wert.lower(), '')}")

    # Dashboard: von der Box gerendert, alle Platzhalter muessen ersetzt sein
    try:
        seite = box.get("/openandhome.esp")
        offen = re.findall(r"\[[^\]<>]+#[^\]<>]+\]", seite)
        if offen:
            bericht.append(f"FEHLER  Dashboard: nicht ersetzte Platzhalter {offen}")
            ok = False
        else:
            bericht.append(f"OK      Dashboard: {seite.count('<tr>')} Zeilen, alle Werte ersetzt")
        for task, wert, zahl, _ in werte:
            if f"{task}#{wert}" in seite:
                continue
            # Zahl mit Punkt oder Komma, nicht Teil einer laengeren Zahl
            zahlen = {float(z.replace(",", ".")) for z in re.findall(r"-?\d+(?:[.,]\d+)?", seite)}
            if float(zahl) not in zahlen:
                bericht.append(f"WARNUNG Dashboard: Wert {task}#{wert}={zahl} nicht gefunden")
        for datei in ("openandhome.css", "temperature.png"):
            box.get("/" + datei)
    except urllib.error.HTTPError as e:
        bericht.append(f"FEHLER  Dashboard: {e.url} -> HTTP {e.code}")
        ok = False
    for zeile in bericht:
        farbe = "\033[32m" if zeile.startswith("OK") else "\033[33m" if zeile.startswith("WARN") else "\033[31m"
        print(f"  {farbe}{zeile}\033[0m")
    return ok, bericht


# --- Ablaeufe ---
def aufsetzen(args):
    port = args.port
    schritt("1/10 Chip erkennen")
    chip, mac = chip_info(port)
    klasse = KLASSEN[chip]
    print(f"{chip} ({klasse['name']}), MAC {mac}")
    alte_ip = usb_ip(port)

    if not args.ohne_flash:
        if flash_leer(port):
            print("2/10 Flash ist leer (neues Board) - keine Sicherung noetig.")
        elif ja("2/10 Vorher kompletten Flash und config.dat sichern?"):
            ziel = os.path.join(BACKUPS, f"{datetime.datetime.now():%Y%m%d-%H%M}_{mac.replace(':', '')}")
            os.makedirs(ziel, exist_ok=True)
            print("Lese Flash (ca. 2 Minuten) ...")
            esptool(port, "read_flash", "0", "0x400000", os.path.join(ziel, "flash_full_4MB.bin"))
            if alte_ip:
                try:
                    # ESP32 liefert unter /download ein TAR mit allen Dateien
                    with open(os.path.join(ziel, "config_download.dat_oder_tar"), "wb") as f:
                        f.write(urllib.request.urlopen(f"http://{alte_ip}/download", timeout=20).read())
                except OSError as e:
                    print(f"config.dat nicht per HTTP ladbar ({e}) - Flash-Sicherung reicht zur Wiederherstellung.")
            print(f"Sicherung: {ziel} (enthaelt WLAN-Daten, nicht ins Repo!)")

        bilder = sorted(glob.glob(os.path.join(ROOT, klasse["image"])))
        if not bilder:
            sys.exit(f"FEHLER: kein Image {klasse['image']} - erst Images laden (Menue i).")
        schritt(f"3/10 Flashen: {os.path.basename(bilder[-1])}")
        if not ja("Flash wird geloescht und neu beschrieben. Weiter?"):
            sys.exit("Abgebrochen.")
        esptool(port, "erase_flash")
        esptool(port, "write_flash", *klasse["flash"], bilder[-1])
        print("Geflasht, warte auf Start ...")
        time.sleep(20)

    schritt("4/10 Netzwerk")
    if "ethernet" in klasse:
        print("Ethernet (Olimex ESP32-POE) per USB einrichten ...")
        sende(port, f"NetworkImportConfig,3,{klasse['ethernet']}", "Save")
    if ja("WLAN-Zugangsdaten setzen?", klasse["wlan"]):
        if args.wlan_datei:
            with open(args.wlan_datei, encoding="utf-8") as f:
                ssid, key = [z.rstrip("\n") for z in f.readlines()[:2]]
            print(f"WLAN aus {args.wlan_datei}: {ssid}")
        else:
            ssid = frage("WLAN-SSID")
            key = getpass.getpass("WPA-Key (unsichtbar): ")
        sende(port, f'WifiSSID,"{ssid}"', f'WifiKey,"{key}"', "Save", "Reboot")
        time.sleep(10)
    box = http_bereit(port, warte_ip(port))
    ip = box.basis.removeprefix("http://")

    schritt("5/10 Basis-config.dat")
    image_aktuell = json.loads(box.get("/json"))["System"].get("Binary Filename", "")
    vorschlag = waehle_variante(port, klasse, image_aktuell, args.am2320)
    box = http_bereit(port, warte_ip(port))
    basis = frage("config.dat", os.path.relpath(vorschlag, os.getcwd()))
    with open(basis, "rb") as f:
        einstellungen = lese_settings(f.read())
    if einstellungen["Syslog_IP"] != "0.0.0.0" or einstellungen["SyslogLevel"]:
        print("WARNUNG: In der Basis-config.dat ist Syslog aktiv - fuer Stable neu sichern.")
    lade_hoch(box, basis, "config.dat")
    sende(port, "Reboot")
    time.sleep(10)
    box = http_bereit(port, warte_ip(port))
    ip = box.basis.removeprefix("http://")

    schritt("6/10 Testname, Unit und Web-Zugriff")
    unit = frage("Unit-Nummer (eindeutig je Testbox)", "1")
    name = frage("Name im Test", f"Testbox{unit}")
    sende(port, f"Name,{name}", f"Unit,{unit}", "Save")
    setze_zugriff(box)

    schritt("7/10 Sensoren erkennen")
    ow = klasse.get("ow_gpios")
    nicht_erkennbar = autokonfiguration(box, port, ow_gpios=ow)
    an = [n for n in nicht_erkennbar if ja(f"Ist '{n}' verbaut?", False)]
    aus = [n for n in nicht_erkennbar if n not in an]
    autokonfiguration(box, port, an, aus, anwenden=True, ow_gpios=ow)
    if "zabbix_controller" in klasse:
        server = args.zabbix or (frage("Zabbix-Server (Sonderanfertigung, leer = kein Zabbix)") or None)
        setze_zabbix(box, klasse["zabbix_controller"], server)

    schritt("8/10 Dashboard")
    dashboard_hochladen(box)

    schritt("9/10 Werte und Dashboard pruefen")
    ok, bericht = pruefe(box, port)
    if not ok and not ja("Pruefung mit Fehlern. Test trotzdem starten?", False):
        sys.exit("Abgebrochen - Box laeuft ohne Syslog.")

    schritt("10/10 Syslog an, Test laeuft")
    setze_syslog(box, "an", args.syslog_ip)
    start = datetime.datetime.now()
    protokoll = Protokoll(os.path.join(PROTOKOLLE, f"{name}_{start:%Y%m%d-%H%M}.txt"))
    info = json.loads(box.get("/json"))["System"]
    protokoll.schreibe(f"# Testprotokoll {name}\nStart:    {start:%Y-%m-%d %H:%M}\n"
                       f"Box:      {chip} MAC {mac}, IP {ip}, Unit {unit}\n"
                       f"Firmware: {info.get('Binary Filename')} (Build {info.get('Build')})\n"
                       f"Config:   {basis}\nSyslog:   {args.syslog_ip}\n\nPruefung Start:")
    for zeile in bericht:
        protokoll.schreibe(f"  {zeile}")
    ende = start + datetime.timedelta(hours=24)
    print(f"\n24h-Test gestartet. Ende fruehestens {ende:%a %d.%m. %H:%M} -> Menue 'Test beenden'.")
    print(f"Protokoll: {protokoll.pfad}")


def beenden(args):
    port = args.port
    if not usb_da(port):
        port = None
    ip = args.host or (usb_ip(port) if port else None) or frage("IP der Box (z. B. aus dem Router)")
    if not ip:
        sys.exit("FEHLER: IP nicht per USB lesbar - --host angeben.")
    box = http_bereit(port, ip) if port else Box(ip, None)
    name = json.loads(box.get("/json"))["System"].get("Unit Name", "")
    protokoll = Protokoll.neuestes(name)

    schritt(f"Abschlusspruefung {name}")
    ok, bericht = pruefe(box, port)
    vorzeitig = False
    if protokoll:
        start = re.search(r"Start:\s+(.+)", open(protokoll.pfad, encoding="utf-8").read())
        if start:
            dauer = datetime.datetime.now() - datetime.datetime.strptime(start.group(1).strip(), "%Y-%m-%d %H:%M")
            print(f"Testdauer: {dauer.total_seconds() / 3600:.1f} h")
            if dauer < datetime.timedelta(hours=24):
                vorzeitig = True
                print("\033[33mWARNUNG: weniger als 24 h - Test zaehlt nicht als bestanden.\033[0m")

    schritt("Syslog aus")
    setze_syslog(box, "aus")

    schritt(f"Auslieferungsname {AUSLIEFERUNG_NAME}, Web-Zugriff")
    kommando(port, box, f"Name,{AUSLIEFERUNG_NAME}", f"Unit,{AUSLIEFERUNG_UNIT}", "Save")
    setze_zugriff(box)

    chip = "ESP32" if "ESP32" in json.loads(box.get("/json"))["System"].get("Binary Filename", "") else "ESP8266"
    vorgabe = KLASSEN[chip].get("wlan_reset", False)
    frage_text = ("WLAN-Daten der Werkstatt loeschen (Professional laeuft beim Kunden ueber LAN)?" if vorgabe
                  else "WLAN-Daten loeschen wie esp_resetap (nur WLAN-Boxen)?")
    wlan = args.wlan_reset or (not args.ohne_wlan_reset and ja(frage_text, vorgabe))
    if wlan:
        schritt("WLAN zuruecksetzen")
        kommando(port, box, "WifiSSID ssid", "WifiKey wpakey", "WifiSSID2 ssid", "WifiKey2 wpakey", "Save", "Reboot")
        print("Gesendet - die Box startet neu und oeffnet den AP.")

    ergebnis = "NICHT BESTANDEN" if not ok else "VORZEITIG BEENDET" if vorzeitig else "BESTANDEN"
    if protokoll:
        protokoll.schreibe(f"\nEnde:     {datetime.datetime.now():%Y-%m-%d %H:%M}\nPruefung Ende:")
        for zeile in bericht:
            protokoll.schreibe(f"  {zeile}")
        protokoll.schreibe(f"Syslog aus, Name {AUSLIEFERUNG_NAME}/Unit {AUSLIEFERUNG_UNIT}, "
                           f"Zugriff {ZUGRIFF_VON}-{ZUGRIFF_BIS}, WLAN {'zurueckgesetzt' if wlan else 'unveraendert'}\n"
                           f"Ergebnis: {ergebnis}")
        print(f"Protokoll: {protokoll.pfad}")
    print(f"\nErgebnis: {ergebnis}")


def kundenpaket(args):
    """Erzeugt das Manifest fuer den Windows-Flasher (Plan 12, nur ESP8266).

    Kein Dateisystem-Abzug von der Box: SPIFFS behaelt ueberschriebene Bloecke,
    ein Abzug enthielte alte WLAN-Daten. Das Manifest verweist auf Firmware,
    Basis-config.dat und Dashboard-Dateien im Repo; die Task-Liste fuer die
    Erkennung wird aus der Basis-config.dat auf der Box gelesen."""
    port = args.port
    schritt("1/3 Box pruefen")
    chip, mac = chip_info(port)
    if chip != "ESP8266":
        sys.exit("FEHLER: Kundenpaket nur fuer Standalone (ESP8266).")
    # chip_id setzt den Chip zurueck - auf den Neustart warten
    box = http_bereit(port, warte_ip(port, 60))

    schritt("2/3 Basis-config.dat laden, Task-Liste lesen")
    quelle = KLASSEN[chip]["am2320"] if args.am2320 else KLASSEN[chip]
    bild = sorted(glob.glob(os.path.join(ROOT, quelle["image"])))[-1]
    image_aktuell = json.loads(box.get("/json"))["System"].get("Binary Filename", "")
    if os.path.basename(bild).removesuffix(".bin") != image_aktuell:
        sys.exit(f"FEHLER: Box laeuft mit {image_aktuell}, fuer diese Variante muss {os.path.basename(bild)} drauf sein.")
    basis = os.path.join(ROOT, quelle["basis"])
    lade_hoch(box, basis, "config.dat")
    sende(port, "Reboot")
    time.sleep(10)
    box = http_bereit(port, warte_ip(port))
    from espeasy_autoconfig import I2C_PLUGINS, lies_task
    tasks, gpio = [], None
    for t in json.loads(box.get("/json"))["Sensors"]:
        nr = t["TaskNumber"]
        _, felder = lies_task(box, nr)
        plugin = int(felder.get("TDNUM", "0") or 0)
        eintrag = {"nr": nr, "name": t["TaskName"], "typ": t["Type"]}
        if plugin == PLUGIN_SYSINFO:
            continue
        if plugin == PLUGIN_DS18B20:
            eintrag["art"] = "ds18b20"
            gpio = int(felder.get("taskdevicepin1", "0")) if gpio is None else gpio
        elif plugin in I2C_PLUGINS:
            eintrag.update(art="i2c", adressen=sorted(I2C_PLUGINS[plugin]))
        else:
            eintrag["art"] = "frage"
        tasks.append(eintrag)
        print(f"  Task {nr:2} {t['TaskName']:<14} {eintrag['art']}")

    schritt("3/3 Manifest")
    relativ = lambda p: os.path.relpath(p, ROOT).replace(os.sep, "/")
    eintrag = lambda p: {"pfad": relativ(p), "sha256": sha256(p)}
    pfad = os.path.join(ROOT, "tools/oh-flasher/manifest.json")
    teil = {"firmware": eintrag(bild), "basis_config": eintrag(basis), "onewire_gpio": gpio or 0, "tasks": tasks}
    manifest = {}
    if os.path.exists(pfad):
        with open(pfad, encoding="utf-8") as f:
            manifest = json.load(f)
    if args.am2320:
        manifest["am2320"] = teil
    else:
        manifest.update(teil)
    manifest.update({
        "version": 1,
        "erzeugt": f"{datetime.datetime.now():%Y-%m-%d %H:%M}",
        "ressourcen": [eintrag(os.path.join(RESSOURCEN, d)) for d in ["header.txt", "footer.txt", *DASHBOARD_DATEIEN]],
    })
    with open(pfad, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
        f.write("\n")
    print(f"  {relativ(pfad)}")
    print("\nKundenpaket fertig. Pruefen und auf devel committen (manifest.json).")


def sha256(pfad):
    import hashlib
    h = hashlib.sha256()
    with open(pfad, "rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def main():
    parser = argparse.ArgumentParser(description="Testablauf fuer openandhome-Sensorboxen.")
    parser.add_argument("aktion", choices=["aufsetzen", "pruefen", "dashboard", "beenden", "kundenpaket"])
    parser.add_argument("--port", default="/dev/ttyUSB0")
    parser.add_argument("--host", help="IP der Box (Standard: per USB gelesen)")
    parser.add_argument("--ohne-flash", action="store_true", help="aufsetzen ohne Sicherung/Flashen")
    parser.add_argument("--zabbix", metavar="SERVER", help="aufsetzen (Professional): Zabbix-Controller mit diesem Server einschalten")
    parser.add_argument("--am2320", action="store_true",
                        help="aufsetzen: AM2320-Variante erzwingen; kundenpaket: AM2320-Teil des Manifests erzeugen")
    parser.add_argument("--wlan-datei", help="Datei mit SSID (Zeile 1) und Key (Zeile 2)")
    parser.add_argument("--syslog-ip", default="192.168.9.4")
    parser.add_argument("--wlan-reset", action="store_true", help="beenden: WLAN ohne Rueckfrage zuruecksetzen")
    parser.add_argument("--ohne-wlan-reset", action="store_true", help="beenden: WLAN nicht zuruecksetzen")
    args = parser.parse_args()

    if args.aktion == "aufsetzen":
        aufsetzen(args)
        return
    if args.aktion == "beenden":
        beenden(args)
        return
    if args.aktion == "kundenpaket":
        kundenpaket(args)
        return
    ip = args.host or usb_ip(args.port)
    if not ip:
        sys.exit("FEHLER: IP nicht per USB lesbar - --host angeben.")
    box = http_bereit(args.port, ip)
    if args.aktion == "dashboard":
        dashboard_hochladen(box)
    else:
        ok, _ = pruefe(box, args.port)
        sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()

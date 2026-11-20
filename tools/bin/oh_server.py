#!/usr/bin/env python3
"""Sensorboxen im Netzwerk finden und an einen openandhome-Server senden lassen.

Plan: plans/server-ansible.md, Abschnitt 6 (Betriebsart a). Nutzt nur die
Python-Standardbibliothek (auch im portablen Python der ohtoolbox).

Je Box (per HTTP, wie ein Browser - es werden nur die noetigen Felder geaendert):
  - Controller 1 (C005 MQTT) an, Server, Port 1883, Benutzer "sensorbox", Passwort,
    Themen openandhome/%sysname%/...
  - bei jedem aktiven Task mit Messwerten "Send to Controller 1"
  - Syslog an den Server (UDP 514, Level Info)
  - Pruefung: die Box meldet sich beim Server (MQTT-Status "Connected").
    Zuerst mit dem Servernamen; klappt das nicht, mit der IP.

Beispiele:
  tools/bin/oh_server.py suchen [--netz 192.168.2.0/24]
  tools/bin/oh_server.py verbinden --server openandhome-server1 [--netz ...] [--box 192.168.2.173]
  tools/bin/oh_server.py trennen --box 192.168.2.173
Passwort: Umgebungsvariable OH_MQTT_PASSWORT, sonst Abfrage (Uebergabeblatt, Benutzer "sensorbox").
"""
import argparse
import concurrent.futures
import getpass
import ipaddress
import json
import os
import socket
import struct
import sys
import time
import urllib.error
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from espeasy_syslog import ADMIN_PASSWORT, LEVEL_INFO, SYSLOG_PORT, Box, FormParser  # noqa: E402

MQTT_PORT = 1883
MQTT_BENUTZER = "sensorbox"
CONTROLLER = 1
PUBLISH = "openandhome/%sysname%/%tskname%/%valname%"
SUBSCRIBE = "openandhome/%sysname%/#"
EINSTELLUNGEN = os.path.join(os.path.expanduser("~"), ".config", "openandhome", "server.json")

HINWEIS = """
So aendern Sie die Einstellung von Hand in der Weboberflaeche einer Sensorbox
(Browser: http://<IP-der-Box>):

 1. Controllers -> bei Nr. 1 "Edit" (Home Assistant (openHAB) MQTT):
    Enabled anhaken, Locate Controller "Use IP address" (oder "Use Hostname"),
    Controller IP bzw. Hostname: {server}, Controller Port: 1883,
    Controller User: sensorbox, Controller Password: siehe Uebergabeblatt,
    Controller Subscribe: openandhome/%sysname%/#,
    Controller Publish:   openandhome/%sysname%/%tskname%/%valname%  -> Submit.
 2. Devices -> bei jedem Fuehler/Sensor "Edit" -> unter "Data Acquisition"
    "Send to Controller 1" anhaken -> Submit.
 3. Tools -> Advanced -> Syslog IP: {server_ip}, Syslog UDP Port: 514,
    Syslog Log Level: Info -> Submit.

Zurueck zum Betrieb ohne Server: Controller 1 "Enabled" abhaken und Syslog IP leeren.
Jede Box braucht einen eigenen Namen (Toolbox "g" oder Config -> Unit Name),
sonst landen die Werte mehrerer Boxen unter demselben Namen.
"""


# --- Netzwerksuche ---------------------------------------------------------------

def eigene_netze():
    """/24-Netz der eigenen IP (Weg zum Internet; es wird nichts gesendet)."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("192.0.2.1", 9))
            ip = s.getsockname()[0]
        return [ipaddress.ip_network(f"{ip}/24", strict=False)]
    except OSError:
        return []


def pruefe_box(ip, timeout=1.5):
    """Liefert Kurzinfo, wenn unter ip eine ESPEasy-Box antwortet, sonst None."""
    try:
        with urllib.request.urlopen(f"http://{ip}/json", timeout=timeout) as r:
            d = json.loads(r.read().decode("utf-8", "replace"))
        s = d.get("System", {})
        image = s.get("Binary Filename", "")
        if "ESP_Easy" not in image and "Build" not in s:
            return None
        return {"ip": str(ip), "name": s.get("Unit Name", "?"), "unit": s.get("Unit Number", "?"), "image": image,
                "tasks": [t for t in d.get("Sensors", []) if t.get("TaskEnabled") == "true" and t.get("TaskValues")]}
    except (OSError, ValueError):
        return None


def finde_boxen(netze, ausgabe=print):
    hosts = [str(h) for n in netze for h in n.hosts()]
    ausgabe(f"Suche Sensorboxen in {', '.join(map(str, netze))} ({len(hosts)} Adressen) ...")
    with concurrent.futures.ThreadPoolExecutor(max_workers=64) as pool:
        boxen = [b for b in pool.map(pruefe_box, hosts) if b]
    boxen.sort(key=lambda b: ipaddress.ip_address(b["ip"]))
    namen = [b["name"] for b in boxen]
    for b in boxen:
        b["doppelt"] = namen.count(b["name"]) > 1
    return boxen


def zeige_boxen(boxen, ausgabe=print):
    if not boxen:
        ausgabe("Keine Sensorbox gefunden.")
    for i, b in enumerate(boxen, 1):
        typ = "Typ 2026" if "ESP32" in b["image"] else "Typ 2025" if "ESP8266" in b["image"] else "?"
        warn = "  << Name doppelt!" if b["doppelt"] else ""
        ausgabe(f" {i:2}) {b['name']:<16} {b['ip']:<15} {typ:<12} {len(b['tasks'])} Sensor(en){warn}")


# --- MQTT (minimal, nur fuer die Pruefung) -----------------------------------------

def _laenge(n):
    out = b""
    while True:
        byte, n = n % 128, n // 128
        out += bytes([byte | (0x80 if n else 0)])
        if not n:
            return out


def _str(s):
    b = s.encode()
    return struct.pack("!H", len(b)) + b


def _lies_paket(sock):
    kopf = sock.recv(1)
    if not kopf:
        raise OSError("Verbindung geschlossen")
    mult, laenge = 1, 0
    while True:
        b = sock.recv(1)[0]
        laenge += (b & 0x7F) * mult
        mult *= 128
        if not b & 0x80:
            break
    daten = b""
    while len(daten) < laenge:
        teil = sock.recv(laenge - len(daten))
        if not teil:
            raise OSError("Verbindung geschlossen")
        daten += teil
    return kopf[0], daten


def mqtt_lies(server, passwort, thema, sekunden=5, benutzer=MQTT_BENUTZER):
    """Abonniert thema und liefert {Thema: Text} aller Meldungen (inkl. gespeicherter) in `sekunden`."""
    ergebnis = {}
    with socket.create_connection((server, MQTT_PORT), timeout=10) as s:
        variabel = _str("MQTT") + bytes([4, 0xC2]) + struct.pack("!H", 30)
        nutz = _str(f"oh-toolbox-{os.getpid()}") + _str(benutzer) + _str(passwort)
        s.sendall(b"\x10" + _laenge(len(variabel + nutz)) + variabel + nutz)
        typ, daten = _lies_paket(s)
        if typ >> 4 != 2 or daten[1] != 0:
            raise PermissionError("MQTT-Anmeldung abgelehnt (Passwort pruefen)")
        sub = struct.pack("!H", 1) + _str(thema) + b"\x00"
        s.sendall(b"\x82" + _laenge(len(sub)) + sub)
        ende = time.time() + sekunden
        while time.time() < ende:
            s.settimeout(max(0.1, ende - time.time()))
            try:
                typ, daten = _lies_paket(s)
            except socket.timeout:
                break
            if typ >> 4 == 3:
                n = struct.unpack("!H", daten[:2])[0]
                rest = daten[2 + n:]
                if (typ >> 1) & 3:
                    rest = rest[2:]
                ergebnis[daten[2:2 + n].decode("utf-8", "replace")] = rest.decode("utf-8", "replace")
        s.sendall(b"\xe0\x00")
    return ergebnis


def mqtt_loesche(server, passwort, thema, benutzer=MQTT_BENUTZER):
    """Loescht eine gespeicherte (retained) Meldung - sonst taeuscht ein alter Status 'Connected'."""
    with socket.create_connection((server, MQTT_PORT), timeout=10) as s:
        variabel = _str("MQTT") + bytes([4, 0xC2]) + struct.pack("!H", 30)
        nutz = _str(f"oh-toolbox-{os.getpid()}") + _str(benutzer) + _str(passwort)
        s.sendall(b"\x10" + _laenge(len(variabel + nutz)) + variabel + nutz)
        typ, daten = _lies_paket(s)
        if typ >> 4 != 2 or daten[1] != 0:
            raise PermissionError("MQTT-Anmeldung abgelehnt (Passwort pruefen)")
        pub = _str(thema)
        s.sendall(b"\x31" + _laenge(len(pub)) + pub)
        s.sendall(b"\xe0\x00")


def meldet_sich(server, passwort, name, sekunden=45):
    """Wartet, bis die Box ihren Status 'Connected' beim Server hinterlegt hat."""
    thema = f"openandhome/{name}/status/LWT"
    ende = time.time() + sekunden
    while time.time() < ende:
        if mqtt_lies(server, passwort, thema, sekunden=3).get(thema) == "Connected":
            return True
        time.sleep(3)
    return False


# --- Box einstellen ----------------------------------------------------------------

def _formular(box, pfad):
    f = FormParser()
    try:
        f.feed(box.get(pfad))
    except urllib.error.HTTPError as e:
        if e.code == 401:
            raise PermissionError("Box lehnt das Admin-Passwort ab (geaendert? --box-passwort angeben "
                                  "oder per Toolbox Menue 7 zuruecksetzen)") from e
        raise
    if "password" in f.felder and len(f.felder) <= 2:
        raise PermissionError("Box verlangt das Admin-Passwort der Weboberflaeche")
    return f.felder


def setze_controller(box, ziel, passwort, per_name):
    p = f"/controllers?index={CONTROLLER}"
    felder = _formular(box, p)
    if felder.get("protocol") != "5":
        raise ValueError(f"Controller {CONTROLLER} ist kein MQTT-Controller (C005) - nichts geaendert")
    felder.update(edit="1", controllerenabled="on", controllerport=str(MQTT_PORT), controlleruser=MQTT_BENUTZER,
                  controllerpassword=passwort, controllersubscribe=SUBSCRIBE, controllerpublish=PUBLISH)
    if per_name:
        felder.update(locatecontroller="1", controllerhostname=ziel)
        felder.pop("controllerip", None)
    else:
        felder.update(locatecontroller="0", controllerip=ziel)
        felder.pop("controllerhostname", None)
    box.post(p, felder)
    neu = _formular(box, p)
    soll = ("controllerhostname" if per_name else "controllerip")
    if neu.get("controllerenabled") != "on" or neu.get(soll) != ziel or neu.get("controlleruser") != MQTT_BENUTZER:
        raise RuntimeError("Box hat die Controller-Einstellung nicht uebernommen")


def setze_senden(box, tasks, an=True):
    """Send to Controller 1 bei allen aktiven Tasks mit Messwerten."""
    namen = []
    for t in tasks:
        p = f"/devices?index={t['TaskNumber']}&page=1"
        felder = _formular(box, p)
        if (felder.get(f"TDSD{CONTROLLER}") == "on") == an:
            namen.append(t["TaskName"])
            continue
        felder["edit"] = "1"
        if an:
            felder[f"TDSD{CONTROLLER}"] = "on"
        else:
            felder.pop(f"TDSD{CONTROLLER}", None)
        box.post(p, felder)
        if (_formular(box, p).get(f"TDSD{CONTROLLER}") == "on") != an:
            raise RuntimeError(f"Task {t['TaskName']}: 'Send to Controller' nicht uebernommen")
        namen.append(t["TaskName"])
    return namen


def setze_syslog(box, ip):
    felder = _formular(box, "/advanced")
    level = [n for n in felder if "syslog" in n.lower() and ("level" in n.lower() or "lvl" in n.lower())]
    if "syslogip" not in felder or len(level) != 1:
        raise RuntimeError("Syslog-Felder auf /advanced nicht gefunden")
    felder.update(edit="1", syslogip=ip or "0.0.0.0", syslogport=SYSLOG_PORT, **{level[0]: LEVEL_INFO if ip else "0"})
    box.post("/advanced", felder)
    neu = _formular(box, "/advanced")
    if neu.get("syslogip") not in ((ip,) if ip else ("", "0.0.0.0")):
        raise RuntimeError("Box hat die Syslog-Einstellung nicht uebernommen")


def server_ip(server):
    """IPv4 des Servers vom PC aus. Ohne Suchdomaene kennt der PC den nackten Namen oft nicht,
    der Router (DNS der Boxen) schon - daher auch .local (mDNS) und .fritz.box versuchen."""
    for name in [server] + ([f"{server}.local", f"{server}.fritz.box"] if "." not in server else []):
        try:
            return socket.gethostbyname(name)
        except OSError:
            continue
    raise SystemExit(f"FEHLER: Server '{server}' nicht gefunden - Name oder IP pruefen.")


def ist_ip(text):
    try:
        ipaddress.ip_address(text)
        return True
    except ValueError:
        return False


def verbinde(b, server, passwort, box_passwort=None, ausgabe=print):
    """Stellt eine Box auf den Server um und prueft, ob sie sich meldet. Liefert True/False."""
    ip = server_ip(server)
    ausgabe(f"\n{b['name']} ({b['ip']}):")
    try:
        box = Box(b["ip"], box_passwort or ADMIN_PASSWORT)
        versuche = [(server, True), (ip, False)] if not ist_ip(server) else [(ip, False)]
        for nr, (ziel, per_name) in enumerate(versuche):
            mqtt_loesche(ip, passwort, f"openandhome/{b['name']}/status/LWT")
            setze_controller(box, ziel, passwort, per_name)
            ausgabe(f"  MQTT-Controller: an, Server {ziel} ({'Name' if per_name else 'IP'})")
            if nr == 0:
                gesendet = setze_senden(box, b["tasks"])
                ausgabe(f"  Senden an Controller 1: {', '.join(gesendet) or '(keine Sensoren aktiv)'}")
                setze_syslog(box, ip)
                ausgabe(f"  Syslog: {ip}:514")
            ausgabe("  Warte, bis sich die Box beim Server meldet ...")
            if meldet_sich(ip, passwort, b["name"]):
                ausgabe(f"  OK - Box meldet sich beim Server{'' if not per_name else ' (per Name)'}.")
                if not per_name and not ist_ip(server):
                    ausgabe("  Hinweis: Der Servername ist im Netz der Box nicht aufloesbar, daher IP eingetragen.\n"
                            "  Richten Sie im Router eine feste IP (DHCP-Reservierung) fuer den Server ein.")
                return True
            if per_name:
                ausgabe("  Keine Meldung per Name - versuche IP ...")
        ausgabe("  FEHLER: Box meldet sich nicht beim Server (Netz/Firewall/Passwort pruefen).")
    except (OSError, ValueError, RuntimeError, PermissionError) as e:
        ausgabe(f"  FEHLER: {e}")
    return False


def trenne(b, box_passwort=None, ausgabe=print):
    ausgabe(f"\n{b['name']} ({b['ip']}):")
    try:
        box = Box(b["ip"], box_passwort or ADMIN_PASSWORT)
        p = f"/controllers?index={CONTROLLER}"
        felder = _formular(box, p)
        if felder.get("protocol") == "5":
            felder["edit"] = "1"
            felder.pop("controllerenabled", None)
            box.post(p, felder)
            ausgabe("  MQTT-Controller: aus")
        setze_syslog(box, "")
        ausgabe("  Syslog: aus")
        return True
    except (OSError, ValueError, RuntimeError, PermissionError) as e:
        ausgabe(f"  FEHLER: {e}")
        return False


# --- Einstellungen und Bedienung -------------------------------------------------

def lade_einstellungen():
    try:
        with open(EINSTELLUNGEN, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return {}


def speichere_einstellungen(daten):
    os.makedirs(os.path.dirname(EINSTELLUNGEN), exist_ok=True)
    with open(EINSTELLUNGEN, "w", encoding="utf-8") as f:
        json.dump(daten, f, indent=2)
    try:
        os.chmod(EINSTELLUNGEN, 0o600)
    except OSError:
        pass


def frage_passwort(server, gespeichert=None):
    if os.environ.get("OH_MQTT_PASSWORT"):
        return os.environ["OH_MQTT_PASSWORT"]
    if gespeichert:
        return gespeichert
    while True:
        pw = getpass.getpass(f"MQTT-Passwort fuer Benutzer 'sensorbox' (Uebergabeblatt): ").strip()
        try:
            mqtt_lies(server_ip(server), pw, "openandhome/-", sekunden=1)
            return pw
        except PermissionError:
            print("Passwort falsch - bitte erneut eingeben.")


def netze_aus(texte):
    netze = eigene_netze()
    for t in texte or []:
        n = ipaddress.ip_network(t.strip(), strict=False)
        if n not in netze:
            netze.append(n)
    return netze


def boxen_waehlen(boxen, eingabe):
    if eingabe.strip().lower() in ("", "a", "alle"):
        return boxen
    nummern = {int(x) for x in eingabe.replace(",", " ").split() if x.isdigit()}
    return [b for i, b in enumerate(boxen, 1) if i in nummern]


def menue(ausgabe=print):
    """Interaktiv (ohtoolbox): Server angeben, Boxen suchen, verbinden oder trennen."""
    e = lade_einstellungen()
    print("\n" + "=" * 60 + "\n Sensorboxen im Netzwerk an einen openandhome-Server senden\n" + "=" * 60)
    server = input(f"Server (Name oder IP) [{e.get('server', 'openandhome-server1')}]: ").strip() \
        or e.get("server", "openandhome-server1")
    ausgabe(f"Server {server} = {server_ip(server)}")
    extra = input(f"Weitere Netze durchsuchen, z. B. 192.168.2.0/24 [{' '.join(e.get('netze', [])) or 'keine'}]: ").strip()
    netze_text = extra.split() if extra else e.get("netze", [])
    passwort = frage_passwort(server, e.get("passwort"))
    boxen = finde_boxen(netze_aus(netze_text), ausgabe)
    zeige_boxen(boxen, ausgabe)
    if not boxen:
        return
    aktion = input("\nv) an den Server senden   t) vom Server trennen   Enter) zurueck: ").strip().lower()
    if aktion not in ("v", "t"):
        return
    auswahl = boxen_waehlen(boxen, input("Welche Boxen? Nummern oder Enter = alle: "))
    if aktion == "v":
        ok = [verbinde(b, server, passwort, ausgabe=ausgabe) for b in auswahl]
        ausgabe(f"\n{sum(ok)} von {len(ok)} Box(en) senden an den Server.")
        if input("Server und Passwort fuer das naechste Mal speichern? (j/n) [j]: ").strip().lower() in ("", "j"):
            speichere_einstellungen({"server": server, "netze": netze_text, "passwort": passwort})
    else:
        ok = [trenne(b, ausgabe=ausgabe) for b in auswahl]
        ausgabe(f"\n{sum(ok)} von {len(ok)} Box(en) getrennt.")
    ausgabe(HINWEIS.format(server=server, server_ip=server_ip(server)))
    if any(b["doppelt"] for b in auswahl):
        ausgabe("ACHTUNG: Mehrere Boxen haben denselben Namen - bitte umbenennen (Toolbox 'g').")


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("aktion", choices=["suchen", "verbinden", "trennen", "hinweis", "menue"])
    parser.add_argument("--server", default="openandhome-server1", help="Name oder IP des Servers")
    parser.add_argument("--netz", action="append", help="weiteres Netz, z. B. 192.168.2.0/24 (mehrfach)")
    parser.add_argument("--box", action="append", help="nur diese Box-IP (mehrfach), sonst alle gefundenen")
    parser.add_argument("--box-passwort", default=ADMIN_PASSWORT,
                        help=f"Admin-Passwort der Weboberflaeche (Standard: Werksvorgabe {ADMIN_PASSWORT})")
    args = parser.parse_args()

    if args.aktion == "menue":
        return menue()
    if args.aktion == "hinweis":
        return print(HINWEIS.format(server=args.server, server_ip=server_ip(args.server)))
    if args.box:
        boxen = [b for b in (pruefe_box(ip, timeout=5) for ip in args.box) if b]
        for b in boxen:
            b["doppelt"] = False
    else:
        boxen = finde_boxen(netze_aus(args.netz))
    zeige_boxen(boxen)
    if args.aktion == "suchen" or not boxen:
        return
    if args.aktion == "verbinden":
        passwort = frage_passwort(args.server)
        ok = [verbinde(b, args.server, passwort, args.box_passwort) for b in boxen]
        print(f"\n{sum(ok)} von {len(ok)} Box(en) senden an den Server.")
    else:
        ok = [trenne(b, args.box_passwort) for b in boxen]
        print(f"\n{sum(ok)} von {len(ok)} Box(en) getrennt.")
    print(HINWEIS.format(server=args.server, server_ip=server_ip(args.server)))
    sys.exit(0 if all(ok) else 1)


if __name__ == "__main__":
    main()

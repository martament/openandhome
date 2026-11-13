#!/usr/bin/env python3
"""Gemeinsame Ablaeufe der Endanwender-Werkzeuge (Toolbox und Flasher).

Dateien (Firmware, Basis-config, Regeln, Dashboard) kommen laut Manifest aus dem
Repo (GitHub, Branch master) bzw. aus der Offline-Kopie im ZIP; das Manifest wird
aus tools/bin/oh_klassen.py erzeugt - dieselbe Quelle wie die Werkstatt.
"""

import getpass
import hashlib
import json
import os
import subprocess
import sys
import time
import urllib.parse
import urllib.request

import serial.tools.list_ports

from espeasy_autoconfig import autokonfiguration, i2c_scan
from espeasy_testbox import (dashboard_hochladen, http_bereit, lade_hoch, sende, setze_zugriff, usb_ip,
                             warte_ip, wlan_verbinden)

GITHUB = "https://raw.githubusercontent.com/martament/openandhome/master/"
MANIFEST = "tools/ohtoolbox/manifest.json"
AM2320_ADRESSE = 0x5C


# --- Ein-/Ausgabe ---
def gruen(text):
    print(f"\033[32m{text}\033[0m")


def rot(text):
    print(f"\033[31m{text}\033[0m")


def ja(text, standard=False):
    antwort = input(f"{text} (j/n) [{'j' if standard else 'n'}]: ").strip().lower()
    return antwort.startswith(("j", "y")) if antwort else standard


def weiter():
    input("Weiter mit Enter ...")


def finde_port():
    ports = sorted(p.device for p in serial.tools.list_ports.comports()
                   if p.vid is not None or "USB" in p.device or "ACM" in p.device)
    if not ports:
        sys.exit("Kein Sensor gefunden. Bitte den Sensor per USB anschliessen und neu starten.")
    return ports[-1]     # zuletzt angeschlossener Port


# --- Dateien aus dem Repo ---
class Quelle:
    """Holt Dateien von GitHub (master), aus der Repo-Arbeitskopie oder aus der Offline-Kopie im ZIP
    und prueft SHA256 gegen das Manifest."""

    def __init__(self, art, paket):
        self.art, self.paket = art, paket
        self.online = art == "github"
        self.repo = os.path.abspath(os.path.join(paket, "..", ".."))
        self.cache = os.path.join(paket, "cache")
        self._manifest = None

    def _lade(self, pfad):
        if self.art == "lokal":
            with open(os.path.join(self.repo, pfad), "rb") as f:
                return f.read()
        if self.online:
            try:
                with urllib.request.urlopen(GITHUB + urllib.parse.quote(pfad), timeout=30) as antwort:
                    return antwort.read()
            except OSError as e:
                print(f"Internet nicht erreichbar ({e.__class__.__name__}) - nehme mitgelieferte Dateien.")
                self.online = False
        with open(os.path.join(self.paket, "daten", pfad), "rb") as f:
            return f.read()

    def manifest(self):
        if self._manifest is None:
            self._manifest = json.loads(self._lade(MANIFEST).decode("utf-8"))
        return self._manifest

    def datei(self, eintrag, unterordner=""):
        daten = self._lade(eintrag["pfad"])
        if hashlib.sha256(daten).hexdigest() != eintrag["sha256"]:
            sys.exit(f"FEHLER: Pruefsumme von {eintrag['pfad']} stimmt nicht - Abbruch.")
        ziel = os.path.join(self.cache, unterordner, os.path.basename(eintrag["pfad"]))
        os.makedirs(os.path.dirname(ziel), exist_ok=True)
        with open(ziel, "wb") as f:
            f.write(daten)
        return ziel

    def ressourcen_ordner(self):
        pfade = [self.datei(r, "ressourcen") for r in self.manifest()["ressourcen"]]
        return os.path.dirname(pfade[0])


# --- Box ---
def box_typ(port):
    """'ESP32' (Professional), 'ESP8266' (Standalone) oder None - per Konsole, ohne Neustart."""
    antwort = " ".join(sende(port, "logentry,%sysbuild_filename%", wartezeit=2))
    for chip in ("ESP32", "ESP8266"):
        if chip in antwort:
            return chip
    return None


def image_name(port):
    for z in sende(port, "logentry,%sysbuild_filename%", wartezeit=2):
        if z.startswith("ESP_Easy"):
            return z.strip()
    return ""


def klasse(quelle, chip, port=None, am2320=None):
    """Manifest-Teil der Box-Klasse; bei Standalone mit AM2320 die AM2320-Variante."""
    k = dict(quelle.manifest()["klassen"][chip])
    if "am2320" in k:
        if am2320 is None and port:
            # Der AM2320 schlaeft und antwortet oft erst beim zweiten Scan
            am2320 = any(AM2320_ADRESSE in i2c_scan(port) for _ in range(2))
        if am2320:
            k.update(k["am2320"])
    return k


def poe_warnung():
    rot("\nSensorbox Professional: USB und Netzwerkkabel (PoE) nie gleichzeitig anschliessen!")
    rot("Das Netzwerkkabel muss abgezogen sein - die Box wird ueber USB versorgt.")
    return ja("Ist das Netzwerkkabel abgezogen?")


def wlan_eingeben():
    ssid = input("Name Ihres WLANs (SSID): ").strip()
    key = getpass.getpass("WLAN-Passwort (Eingabe unsichtbar): ")
    return ssid, key


def wlan_loeschen(port):
    sende(port, "WifiSSID ssid", "WifiKey wpakey", "WifiSSID2 ssid", "WifiKey2 wpakey", "Save")


def ins_netz(port, chip):
    """Sorgt fuer eine Netzverbindung (fuer die Weboberflaeche). Liefert True, wenn das WLAN nur
    voruebergehend gesetzt wurde (Professional) und danach wieder geloescht werden soll."""
    if usb_ip(port):
        return False
    if chip == "ESP32":
        print("Fuer die Einrichtung verbindet sich die Box kurz mit Ihrem WLAN; die Daten werden danach geloescht.")
    else:
        print("Fuer die Einrichtung muss der Sensor in Ihrem WLAN sein.")
    wlan_verbinden(port, *wlan_eingeben())
    return chip == "ESP32"


def abschluss(port, chip, box, temporaer):
    if temporaer:
        wlan_loeschen(port)
        gruen("\nFertig. Die WLAN-Daten sind wieder geloescht.")
        print("Ziehen Sie jetzt ZUERST das USB-Kabel ab und stecken Sie DANACH das Netzwerkkabel (PoE) an.")
        print("Die IP-Adresse zeigt das Display bzw. Ihr Router (Geraet 'Sensorbox1').")
    elif box:
        gruen(f"\nFertig. Ihr Sensor ist erreichbar unter {box.basis}/openandhome.esp")


# --- esptool (mitgeliefert im portablen Python) ---
def esptool(port, *argumente, site_packages=None):
    umgebung = dict(os.environ)
    if site_packages and os.path.isdir(site_packages):
        umgebung["PYTHONPATH"] = site_packages
    befehl = [sys.executable, "-m", "esptool", "--port", port, "--baud", "460800", *argumente]
    if subprocess.run(befehl, env=umgebung).returncode != 0:
        sys.exit("FEHLER beim Flashen. Sensor neu anstecken und noch einmal versuchen.")


# --- Ablaeufe ---
def sensoren_einrichten(port, k, ressourcen):
    """Sensoren erkennen und einschalten, Fuehleradressen, Display, Dashboard, Zugriffsbereich."""
    box = http_bereit(port, warte_ip(port))
    print("Erkenne angeschlossene Sensoren ...")
    nicht_erkennbar = autokonfiguration(box, port, ow_gpios=k.get("ow_gpios"), leise=True)
    an = [n for n in nicht_erkennbar if ja(f"Ist '{n}' an Ihrem Sensor angeschlossen?")]
    aus = [n for n in nicht_erkennbar if n not in an]
    autokonfiguration(box, port, an, aus, anwenden=True, ow_gpios=k.get("ow_gpios"), leise=True)
    dashboard_hochladen(box, ablage=os.path.dirname(ressourcen), ressourcen=ressourcen)
    setze_zugriff(box)
    aktiv = [t["TaskName"] for t in json.loads(box.get("/json"))["Sensors"]
             if t["TaskEnabled"] == "true" and "System" not in t["Type"]]
    print("Aktiv:", ", ".join(aktiv) or "keine Sensoren")
    return box


def grundkonfiguration(port, quelle, k, chip, temporaer=None):
    """Basis-config + Regeln hochladen, Neustart, Sensoren einrichten (Einstellungen werden ersetzt).

    temporaer: Ergebnis eines vorherigen ins_netz(); None = hier pruefen."""
    ressourcen = quelle.ressourcen_ordner()
    if temporaer is None:
        temporaer = ins_netz(port, chip)
    box = http_bereit(port, warte_ip(port))
    # Zugriff dauerhaft erlauben: ClearAccessBlock gilt nur bis die Box ihre Einstellungen neu laedt
    # (passiert beim config.dat-Upload) - danach waere der Regel-Upload gesperrt
    setze_zugriff(box)
    lade_hoch(box, quelle.datei(k["basis_config"]), "config.dat")
    if "regeln" in k:
        # Zeit nur lokal: Regeln schalten NTP mit Router / 192.168.178.1 ein
        lade_hoch(box, quelle.datei(k["regeln"], "regeln"), "rules1.txt")
    sende(port, "Reboot")
    time.sleep(10)
    sende(port, "UseNTP,0", "Save")     # ab Werk kein Zeitserver im Internet
    box = sensoren_einrichten(port, k, ressourcen)
    abschluss(port, chip, box, temporaer)


def sensoren_neu(port, quelle, k, chip):
    """Nur Sensoren neu erkennen - Einstellungen bleiben."""
    ressourcen = quelle.ressourcen_ordner()
    temporaer = ins_netz(port, chip)
    box = sensoren_einrichten(port, k, ressourcen)
    abschluss(port, chip, box, temporaer)


def neu_aufspielen(port, quelle, k, chip, site_packages):
    """Loeschen, aktuelles Image schreiben, Ethernet (Professional), danach Grundkonfiguration."""
    firmware = quelle.datei(k["firmware"])
    esptool(port, "erase_flash", site_packages=site_packages)
    esptool(port, "write_flash", *k["flash"], firmware, site_packages=site_packages)
    print("Warte auf den Start des Sensors ...")
    time.sleep(20)
    if "ethernet" in k:
        # Ethernet (Olimex ESP32-POE) per USB einrichten - geht ohne Netzwerk
        sende(port, f"NetworkImportConfig,3,{k['ethernet']}", "Save")


def firmware_update(port, quelle, k, site_packages):
    """Nur die Firmware erneuern - Einstellungen und Dateisystem bleiben."""
    if "firmware_update" in k:
        # ESP32: nur die App nach app0, otadata loeschen -> startet app0; NVS/Ethernet bleiben
        esptool(port, "write_flash", *k["update"], quelle.datei(k["firmware_update"]), site_packages=site_packages)
        esptool(port, "erase_region", *k["update_loeschen"], site_packages=site_packages)
    else:
        esptool(port, "write_flash", *k["update"], quelle.datei(k["firmware"]), site_packages=site_packages)

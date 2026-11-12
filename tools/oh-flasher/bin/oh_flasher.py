#!/usr/bin/env python3
"""openandhome-Flasher fuer Temperatursensoren (Standalone, ESP8266).

Laedt die freigegebene Firmware und das Basis-Dateisystem aus dem
openandhome-Repo (GitHub, Branch master), prueft SHA256, flasht den Sensor
und erkennt die angeschlossenen Sensoren selbst. Mit WLAN richtet er auch
Fuehler-Adressen, Display und Dashboard automatisch ein (Grundeinstellungen
per HTTP). Ohne WLAN braucht er ein Dateisystem-Image im Manifest.
Ohne Internet nimmt er die mitgelieferten Dateien.

Start unter Windows: start_flasher.bat. Unter Linux (Werkstatt-Test):
  python3 tools/oh-flasher/bin/oh_flasher.py [--port /dev/ttyUSB0] [--quelle lokal]
"""

import argparse
import getpass
import hashlib
import json
import os
import subprocess
import sys
import time
import urllib.parse
import urllib.request

HIER = os.path.dirname(os.path.abspath(__file__))
FLASHER = os.path.dirname(HIER)                       # .../oh-flasher
REPO = os.path.abspath(os.path.join(FLASHER, "..", ".."))
GITHUB = "https://raw.githubusercontent.com/martament/openandhome/master/"
CACHE = os.path.join(FLASHER, "cache")
DATEN = os.path.join(FLASHER, "daten")                # Offline-Kopie im ZIP
SITE_PACKAGES = os.path.join(HIER, "pythonportable", "Lib", "site-packages")

# Werkstatt-Module: im ZIP unter bin/lib, im Repo unter tools/bin
sys.path[:0] = [os.path.join(HIER, "lib"), os.path.join(REPO, "tools", "bin")]
import serial  # noqa: E402
import serial.tools.list_ports  # noqa: E402
from espeasy_autoconfig import autokonfiguration, i2c_scan, oeffne  # noqa: E402
from espeasy_testbox import (dashboard_hochladen, http_bereit, lade_hoch, sende, setze_zugriff, usb_ip,  # noqa: E402
                             warte_ip, wlan_verbinden)  # noqa: E402


def gruen(text):
    print(f"\033[32m{text}\033[0m")


def ja(text, standard=False):
    antwort = input(f"{text} (j/n) [{'j' if standard else 'n'}]: ").strip().lower()
    return antwort.startswith(("j", "y")) if antwort else standard


def finde_port():
    ports = sorted(p.device for p in serial.tools.list_ports.comports()
                   if p.vid is not None or "USB" in p.device or "ACM" in p.device)
    if not ports:
        sys.exit("Kein Sensor gefunden. Bitte den Sensor per USB anschliessen und neu starten.")
    return ports[-1]     # wie bisher: zuletzt angeschlossener Port


# --- Dateien aus dem Repo ---
class Quelle:
    """Holt Dateien von GitHub (master) bzw. lokal und prueft SHA256 gegen das Manifest."""

    def __init__(self, art):
        self.art = art
        self.online = art == "github"
        os.makedirs(CACHE, exist_ok=True)

    def _lade(self, pfad):
        if self.art == "lokal":
            with open(os.path.join(REPO, pfad), "rb") as f:
                return f.read()
        if self.online:
            try:
                with urllib.request.urlopen(GITHUB + urllib.parse.quote(pfad), timeout=30) as antwort:
                    return antwort.read()
            except OSError as e:
                print(f"Internet nicht erreichbar ({e.__class__.__name__}) - nehme mitgelieferte Dateien.")
                self.online = False
        with open(os.path.join(DATEN, pfad), "rb") as f:
            return f.read()

    def manifest(self):
        return json.loads(self._lade("tools/oh-flasher/manifest.json").decode("utf-8"))

    def datei(self, eintrag, unterordner=""):
        daten = self._lade(eintrag["pfad"])
        if hashlib.sha256(daten).hexdigest() != eintrag["sha256"]:
            sys.exit(f"FEHLER: Pruefsumme von {eintrag['pfad']} stimmt nicht - Abbruch.")
        ziel = os.path.join(CACHE, unterordner, os.path.basename(eintrag["pfad"]))
        os.makedirs(os.path.dirname(ziel), exist_ok=True)
        with open(ziel, "wb") as f:
            f.write(daten)
        return ziel


# --- esptool ---
def esptool(port, *argumente):
    umgebung = dict(os.environ)
    if os.path.isdir(SITE_PACKAGES):
        umgebung["PYTHONPATH"] = SITE_PACKAGES
    befehl = [sys.executable, "-m", "esptool", "--port", port, "--baud", "460800", *argumente]
    if subprocess.run(befehl, env=umgebung).returncode != 0:
        sys.exit("FEHLER beim Flashen. Sensor neu anstecken und noch einmal versuchen.")


def erkenne_chip(port):
    """'ESP8266' (Standalone) oder 'ESP32' (Professional)."""
    umgebung = dict(os.environ, PYTHONPATH=SITE_PACKAGES) if os.path.isdir(SITE_PACKAGES) else None
    ausgabe = subprocess.run([sys.executable, "-m", "esptool", "--port", port, "chip_id"],
                             capture_output=True, text=True, env=umgebung).stdout
    if "ESP32" in ausgabe:
        return "ESP32"
    if "ESP8266" in ausgabe:
        return "ESP8266"
    sys.exit("Kein openandhome-Sensor erkannt. Sensor neu anstecken und noch einmal versuchen.")


def poe_warnung():
    print("\n\033[31mSensorbox Professional: USB und Netzwerkkabel (PoE) nie gleichzeitig anschliessen!\033[0m")
    print("\033[31mDas Netzwerkkabel muss jetzt abgezogen sein - die Box wird ueber USB versorgt.\033[0m")
    return ja("Ist das Netzwerkkabel abgezogen?")


def wlan_eingeben():
    ssid = input("Name Ihres WLANs (SSID): ").strip()
    key = getpass.getpass("WLAN-Passwort (Eingabe unsichtbar): ")
    return ssid, key


def wlan_loeschen(port):
    sende(port, "WifiSSID ssid", "WifiKey wpakey", "WifiSSID2 ssid", "WifiKey2 wpakey", "Save")


def professional_ende():
    gruen("\nFertig. Die WLAN-Daten sind wieder geloescht.")
    print("Ziehen Sie jetzt ZUERST das USB-Kabel ab und stecken Sie DANACH das Netzwerkkabel (PoE) an.")
    print("Die IP-Adresse zeigt das Display bzw. Ihr Router (Geraet 'Sensorbox1').")


def sensoren_einrichten(port, manifest, ressourcen):
    """Sensoren erkennen, Dashboard, Zugriffsbereich (Box ist im WLAN)."""
    box = http_bereit(port, warte_ip(port))
    an, aus = [], []
    for t in manifest["tasks"]:
        if t["art"] == "frage":
            (an if ja(f"Ist '{t['name']}' ({t['typ']}) an Ihrem Sensor angeschlossen?") else aus).append(t["name"])
    autokonfiguration(box, port, an, aus, anwenden=True, ow_gpios=manifest.get("ow_gpios"))
    dashboard_hochladen(box, ablage=CACHE, ressourcen=os.path.dirname(ressourcen[0]))
    setze_zugriff(box)
    return box


# --- Ablaeufe ---
def neu_aufsetzen(port, quelle):
    manifest = quelle.manifest()
    chip = erkenne_chip(port)
    if chip == "ESP32":
        if "professional" not in manifest:
            sys.exit("Fuer die Sensorbox Professional gibt es in diesem Stand keine Dateien - bitte Support kontaktieren.")
        if not poe_warnung():
            return
        manifest = dict(manifest, **manifest["professional"])
        print("Fuer die Einrichtung verbindet sich die Box kurz mit Ihrem WLAN; die Daten werden danach geloescht.")
    print(f"Freigegebener Stand vom {manifest['erzeugt']}: {os.path.basename(manifest['firmware']['pfad'])}")
    firmware = quelle.datei(manifest["firmware"])
    ressourcen = [quelle.datei(r, "ressourcen") for r in manifest["ressourcen"]]
    ssid, key = wlan_eingeben()
    if not ja("Der Sensor wird vollstaendig geloescht und neu aufgesetzt. Weiter?", True):
        return

    gruen("\n1/4 Loesche den Sensor ...")
    esptool(port, "erase_flash")
    gruen("2/4 Schreibe Firmware ...")
    if chip == "ESP32":
        esptool(port, "write_flash", "0x0", firmware)
    else:
        esptool(port, "write_flash", "--flash_size", "4MB", "0x0", firmware)
    print("Warte auf den Start des Sensors ...")
    time.sleep(20)
    if chip == "ESP32":
        # Ethernet (Olimex ESP32-POE) per USB einrichten - geht ohne Netzwerk
        sende(port, f"NetworkImportConfig,3,{manifest['ethernet']}", "Save")

    gruen("3/4 Verbinde mit Ihrem WLAN und lade die Grundeinstellungen ...")
    wlan_verbinden(port, ssid, key)
    # Der AM2320 braucht ein anderes Image; er schlaeft und antwortet oft erst beim zweiten Scan
    if chip == "ESP8266" and "am2320" in manifest and any(0x5C in i2c_scan(port) for _ in range(2)):
        print("  AM2320 erkannt - spiele die passende Firmware ein (Einstellungen bleiben) ...")
        manifest = dict(manifest, **manifest["am2320"])
        esptool(port, "write_flash", "--flash_size", "4MB", "0x0", quelle.datei(manifest["firmware"]))
        time.sleep(20)
    box = http_bereit(port, warte_ip(port))
    lade_hoch(box, quelle.datei(manifest["basis_config"]), "config.dat")
    if "regeln" in manifest:
        # Zeitserver-Rueckfall auf Router / 192.168.178.1
        lade_hoch(box, quelle.datei(manifest["regeln"], "regeln"), "rules1.txt")
    sende(port, "Reboot")
    time.sleep(10)

    gruen("4/4 Erkenne angeschlossene Sensoren und richte sie ein ...")
    box = sensoren_einrichten(port, manifest, ressourcen)
    if chip == "ESP32":
        wlan_loeschen(port)
        professional_ende()
    else:
        gruen(f"\nFertig. Ihr Sensor ist erreichbar unter {box.basis}")


def sensoren_neu(port, quelle):
    """Sensoren neu erkennen, Einstellungen bleiben (z. B. nach Tausch oder Erweiterung eines Fuehlers)."""
    manifest = quelle.manifest()
    chip = erkenne_chip(port)
    if chip == "ESP32":
        if "professional" not in manifest or not poe_warnung():
            return
        manifest = dict(manifest, **manifest["professional"])
    time.sleep(15)                    # chip_id startet den Sensor neu
    if chip == "ESP8266" and "am2320" in manifest and any(0x5C in i2c_scan(port) for _ in range(2)):
        manifest = dict(manifest, **manifest["am2320"])
    ressourcen = [quelle.datei(r, "ressourcen") for r in manifest["ressourcen"]]
    temporaer = False
    if not usb_ip(port):
        print("Fuer die Erkennung muss der Sensor im WLAN sein.")
        temporaer = chip == "ESP32"
        wlan_verbinden(port, *wlan_eingeben())
    box = sensoren_einrichten(port, manifest, ressourcen)
    if temporaer:
        wlan_loeschen(port)
        professional_ende()
    else:
        gruen(f"\nFertig. Ihr Sensor ist erreichbar unter {box.basis}")


def nur_firmware(port, quelle):
    manifest = quelle.manifest()
    if erkenne_chip(port) == "ESP32":
        print("Fuer die Sensorbox Professional bitte 'Sensor neu aufsetzen' waehlen oder den Support kontaktieren.")
        return
    firmware = quelle.datei(manifest["firmware"])
    gruen("Schreibe neue Firmware. Ihre Einstellungen bleiben erhalten.")
    esptool(port, "write_flash", "--flash_size", "4MB", "0x0", firmware)
    gruen("Fertig.")


def debug(port):
    print("Ausgaben des Sensors (Beenden mit STRG+C):\n")
    for zeile in sende(port, "ResetFlashWriteCounter", "Settings", wartezeit=2):
        print(zeile)
    try:
        with oeffne(port, timeout=1) as s:
            while True:
                zeile = s.readline().decode("latin-1").rstrip()
                if zeile:
                    print(zeile)
    except KeyboardInterrupt:
        pass


def main():
    parser = argparse.ArgumentParser(description="openandhome-Flasher")
    parser.add_argument("--port", help="COM-Port bzw. /dev/ttyUSB0 (Standard: automatisch)")
    parser.add_argument("--quelle", choices=["github", "lokal", "offline"], default="github",
                        help="github = freigegebener Stand (master), lokal = Repo-Arbeitskopie, offline = ZIP-Inhalt")
    args = parser.parse_args()
    if os.name == "nt":
        os.system("")      # ANSI-Farben in der Windows-Konsole einschalten

    port = args.port or finde_port()
    quelle = Quelle(args.quelle)
    print("*" * 78)
    print(f" openandhome-Flasher - Sensor an {port}")
    print("*" * 78)
    print(" Notfall-Werkzeug. Fuer WLAN, Name, Zeitserver usw. bitte die openandhome-Toolbox nutzen.")
    print("*" * 78)
    print(" 1) Sensoren neu erkennen (Einstellungen bleiben, z. B. nach Fuehlertausch)")
    print(" 2) Sensor neu aufsetzen (loeschen, Firmware, Grundeinstellungen, Sensoren erkennen)")
    print(" 3) Nur Firmware aktualisieren (nur Standalone, Einstellungen bleiben)")
    print(" 4) Debug (Ausgaben des Sensors anzeigen)")
    print(" 5) Beenden")
    wahl = input("Ihre Wahl [5]: ").strip() or "5"
    if wahl == "1":
        sensoren_neu(port, quelle)
    elif wahl == "2":
        neu_aufsetzen(port, quelle)
    elif wahl == "3":
        nur_firmware(port, quelle)
    elif wahl == "4":
        debug(port)


if __name__ == "__main__":
    main()

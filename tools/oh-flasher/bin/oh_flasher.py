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
from espeasy_autoconfig import autokonfiguration, oeffne, i2c_hinweise, i2c_scan, ow_scan  # noqa: E402
from espeasy_testbox import dashboard_hochladen, http_bereit, lade_hoch, sende, setze_zugriff, warte_ip  # noqa: E402


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


def pruefe_chip(port):
    umgebung = dict(os.environ, PYTHONPATH=SITE_PACKAGES) if os.path.isdir(SITE_PACKAGES) else None
    ausgabe = subprocess.run([sys.executable, "-m", "esptool", "--port", port, "chip_id"],
                             capture_output=True, text=True, env=umgebung).stdout
    if "ESP8266" not in ausgabe:
        sys.exit("Dieser Flasher ist nur fuer den openandhome-Temperatursensor (ESP8266).")


# --- Ablaeufe ---
def erkenne_und_schalte(port, manifest):
    """USB: I2C- und 1-Wire-Scan, passende Tasks ein-/ausschalten. Liefert (an, aus, Anzahl Fuehler)."""
    i2c = i2c_scan(port)
    i2c_hinweise(i2c, {a for t in manifest["tasks"] if t["art"] == "i2c" for a in t["adressen"]})
    fuehler = ow_scan(port, manifest["onewire_gpio"])
    befehle, an, aus, ds = [], [], [], 0
    for t in manifest["tasks"]:
        if t["art"] == "ds18b20":
            ds += 1
            aktiv = ds <= len(fuehler)
        elif t["art"] == "i2c":
            aktiv = bool(set(t["adressen"]) & i2c)
        else:
            aktiv = ja(f"Ist '{t['name']}' ({t['typ']}) an Ihrem Sensor angeschlossen?")
            (an if aktiv else aus).append(t["name"])
        befehle.append(f"{'TaskEnable' if aktiv else 'TaskDisable'},{t['nr']}")
        if aktiv:
            print(f"  gefunden: {t['name']} ({t['typ']})")
    print(f"  {len(fuehler)} Temperaturfuehler am 1-Wire-Bus")
    sende(port, *befehle, "Save")
    return an, aus, len(fuehler)


def neu_aufsetzen(port, quelle):
    manifest = quelle.manifest()
    print(f"Freigegebener Stand vom {manifest['erzeugt']}: {os.path.basename(manifest['firmware']['pfad'])}")
    firmware = quelle.datei(manifest["firmware"])
    pruefe_chip(port)

    mit_wlan = ja("Sensor dabei in Ihr WLAN einbinden? Dann wird alles automatisch eingerichtet.", True)
    if not mit_wlan and "dateisystem" not in manifest:
        print("\nOhne WLAN ist das Neu-Aufsetzen mit diesem Stand noch nicht moeglich.")
        print("Bitte mit WLAN starten oder unseren Support kontaktieren.")
        return
    if mit_wlan:
        ssid = input("Name Ihres WLANs (SSID): ").strip()
        key = getpass.getpass("WLAN-Passwort (Eingabe unsichtbar): ")
    if not ja("Der Sensor wird vollstaendig geloescht und neu aufgesetzt. Weiter?", True):
        return

    gruen("\n1/4 Loesche den Sensor ...")
    esptool(port, "erase_flash")
    gruen("2/4 Schreibe Firmware ...")
    if mit_wlan:
        esptool(port, "write_flash", "--flash_size", "4MB", "0x0", firmware)
    else:
        dateisystem = quelle.datei(manifest["dateisystem"])
        esptool(port, "write_flash", "--flash_size", "4MB", "0x0", firmware,
                manifest["dateisystem"]["adresse"], dateisystem)
    print("Warte auf den Start des Sensors ...")
    time.sleep(20)

    if not mit_wlan:
        gruen("3/4 Erkenne angeschlossene Sensoren ...")
        _, _, anzahl = erkenne_und_schalte(port, manifest)
        sende(port, "Reboot")
        gruen("4/4 Fertig.")
        print("Der Sensor oeffnet jetzt sein eigenes WLAN (Access Point).")
        print("Binden Sie ihn wie in der Anleitung beschrieben in Ihr WLAN ein.")
        if anzahl > 1:
            print("Waehlen Sie danach in der Oberflaeche unter 'Devices' bei jedem Fuehler die Device-Adresse.")
        return

    gruen("3/4 Verbinde mit Ihrem WLAN und lade die Grundeinstellungen ...")
    ressourcen = [quelle.datei(r, "ressourcen") for r in manifest["ressourcen"]]
    sende(port, f'WifiSSID,"{ssid}"', f'WifiKey,"{key}"', "Save", "Reboot")
    time.sleep(10)
    box = http_bereit(port, warte_ip(port))
    # Der AM2320 braucht ein anderes Image; er schlaeft und antwortet oft erst beim zweiten Scan
    if "am2320" in manifest and any(0x5C in i2c_scan(port) for _ in range(2)):
        print("  AM2320 erkannt - spiele die passende Firmware ein (Einstellungen bleiben) ...")
        manifest = dict(manifest, **manifest["am2320"])
        esptool(port, "write_flash", "--flash_size", "4MB", "0x0", quelle.datei(manifest["firmware"]))
        time.sleep(20)
        box = http_bereit(port, warte_ip(port))
    basis = quelle.datei(manifest["basis_config"])
    lade_hoch(box, basis, "config.dat")
    sende(port, "Reboot")
    time.sleep(10)
    box = http_bereit(port, warte_ip(port))

    gruen("4/4 Erkenne angeschlossene Sensoren und richte sie ein ...")
    an, aus = [], []
    for t in manifest["tasks"]:
        if t["art"] == "frage":
            (an if ja(f"Ist '{t['name']}' ({t['typ']}) an Ihrem Sensor angeschlossen?") else aus).append(t["name"])
    autokonfiguration(box, port, an, aus, anwenden=True)
    dashboard_hochladen(box, ablage=CACHE, ressourcen=os.path.dirname(ressourcen[0]))
    setze_zugriff(box)
    gruen(f"\nFertig. Ihr Sensor ist erreichbar unter {box.basis}")


def nur_firmware(port, quelle):
    manifest = quelle.manifest()
    firmware = quelle.datei(manifest["firmware"])
    pruefe_chip(port)
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
    print(" 1) Sensor neu aufsetzen (loeschen, Firmware, Sensoren erkennen, WLAN)")
    print(" 2) Nur Firmware aktualisieren (Einstellungen bleiben erhalten)")
    print(" 3) Debug (Ausgaben des Sensors anzeigen)")
    print(" 4) Beenden")
    wahl = input("Ihre Wahl [4]: ").strip() or "4"
    if wahl == "1":
        neu_aufsetzen(port, quelle)
    elif wahl == "2":
        nur_firmware(port, quelle)
    elif wahl == "3":
        debug(port)


if __name__ == "__main__":
    main()

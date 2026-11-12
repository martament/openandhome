#!/usr/bin/env python3
"""OH-Flasher - Firmware aktualisieren oder Sensor neu aufspielen (Notloesung).

Fuer alles andere (WLAN, Name, Zeitserver, Sensoren) ist die Toolbox da.
Neu aufspielen schreibt das aktuelle Image und richtet danach die Grundkonfiguration
ein - mit denselben Ablaeufen wie die Toolbox.
Start: start_flasher.bat (Windows) bzw. flasher.sh (Linux).
"""

import argparse
import os
import subprocess
import sys
import time

HIER = os.path.dirname(os.path.abspath(__file__))
PAKET = os.path.dirname(HIER)
SITE_PACKAGES = os.path.join(HIER, "pythonportable", "Lib", "site-packages")
sys.path[:0] = [os.path.join(HIER, "lib"), os.path.join(PAKET, "..", "bin")]

import oh_kunde as k  # noqa: E402
from espeasy_autoconfig import oeffne  # noqa: E402
from espeasy_testbox import sende  # noqa: E402


def erkenne_chip(port):
    """Per Konsole (laufende Firmware), sonst per esptool (auch bei leerem/defektem Sensor)."""
    chip = k.box_typ(port)
    if chip:
        return chip
    umgebung = dict(os.environ, PYTHONPATH=SITE_PACKAGES) if os.path.isdir(SITE_PACKAGES) else None
    ausgabe = subprocess.run([sys.executable, "-m", "esptool", "--port", port, "chip_id"],
                             capture_output=True, text=True, env=umgebung).stdout
    for chip in ("ESP32", "ESP8266"):
        if chip in ausgabe:
            return chip
    sys.exit("Kein openandhome-Sensor erkannt. Sensor neu anstecken und noch einmal versuchen.")


def update(port, quelle, chip):
    print("\n--- Firmware aktualisieren (Einstellungen bleiben) ---")
    # Standalone: collection_H, wenn sie schon laeuft oder ein AM2320 antwortet, sonst climate_B
    am2320 = True if chip == "ESP8266" and "collection_H" in k.image_name(port) else None
    klasse = k.klasse(quelle, chip, port, am2320=am2320)
    neu = os.path.basename(klasse.get("firmware_update", klasse["firmware"])["pfad"])
    print(f"Spiele {neu} ein.")
    if not k.ja("Weiter?", True):
        return
    k.firmware_update(port, quelle, klasse, SITE_PACKAGES)
    k.gruen("Fertig. Der Sensor startet mit der neuen Firmware; Ihre Einstellungen bleiben erhalten.")


def neu_aufspielen(port, quelle, chip):
    print("\n--- Sensor neu aufspielen (Notfall) ---")
    print("Der Sensor wird vollstaendig geloescht, das aktuelle Image eingespielt und die")
    print("Grundkonfiguration eingerichtet. Danach werden die Sensoren erkannt.")
    if not k.ja("Alle Einstellungen gehen verloren. Weiter?"):
        return
    standard = k.klasse(quelle, chip, am2320=False)
    k.neu_aufspielen(port, quelle, standard, chip, SITE_PACKAGES)
    temporaer = k.ins_netz(port, chip)     # WLAN fuer die Einrichtung (Professional: danach geloescht)
    klasse = k.klasse(quelle, chip, port)
    if klasse["firmware"] != standard["firmware"]:
        print("AM2320 erkannt - spiele die passende Firmware ein (Einstellungen bleiben) ...")
        k.firmware_update(port, quelle, klasse, SITE_PACKAGES)
        time.sleep(20)
    k.grundkonfiguration(port, quelle, klasse, chip, temporaer)


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
    parser = argparse.ArgumentParser(description="OH-Flasher")
    parser.add_argument("--port", help="COM-Port bzw. /dev/ttyUSB0 (Standard: automatisch)")
    parser.add_argument("--quelle", choices=["github", "lokal", "offline"], default="github")
    args = parser.parse_args()
    if os.name == "nt":
        os.system("")
    port = args.port or k.finde_port()
    quelle = k.Quelle(args.quelle, PAKET)
    print("*" * 70)
    print(f" OH-Flasher - Sensor an {port}")
    print(" Fuer WLAN, Name, Zeitserver und Sensoren bitte die Toolbox verwenden.")
    print("*" * 70)
    chip = erkenne_chip(port)
    print(f"Sensorbox {'Professional' if chip == 'ESP32' else 'Standalone'} erkannt, "
          f"freigegebener Stand: {quelle.manifest()['stand']}")
    if chip == "ESP32" and not k.poe_warnung():
        return
    print(" 1) Firmware aktualisieren (Einstellungen bleiben)")
    print(" 2) Sensor neu aufspielen und einrichten (Notfall, alle Einstellungen gehen verloren)")
    print(" 3) Debug (Ausgaben des Sensors anzeigen)")
    print(" q) Beenden")
    wahl = input("Ihre Wahl: ").strip().lower()
    if wahl == "1":
        update(port, quelle, chip)
    elif wahl == "2":
        neu_aufspielen(port, quelle, chip)
    elif wahl == "3":
        debug(port)


if __name__ == "__main__":
    main()

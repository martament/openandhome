#!/usr/bin/env python3
"""openandhome-Toolbox - Standardwerkzeug fuer Endanwender (Standalone und Professional).

Arbeitet ueber das USB-Kabel: WLAN, Name, Zeitserver, Resets, Diagnose sowie
Grundkonfiguration und Sensorerkennung (dafuer kurz per WLAN im Netz).
Start: start_toolbox.bat (Windows) bzw. toolbox.sh (Linux).
"""

import argparse
import os
import re
import sys
import time

HIER = os.path.dirname(os.path.abspath(__file__))
PAKET = os.path.dirname(HIER)
# Module: im ZIP unter bin/lib, im Repo unter tools/bin
sys.path[:0] = [os.path.join(HIER, "lib"), os.path.join(PAKET, "..", "bin")]

import oh_kunde as k  # noqa: E402
from espeasy_autoconfig import oeffne  # noqa: E402
from espeasy_testbox import sende, usb_ip, wlan_verbinden  # noqa: E402

TITEL = "openandhome - Toolbox v4.0"


def befehle(port, titel, *kommandos):
    print(f"\n{titel} ...")
    sende(port, "ResetFlashWriteCounter", *kommandos, "Save")
    k.gruen("Erledigt.")
    k.weiter()


def wlan(port, chip):
    print("\n--- WLAN-Zugangsdaten setzen ---")
    if chip == "ESP32":
        print("Die Sensorbox Professional arbeitet mit dem Netzwerkkabel; WLAN brauchen Sie nur ohne Kabel.")
        if not k.ja("Trotzdem WLAN setzen?"):
            return
    ip = wlan_verbinden(port, *k.wlan_eingeben())
    k.gruen(f"Verbunden. Ihr Sensor ist erreichbar unter: http://{ip}/openandhome.esp")
    k.weiter()


def name(port):
    print("\n--- Geraetename aendern ---")
    print("Bei mehreren Sensoren braucht jeder einen eigenen Namen (z. B. Keller, Heizung).")
    neu = input("Neuer Name (Buchstaben, Ziffern, - und _; leer = Abbruch): ").strip()
    if not re.fullmatch(r"[A-Za-z0-9_-]{1,24}", neu):
        print("Abgebrochen.")
        return
    befehle(port, "Geraetename setzen", f"Name,{neu}")


def ntp(port):
    print("\n--- Zeitserver (NTP) setzen ---")
    print("Standard ist de.pool.ntp.org (Internet). Ohne Internet z. B. die Adresse Ihres Routers")
    print("(FRITZ!Box: 192.168.178.1) eintragen.")
    server = input("NTP-Server (leer = Abbruch): ").strip()
    if not re.fullmatch(r"[A-Za-z0-9.-]+", server):
        print("Abgebrochen.")
        return
    befehle(port, "Zeitserver setzen", f"NTPHost,{server}")


def einstellungen(port):
    print()
    for z in sende(port, "ResetFlashWriteCounter", "Settings", wartezeit=3):
        if not z.startswith(("Cmd", ">")):
            print(z)
    k.weiter()


def debugger(port):
    datei = os.path.abspath("oh-debug.txt")
    print(f"\nAusgaben des Sensors, gespeichert in {datei}. Beenden mit STRG+C.\n")
    with open(datei, "a", encoding="utf-8") as log:
        log.write(f"--- Debug Log Start: {time.ctime()} ---\n")
        for z in sende(port, "ResetFlashWriteCounter", "Settings", wartezeit=2):
            print(z)
            log.write(z + "\n")
        try:
            with oeffne(port, timeout=1) as s:
                while True:
                    z = s.readline().decode("latin-1").rstrip()
                    if z:
                        print(z)
                        log.write(z + "\n")
        except KeyboardInterrupt:
            pass
    print(f"\nLog gespeichert: {datei}")
    k.weiter()


def grundkonfiguration(port, quelle, chip):
    print("\n--- Grundkonfiguration wiederherstellen ---")
    print("Alle Einstellungen (Name, Sensoren, Display, Zeitserver) werden auf den Auslieferungszustand gesetzt;")
    print("danach erkennt die Toolbox die angeschlossenen Sensoren. Die Firmware bleibt unveraendert.")
    if not k.ja("Weiter?"):
        return
    klasse = k.klasse(quelle, chip, port)
    if chip == "ESP8266" and "am2320" in quelle.manifest()["klassen"][chip]:
        braucht = os.path.basename(klasse["firmware"]["pfad"]).replace(".bin", "")
        if braucht != k.image_name(port):
            k.rot(f"Fuer Ihre Sensoren ist die Firmware {braucht} noetig - bitte mit dem OH-Flasher "
                  "(Menue 'Firmware aktualisieren') einspielen und danach hier fortfahren.")
            k.weiter()
            return
    k.grundkonfiguration(port, quelle, klasse, chip)
    k.weiter()


def sensoren(port, quelle, chip):
    print("\n--- Sensoren neu erkennen ---")
    print("Z. B. nach dem Tausch oder Hinzufuegen eines Fuehlers. Ihre Einstellungen bleiben erhalten.")
    k.sensoren_neu(port, quelle, k.klasse(quelle, chip, port), chip)
    k.weiter()


def main():
    parser = argparse.ArgumentParser(description=TITEL)
    parser.add_argument("--port", help="COM-Port bzw. /dev/ttyUSB0 (Standard: automatisch)")
    parser.add_argument("--quelle", choices=["github", "lokal", "offline"], default="github")
    args = parser.parse_args()
    if os.name == "nt":
        os.system("")      # ANSI-Farben in der Windows-Konsole
    port = args.port or k.finde_port()
    quelle = k.Quelle(args.quelle, PAKET)

    print("Erkenne Sensorbox ...")
    chip = k.box_typ(port)
    typ = {"ESP32": "Professional", "ESP8266": "Standalone"}.get(chip, "unbekannt")
    if chip == "ESP32" and not k.poe_warnung():
        return

    menue = {
        "1": ("WLAN-Zugangsdaten setzen (mit Verbindungspruefung)", lambda: wlan(port, chip)),
        "2": ("Neustart", lambda: befehle(port, "Neustart", "Reboot")),
        "3": ("Einstellungen anzeigen", lambda: einstellungen(port)),
        "4": ("Debugger (Ausgaben anzeigen und speichern)", lambda: debugger(port)),
        "5": ("WLAN-Daten loeschen", lambda: befehle(port, "WLAN-Daten loeschen", "WifiSSID ssid", "WifiKey wpakey",
                                                     "WifiSSID2 ssid", "WifiKey2 wpakey")),
        "6": ("Reset DHCP (feste IP-Adresse aufheben)",
              lambda: befehle(port, "Reset DHCP", "IP 0.0.0.0", *(["ethip,0.0.0.0"] if chip == "ESP32" else []))),
        "7": ("Admin-Passwort zuruecksetzen", lambda: befehle(port, "Admin-Passwort zuruecksetzen", "password")),
        "8": ("WLAN-Zugangspunkt starten", lambda: befehle(port, "WLAN-Zugangspunkt starten", "WifiAPMode")),
        "9": ("IP-Filter zuruecksetzen (bis zum Neustart)", lambda: befehle(port, "IP-Filter zuruecksetzen",
                                                                          "ClearAccessBlock")),
        "n": ("Zeitserver (NTP) setzen", lambda: ntp(port)),
        "g": ("Geraetename aendern", lambda: name(port)),
        "s": ("Sensoren neu erkennen (Einstellungen bleiben)", lambda: sensoren(port, quelle, chip)),
        "k": ("Grundkonfiguration wiederherstellen", lambda: grundkonfiguration(port, quelle, chip)),
    }
    while True:
        print("\n" + "=" * 60)
        print(f" {TITEL}")
        print(f" Sensor an {port} - Sensorbox {typ}" + (f" - IP {usb_ip(port) or 'keine'}" if chip else ""))
        if chip == "ESP32":
            k.rot(" ACHTUNG: Netzwerkkabel (PoE) muss abgezogen sein, solange USB steckt!")
        print("=" * 60)
        for taste, (text, _) in menue.items():
            print(f" {taste}) {text}")
        print(" q) Beenden")
        wahl = input("Ihre Wahl: ").strip().lower()
        if wahl == "q":
            return
        if wahl in menue:
            if wahl in ("s", "k") and not chip:
                k.rot("Sensorbox nicht erkannt - bitte den OH-Flasher verwenden.")
                continue
            menue[wahl][1]()


if __name__ == "__main__":
    main()

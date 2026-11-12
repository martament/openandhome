#!/usr/bin/env python3
"""Box-Klassen von openandhome - die eine Quelle fuer Werkstatt, Toolbox und Flasher.

Je Chip: Images, Basis-config, Regeln und Hardware-Angaben. Das Manifest fuer
Toolbox/Flasher (tools/ohtoolbox/manifest.json) wird daraus erzeugt:

  python3 tools/bin/oh_klassen.py        -> schreibt das Manifest neu
"""

import glob
import hashlib
import json
import os
import re

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
MANIFEST = "tools/ohtoolbox/manifest.json"
RESSOURCEN = "configs/espeasy/standalone/resources"
DASHBOARD_DATEIEN = ["temperature.png", "temperature1.png", "humidity.png", "distance.png",
                     "openandhome_32.png", "openandhome.css"]

KLASSEN = {
    "ESP8266": {
        "name": "standalone",
        "image": "configs/espeasy/standalone/ESP_Easy_mega_*_climate_B_ESP8266_4M1M.bin",
        "flash": ["--flash_size", "4MB", "0x0"],
        # Update: dasselbe Image an 0x0 - das Dateisystem (0x300000) bleibt erhalten
        "update": ["--flash_size", "4MB", "0x0"],
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
        # Update: nur die App nach app0, otadata loeschen (startet dann app0);
        # NVS (Ethernet) und Dateisystem bleiben erhalten
        "update_image": "configs/espeasy/professional/ESP_Easy_mega_*_collection_A_ESP32_4M316k.bin",
        "update": ["0x10000"],
        "update_loeschen": ["0xe000", "0x2000"],
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


def pfad(muster):
    """Neueste Datei zu einem Glob-Muster (relativ zum Repo)."""
    treffer = sorted(glob.glob(os.path.join(ROOT, muster)))
    if not treffer:
        raise FileNotFoundError(f"keine Datei fuer {muster} - erst Images laden (espeasy_download.py)")
    return treffer[-1]


def regeln(basis):
    """rules1.txt neben der Basis-config, falls vorhanden."""
    p = os.path.join(ROOT, os.path.dirname(basis), "rules1.txt")
    return p if os.path.exists(p) else None


def _eintrag(p):
    with open(p, "rb") as f:
        sha = hashlib.sha256(f.read()).hexdigest()
    return {"pfad": os.path.relpath(p, ROOT).replace(os.sep, "/"), "sha256": sha}


def _teil(definition):
    teil = {"firmware": _eintrag(pfad(definition["image"])),
            "basis_config": _eintrag(os.path.join(ROOT, definition["basis"]))}
    if regeln(definition["basis"]):
        teil["regeln"] = _eintrag(regeln(definition["basis"]))
    return teil


def manifest_erzeugen():
    """Manifest fuer Toolbox/Flasher aus KLASSEN (Pfade + SHA256)."""
    klassen = {}
    for chip, k in KLASSEN.items():
        teil = _teil(k)
        teil.update(name=k["name"], flash=k["flash"], update=k["update"])
        if "update_image" in k:
            teil["firmware_update"] = _eintrag(pfad(k["update_image"]))
            teil["update_loeschen"] = k["update_loeschen"]
        for schluessel in ("ethernet", "ow_gpios"):
            if schluessel in k:
                teil[schluessel] = k[schluessel]
        if "am2320" in k:
            teil["am2320"] = _teil(k["am2320"])
        klassen[chip] = teil
    # Stand = Release-Tag der Firmware (stabil, damit die CI ein veraltetes Manifest erkennt)
    tag = re.search(r"mega_(\d{8})", klassen["ESP8266"]["firmware"]["pfad"]).group(1)
    return {
        "version": 2,
        "stand": f"mega-{tag}",
        "ressourcen": [_eintrag(os.path.join(ROOT, RESSOURCEN, d))
                       for d in ["header.txt", "footer.txt", *DASHBOARD_DATEIEN]],
        "klassen": klassen,
    }


def manifest_schreiben():
    m = manifest_erzeugen()
    ziel = os.path.join(ROOT, MANIFEST)
    with open(ziel, "w", encoding="utf-8") as f:
        json.dump(m, f, indent=2, ensure_ascii=False)
        f.write("\n")
    return ziel


if __name__ == "__main__":
    print("geschrieben:", os.path.relpath(manifest_schreiben(), ROOT))

#!/usr/bin/env python3
"""Baut ein LittleFS-Image fuer die Professional-Box (ESP32, Plan 14).

Die Professional-Box (Olimex ESP32-POE) hat am USB kein Netzwerk; die
Grundkonfiguration muss deshalb beim Flashen als Dateisystem-Image mit.
Inhalt: config.dat (Name/Unit gepatcht), security.dat, notification.dat
und optional Dashboard-Dateien. mklittlefs wird aus dem offiziellen Release
geladen und per SHA256 geprueft.

  tools/bin/espeasy_fsimage.py --basis configs/espeasy/professional/basis \\
      --name Testbox1 --unit 1 --ausgabe /tmp/fs.bin
"""

import argparse
import hashlib
import os
import shutil
import subprocess
import sys
import tarfile
import tempfile
import urllib.request

MKLITTLEFS_URL = ("https://github.com/earlephilhower/mklittlefs/releases/download/4.1.0/"
                  "x86_64-linux-gnu-mklittlefs-42acb97.tar.gz")
MKLITTLEFS_SHA256 = "e3a691654ca8c27409199d3bcdc5af4c85ecf91da2f96b09f17a0e03c0149f1e"
CACHE = os.path.expanduser("~/.cache/openandhome/mklittlefs")
# Partition spiffs in esp32_partition_app1810k_spiffs316k.csv
FS_ADRESSE, FS_GROESSE = 0x3B1000, 0x4F000
SECURITY_DEFAULTS = {b"ssid", b"wpakey", b"configesp"}
# Offsets in config.dat (SettingsStruct, siehe espeasy_configcheck.py)
OFFSET_UNIT, OFFSET_NAME, NAME_LAENGE = 27, 28, 26


def mklittlefs():
    pfad = os.path.join(CACHE, "mklittlefs", "mklittlefs")
    if os.path.exists(pfad):
        return pfad
    os.makedirs(CACHE, exist_ok=True)
    daten = urllib.request.urlopen(MKLITTLEFS_URL, timeout=60).read()
    if hashlib.sha256(daten).hexdigest() != MKLITTLEFS_SHA256:
        sys.exit("FEHLER: mklittlefs-Download hat falsche Pruefsumme.")
    archiv = os.path.join(CACHE, "mklittlefs.tar.gz")
    with open(archiv, "wb") as f:
        f.write(daten)
    with tarfile.open(archiv) as t:
        t.extractall(CACHE, filter="data")
    os.chmod(pfad, 0o755)
    return pfad


def patche_name(config, name, unit):
    daten = bytearray(config)
    roh = name.encode("ascii")
    if len(roh) >= NAME_LAENGE:
        sys.exit(f"FEHLER: Name '{name}' zu lang (max. {NAME_LAENGE - 1} Zeichen).")
    daten[OFFSET_NAME:OFFSET_NAME + NAME_LAENGE] = roh.ljust(NAME_LAENGE, b"\0")
    daten[OFFSET_UNIT] = int(unit)
    # config.dat hat keine Pruefsumme ueber den Namen, ESPEasy liest ihn direkt
    return bytes(daten)


def pruefe_security(pfad):
    with open(pfad, "rb") as f:
        worte = {w for w in f.read().split(b"\0") if len(w) >= 4 and w.isascii() and w.decode().isprintable()}
    if not worte <= SECURITY_DEFAULTS:
        sys.exit(f"FEHLER: {pfad} enthaelt Nicht-Default-Werte (WLAN/Passwort) - nicht verwenden.")


def baue(basis, name, unit, ausgabe, extra=()):
    """basis: Ordner mit config.dat, security.dat, notification.dat."""
    with tempfile.TemporaryDirectory() as tmp:
        for datei in ("config.dat", "security.dat", "notification.dat"):
            quelle = os.path.join(basis, datei)
            if not os.path.exists(quelle):
                if datei == "config.dat":
                    sys.exit(f"FEHLER: {quelle} fehlt.")
                continue
            if datei == "security.dat":
                pruefe_security(quelle)
            shutil.copy(quelle, os.path.join(tmp, datei))
        with open(os.path.join(tmp, "config.dat"), "rb") as f:
            config = f.read()
        with open(os.path.join(tmp, "config.dat"), "wb") as f:
            f.write(patche_name(config, name, unit))
        for pfad in extra:
            shutil.copy(pfad, os.path.join(tmp, os.path.basename(pfad)))
        befehl = [mklittlefs(), "-c", tmp, "-b", "4096", "-p", "256", "-s", str(FS_GROESSE), ausgabe]
        ergebnis = subprocess.run(befehl, capture_output=True, text=True)
        if ergebnis.returncode != 0:
            sys.exit(f"FEHLER mklittlefs:\n{ergebnis.stdout}{ergebnis.stderr}")
    return ausgabe


def main():
    parser = argparse.ArgumentParser(description="LittleFS-Image fuer die Professional-Box bauen.")
    parser.add_argument("--basis", required=True, help="Ordner mit config.dat, security.dat, notification.dat")
    parser.add_argument("--name", required=True)
    parser.add_argument("--unit", default="0")
    parser.add_argument("--ausgabe", required=True)
    parser.add_argument("--extra", nargs="*", default=[], help="weitere Dateien (Dashboard, Icons)")
    args = parser.parse_args()
    baue(args.basis, args.name, args.unit, args.ausgabe, args.extra)
    print(f"{args.ausgabe}: LittleFS {FS_GROESSE:#x} Byte fuer Adresse {FS_ADRESSE:#x}")


if __name__ == "__main__":
    main()

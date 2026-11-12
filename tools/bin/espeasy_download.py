#!/usr/bin/env python3
"""Laedt offizielle ESPEasy-Release-Images fuer openandhome (Plan D1).

Quelle: GitHub Releases von letscontrolit/ESPEasy. Das Skript
- laeuft nur auf dem Branch 'devel' (Downloads nur dort, siehe AGENTS.md),
- prueft die ZIP-Archive gegen den SHA256-Digest von GitHub,
- legt pro Geraeteklasse die freigegebenen Images ab (Standalone: climate_B, collection_H fuer AM2320),
- schreibt readme_image.txt mit Release-Tag, Asset, SHA256 und Flash-Adressen.

Beispiele:
  tools/bin/espeasy_download.py                    # neuestes Release, beide Klassen
  tools/bin/espeasy_download.py --tag mega-20260720 --klasse professional
  tools/bin/espeasy_download.py --dry-run
"""

import argparse
import datetime
import hashlib
import json
import os
import re
import subprocess
import sys
import urllib.request
import zipfile

REPO = "letscontrolit/ESPEasy"
API = f"https://api.github.com/repos/{REPO}/releases"
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
CACHE = os.path.join(os.path.expanduser("~"), ".cache", "openandhome", "espeasy")

KLASSEN = {
    "professional": {
        "zip": "_ESP32_binaries.zip",
        "bild": re.compile(r"^ESP_Easy_mega_\d+_collection_A_ESP32_4M316k(\.factory)?\.bin$"),
        "alt": re.compile(r"^ESP_Easy_mega_\d+_collection_A_ESP32_4M316k.*\.bin$"),
        "ziel": "configs/espeasy/professional",
        "beschreibung": "Professional (ESP32 4MB, Ethernet, LittleFS)",
        "flash": [
            "factory.bin -> 0x000000 (Neu-Aufspielen), .bin -> 0x10000 (Update)",
            "Filesystem LittleFS @0x3B1000, Groesse 0x4F000 (esp32_partition_app1810k_spiffs316k.csv)",
            "config.dat/Dashboard per Web-Upload (Werkstatt-Tool bzw. OH-Flasher)",
        ],
    },
    "standalone": {
        "zip": "_ESP82xx_binaries.zip",
        "bild": re.compile(r"^ESP_Easy_mega_\d+_(climate_B|collection_H)_ESP8266_4M1M\.bin$"),
        "alt": re.compile(r"^ESP_Easy_mega_\d+_(collection_A|climate_B|collection_H)_ESP8266_4M1M.*\.bin$"),
        "ziel": "configs/espeasy/standalone",
        "beschreibung": "Standalone/Wemos (ESP8266 4M1M, SPIFFS) - climate_B Standard, collection_H bei AM2320",
        "flash": [
            ".bin -> 0x000000 (Neu-Aufspielen und Update)",
            "Filesystem SPIFFS @0x300000, Groesse 0x100000",
            "config.dat/Dashboard per Web-Upload (Werkstatt-Tool bzw. OH-Flasher)",
        ],
        # Siehe Plan Abschnitt 5 C: bei LittleFS-Collection fuer 4M1M neu bewerten
        "hinweis": re.compile(r"collection.*ESP8266_4M1M.*LittleFS", re.IGNORECASE),
    },
}


def fehler(text):
    print(f"FEHLER: {text}", file=sys.stderr)
    sys.exit(1)


def git(*args):
    return subprocess.run(["git", "-C", ROOT, *args], capture_output=True, text=True)


def pruefe_branch():
    branch = git("rev-parse", "--abbrev-ref", "HEAD").stdout.strip()
    if branch != "devel":
        fehler(f"Downloads nur auf Branch 'devel' (aktuell: '{branch}').")


def hole_release(tag):
    url = f"{API}/latest" if tag is None else f"{API}/tags/{tag}"
    with urllib.request.urlopen(url, timeout=30) as antwort:
        return json.load(antwort)


def sha256_datei(pfad):
    h = hashlib.sha256()
    with open(pfad, "rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def lade_asset(asset, tag):
    ordner = os.path.join(CACHE, tag)
    os.makedirs(ordner, exist_ok=True)
    pfad = os.path.join(ordner, asset["name"])
    soll = (asset.get("digest") or "").removeprefix("sha256:")

    if os.path.exists(pfad) and soll and sha256_datei(pfad) == soll:
        print(f"  Cache: {pfad}")
        return pfad

    print(f"  Lade {asset['name']} ({asset['size'] / 1e6:.1f} MB) ...")
    teil = pfad + ".part"
    with urllib.request.urlopen(asset["browser_download_url"], timeout=60) as antwort, open(teil, "wb") as f:
        while block := antwort.read(1 << 20):
            f.write(block)
    ist = sha256_datei(teil)
    if soll and ist != soll:
        os.remove(teil)
        fehler(f"SHA256 von {asset['name']} stimmt nicht (soll {soll}, ist {ist}).")
    if not soll:
        print("  WARNUNG: GitHub liefert keinen Digest, ZIP ungeprueft.")
    os.replace(teil, pfad)
    return pfad


def entferne_alte(ziel, muster, neu, dry_run):
    for name in sorted(os.listdir(ziel)):
        if not muster.match(name) or name in neu:
            continue
        pfad = os.path.join(ziel, name)
        print(f"  Entferne altes Image: {os.path.relpath(pfad, ROOT)}")
        if dry_run:
            continue
        if git("ls-files", "--error-unmatch", pfad).returncode == 0:
            git("rm", "-q", pfad)
        else:
            os.remove(pfad)


def schreibe_readme(ziel, klasse, release, asset, dateien):
    zeilen = [
        f"# Firmware-Image {klasse['beschreibung']}",
        "# Automatisch erzeugt von tools/bin/espeasy_download.py - nicht von Hand aendern.",
        "",
        f"Quelle:        https://github.com/{REPO}/releases/tag/{release['tag_name']}",
        f"Release-Tag:   {release['tag_name']} (veroeffentlicht {release['published_at'][:10]})",
        f"Asset:         {asset['name']}",
        f"Asset-SHA256:  {(asset.get('digest') or 'unbekannt').removeprefix('sha256:')}",
        f"Heruntergeladen: {datetime.date.today().isoformat()}",
        "",
        "Dateien (SHA256):",
    ]
    zeilen += [f"  {sha}  {name}" for name, sha in dateien]
    zeilen += ["", "Flashen:"] + [f"  - {z}" for z in klasse["flash"]]
    zeilen += [
        "",
        "Test (24h, Syslog 192.168.9.4) und Freigabe: siehe plans/espeasy-fertig-images.md, Abschnitt 6.",
        "Getestet am: (offen)",
        "",
    ]
    with open(os.path.join(ziel, "readme_image.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(zeilen))


def verarbeite(name, klasse, release, dry_run, alte_behalten):
    print(f"\n== {klasse['beschreibung']}")
    asset = next((a for a in release["assets"] if a["name"].endswith(klasse["zip"])), None)
    if asset is None:
        fehler(f"Kein Asset '*{klasse['zip']}' im Release {release['tag_name']}.")
    if dry_run:
        print(f"  (dry-run) wuerde {asset['name']} laden")
        return

    zip_pfad = lade_asset(asset, release["tag_name"])
    ziel = os.path.join(ROOT, klasse["ziel"])
    dateien = []
    with zipfile.ZipFile(zip_pfad) as archiv:
        namen = {os.path.basename(n): n for n in archiv.namelist() if not n.endswith("/")}
        if "hinweis" in klasse:
            for n in namen:
                if klasse["hinweis"].search(n):
                    print(f"  HINWEIS: {n} vorhanden - LittleFS-Wechsel neu bewerten (Plan 5 C).")
        treffer = sorted(n for n in namen if klasse["bild"].match(n))
        if not treffer:
            fehler(f"Kein passendes Image in {asset['name']} ({klasse['bild'].pattern}).")
        if not alte_behalten:
            entferne_alte(ziel, klasse["alt"], set(treffer), dry_run)
        for n in treffer:
            pfad = os.path.join(ziel, n)
            with archiv.open(namen[n]) as quelle, open(pfad, "wb") as f:
                f.write(quelle.read())
            dateien.append((n, sha256_datei(pfad)))
            print(f"  Neu: {os.path.relpath(pfad, ROOT)}")
    schreibe_readme(ziel, klasse, release, asset, dateien)
    print(f"  readme: {os.path.relpath(os.path.join(ziel, 'readme_image.txt'), ROOT)}")


def main():
    parser = argparse.ArgumentParser(description="Offizielle ESPEasy-Images fuer openandhome laden (nur auf devel).")
    parser.add_argument("--tag", help="Release-Tag, z. B. mega-20260720 (Standard: neuestes Release)")
    parser.add_argument("--klasse", choices=[*KLASSEN, "alle"], default="alle")
    parser.add_argument("--dry-run", action="store_true", help="nur anzeigen, nichts laden oder aendern")
    parser.add_argument("--alte-behalten", action="store_true", help="vorhandene collection_A-Images nicht entfernen")
    args = parser.parse_args()

    pruefe_branch()
    release = hole_release(args.tag)
    print(f"Release {release['tag_name']} vom {release['published_at'][:10]}")

    for name, klasse in KLASSEN.items():
        if args.klasse in (name, "alle"):
            verarbeite(name, klasse, release, args.dry_run, args.alte_behalten)

    if not args.dry_run:
        print("\nFertig. Pruefen und committen, z. B.:")
        print("  git add -A configs/espeasy/professional configs/espeasy/standalone && git status")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Baut oh-flasher.zip fuer Kunden (Plan 12, FL-8).

Inhalt: Startdateien, portables Python, oh_flasher.py, die benoetigten
Werkstatt-Module (bin/lib) und unter daten/ eine Offline-Kopie aller im
Manifest genannten Dateien. Vorher prueft es die SHA256-Werte des Manifests.

  python3 tools/oh-flasher/paket_bauen.py      -> tools/oh-flasher/dist/oh-flasher.zip
"""

import hashlib
import json
import os
import sys
import zipfile

FLASHER = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(FLASHER, "..", ".."))
MODULE = ["espeasy_autoconfig.py", "espeasy_configcheck.py", "espeasy_syslog.py", "espeasy_testbox.py"]


def main():
    with open(os.path.join(FLASHER, "manifest.json"), encoding="utf-8") as f:
        manifest = json.load(f)
    eintraege = [manifest["firmware"], manifest["basis_config"], *manifest["ressourcen"]]
    if "dateisystem" in manifest:
        eintraege.append(manifest["dateisystem"])
    if "am2320" in manifest:
        eintraege += [manifest["am2320"]["firmware"], manifest["am2320"]["basis_config"]]
    eintraege += [teil["regeln"] for teil in (manifest, manifest.get("am2320", {})) if "regeln" in teil]
    for e in eintraege:
        with open(os.path.join(REPO, e["pfad"]), "rb") as f:
            if hashlib.sha256(f.read()).hexdigest() != e["sha256"]:
                sys.exit(f"FEHLER: {e['pfad']} passt nicht zum Manifest - erst Kundenpaket neu erzeugen.")

    os.makedirs(os.path.join(FLASHER, "dist"), exist_ok=True)
    ziel = os.path.join(FLASHER, "dist", "oh-flasher.zip")
    with zipfile.ZipFile(ziel, "w", zipfile.ZIP_DEFLATED) as z:
        for name in ("start_flasher.bat", "Readme.md"):
            z.write(os.path.join(FLASHER, name), f"oh-flasher/{name}")
        for name in ("openandhome-flasher.ps1", "oh_flasher.py"):
            z.write(os.path.join(FLASHER, "bin", name), f"oh-flasher/bin/{name}")
        for name in MODULE:
            z.write(os.path.join(REPO, "tools", "bin", name), f"oh-flasher/bin/lib/{name}")
        python = os.path.join(FLASHER, "bin", "pythonportable")
        for wurzel, _, dateien in os.walk(python):
            for d in dateien:
                pfad = os.path.join(wurzel, d)
                z.write(pfad, "oh-flasher/bin/" + os.path.relpath(pfad, os.path.join(FLASHER, "bin")).replace(os.sep, "/"))
        z.write(os.path.join(FLASHER, "manifest.json"), "oh-flasher/daten/tools/oh-flasher/manifest.json")
        for e in eintraege:
            z.write(os.path.join(REPO, e["pfad"]), f"oh-flasher/daten/{e['pfad']}")
    print(f"{os.path.relpath(ziel, REPO)} ({os.path.getsize(ziel) / 1e6:.1f} MB), Stand {manifest['erzeugt']}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Baut ohtoolbox.zip fuer Kunden (Toolbox + OH-Flasher).

Inhalt: Starter, portables Python (Windows), oh_toolbox.py, oh_flasher.py, die
gemeinsamen Module (bin/lib) und unter daten/ eine Offline-Kopie aller Dateien
aus dem Manifest. Vorher wird geprueft, ob das Manifest zu den Dateien passt
(sonst: python3 tools/bin/oh_klassen.py ausfuehren und committen).

  python3 tools/ohtoolbox/paket_bauen.py        -> tools/ohtoolbox/dist/ohtoolbox.zip
  python3 tools/ohtoolbox/paket_bauen.py --nur-pruefen
"""

import argparse
import json
import os
import sys
import zipfile

PAKET = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(PAKET, "..", ".."))
sys.path.insert(0, os.path.join(REPO, "tools", "bin"))
from oh_klassen import MANIFEST, manifest_erzeugen  # noqa: E402

MODULE = ["espeasy_autoconfig.py", "espeasy_configcheck.py", "espeasy_syslog.py", "espeasy_testbox.py",
          "oh_klassen.py", "oh_kunde.py"]
STARTER = ["start_toolbox.bat", "start_flasher.bat", "toolbox.sh", "flasher.sh", "README.md"]


def eintraege(manifest):
    alle = list(manifest["ressourcen"])
    for teil in manifest["klassen"].values():
        for t in (teil, teil.get("am2320", {})):
            alle += [t[s] for s in ("firmware", "firmware_update", "basis_config", "regeln") if s in t]
    return alle


def main():
    parser = argparse.ArgumentParser(description="ohtoolbox.zip bauen")
    parser.add_argument("--nur-pruefen", action="store_true", help="nur pruefen, ob das Manifest aktuell ist")
    args = parser.parse_args()

    with open(os.path.join(REPO, MANIFEST), encoding="utf-8") as f:
        manifest = json.load(f)
    if manifest != manifest_erzeugen():
        sys.exit("FEHLER: manifest.json ist veraltet - python3 tools/bin/oh_klassen.py ausfuehren und committen.")
    print(f"Manifest aktuell (Stand {manifest['stand']}).")
    if args.nur_pruefen:
        return

    os.makedirs(os.path.join(PAKET, "dist"), exist_ok=True)
    ziel = os.path.join(PAKET, "dist", "ohtoolbox.zip")
    with zipfile.ZipFile(ziel, "w", zipfile.ZIP_DEFLATED) as z:
        for name in STARTER:
            info = zipfile.ZipInfo.from_file(os.path.join(PAKET, name), f"ohtoolbox/{name}")
            with open(os.path.join(PAKET, name), "rb") as f:
                z.writestr(info, f.read(), zipfile.ZIP_DEFLATED)     # Rechte der .sh behalten
        for name in ("oh_toolbox.py", "oh_flasher.py"):
            z.write(os.path.join(PAKET, "bin", name), f"ohtoolbox/bin/{name}")
        for name in MODULE:
            z.write(os.path.join(REPO, "tools", "bin", name), f"ohtoolbox/bin/lib/{name}")
        python = os.path.join(PAKET, "bin", "pythonportable")
        for wurzel, ordner, dateien in os.walk(python):
            ordner[:] = [o for o in ordner if o != "__pycache__"]
            for d in dateien:
                p = os.path.join(wurzel, d)
                z.write(p, "ohtoolbox/bin/" + os.path.relpath(p, os.path.join(PAKET, "bin")).replace(os.sep, "/"))
        z.write(os.path.join(REPO, MANIFEST), f"ohtoolbox/daten/{MANIFEST}")
        for e in eintraege(manifest):
            z.write(os.path.join(REPO, e["pfad"]), f"ohtoolbox/daten/{e['pfad']}")
    print(f"{os.path.relpath(ziel, REPO)} ({os.path.getsize(ziel) / 1e6:.1f} MB)")


if __name__ == "__main__":
    main()

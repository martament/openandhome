#!/usr/bin/env python3
"""Liest die wichtigsten Werte aus einer ESPEasy-config.dat (nur lesend, Plan B3).

Prueft vor allem die Release-Regel: in einer Stable-config.dat darf keine
Syslog-IP stehen und der Syslog-Level muss 0 sein. Exit-Code 1, wenn eine
Datei die Regel verletzt oder nicht plausibel gelesen werden kann.

Offsets nach SettingsStruct.h (ESPEasy mega), gleich fuer ESP8266 und ESP32.
Akzeptiert auch Backup-Tars (config_*.tar) und prueft dort zusaetzlich security.dat.

Beispiele:
  tools/bin/espeasy_configcheck.py configs/espeasy/professional/config.dat
  tools/bin/espeasy_configcheck.py $(git ls-files 'configs/*config.dat')
"""

import struct
import sys
import tarfile

LOGLEVEL = {0: "None", 1: "Error", 2: "Info", 3: "Debug", 4: "Debug More", 9: "Debug dev"}
SECURITY_DEFAULTS = {b"ssid", b"wpakey", b"configesp"}


def cstr(daten):
    return daten.split(b"\0", 1)[0].decode("latin-1")


def ip(daten):
    return ".".join(str(b) for b in daten)


def lese_settings(daten):
    if len(daten) < 164:
        raise ValueError("Datei zu kurz fuer SettingsStruct")
    pid, version, build = struct.unpack_from("<Iih", daten, 0)
    return {
        "PID": pid,
        "Version": version,
        "Build": build,
        "IP": ip(daten[10:14]),
        "Unit": daten[27],
        "Name": cstr(daten[28:54]),
        "NTPHost": cstr(daten[54:118]),
        "Delay": struct.unpack_from("<I", daten, 120)[0],
        "I2C SDA/SCL": f"{struct.unpack_from('<b', daten, 124)[0]}/{struct.unpack_from('<b', daten, 125)[0]}",
        "Syslog_IP": ip(daten[145:149]),
        "SyslogLevel": daten[156],
        "SerialLogLevel": daten[157],
        "WebLogLevel": daten[158],
    }


def plausibel(werte):
    name_ok = werte["Name"] != "" and werte["Name"].isprintable()
    level_ok = all(werte[k] in LOGLEVEL for k in ("SyslogLevel", "SerialLogLevel", "WebLogLevel"))
    return name_ok and level_ok


def pruefe_security(daten):
    """True, wenn security.dat nur Defaults bzw. leere Felder enthaelt."""
    worte = {w for w in daten.split(b"\0") if len(w) >= 4 and w.isascii() and w.decode().isprintable()}
    return worte <= SECURITY_DEFAULTS


def pruefe(name, daten):
    werte = lese_settings(daten)
    print(f"== {name}")
    for k, v in werte.items():
        if k.endswith("LogLevel") or k == "SyslogLevel":
            v = f"{v} ({LOGLEVEL.get(v, '?')})"
        print(f"   {k:<15} {v}")
    fehler = []
    if not plausibel(werte):
        fehler.append("Werte unplausibel - anderes Struct-Layout (alte ESPEasy-Version?)")
    if werte["Syslog_IP"] != "0.0.0.0" or werte["SyslogLevel"] != 0:
        fehler.append("Syslog aktiv - nicht als Stable-config.dat verwenden")
    return fehler


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(2)
    gesamt = 0
    for pfad in sys.argv[1:]:
        try:
            if tarfile.is_tarfile(pfad):
                with tarfile.open(pfad) as tar:
                    fehler = pruefe(f"{pfad}:config.dat", tar.extractfile("config.dat").read())
                    if "security.dat" in tar.getnames() and not pruefe_security(tar.extractfile("security.dat").read()):
                        fehler.append("security.dat enthaelt Nicht-Default-Werte (WLAN/Passwort) - nicht committen")
            else:
                with open(pfad, "rb") as f:
                    fehler = pruefe(pfad, f.read())
        except (OSError, ValueError, KeyError) as e:
            fehler = [str(e)]
            print(f"== {pfad}")
        for text in fehler:
            print(f"   !! {text}")
        print(f"   -> {'NICHT OK' if fehler else 'OK'}")
        gesamt += bool(fehler)
    sys.exit(1 if gesamt else 0)


if __name__ == "__main__":
    main()

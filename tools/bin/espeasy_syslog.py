#!/usr/bin/env python3
"""Syslog einer ESPEasy-Box per HTTP an- oder abschalten (Plan T1/T2).

ESPEasy hat kein Syslog-Kommando; Syslog-IP und -Level stehen auf
Tools -> Advanced (/advanced). Das Skript liest das komplette Formular,
aendert nur Syslog-IP und Syslog-Level und schickt alle anderen Felder
unveraendert zurueck - ESPEasy setzt fehlende Checkboxen sonst auf "aus".

Beispiele:
  tools/bin/espeasy_syslog.py 192.168.9.50 status
  tools/bin/espeasy_syslog.py 192.168.9.50 an            # 192.168.9.4, Level Info
  tools/bin/espeasy_syslog.py 192.168.9.50 aus
  tools/bin/espeasy_syslog.py 192.168.9.50 an --passwort geheim
"""

import argparse
import http.client
import http.cookiejar
import re
import socket
import sys
import urllib.parse
import urllib.request
from html.parser import HTMLParser

TEST_SYSLOG_IP = "192.168.9.4"
LEVEL_INFO = "2"
SYSLOG_PORT = "514"


class FormParser(HTMLParser):
    """Sammelt alle Felder so, wie ein Browser sie absenden wuerde."""

    def __init__(self):
        super().__init__()
        self.felder = {}
        self.reihenfolge = []
        self._select = None
        self._select_erste = None

    def _setze(self, name, wert):
        if name not in self.felder:
            self.reihenfolge.append(name)
        self.felder[name] = wert

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        name = a.get("name")
        if tag == "input" and name:
            typ = (a.get("type") or "text").lower()
            if typ in ("checkbox", "radio"):
                if "checked" in a:
                    self._setze(name, a.get("value", "on"))
            elif typ not in ("submit", "button", "file"):
                self._setze(name, a.get("value", ""))
        elif tag == "select" and name:
            self._select, self._select_erste = name, None
        elif tag == "option" and self._select:
            wert = a.get("value", "")
            if self._select_erste is None:
                self._select_erste = wert
            if "selected" in a:
                self._setze(self._select, wert)

    def handle_endtag(self, tag):
        if tag == "select" and self._select:
            if self._select not in self.felder and self._select_erste is not None:
                self._setze(self._select, self._select_erste)
            self._select = None


class Box:
    def __init__(self, host, passwort):
        self.basis = f"http://{host}"
        self.cookies = http.cookiejar.CookieJar()
        self.oeffner = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(self.cookies))
        if passwort:
            self.post("/login", {"password": passwort})

    def get(self, pfad):
        try:
            with self.oeffner.open(self.basis + pfad, timeout=15) as antwort:
                return antwort.read().decode("utf-8", "replace")
        except http.client.BadStatusLine:
            # ESPEasy liefert .esp-Seiten ohne HTTP-Header (nur Body) -> roh lesen
            return self._get_roh(pfad)

    def _get_roh(self, pfad):
        host = urllib.parse.urlsplit(self.basis).netloc
        cookies = "; ".join(f"{c.name}={c.value}" for c in self.cookies)
        anfrage = f"GET {pfad} HTTP/1.0\r\nHost: {host}\r\n"
        if cookies:
            anfrage += f"Cookie: {cookies}\r\n"
        teile = []
        with socket.create_connection((host.split(":")[0], int(host.partition(":")[2] or 80)), timeout=15) as s:
            s.sendall((anfrage + "Connection: close\r\n\r\n").encode())
            while daten := s.recv(4096):
                teile.append(daten)
        text = b"".join(teile).decode("utf-8", "replace")
        if text.startswith("HTTP/"):
            text = text.split("\r\n\r\n", 1)[-1]
        return text

    def post(self, pfad, felder):
        daten = urllib.parse.urlencode(felder).encode()
        with self.oeffner.open(self.basis + pfad, data=daten, timeout=15) as antwort:
            return antwort.read().decode("utf-8", "replace")


def lies_formular(html):
    parser = FormParser()
    parser.feed(html)
    felder = parser.felder
    if "syslogip" not in felder:
        if "password" in felder:
            sys.exit("FEHLER: Box verlangt das Admin-Passwort (--passwort).")
        sys.exit("FEHLER: Feld 'syslogip' nicht gefunden - ist das eine ESPEasy-Box?")
    kandidaten = [n for n in felder if re.search(r"syslog", n, re.I) and re.search(r"level|lvl", n, re.I)]
    if len(kandidaten) != 1:
        sys.exit(f"FEHLER: Syslog-Level-Feld nicht eindeutig: {kandidaten or 'keins'}; Felder: {sorted(felder)}")
    return felder, kandidaten[0]


def zeige(felder, level_feld):
    print(f"Syslog-IP:    {felder['syslogip'] or '(leer)'}, UDP-Port {felder.get('syslogport', '?')}")
    print(f"Syslog-Level: {felder[level_feld]} (Feld '{level_feld}')")


def main():
    parser = argparse.ArgumentParser(description="Syslog einer ESPEasy-Box per HTTP setzen/loeschen.")
    parser.add_argument("host", help="IP oder Hostname der Box")
    parser.add_argument("aktion", choices=["status", "an", "aus"])
    parser.add_argument("--ip", default=TEST_SYSLOG_IP, help=f"Syslog-Server (Standard {TEST_SYSLOG_IP})")
    parser.add_argument("--level", default=LEVEL_INFO, help="Syslog-Level bei 'an' (Standard 2 = Info)")
    parser.add_argument("--passwort", help="Admin-Passwort der Box, falls gesetzt")
    args = parser.parse_args()

    setze_syslog(Box(args.host, args.passwort), args.aktion, args.ip, args.level)


def setze_syslog(box, aktion, ip=TEST_SYSLOG_IP, level=LEVEL_INFO):
    """aktion: 'status', 'an' oder 'aus'. Beendet mit Fehler, wenn die Box die Werte nicht uebernimmt."""
    felder, level_feld = lies_formular(box.get("/advanced"))
    zeige(felder, level_feld)
    if aktion == "status":
        return

    felder["syslogip"] = ip if aktion == "an" else "0.0.0.0"
    felder["syslogport"] = SYSLOG_PORT      # Basis-config hatte 5140, der Server lauscht auf 514
    felder[level_feld] = level if aktion == "an" else "0"
    felder["edit"] = "1"
    print(f"\nSende: Syslog-IP {felder['syslogip']}, Level {felder[level_feld]} ...")
    box.post("/advanced", felder)

    neu, _ = lies_formular(box.get("/advanced"))
    zeige(neu, level_feld)
    soll_ip = {"an": ip, "aus": "0.0.0.0"}[aktion]
    if (neu["syslogip"] not in (soll_ip, "" if soll_ip == "0.0.0.0" else soll_ip) or neu[level_feld] != felder[level_feld]
            or neu.get("syslogport", SYSLOG_PORT) != SYSLOG_PORT):
        sys.exit("FEHLER: Box hat die Werte nicht uebernommen.")
    geaendert = [n for n in felder if n not in ("syslogip", "syslogport", level_feld, "edit") and neu.get(n) != felder[n]]
    if geaendert:
        print(f"WARNUNG: weitere Felder haben sich geaendert: {geaendert}")
    print("OK - gespeichert.")


if __name__ == "__main__":
    main()

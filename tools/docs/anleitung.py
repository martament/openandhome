#!/usr/bin/env python3
"""Baut die Bedienungsanleitungen aus der Word-Vorlage tools/docs/vorlage.docx.

Je eine Anleitung fuer alle Professional- und fuer alle Standalone-Boxen: keine
Angaben zu einzelnen Ausstattungen (Fuehleranzahl, Zusatzsensoren) oder Firmware-Versionen.

Standalone und Professional sind verschiedene Boxen (Gehaeuse, Board, Fuehler,
Stromversorgung) - box-spezifische Inhalte stehen getrennt je Variante, nur
allgemeine Bausteine (Messreihe, Sicherheit, Konformitaet, Entsorgung, Kontakt,
allgemeine Fehlerbilder) werden geteilt.

Vorlage (Formatvorlagen, Kopf-/Fusszeile, Logo, Nummerierung) bleibt erhalten,
nur der Inhalt von word/document.xml wird ersetzt.

  python3 tools/docs/anleitung.py --variante professional
  python3 tools/docs/anleitung.py --variante standalone
"""

import argparse
import os
import re
import zipfile
from xml.sax.saxutils import escape

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
# Vorlage: Formatvorlagen, Kopf-/Fusszeile, Logo, Nummerierung (urspruenglich aus der Anleitung 2023.1)
VORLAGE = os.path.join(ROOT, "tools/docs/vorlage.docx")
ZIELE = {
    "professional": "docs/2026 openandhome - Bedienungsanleitung - Professional.docx",
    "standalone": "docs/2026 openandhome - Bedienungsanleitung - Standalone.docx",
}
TITEL = {
    "professional": "Bedienungsanleitung Sensorbox Professional",
    "standalone": "Bedienungsanleitung Sensorbox Standalone",
}
STAND = "Stand: 12.11.2026"
DATUM_ISO = "2026-11-12T12:00:00Z"
FIRMA = "Ament & Heinrichs OpenandHome GbR"
SEITE_BREITE = 10432          # A4 minus Raender (737 dxa je Seite)
NUM_SCHRITTE, NUM_PUNKTE, NUM_SCHRITTE_2 = 1, 2, 13   # 13 wird beim Bauen angelegt (Neustart bei A)


# --- Bausteine fuer WordprocessingML ---
def lauf(text, fett=False, groesse=None, kursiv=False):
    rpr = ""
    if fett:
        rpr += "<w:b/><w:bCs/>"
    if kursiv:
        rpr += "<w:i/><w:iCs/>"
    if groesse:
        rpr += f'<w:sz w:val="{groesse}"/><w:szCs w:val="{groesse}"/>'
    rpr = f"<w:rPr>{rpr}</w:rPr>" if rpr else ""
    return f'<w:r>{rpr}<w:t xml:space="preserve">{escape(text)}</w:t></w:r>'


def absatz(*teile, stil=None, nummer=None, mitte=False, abstand_vor=None, zusammen=False):
    """teile: Strings (normal) oder (text, {'fett':..}) Tupel."""
    ppr = ""
    if stil:
        ppr += f'<w:pStyle w:val="{stil}"/>'
    if zusammen:
        ppr += "<w:keepNext/>"
    if nummer:
        ppr += f'<w:numPr><w:ilvl w:val="0"/><w:numId w:val="{nummer}"/></w:numPr>'
    if abstand_vor:
        ppr += f'<w:spacing w:before="{abstand_vor}"/>'
    if mitte:
        ppr += '<w:jc w:val="center"/>'
    runs = "".join(lauf(t) if isinstance(t, str) else lauf(t[0], **t[1]) for t in teile)
    return f'<w:p>{"<w:pPr>" + ppr + "</w:pPr>" if ppr else ""}{runs}</w:p>'


def ueberschrift(text):
    return absatz((text, {"fett": True, "groesse": 26}), abstand_vor=240, zusammen=True)


def punkt(*teile):
    return absatz(*teile, stil="Listenabsatz", nummer=NUM_PUNKTE)


def schritt(*teile, liste=NUM_SCHRITTE):
    return absatz(*teile, stil="Listenabsatz", nummer=liste)


def fett(text):
    return (text, {"fett": True})


def tabelle(zeilen, breite_links=3400):
    breiten = (breite_links, SEITE_BREITE - breite_links)
    rand = "".join(f'<w:{s} w:val="single" w:sz="4" w:space="0" w:color="000001"/>'
                   for s in ("top", "left", "bottom", "right"))
    xml = (f'<w:tbl><w:tblPr><w:tblW w:w="{SEITE_BREITE}" w:type="dxa"/>'
           f'<w:tblBorders>{rand}<w:insideH w:val="single" w:sz="4" w:space="0" w:color="000001"/>'
           f'<w:insideV w:val="single" w:sz="4" w:space="0" w:color="000001"/></w:tblBorders><w:tblLayout w:type="fixed"/>'
           f'<w:tblCellMar><w:top w:w="55" w:type="dxa"/><w:left w:w="80" w:type="dxa"/>'
           f'<w:bottom w:w="55" w:type="dxa"/><w:right w:w="80" w:type="dxa"/></w:tblCellMar></w:tblPr>'
           f'<w:tblGrid><w:gridCol w:w="{breiten[0]}"/><w:gridCol w:w="{breiten[1]}"/></w:tblGrid>')
    for links, rechts in zeilen:
        xml += "<w:tr><w:trPr><w:cantSplit/></w:trPr>"
        for i, inhalt in enumerate((links, rechts)):
            absaetze = inhalt if isinstance(inhalt, list) else [inhalt]
            inner = "".join(absatz((a, {"fett": i == 0})) for a in absaetze)
            xml += f'<w:tc><w:tcPr><w:tcW w:w="{breiten[i]}" w:type="dxa"/></w:tcPr>{inner}</w:tc>'
        xml += "</w:tr>"
    return xml + "</w:tbl>" + absatz("")


# --- Gemeinsame Bausteine ---
DS18B20_DATEN = ["DS18B20 in Edelstahlhülse Ø 6 × 50 mm, wasserdicht, schwarzes Kabel",
                 "Messbereich −20 °C bis +125 °C",
                 "Genauigkeit ±0,5 °C im Bereich −10 °C bis +85 °C (Herstellerangabe)"]
WASSER_DATEN = ["Typ WLS-06, schwarz, ABS, Temperaturbereich −20 °C bis +80 °C",
                "Meldet eindringendes Wasser; auch als Überwachungs- oder Türkontakt nutzbar"]
SOFTWARE = "ESPEasy (quelloffen); die installierte Version zeigt die Weboberfläche unter „Tools“ → „Info“"
HTU21D_DATEN = ["HTU21D für Temperatur und relative Luftfeuchtigkeit",
                "Luftfeuchtigkeit 0–100 % rF, Genauigkeit typ. ±2 % rF (20–80 % rF)",
                "Temperatur −40 °C bis +125 °C, Genauigkeit typ. ±0,3 °C"]


def einleitung(t, gilt_fuer):
    t.append(absatz("Diese Anleitung gilt für:"))
    t.append(absatz(*gilt_fuer))
    t.append(absatz("Diese Bedienungsanleitung enthält wichtige Informationen zur Inbetriebnahme und Handhabung. "
                    "Lesen Sie sie aufmerksam durch und bewahren Sie sie sorgfältig auf. "
                    "Beachten Sie unbedingt die Sicherheitshinweise in dieser Anleitung!"))


def anwendungsbereich(t, beispiele):
    t.append(ueberschrift("Anwendungsbereich"))
    t.append(absatz("Die Sensorbox ist in einem feuchtigkeitsgeschützten Gehäuse eingebaut und eignet sich für den "
                    "Innen- und den geschützten Außenbereich, privat wie gewerblich. Einige Beispiele:"))
    for b in beispiele:
        t.append(punkt(b))


def hinweis_ip_bereich(t):
    t.append(absatz(fett("Hinweis: "),
                    "Die Weboberfläche ist ab Werk nur aus Netzen mit Adressen 192.168.x.x erreichbar. Nutzen Sie "
                    "ein anderes Netz (z. B. 10.x.x.x), wenden Sie sich bitte an unseren Support."))


def abrufen(t, mit_zabbix):
    t.append(ueberschrift("Messwerte abrufen und einbinden"))
    t.append(tabelle([
        ("Dashboard", "http://<Adresse>/openandhome.esp"),
        ("JSON (alle Werte)", "http://<Adresse>/json"),
        ("Prometheus-Metriken", "http://<Adresse>/metrics"),
        ("Einstellungen", "http://<Adresse>/ (Menü Config, Controllers, Devices)"),
    ]))
    t.append(absatz(fett("MQTT (z. B. openHAB, Home Assistant, ioBroker, Node-RED, openandhome-Datenlogger): "),
                    "Menü „Controllers“ → Controller 1 „Home Assistant (openHAB) MQTT“ → „Edit“. Tragen Sie Ihren "
                    "MQTT-Server ein, setzen Sie den Haken bei „Enabled“ und speichern Sie mit „Submit“. Die Werte "
                    "erscheinen unter openandhome/<Name>/<Fühler>/<Messwert>, z. B. "
                    "openandhome/Sensorbox1/Fuehler1/Temperatur."))
    if mit_zabbix:
        t.append(absatz(fett("Zabbix: "),
                        "Menü „Controllers“ → Controller 2 „Zabbix“ → „Edit“, Zabbix-Server eintragen, „Enabled“ "
                        "setzen und mit „Submit“ speichern."))
    t.append(absatz("Weitere Möglichkeiten beschreibt die Dokumentation der Software ESPEasy: "
                    "https://espeasy.readthedocs.io"))


def toolbox(t, professional):
    """Abschnitt zur openandhome-Toolbox (Standardwerkzeug, USB)."""
    t.append(ueberschrift("openandhome-Toolbox"))
    t.append(absatz("Mit der Toolbox richten Sie die Sensorbox über das USB-Kabel ein und beheben die häufigsten "
                    "Probleme. Download: ", fett("https://github.com/martament/openandhome/releases/latest"),
                    " – dort „ohtoolbox.zip“ herunterladen, entpacken und „start_toolbox.bat“ (Windows) bzw. "
                    "„toolbox.sh“ (Linux) starten."))
    if professional:
        t.append(absatz(fett("Achtung: "), "Ziehen Sie vorher das PoE-Netzwerkkabel ab – USB und PoE nie gleichzeitig. "
                        "Für die Funktionen „Sensoren neu erkennen“ und „Grundkonfiguration“ verbindet sich die "
                        "Sensorbox kurz mit Ihrem WLAN; die Daten werden danach wieder gelöscht."))
    for b in ("Sensoren neu erkennen – nach dem Tausch oder Hinzufügen eines Fühlers",
              "Zeitserver (NTP) setzen, Gerätename ändern",
              *(() if professional else ("WLAN-Zugangsdaten setzen (mit Verbindungsprüfung) oder löschen",)),
              "Grundkonfiguration wiederherstellen, IP-Filter oder Admin-Passwort zurücksetzen",
              "Notfall und Updates: der mitgelieferte OH-Flasher („start_flasher.bat“ bzw. „flasher.sh“)"):
        t.append(punkt(b))


def messreihe(t):
    t.append(ueberschrift("Messreihe"))
    t.append(absatz("Der Golden Master Sensorbox Openandhome wurde in einer Messreihe mit einem geeichten Testo 112 "
                    "(NTC −25…120 °C) kalibriert. Alle ausgelieferten Sensorboxen werden mit einer Vergleichsmessung "
                    "am Golden Master geprüft und vor der Auslieferung 24 Stunden im Dauerbetrieb getestet. "
                    "Abweichungen liegen bei maximal ±0,5 °C gegenüber dem Golden Master."))


def sicherheit(t, speziell):
    t.append(ueberschrift("Sicherheitshinweise / Risikobewertung"))
    for b in [*speziell,
              "Die Sensorbox ist in einem stabilen Gehäuse eingebaut; schützen Sie sie zusätzlich gegen Schlag.",
              "Betreiben Sie die Sensorbox nicht in unmittelbarer Nähe von Strahlungsquellen wie Mikrowellen, "
              "Elektromotoren oder Pumpen.",
              "Die Sensorbox ist nicht für Kinder und Tiere geeignet.",
              "Die Geräte dürfen nicht in explosionsgefährdeten Bereichen verwendet werden.",
              "Öffnen Sie das Gerät nicht eigenmächtig.",
              "Für Schäden durch unsachgemäßen Umgang, Veränderung oder Nichtbeachtung dieser Anleitung übernehmen "
              "wir keine Haftung."]:
        t.append(punkt(b))
    t.append(absatz("In einer internen Testreihe zur allgemeinen Produktsicherheit wurde unser Produkt als sicher "
                    "eingestuft. Haben Sie Verbesserungsvorschläge, schreiben Sie uns – wir prüfen jede Anregung."))


def konformitaet_entsorgung(t):
    t.append(ueberschrift("Konformitätserklärung"))
    t.append(absatz("Die Konformitätserklärung finden Sie im Onlineshop beim Produkt. Die vollständige Erklärung "
                    "erhalten Sie auch per E-Mail an info@openandhome.de."))
    t.append(ueberschrift("Entsorgungshinweise"))
    t.append(punkt("Entsorgen Sie das Gerät nicht im Hausmüll; beachten Sie die geltenden Entsorgungsvorschriften."))
    t.append(punkt("Altgeräte können Sie direkt an uns zurückgeben. So vermeiden wir Elektroschrott und nutzen "
                   "Rohstoffe weiter."))


FEHLER_HTTPS = ("Webseite ist nicht erreichbar",
                "Achten Sie darauf, dass die Adresse mit http:// beginnt. Manche Browser ersetzen sie durch "
                "https://, die Sensorbox ist aber nur über http:// erreichbar.")
FEHLER_IP_BLOCKED = ("Meldung „IP blocked“",
                     "Ihr Netz verwendet keine Adressen 192.168.x.x. Mit der Toolbox („IP-Filter zurücksetzen“) "
                     "ist die Weboberfläche bis zum nächsten Neustart erreichbar; dauerhaft passen Sie den Bereich "
                     "unter „Config“ → „Client IP filtering“ an oder wenden sich an unseren Support.")
FEHLER_TEMPERATUR = ("Angezeigte Temperatur ist zu hoch oder zu niedrig",
                     "Nach einem Standortwechsel braucht der Fühler einige Minuten. Für eine Differenz von ±5 °C "
                     "sind etwa 10 Minuten Wartezeit nötig.")


def schluss(t):
    t.append(absatz(f"Irrtum und technische Änderungen vorbehalten. {STAND}", mitte=True, abstand_vor=240))
    t.append(absatz("Kopieren der Bedienungsanleitung in jeglicher Form (auch auszugsweise) nur nach schriftlicher "
                    "Zustimmung.", mitte=True))
    t.append(ueberschrift("Kontakt"))
    t.append(absatz("Fragen zum Produkt: info@openandhome.de"))
    t.append(absatz("Onlineshop: https://openandhome.de"))
    t.append(absatz("Ament & Heinrichs OpenandHome GbR, Kirchstraße 6, 97511 Lülsfeld"))


# --- Professional (Olimex ESP32-POE, nicht ISO, PoE) ---
def inhalt_professional():
    t = []
    einleitung(t, [fett("Sensorbox Professional"),
                   " (alle Ausführungen) – Netzwerkanschluss mit Stromversorgung über das Netzwerkkabel (PoE), "
                   "je nach Ausstattung mit Temperaturfühlern, Kombifühler für Temperatur und Luftfeuchtigkeit, "
                   "Wassersensor und Display."])

    t.append(ueberschrift("Funktionsbeschreibung"))
    t.append(absatz("Die Sensorbox misst je nach Ausstattung mit bis zu vier Temperaturfühlern (DS18B20), einem "
                    "Kombifühler für Temperatur und Luftfeuchtigkeit (HTU21D) und einem Wassersensor, der "
                    "eindringendes Wasser meldet oder als Überwachungs- bzw. Türkontakt dient."))
    t.append(absatz("Strom und Netzwerk erhält die Sensorbox über ein einziges Netzwerkkabel (Power over Ethernet, "
                    "PoE) – ein Netzteil ist nicht nötig."))
    t.append(absatz("Ein Display (je nach Ausstattung) zeigt die aktuellen Messwerte sowie abwechselnd die "
                    "Netzwerkadresse (IP-Adresse) und den Namen der Sensorbox. Die Sensorbox bezieht ihre "
                    "IP-Adresse automatisch von Ihrem Router (DHCP)."))
    t.append(absatz("Über eine eingebaute Webseite (Dashboard) rufen Sie die Werte im Browser ab. Für die Einbindung "
                    "in Ihre Systeme stellt die Sensorbox die Messwerte als JSON und als Prometheus-Metriken bereit "
                    "und kann sie per MQTT oder an Zabbix weitergeben. Ab Werk sendet die Sensorbox keine Daten aus "
                    "Ihrem Netz."))
    anwendungsbereich(t, ["Server- und Netzwerkschränke sowie Serverräume (Temperatur, Luftfeuchtigkeit, "
                          "Wassereintritt, Türkontakt)",
                          "Heizung: Vorlauf, Rücklauf, Boiler, Solaranlage",
                          "Kühl- und Lagerräume (z. B. Wildbret), Klimaüberwachung",
                          "Temperaturüberwachung bei Schüttgut (z. B. Getreide)"])

    t.append(ueberschrift("Inbetriebnahme"))
    t.append(schritt("Verbinden Sie die Sensorbox mit einem Netzwerkkabel mit einem Netzwerkanschluss, der PoE "
                     "liefert (PoE-Switch oder PoE-Injektor nach IEEE 802.3af)."))
    t.append(schritt("Die Sensorbox startet. Nach etwa einer halben Minute ist sie im Netz erreichbar; mit Display "
                     "zeigt sie die Messwerte sowie abwechselnd die IP-Adresse und den Namen „Sensorbox1“."))
    t.append(schritt("Öffnen Sie im Browser das Dashboard: ", fett("http://<IP-Adresse>/openandhome.esp"),
                     " – die IP-Adresse lesen Sie im Display oder in Ihrem Router ab. Je nach Router funktioniert auch ",
                     fett("http://sensorbox1/openandhome.esp"), " (bei einer FRITZ!Box auch http://sensorbox1.fritz.box)."))
    t.append(schritt("Das Dashboard zeigt die Werte aller angeschlossenen Fühler. Der Wassersensor meldet 0 "
                     "(trocken bzw. Kontakt offen) oder 1 (Wasser erkannt bzw. Kontakt geschlossen). Speichern Sie die "
                     "Adresse als Lesezeichen."))
    t.append(schritt("Setzen Sie mehrere Sensorboxen ein, geben Sie jeder einen eigenen Namen: ",
                     fett("http://<IP-Adresse>/config"), ", Feld „Unit Name“ ändern und mit „Submit“ speichern."))
    t.append(schritt("Empfehlung: Vergeben Sie auf derselben Seite ein Administrator-Passwort, damit niemand in Ihrem "
                     "Netz die Einstellungen ändern kann."))
    hinweis_ip_bereich(t)

    t.append(ueberschrift("Uhrzeit (Zeitserver)"))
    t.append(absatz("Die Sensorbox holt die Uhrzeit ab Werk aus Ihrem eigenen Netz: etwa eine halbe Minute nach "
                    "dem Start von Ihrem Router, sonst von 192.168.178.1 (Standard der FRITZ!Box). Erst wenn beide "
                    "15 Minuten lang nicht antworten, fragt sie im Internet nach (de.pool.ntp.org). Damit sie ohne "
                    "Internet auskommt, muss Ihr Router als Zeitserver arbeiten (FRITZ!Box: "
                    "„Heimnetz > Netzwerk > Netzwerkeinstellungen > Zeitsynchronisation“)."))
    t.append(absatz("Einen eigenen Zeitserver (z. B. de.pool.ntp.org im Internet) tragen Sie unter ",
                    fett("http://<IP-Adresse>/advanced"), " im Feld „NTP Hostname“ ein, setzen den Haken bei "
                    "„Use NTP“, entfernen den Haken bei „Rules“ und speichern mit „Submit“."))
    t.append(absatz("Alternativ setzen Sie den Zeitserver mit der openandhome-Toolbox (Menüpunkt „Zeitserver (NTP) "
                    "setzen“; Download unter https://github.com/martament/openandhome/releases/latest). "
                    "Die Toolbox verbindet sich über den USB-Anschluss im Inneren der Sensorbox."))
    t.append(absatz(fett("Achtung: "), "Ziehen Sie vorher unbedingt das PoE-Netzwerkkabel ab. USB und PoE dürfen "
                    "nie gleichzeitig angeschlossen sein – der Messumformer ist nicht galvanisch getrennt, "
                    "angeschlossene Geräte können beschädigt werden. Die Sensorbox wird während der Einstellung über "
                    "USB versorgt; stecken Sie danach erst das USB-Kabel ab und dann das Netzwerkkabel wieder an."))
    abrufen(t, mit_zabbix=True)

    toolbox(t, professional=True)

    t.append(ueberschrift("Ihre Sensorbox Professional"))
    for b in ("Mit deutscher Bedienungsanleitung und deutschem Support",
              "Keine Datenübertragung aus Ihrem Netz",
              "Mit quelloffener Software (ESPEasy)",
              "Vorbereitet für Zabbix, Prometheus, MQTT, Centreon, Nagios, JSON- und HTTP-Schnittstellen"):
        t.append(punkt(b))
    messreihe(t)

    t.append(ueberschrift("Technische Daten"))
    t.append(tabelle([
        ("Gehäuse", "Kunststoffgehäuse 155 × 90 × 62 mm (L × B × H), grau/klar, feuchtigkeitsbeständig und staubdicht"),
        ("Messumformer", "Olimex ESP32-POE mit Ethernet (10/100 Mbit/s), nicht galvanisch getrennt"),
        ("Stromversorgung", "Power over Ethernet nach IEEE 802.3af über das Netzwerkkabel"),
        ("Netzwerk", "Ethernet, IP-Adresse per DHCP"),
        ("Software", SOFTWARE),
        ("Temperaturfühler (je nach Ausstattung bis zu 4)", DS18B20_DATEN),
        ("Kombifühler (je nach Ausstattung)", HTU21D_DATEN),
        ("Wassersensor (je nach Ausstattung)", WASSER_DATEN),
        ("Display (je nach Ausstattung)", "OLED-Display: Messwerte, IP-Adresse und Gerätename"),
        ("Kabeldurchführungen", "Gummitüllen M16/M25 aus EPDM, grau"),
    ]))
    sicherheit(t, [
        "Betreiben Sie die Sensorbox nur an einem PoE-Anschluss nach IEEE 802.3af (PoE-Switch oder PoE-Injektor).",
        "Der USB-Anschluss im Inneren ist nur für unseren Service vorgesehen. Er darf nie gleichzeitig mit dem "
        "PoE-Netzwerkkabel verbunden sein: Der Messumformer ist nicht galvanisch von der PoE-Versorgung getrennt, "
        "angeschlossene Geräte können beschädigt werden.",
        "Ein Kombifühler misst die Luftfeuchtigkeit; tauchen Sie ihn nicht in Wasser und schützen Sie ihn vor "
        "Kondenswasser.",
    ])
    konformitaet_entsorgung(t)

    t.append(ueberschrift("Fehlerbeschreibung"))
    t.append(tabelle([
        FEHLER_HTTPS,
        ("Sensorbox startet nicht, nicht im Netz",
         "Prüfen Sie, ob der Netzwerkanschluss PoE liefert (Anschluss am PoE-Switch aktiv bzw. Injektor mit Strom "
         "versorgt) und ob das Kabel richtig eingesteckt ist. Versuchen Sie einen anderen PoE-Anschluss."),
        ("IP-Adresse unbekannt",
         "Lesen Sie die IP-Adresse im Display ab (falls vorhanden) oder suchen Sie in Ihrem Router nach dem Gerät "
         "„Sensorbox1“."),
        FEHLER_IP_BLOCKED,
        ("Ein Fühler zeigt keinen Wert oder „NaN“",
         "Prüfen Sie Kabel und Stecker des Fühlers. Starten Sie die Sensorbox neu, indem Sie das Netzwerkkabel "
         "für etwa 10 Sekunden abziehen."),
        FEHLER_TEMPERATUR,
    ], breite_links=3600))
    schluss(t)
    return "".join(t)


# --- Standalone (WeMos D1 mini, ESP8266, WLAN, USB-Netzteil) ---
def inhalt_standalone():
    t = []
    einleitung(t, [fett("Sensorbox Standalone"),
                   " (alle Ausführungen) – Sensorbox mit WLAN und Stromversorgung über USB, je nach Ausstattung mit "
                   "Temperaturfühlern, Kombifühler für Temperatur und Luftfeuchtigkeit, Wassersensor, Abstandssensor "
                   "und Display."])

    t.append(ueberschrift("Funktionsbeschreibung"))
    t.append(absatz("Die Sensorbox misst je nach Ausstattung mit bis zu vier Temperaturfühlern (DS18B20), einem "
                    "Kombifühler für Temperatur und Luftfeuchtigkeit (HTU21D oder AM2320), einem Wassersensor oder "
                    "einem Abstandssensor (z. B. für Füllstände). Die angeschlossenen Fühler werden bei der Einrichtung "
                    "in unserer Werkstatt automatisch erkannt."))
    t.append(absatz("Die Stromversorgung erfolgt über ein USB-Kabel. Ein Netzteil ist nicht im Lieferumfang "
                    "enthalten; Sie benötigen ein USB-Netzteil mit 5 Volt DC und mindestens 500 mA."))
    t.append(absatz("Die Sensorbox wird in Ihr WLAN eingebunden. Alternativ öffnet sie ein eigenes WLAN, über das "
                    "Sie die Werte direkt mit dem Smartphone abrufen (geringe Reichweite). Über eine eingebaute "
                    "Webseite (Dashboard) sehen Sie die Werte im Browser. Ab Werk sendet die Sensorbox keine Daten "
                    "aus Ihrem Netz."))
    anwendungsbereich(t, ["Kühlschrank-, Gefrier- und Kühlraumtemperatur",
                          "Heizung: Vorlauf, Rücklauf, Boiler, Solaranlage",
                          "Pool, Schwimmbad, Gartenteich, Sauna",
                          "Außen- und Zimmertemperatur, Luftfeuchtigkeit im Raum",
                          "Lagertemperatur (z. B. Wildbret), Schüttgut (z. B. Getreide)"])

    t.append(ueberschrift("Inbetriebnahme mit Ihrem WLAN-Router (Reichweite im gesamten WLAN)"))
    t.append(schritt("Versorgen Sie die Sensorbox über das USB-Kabel mit Strom (USB-Netzteil 5 V, mindestens 500 mA)."))
    t.append(schritt("Öffnen Sie an Ihrem Smartphone oder Laptop die WLAN-Einstellungen und suchen Sie nach Netzen. "
                     "Die Sensorbox öffnet nach kurzer Zeit ein eigenes WLAN mit dem Namen ", fett("„Sensorbox1“"), "."))
    t.append(schritt("Verbinden Sie sich mit diesem WLAN. Das Passwort lautet: ", fett("configesp")))
    t.append(schritt("Erscheint eine Meldung wie „Keine Internetverbindung“, behalten Sie die Verbindung trotzdem bei."))
    t.append(schritt("Öffnen Sie im Browser die Adresse ", fett("http://192.168.4.1/setup"), "."))
    t.append(schritt("Wählen Sie Ihr WLAN aus der Liste oder tragen Sie den Namen ein, geben Sie das Passwort Ihres "
                     "WLANs ein und speichern Sie mit „Connect“."))
    t.append(schritt("Die Sensorbox verbindet sich mit Ihrem WLAN. Verbinden Sie Ihr Smartphone oder Ihren Laptop "
                     "wieder mit Ihrem eigenen WLAN."))
    t.append(schritt("Öffnen Sie das Dashboard: ", fett("http://sensorbox1/openandhome.esp"),
                     " (bei einer FRITZ!Box auch http://sensorbox1.fritz.box). Mit Display sehen Sie dort auch die "
                     "IP-Adresse; dann funktioniert ", fett("http://<IP-Adresse>/openandhome.esp"), "."))
    t.append(schritt("Ist die Sensorbox nicht erreichbar, suchen Sie in Ihrem Router unter „Heimnetz“ nach dem Gerät "
                     "„Sensorbox1“. Es kann einen Moment dauern, bis der Name erreichbar ist."))
    t.append(schritt("Empfehlung: Vergeben Sie unter ", fett("http://sensorbox1/config"),
                     " ein Administrator-Passwort. Setzen Sie mehrere Sensorboxen ein, geben Sie dort jeder einen "
                     "eigenen Namen („Unit Name“)."))
    hinweis_ip_bereich(t)

    t.append(absatz(fett("Alternativ mit der openandhome-Toolbox: "),
                    "Verbinden Sie die Sensorbox per USB-Kabel mit Ihrem Rechner, starten Sie die Toolbox und wählen "
                    "Sie „WLAN-Zugangsdaten setzen“. Die Toolbox prüft die Verbindung und zeigt am Ende die Adresse "
                    "Ihres Dashboards (Download siehe Abschnitt „openandhome-Toolbox“)."))

    t.append(ueberschrift("Inbetriebnahme nur mit dem Smartphone (geringe Reichweite)"))
    t.append(absatz("Diese Möglichkeit nutzen Sie, wenn am Einsatzort kein WLAN vorhanden ist."))
    t.append(schritt("Versorgen Sie die Sensorbox über das USB-Kabel mit Strom.", liste=NUM_SCHRITTE_2))
    t.append(schritt("Verbinden Sie Ihr Smartphone mit dem WLAN ", fett("„Sensorbox1“"), " (Passwort ",
                     fett("configesp"), ").", liste=NUM_SCHRITTE_2))
    t.append(schritt("Bestätigen Sie, dass Sie das WLAN ohne Internetzugang verwenden möchten.", liste=NUM_SCHRITTE_2))
    t.append(schritt("Öffnen Sie im Browser ", fett("http://192.168.4.1/openandhome.esp"), ".", liste=NUM_SCHRITTE_2))
    t.append(absatz(fett("Wichtig: "), "Hat die Sensorbox schon einmal WLAN-Zugangsdaten erhalten, versucht sie "
                    "ständig, dieses WLAN zu erreichen. Löschen Sie dann die Zugangsdaten (siehe Fehlerbeschreibung)."))
    t.append(ueberschrift("Uhrzeit (Zeitserver)"))
    t.append(absatz("Die Sensorbox holt die Uhrzeit ab Werk aus Ihrem eigenen Netz: etwa eine halbe Minute nach "
                    "dem Start von Ihrem Router, sonst von 192.168.178.1 (Standard der FRITZ!Box). Erst wenn beide "
                    "15 Minuten lang nicht antworten, fragt sie im Internet nach (de.pool.ntp.org). Damit sie ohne "
                    "Internet auskommt, muss Ihr Router als Zeitserver arbeiten (FRITZ!Box: "
                    "„Heimnetz > Netzwerk > Netzwerkeinstellungen > Zeitsynchronisation“)."))
    t.append(absatz("Einen eigenen Zeitserver (z. B. de.pool.ntp.org im Internet) tragen Sie unter ",
                    fett("http://sensorbox1/advanced"), " im Feld „NTP Hostname“ ein, setzen den Haken bei "
                    "„Use NTP“, entfernen den Haken bei „Rules“ und speichern mit „Submit“ – oder mit der openandhome-Toolbox "
                    "über das USB-Kabel (Menüpunkt „Zeitserver (NTP) setzen“; Download unter "
                    "https://github.com/martament/openandhome/releases/latest)."))
    abrufen(t, mit_zabbix=False)

    toolbox(t, professional=False)

    t.append(ueberschrift("Ihre Sensorbox mit WLAN"))
    for b in ("Mit deutscher Bedienungsanleitung und deutschem Support",
              "Keine Datenübertragung aus Ihrem Netz",
              "Mit quelloffener Software (ESPEasy)",
              "Vorbereitet für openHAB, Home Assistant, FHEM, Domoticz, Node-RED, ioBroker und unseren Datenlogger"):
        t.append(punkt(b))
    messreihe(t)

    t.append(ueberschrift("Technische Daten"))
    t.append(tabelle([
        ("Gehäuse", "Kunststoffgehäuse KH-F20, 82 × 58 × 35 mm (L × B × H), grau/klar, feuchtigkeitsbeständig "
                    "und staubdicht"),
        ("Messumformer", "WeMos D1 mini (ESP8266) mit WLAN 2,4 GHz, eingebaut im Gehäuse"),
        ("Stromversorgung", "USB, 5 V DC, mindestens 500 mA (Netzteil nicht im Lieferumfang)"),
        ("Software", SOFTWARE),
        ("Temperaturfühler (je nach Ausstattung bis zu 4)", DS18B20_DATEN),
        ("Kombifühler (je nach Ausstattung)", [*HTU21D_DATEN, "alternativ AM2320 (Temperatur und Luftfeuchtigkeit)"]),
        ("Wassersensor (je nach Ausstattung)", WASSER_DATEN),
        ("Abstandssensor (je nach Ausstattung)", "Ultraschall HC-SR04, z. B. für Füllstandsmessung"),
        ("Display (je nach Ausstattung)", "OLED-Display mit den aktuellen Messwerten"),
        ("Kabeldurchführung", "Gummitülle M16 aus EPDM, grau"),
    ], breite_links=3900))
    sicherheit(t, ["Betreiben Sie die Sensorbox nur mit der vorgesehenen Schutzkleinspannung 5 V DC über USB.",
                   "Ein Kombifühler misst die Luftfeuchtigkeit; tauchen Sie ihn nicht in Wasser und schützen Sie ihn "
                   "vor Kondenswasser."])
    konformitaet_entsorgung(t)

    t.append(ueberschrift("Fehlerbeschreibung"))
    t.append(tabelle([
        FEHLER_HTTPS,
        ("Keine Sensordaten, Gerät setzt aus",
         "Prüfen Sie Netzteil und USB-Kabel: Es müssen 5 V DC mit mindestens 500 mA anliegen. Eventuell hat sich "
         "der USB-Stecker gelöst."),
        ("WLAN-Daten falsch eingegeben",
         "Trennen Sie die Sensorbox kurz vom Strom. Findet sie Ihr WLAN nicht, öffnet sie nach kurzer Zeit wieder "
         "ihr eigenes WLAN „Sensorbox1“ und Sie beginnen erneut bei Schritt B. Bringen Sie die Sensorbox "
         "gegebenenfalls aus der Reichweite Ihres WLANs."),
        ("Sensorbox soll ohne WLAN-Router laufen, Zugangsdaten sind gespeichert",
         "Am einfachsten mit der Toolbox: „WLAN-Daten löschen“. Oder gehen Sie wie bei der Inbetriebnahme vor und "
         "geben Sie als WLAN-Name „ssid“ und als Passwort „wpakey“ ein."),
        ("Mit dem WLAN der Sensorbox verbunden, Seiten nicht erreichbar",
         "Entfernen Sie das WLAN „Sensorbox1“ aus den gespeicherten WLANs Ihres Geräts und beginnen Sie erneut."),
        FEHLER_IP_BLOCKED,
        FEHLER_TEMPERATUR,
    ], breite_links=3900))
    schluss(t)
    return "".join(t)


INHALT = {"professional": inhalt_professional, "standalone": inhalt_standalone}


def baue(variante, vorlage, ziel):
    with zipfile.ZipFile(vorlage) as alt:
        x = alt.read("word/document.xml").decode("utf-8")
        kopf, rest = x.split("<w:body>", 1)
        titel = re.match(r"\s*(<w:p[ >].*?</w:p>)", rest, re.S).group(1)
        titel = re.sub(r"Bedienungsanleitung Sensor[^<]*", TITEL[variante], titel, count=1)
        sect = re.search(r"<w:sectPr.*?</w:sectPr>", rest, re.S).group(0)
        neu = kopf + "<w:body>" + titel + INHALT[variante]() + sect + "</w:body></w:document>"
        with zipfile.ZipFile(ziel, "w", zipfile.ZIP_DEFLATED) as z:
            for eintrag in alt.infolist():
                if eintrag.filename == "word/media/image2.png":
                    continue          # altes Dashboard-Bild (2 Fuehler, ohne Werte) entfaellt
                daten = alt.read(eintrag.filename)
                if eintrag.filename == "word/document.xml":
                    daten = neu.encode("utf-8")
                elif eintrag.filename == "word/_rels/document.xml.rels":
                    daten = re.sub(rb'<Relationship [^>]*Target="media/image2.png"/>', b"", daten)
                elif eintrag.filename == "word/numbering.xml":
                    daten = zweite_schrittliste(daten.decode("utf-8")).encode("utf-8")
                elif eintrag.filename == "docProps/core.xml":
                    daten = re.sub(rb"<dc:title>[^<]*</dc:title>",
                                   f"<dc:title>{TITEL[variante]}</dc:title>".encode(), daten)
                    for feld in (rb"dcterms:created", rb"dcterms:modified"):
                        daten = re.sub(rb"(<" + feld + rb"[^>]*>)[^<]*", rb"\g<1>" + DATUM_ISO.encode(), daten)
                    daten = re.sub(rb"(<cp:lastModifiedBy>)[^<]*", rb"\g<1>openandhome", daten)
                elif eintrag.filename == "docProps/app.xml":
                    daten = re.sub(rb"(<Company>)[^<]*", rb"\g<1>" + escape(FIRMA).encode(), daten)
                z.writestr(eintrag, daten)
    print("geschrieben:", os.path.relpath(ziel, ROOT))


def zweite_schrittliste(numbering):
    """Legt numId 13 an: gleiche Formatierung wie numId 1 (A), B), ...), beginnt aber wieder bei A."""
    abstrakt = re.search(rf'<w:num w:numId="{NUM_SCHRITTE}"[^>]*>.*?<w:abstractNumId w:val="(\d+)"/>',
                         numbering, re.S).group(1)
    if f'w:numId="{NUM_SCHRITTE_2}"' in numbering:
        return numbering          # Vorlage hat die Liste schon
    neu = (f'<w:num w:numId="{NUM_SCHRITTE_2}"><w:abstractNumId w:val="{abstrakt}"/>'
           f'<w:lvlOverride w:ilvl="0"><w:startOverride w:val="1"/></w:lvlOverride></w:num>')
    return numbering.replace("</w:numbering>", neu + "</w:numbering>")


def main():
    parser = argparse.ArgumentParser(description="Bedienungsanleitung erzeugen")
    parser.add_argument("--variante", choices=sorted(INHALT), required=True)
    parser.add_argument("--vorlage", default=VORLAGE)
    parser.add_argument("--ziel", help="Standard: docs/2026 openandhome - Bedienungsanleitung - <Variante>.docx")
    args = parser.parse_args()
    baue(args.variante, args.vorlage, args.ziel or os.path.join(ROOT, ZIELE[args.variante]))


if __name__ == "__main__":
    main()

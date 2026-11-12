#!/usr/bin/env python3
"""Baut die Anleitung Professional Typ 2026.1 auf Basis der Word-Vorlage 2023.1.

Vorlage (Formatvorlagen, Kopf-/Fusszeile, Logo, Nummerierung) bleibt erhalten,
nur der Inhalt von word/document.xml wird ersetzt.
  python3 tools/docs/anleitung_professional.py \
      "docs/2023 openandhome - Bedienungsanleitung - Professional Typ2023-1-Vers 2.docx" \
      "docs/2026 openandhome - Bedienungsanleitung - Professional Typ2026-1.docx"
"""

import re
import sys
import zipfile
from xml.sax.saxutils import escape

VORLAGE, ZIEL = sys.argv[1], sys.argv[2]
SEITE_BREITE = 10432          # A4 minus Raender (737 dxa je Seite)


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
    return absatz(*teile, stil="Listenabsatz", nummer=2)


def schritt(*teile):
    return absatz(*teile, stil="Listenabsatz", nummer=1)


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


def inhalt():
    t = []
    t.append(absatz("Diese Anleitung gilt für:"))
    t.append(absatz(("Temperatursensor Professional Typ 2026.1", {"fett": True}),
                    " – mit 3 Temperaturfühlern, Kombifühler für Temperatur und Luftfeuchtigkeit, "
                    "Display und Netzwerkanschluss mit Stromversorgung über das Netzwerkkabel (PoE)."))
    t.append(absatz("Diese Bedienungsanleitung enthält wichtige Informationen zur Inbetriebnahme und Handhabung. "
                    "Lesen Sie sie aufmerksam durch und bewahren Sie sie sorgfältig auf. "
                    "Beachten Sie unbedingt die Sicherheitshinweise in dieser Anleitung!"))

    t.append(ueberschrift("Funktionsbeschreibung"))
    t.append(absatz("Die Sensorbox misst mit drei Temperaturfühlern (DS18B20) und einem Kombifühler (HTU21D) "
                    "Temperaturen und die Luftfeuchtigkeit. Strom und Netzwerk erhält sie über ein einziges "
                    "Netzwerkkabel (Power over Ethernet, PoE) – ein Netzteil ist nicht nötig."))
    t.append(absatz("Das eingebaute Display zeigt die aktuellen Messwerte sowie abwechselnd die Netzwerkadresse "
                    "(IP-Adresse) und den Namen der Sensorbox. Die Sensorbox bezieht ihre IP-Adresse automatisch "
                    "von Ihrem Router (DHCP)."))
    t.append(absatz("Über eine eingebaute Webseite (Dashboard) rufen Sie die Werte im Browser ab. Für die Einbindung "
                    "in Ihre Systeme stellt die Sensorbox die Messwerte als JSON und als Prometheus-Metriken bereit "
                    "und kann sie per MQTT oder an Zabbix weitergeben. Ab Werk sendet die Sensorbox keine Daten aus "
                    "Ihrem Netz."))

    t.append(ueberschrift("Anwendungsbereich"))
    t.append(absatz("Die Sensorbox ist in einem feuchtigkeitsgeschützten Gehäuse eingebaut und eignet sich für den "
                    "Innen- und den geschützten Außenbereich, privat wie gewerblich. Einige Beispiele:"))
    for b in ("Server- und Netzwerkschränke sowie Serverräume (Temperatur und Luftfeuchtigkeit)",
              "Heizung: Vorlauf, Rücklauf, Boiler, Solaranlage",
              "Kühl- und Lagerräume (z. B. Wildbret), Klimaüberwachung",
              "Temperaturüberwachung bei Schüttgut (z. B. Getreide)"):
        t.append(punkt(b))

    t.append(ueberschrift("Inbetriebnahme"))
    t.append(schritt("Verbinden Sie die Sensorbox mit einem Netzwerkkabel mit einem Netzwerkanschluss, der PoE "
                     "liefert (PoE-Switch oder PoE-Injektor nach IEEE 802.3af)."))
    t.append(schritt("Die Sensorbox startet. Nach etwa einer halben Minute zeigt das Display die Messwerte sowie "
                     "abwechselnd die IP-Adresse und den Namen „Sensorbox1“."))
    t.append(schritt("Öffnen Sie im Browser das Dashboard: ",
                     ("http://<IP-Adresse>/openandhome.esp", {"fett": True}),
                     " – die IP-Adresse lesen Sie im Display ab. Je nach Router funktioniert auch ",
                     ("http://sensorbox1/openandhome.esp", {"fett": True}),
                     " (bei einer FRITZ!Box auch http://sensorbox1.fritz.box)."))
    t.append(schritt("Das Dashboard zeigt die Werte von Fühler 1 bis 3 sowie Temperatur und Luftfeuchtigkeit des "
                     "Kombifühlers. Speichern Sie die Adresse als Lesezeichen."))
    t.append(schritt("Setzen Sie mehrere Sensorboxen ein, geben Sie jeder einen eigenen Namen: ",
                     ("http://<IP-Adresse>/config", {"fett": True}),
                     ", Feld „Unit Name“ ändern und mit „Submit“ speichern."))
    t.append(schritt("Empfehlung: Vergeben Sie auf derselben Seite ein Administrator-Passwort, damit niemand in Ihrem "
                     "Netz die Einstellungen ändern kann."))
    t.append(absatz(("Hinweis: ", {"fett": True}),
                    "Die Weboberfläche ist ab Werk nur aus Netzen mit Adressen 192.168.x.x erreichbar. Nutzen Sie "
                    "ein anderes Netz (z. B. 10.x.x.x), wenden Sie sich bitte an unseren Support."))

    t.append(ueberschrift("Messwerte abrufen und einbinden"))
    t.append(tabelle([
        ("Dashboard", "http://<IP-Adresse>/openandhome.esp"),
        ("JSON (alle Werte)", "http://<IP-Adresse>/json"),
        ("Prometheus-Metriken", "http://<IP-Adresse>/metrics"),
        ("Einstellungen", "http://<IP-Adresse>/ (Menü Config, Controllers, Devices)"),
    ]))
    t.append(absatz(("MQTT (z. B. openHAB, Home Assistant, ioBroker, Node-RED): ", {"fett": True}),
                    "Menü „Controllers“ → Controller 1 „Home Assistant (openHAB) MQTT“ → „Edit“. Tragen Sie Ihren "
                    "MQTT-Server ein, setzen Sie den Haken bei „Enabled“ und speichern Sie mit „Submit“. Die Werte "
                    "erscheinen unter openandhome/<Name>/<Fühler>/<Messwert>, z. B. "
                    "openandhome/Sensorbox1/Fuehler1/Temperatur."))
    t.append(absatz(("Zabbix: ", {"fett": True}),
                    "Menü „Controllers“ → Controller 2 „Zabbix“ → „Edit“, Zabbix-Server eintragen, „Enabled“ "
                    "setzen und mit „Submit“ speichern."))
    t.append(absatz("Weitere Möglichkeiten (z. B. Centreon, Nagios, HTTP-Abfragen) beschreibt die Dokumentation der "
                    "Software ESPEasy: https://espeasy.readthedocs.io"))

    t.append(ueberschrift("Ihre Sensorbox Professional"))
    for b in ("Mit deutscher Bedienungsanleitung und deutschem Support",
              "Keine Datenübertragung aus Ihrem Netz",
              "Mit quelloffener Software (ESPEasy)",
              "Vorbereitet für Zabbix, Prometheus, MQTT, Centreon, Nagios, JSON- und HTTP-Schnittstellen"):
        t.append(punkt(b))

    t.append(ueberschrift("Messreihe"))
    t.append(absatz("Der Golden Master Sensorbox Openandhome wurde in einer Messreihe mit einem geeichten Testo 112 "
                    "(NTC −25…120 °C) kalibriert. Alle ausgelieferten Sensorboxen werden mit einer Vergleichsmessung "
                    "am Golden Master geprüft und vor der Auslieferung 24 Stunden im Dauerbetrieb getestet. "
                    "Abweichungen liegen bei maximal ±0,5 °C gegenüber dem Golden Master."))

    t.append(ueberschrift("Technische Daten"))
    t.append(tabelle([
        ("Gehäuse", "Kunststoffgehäuse 155 × 90 × 62 mm (L × B × H), grau/klar, feuchtigkeitsbeständig und staubdicht"),
        ("Messumformer", "Olimex ESP32-POE-ISO mit Ethernet (10/100 Mbit/s)"),
        ("Stromversorgung", "Power over Ethernet nach IEEE 802.3af über das Netzwerkkabel"),
        ("Netzwerk", "Ethernet, IP-Adresse per DHCP"),
        ("Software", "ESPEasy (Version mega-20260720)"),
        ("Display", "OLED-Display: Messwerte, IP-Adresse und Gerätename"),
        ("Temperaturfühler (3 Stück)", ["DS18B20 in Edelstahlhülse Ø 6 × 50 mm, wasserdicht, schwarzes Kabel",
                                         "Messbereich −20 °C bis +125 °C",
                                         "Genauigkeit ±0,5 °C im Bereich −10 °C bis +85 °C (Herstellerangabe)"]),
        ("Kombifühler", ["HTU21D für Temperatur und relative Luftfeuchtigkeit",
                         "Luftfeuchtigkeit 0–100 % rF, Genauigkeit typ. ±2 % rF (20–80 % rF)",
                         "Temperatur −40 °C bis +125 °C, Genauigkeit typ. ±0,3 °C"]),
        ("Kabeldurchführungen", "Gummitüllen M16/M25 aus EPDM, grau"),
    ]))

    t.append(ueberschrift("Sicherheitshinweise / Risikobewertung"))
    for b in ("Betreiben Sie die Sensorbox nur an einem PoE-Anschluss nach IEEE 802.3af (PoE-Switch oder PoE-Injektor).",
              "Der USB-Anschluss im Inneren ist nur für unseren Service vorgesehen.",
              "Die Sensorbox ist in einem stabilen Gehäuse eingebaut; schützen Sie sie zusätzlich gegen Schlag.",
              "Der Kombifühler misst die Luftfeuchtigkeit; tauchen Sie ihn nicht in Wasser und schützen Sie ihn "
              "vor Kondenswasser.",
              "Betreiben Sie die Sensorbox nicht in unmittelbarer Nähe von Strahlungsquellen wie Mikrowellen, "
              "Elektromotoren oder Pumpen.",
              "Die Sensorbox ist nicht für Kinder und Tiere geeignet.",
              "Die Geräte dürfen nicht in explosionsgefährdeten Bereichen verwendet werden.",
              "Öffnen Sie das Gerät nicht eigenmächtig.",
              "Für Schäden durch unsachgemäßen Umgang, Veränderung oder Nichtbeachtung dieser Anleitung übernehmen "
              "wir keine Haftung."):
        t.append(punkt(b))
    t.append(absatz("In einer internen Testreihe zur allgemeinen Produktsicherheit wurde unser Produkt als sicher "
                    "eingestuft. Haben Sie Verbesserungsvorschläge, schreiben Sie uns – wir prüfen jede Anregung."))

    t.append(ueberschrift("Konformitätserklärung"))
    t.append(absatz("Die Konformitätserklärung finden Sie im Onlineshop beim Produkt. Die vollständige Erklärung "
                    "erhalten Sie auch per E-Mail an info@openandhome.de."))

    t.append(ueberschrift("Fehlerbeschreibung"))
    t.append(tabelle([
        ("Webseite ist nicht erreichbar",
         "Achten Sie darauf, dass die Adresse mit http:// beginnt. Manche Browser ersetzen sie durch https://, "
         "die Sensorbox ist aber nur über http:// erreichbar."),
        ("Display bleibt dunkel, Sensorbox startet nicht",
         "Prüfen Sie, ob der Netzwerkanschluss PoE liefert (Anschluss am PoE-Switch aktiv bzw. Injektor mit Strom "
         "versorgt) und ob das Kabel richtig eingesteckt ist. Versuchen Sie einen anderen PoE-Anschluss."),
        ("IP-Adresse unbekannt",
         "Lesen Sie die IP-Adresse im Display ab oder suchen Sie in Ihrem Router nach dem Gerät „Sensorbox1“."),
        ("Meldung „IP blocked“",
         "Ihr Netz verwendet keine Adressen 192.168.x.x. Bitte wenden Sie sich an unseren Support."),
        ("Ein Fühler zeigt keinen Wert oder „NaN“",
         "Prüfen Sie Kabel und Stecker des Fühlers. Starten Sie die Sensorbox neu, indem Sie das Netzwerkkabel "
         "für etwa 10 Sekunden abziehen."),
        ("Angezeigte Temperatur ist zu hoch oder zu niedrig",
         "Nach einem Standortwechsel braucht der Fühler einige Minuten. Für eine Differenz von ±5 °C sind etwa "
         "10 Minuten Wartezeit nötig."),
    ], breite_links=3600))

    t.append(absatz("Irrtum und technische Änderungen vorbehalten.", mitte=True, abstand_vor=240))
    t.append(absatz("Kopieren der Bedienungsanleitung in jeglicher Form (auch auszugsweise) nur nach schriftlicher "
                    "Zustimmung.", mitte=True))
    t.append(ueberschrift("Kontakt"))
    t.append(absatz("Fragen zum Produkt: info@openandhome.de"))
    t.append(absatz("Onlineshop: https://openandhome.de"))
    t.append(absatz("Ament & Heinrichs OpenandHome GbR, Kirchstraße 6, 97511 Lülsfeld"))
    return "".join(t)


with zipfile.ZipFile(VORLAGE) as alt:
    x = alt.read("word/document.xml").decode("utf-8")
    kopf, rest = x.split("<w:body>", 1)
    titel = re.match(r"\s*(<w:p[ >].*?</w:p>)", rest, re.S).group(1)
    titel = titel.replace("Bedienungsanleitung Sensor 2023.1", "Bedienungsanleitung Sensor Professional 2026.1")
    sect = re.search(r"<w:sectPr.*?</w:sectPr>", rest, re.S).group(0)
    neu = kopf + "<w:body>" + titel + inhalt() + sect + "</w:body></w:document>"
    with zipfile.ZipFile(ZIEL, "w", zipfile.ZIP_DEFLATED) as z:
        for eintrag in alt.infolist():
            if eintrag.filename == "word/media/image2.png":
                continue          # altes Dashboard-Bild (2 Fühler, ohne Werte) entfaellt
            daten = alt.read(eintrag.filename)
            if eintrag.filename == "word/document.xml":
                daten = neu.encode("utf-8")
            elif eintrag.filename == "word/_rels/document.xml.rels":
                daten = re.sub(rb'<Relationship [^>]*Target="media/image2.png"/>', b"", daten)
            elif eintrag.filename == "docProps/core.xml":
                daten = re.sub(rb"<dc:title>[^<]*</dc:title>",
                               "<dc:title>Bedienungsanleitung Sensor Professional 2026.1</dc:title>".encode(), daten)
            z.writestr(eintrag, daten)
print("geschrieben:", ZIEL)

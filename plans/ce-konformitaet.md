# Plan: CE-Konformität für Sensorbox Typ 2026 und Typ 2025

Stand: 20.11.2026 · Plan, noch keine Umsetzung.
Ablage der fertigen Dokumente: `openandhome/15 - Konformität/Typ2026/` und `…/Typ2025/`
(ownCloud, nicht im Git-Repo).

Kennzeichnung: **[Pflicht]** gesetzlich nötig · **[Empfohlen]** nicht vorgeschrieben, senkt das
Risiko deutlich · **[Optional]** nur bei Bedarf.

Hinweis: technische Ausarbeitung, keine Rechtsberatung. Normenstände vor der Unterschrift im
Amtsblatt der EU prüfen.

---

## 1. Rahmenfestlegungen (20.11.2026)

- Die Sensorboxen heißen ab sofort **Typ 2026** und **Typ 2025**. Alle Bezeichnungen und
  Beschreibungen (Erklärungen, Anleitungen, Etiketten, Shop, Quelltexte) werden umgestellt.
- **Typ 2026** = primärer Sensor, ESP32, LAN/PoE, für Gewerbe.
- **Typ 2025** = sekundärer Sensor, ESP8266, nur WLAN.
- Bestückung und Ausstattungsvarianten bleiben; beide Typen sind im Shop erhältlich.
- Gewerbe wird nur mit Typ 2026 angesprochen.
- Die Konformitätserklärungen werden für beide Typen manuell erstellt.
- Unterschrift durch **beide Gesellschafter**.
- Ältere Typen (2020, 2021.1, 2023.1) werden nicht mehr verkauft; ihre Erklärungen bleiben nur im Archiv.

| | **Typ 2026** | **Typ 2025** |
|---|---|---|
| Controller | Olimex **ESP32-POE** Rev. **M2** (ohne ISO, ohne IND; PoE-Klasse 0; Aufdruck Board-Rückseite) | **AZ-Delivery D1 mini** (ESP8266, ESP-12F) |
| Anbindung | LAN/PoE, WLAN als Fallback | nur WLAN |
| Versorgung | PoE oder USB 5 V, nie gleichzeitig (keine galvanische Trennung) | USB 5 V |
| Trägerplatine | eigene **150x80 V1.9** (Gerber 2026-01-31) | eigene **79x59 V1.9** (Gerber 2024-07-09) |
| Leiterplatten-Oberfläche | bleifrei (JLCPCB, RoHS-Zertifikat) | bleifrei (JLCPCB, RoHS-Zertifikat) |
| Gehäuse | 155x90x62 mm (Sintron) | 132,2x68,7x50,1 mm (ABS/PC) |
| Varianten | DS18B20-Fühler, HTU21D, OLED, WLS-06 Wassersensor | DS18B20-Fühler, HTU21D/AM2320, OLED, HC-SR04 |

Die Varianten werden in der jeweiligen Erklärung aufgezählt; eine Erklärung je Typ genügt.

Zulieferernachweis: aktuelle Olimex-EU-Erklärung für **ESP32-POE** besorgen (die vorhandene gilt
für ESP32-POE-ISO). Die Bauteilliste 2026 nennt noch „ESP-POE-IND“ – auf ESP32-POE korrigieren.

---

## 2. Ausgangslage

| Dokument | Stand | Was noch fehlt |
|---|---|---|
| `Konformitätserklärung-Professionalbox-2026.docx` | Entwurf | Notizen entfernen, Normen als Text statt Bild, Cybersecurity, Varianten, Hard-/Firmware-Stand, Unterzeichner |
| `Konformitätserklärung-Standalone Box-2025-1.docx` | Entwurf auf Basis der 2026er Vorlage | Grundlage auf **AZ-Delivery D1 mini / ESP8266** umstellen, „2021.1“ streichen, sonst wie oben |
| Olimex-DoC (2021) | liegt vor | nennt Norm-Entwürfe und EN 62368-1:2014 – nur als Zulieferernachweis nutzen, nicht als eigene Normenliste |
| AZ-Delivery-DoC D1 mini (2018) | liegt vor | aktuelle Fassung bei AZ-Delivery anfragen |
| `Openandhome Konformitätsermittlung.docx` | 2020 | Messgeräte-RL 2014/32/EU und MI-004 sind nicht einschlägig; Cybersecurity, GPSR, CRA ergänzen |

Klarstellung: Typ 2026 hat mit dem ESP32 Funk an Bord und nutzt WLAN als Fallback, also gilt die
**Funkanlagenrichtlinie (RED)**, nicht nur die EMV-Richtlinie.

---

## 3. Rechtsrahmen

| Regelung | Inhalt | Status |
|---|---|---|
| **RED 2014/53/EU** (DE: FuAG) | Sicherheit Art. 3.1a, EMV Art. 3.1b, Funk Art. 3.2 | [Pflicht] |
| **DelVO (EU) 2022/30** zur RED | Cybersecurity Art. 3.3 d (Netz), e (personenbezogene Daten). Gilt seit 01.08.2025, ab 11.12.2027 durch den CRA abgelöst | [Pflicht] |
| **RoHS 2011/65/EU** + (EU) 2015/863 | Stoffbeschränkungen | [Pflicht] |
| EMV-RL, Niederspannungs-RL | durch RED Art. 3.1 abgedeckt, nicht separat aufführen | entfällt |
| **ElektroG / WEEE** | **nicht registriert** – siehe 3.1 | [Pflicht], **offen und dringend** |
| **GPSR (EU) 2023/988** | Risikoanalyse, Herstellerangaben und Identifikation am Produkt, Pflichtangaben im Shop | [Pflicht] |
| **CRA (EU) 2024/2847** | Meldepflicht aktiv ausgenutzter Schwachstellen seit **11.09.2026**; volle Pflichten ab **11.12.2027** | [Pflicht] Meldeweg jetzt |
| REACH Art. 33 | Auskunft zu SVHC auf Anfrage | [Pflicht] auf Anfrage |
| VerpackG | LUCID-Registrierung | erledigt, jährlich melden |

### 3.1 ElektroG: Reicht der Rücknahmehinweis in der Anleitung?

**Nein.** Der Hinweis „Altgeräte können Sie direkt an uns zurückgeben“ ersetzt die Registrierung nicht.

- Wer Elektrogeräte unter eigenem Namen erstmals in Deutschland verkauft, ist **Hersteller** und
  muss sich **vor dem Anbieten** bei der stiftung ear registrieren (§ 6 Abs. 1 ElektroG).
- Es gibt **keine Ausnahme** für Kleingewerbe, Kleinunternehmer oder kleine Stückzahlen; die
  Pflicht gilt ab dem ersten Gerät. Erleichterungen gibt es nur bei den Gebühren (Härtefall).
- Für Geräte an Privatkunden (B2C) ist zusätzlich eine **insolvenzsichere Garantie** nötig
  (laut Memo 2023 rund 400 €/Jahr). Für reine B2B-Geräte entfällt die Garantie.
- Folgen ohne Registrierung: Abmahnung durch Wettbewerber, Bußgeld, Vertriebsverbot.

**Möglichkeiten:**

| | Weg | Bewertung |
|---|---|---|
| A | Beide Typen selbst bei der stiftung ear registrieren (B2C, mit Garantie) | rechtssicher, laufende Kosten und Meldungen |
| B | Dienstleister (Rücknahmesystem/Bevollmächtigter) übernimmt Registrierung, Garantie und Meldungen | weniger Aufwand bei kleinen Mengen. [Empfohlen] |
| C | Typ 2026 nur an Gewerbe verkaufen und **B2B** registrieren (ohne Garantie); Typ 2025 B2C registrieren oder einstellen | günstiger für Typ 2026; Shop braucht B2B-Bestellweg |

Bis zur Registrierung dürfen die Geräte streng genommen nicht angeboten werden.

**Anleitung, Entsorgungstext [Pflicht nach § 18 ElektroG]:** Der Text in
`tools/docs/anleitung.py` (`konformitaet_entsorgung`) ist zu knapp. Ergänzen:
- Bedeutung des Symbols durchgestrichene Mülltonne, Pflicht zur getrennten Sammlung,
- Rückgabe bei kommunalen Sammelstellen **und** bei uns (Anschrift),
- vor der Rückgabe persönliche Daten löschen (WLAN-Zugangsdaten, Passwort → Toolbox),
- WEEE-Reg.-Nr., sobald vorhanden.

Marktüberwachung: **Bundesnetzagentur** (Funk/EMV), Gewerbeaufsicht (Produktsicherheit),
BSI/ENISA (CRA-Meldungen).

---

## 4. Konformitätsbewertung

**Ziel: Modul A (Selbsterklärung, ohne benannte Stelle).** Voraussetzung: Für jede Anforderung
werden harmonisierte Normen vollständig angewendet.

| Anforderung | Norm (Stand prüfen) | Nachweis | Status |
|---|---|---|---|
| Funk 3.2 | ETSI EN 300 328 | Prüfberichte des Funkmoduls (Espressif/Olimex bzw. AZ-Delivery); gültig, weil Modul und Antenne unverändert | [Pflicht] Unterlagen beschaffen |
| EMV 3.1b | ETSI EN 301 489-1, -17 | eigene Bewertung des Endgeräts (Platine, Kabel, Fühler, Netzteil) | [Pflicht] |
| Sicherheit 3.1a | EN IEC 62368-1 | eigene Bewertung: 5 V / PoE ≤ 57 V (Schutzkleinspannung), Erwärmung, Gehäuse | [Pflicht] |
| Exposition 3.1a | EN 62479 | Kleinleistungsnachweis anhand der Moduldaten | [Pflicht] |
| Cyber 3.3d | **EN 18031-1:2024** | Bewertung nach Norm | [Pflicht] |
| Cyber 3.3e | EN 18031-2:2024 | begründen, ob personenbezogene Daten verarbeitet werden (WLAN-Zugangsdaten, Gerätename) | [Pflicht] Prüfung |
| RoHS | EN IEC 63000 | Lieferantenerklärungen + Bewertung je Bauteil | [Pflicht] |

**EMV-Labormessung:** [Optional] – nur wenn die Bundesnetzagentur Nachweise anfordert, bei
einer Beanstandung oder wenn ein Großkunde einen Prüfbericht verlangt. Bis dahin wird die
EMV-Bewertung schriftlich begründet (zertifizierte Funkmodule, Schutzkleinspannung, keine
Schaltregler auf der eigenen Platine, Erfahrung seit 2020, 24-h-Tests).

### 4.1 Passwort und Betrieb im eigenen Netz

**Frage:** Gilt die Cybersecurity-Pflicht auch, wenn die Box nur im eigenen Netz läuft?

**Antwort: Ja.** Entscheidend ist, was das Gerät **kann**, nicht wie es eingesetzt wird.

- Die DelVO 2022/30 erfasst jedes Funkgerät, das „selbst über das Internet kommunizieren kann,
  direkt oder über andere Geräte“. Die Boxen sprechen TCP/IP und erreichen über jeden Router
  das Internet.
- Auch die enge Auslegung der Industrie (Orgalim: „ohne weitere Änderung für die Kommunikation
  über das Internet ausgelegt“) greift hier. Zusätzlich fragt unsere eigene Regel `rules1.txt`
  nach 15 Minuten `de.pool.ntp.org` im Internet ab.
- Ein Hinweis in der Anleitung „nur im eigenen Netz betreiben“ ändert den Anwendungsbereich nicht.

**Passwort-Einschränkung:** Laut Durchführungsbeschluss (EU) 2025/138 gibt EN 18031-1 keine
Vermutungswirkung, wenn der Nutzer **kein Passwort setzen und verwenden muss** (Abschnitte
6.2.5.1/6.2.5.2). ESPEasy läuft ab Werk ohne Passwort.

**Festlegung 20.11.2026:** Ein Admin-Passwort für alle Boxen (Benutzer `admin`, Passwort `configesp`,
gleich dem AP-Schlüssel). Der Anwender wird in der Bedienungsanleitung angewiesen, es **bei der
Inbetriebnahme zu ändern** (Inbetriebnahme-Schritt und Abschnitt „Zugang zu den Einstellungen“).
So steht es in der Konformitätserklärung (Nr. 6) und in der Cyber-Bewertung (Dokument 11).
Umgesetzt in Werkstatt (Aufsetzen und Testende, mit Prüfung), Toolbox (Menü 7, Grundkonfiguration)
und Bedienungsanleitung.

Alternative, falls die Marktüberwachung das beanstandet: Passwort pro Box (Werkstatt erzeugt es,
Etikett/Beiblatt) – Änderung nur in `setze_passwort()` und am Etikett. Ab **11.12.2027** (CRA, „sicher
ab Werk“) die Werkseinstellung erneut bewerten.

**Ergebnis Quelltext ESPEasy `mega-20261119`** (nicht an der Box getestet):

- Geschützt (HTTP-Digest, Benutzer `admin`): Konfigurationsseiten, `/upload`, `/download`.
- Ohne Passwort lesbar: `/json`, `/metrics`, `.esp`-Dateien (Dashboard), `/setup` –
  Zabbix/Prometheus brauchen keine Anmeldung.
- Werkzeuge melden sich per Digest an (Test gegen Nachbildung bestanden). **An einer echten Box
  testen [Pflicht]:** Werkstatt Menü 1 und 3, Toolbox 7/k/s, Dashboard-Upload, Syslog, oh_server.

---

## 5. Kennzeichnung und Identifikation

RED Art. 10 Abs. 6 und GPSR Art. 9 verlangen am Gerät eine **Typ-, Chargen- oder Seriennummer
oder ein anderes Identifikationsmerkmal**. Eine Seriennummer ist also nicht nötig.

**Festlegung:** Typ + Platinengröße und -version genügen:

- Typ 2026: `Typ 2026 · 150x80 V1.9`
- Typ 2025: `Typ 2025 · 79x59 V1.9`

Bei einer neuen Platinenversion ändert sich die Kennung automatisch, betroffene Geräte lassen
sich damit eingrenzen.

[Optional] Feinere Rückverfolgung ohne Mehraufwand: Die MAC-Adresse jeder Box steht bereits im
Werkstatt-Testprotokoll (`~/openandhome-testprotokolle/`), zusammen mit Testdatum und Firmware.

**Etikett [Pflicht]:** CE (≥ 5 mm), Typ + Platinenversion, Hersteller mit Anschrift und Mail,
Symbol durchgestrichene Mülltonne. Vorlagen `2026 - … Typ 2026 Aufdruck 36 mm.lbx` und `2025 - … Typ 2025 …` anpassen.

---

## 6. Dokumentenpaket je Typ (technische Dokumentation, RED Anhang V)

Aufbewahrung **10 Jahre** nach dem letzten Inverkehrbringen [Pflicht].

**Entwürfe erstellt 20.11.2026:** `openandhome/00 - 2026 - Neue Dokumente/CE/` (Übersicht 00, je Typ 01–14, gemeinsam 16, 17). Status und offene Punkte stehen in `00_Übersicht_CE-Unterlagen.docx`.

| Nr. | Dokument | Status |
|---|---|---|
| 01 | **EU-Konformitätserklärung** (vollständig, unterschrieben von beiden Gesellschaftern) | [Pflicht] |
| 02 | **Vereinfachte Erklärung** für Anleitung/Webseite mit Link auf die vollständige | [Pflicht] |
| 03 | Produktbeschreibung: Fotos, Varianten, Einsatzzweck, Blockschaltbild | [Pflicht] |
| 04 | Schaltplan, Layout, Gerber, Bestückungsplan (150x80 Rev 1.9 bzw. 79x59) | [Pflicht] |
| 05 | **Bauteilliste mit Konformitätsnachweisen** (Auftrag 3) | [Pflicht] |
| 06 | Zulieferernachweise: Olimex-DoC (passend zu P1), AZ-Delivery-DoC D1 mini, Funkmodul-Zertifikate, RoHS-Erklärungen | [Pflicht] |
| 07 | Normenliste und Prüfmatrix (Anforderung → Norm → Nachweis) | [Pflicht] |
| 08 | **Risikobeurteilung** (elektrisch, thermisch, mechanisch, Fehlgebrauch, Cyber) – auf Basis `13 - Messreihe - Risikobewertung` | [Pflicht] |
| 09 | Eigene Prüfungen: Funktion, 24-h-Test, Temperaturgenauigkeit, Erwärmung | [Pflicht] |
| 10 | EMV-Labormessung | [Optional] |
| 11 | **Cybersecurity-Bewertung** EN 18031-1 (Begründung zu -2) | [Pflicht] |
| 12 | **Bedienungsanleitung** mit Pflichtangaben: Hersteller, Typ, Frequenzband 2400–2483,5 MHz und max. Sendeleistung, Sicherheitshinweise, Entsorgung, WEEE-Nr., vereinfachte Erklärung | [Pflicht] |
| 13 | Etikettenvorlage (Abschnitt 5) | [Pflicht] |
| 14 | Firmware-Stand je Charge (Image, SHA256 aus `readme_image.txt`) | [Pflicht] |
| 15 | Chargen-/MAC-Liste (Rückverfolgbarkeit) | [Pflicht] |
| 16 | Schwachstellenprozess (CRA): Meldeadresse, Registrierung ENISA-Meldeplattform | [Pflicht] |
| 17 | Änderungsprotokoll: wann eine Neubewertung nötig ist | [Empfohlen] |
| 18 | Erklärungen und Anleitungen als PDF auf der Webseite | [Empfohlen] |

---

## 7. Auftrag 2 – Übersicht Platinen- und Komponentenstände

| Feld | Typ 2026 | Typ 2025 |
|---|---|---|
| Trägerplatine | **150x80 V1.9**, Gerber/BOM 2026-01-31 | **79x59 V1.9**, Gerber 2024-07-09 |
| Controller-Board | Olimex ESP32-POE, Hardware-Revision vom Board | AZ-Delivery D1 mini, Version vom Board |
| Funkmodul | ESP32-Modul auf dem Olimex-Board (Typ ablesen) | ESP-12F (ESP8266EX) |
| Gehäuse, Durchführungen | Sintron 155x90x62, M16/M25 EPDM | ABS/PC 132x69x50, M16 |
| Firmware | ESPEasy `collection_A_ESP32_4M316k` (Tag aus `readme_image.txt`) | ESPEasy `climate_B_ESP8266_4M1M` bzw. `collection_H` |
| Konfiguration | `configs/espeasy/professional/basis` | `configs/espeasy/standalone/basis`, `basis_am2320` |

Regel: **Neue Platinenrevision, anderes Controller-Board oder anderer Lieferant für ein Funkteil
= Neubewertung** (Dokument 17).

---

## 8. Auftrag 3 – Bauteilliste für die Konformität

Quellen: `00 - 2026 - Neue Dokumente/11_2026 - … Bauteilliste - Bestellliste 2026.xlsx`,
`03 - Zeichnungen/easyeda/150x80/BOM_SensorboxProfessional_2026-01-31.csv`,
`03 - Zeichnungen/easyeda/79x59/BOM_79x59_2022-04-03.csv`.

**Spalten:** Pos · Baugruppe · Bauteil · Hersteller · Typ/Teilenummer · Lieferant · Variante
(Standard/Option) · elektrisch aktiv · Funk · Nachweis (CE / RoHS / REACH) · Dateiname
Nachweis · Bewertung.

**Einteilung:**

1. **Funk (Nachweis zwingend):** Olimex ESP32-POE, AZ-Delivery D1 mini.
2. **Elektrisch aktiv (RoHS-Nachweis):** Trägerplatinen + SMD-Teile (LCSC/JLCPCB liefern
   RoHS-Angaben), DS18B20-Fühler, HTU21D/AM2320, OLED, HC-SR04, WLS-06, ggf. USB-Kabel.
3. **Mechanisch (Bewertung genügt):** Gehäuse, Kabeldurchführungen, Schrauben, Kabelhalter,
   Hutschienen-Clip.
4. **Beipack:** Anleitung, Etikett, Karton.

Fühler, Display und Sensoren kommen teils von eBay/AliExpress. Für RoHS: Lieferantenangaben
anfragen; wo keine kommen, die Lücke in der Bewertung begründen. [Empfohlen] mittelfristig
EU-Lieferanten mit Nachweis bevorzugen.

---

## 9. Ablauf

1. **ElektroG-Registrierung** (3.1) entscheiden und beantragen – dringend.
2. Passwort: Variante festlegen (4.1), testen, Werkstatt und Anleitung anpassen.
3. Zulieferernachweise beschaffen (Olimex ESP32-POE, AZ-Delivery D1 mini, Funkmodule, RoHS).
4. Bauteilliste (Auftrag 3) und Versionsübersicht (Auftrag 2) erstellen.
5. Risikobeurteilung, EMV-Begründung und Cyber-Bewertung schreiben.
6. **Konformitätserklärungen Typ 2026 und Typ 2025** neu aufsetzen (RED Anhang VI) und
   unterschreiben.
7. Vereinfachte Erklärung, Anleitungen (`docs/`, `tools/docs/anleitung.py`), Etiketten anpassen.
8. [Optional] MAC-Liste aus den Testprotokollen als Rückverfolgung führen.
9. CRA-Meldeweg einrichten.
10. Webseite: PDFs und Pflichtangaben (siehe `plans/webseite-gewerbe.md`).
11. Bis 11.12.2027: Umstieg auf CRA vorbereiten.

---

## 10. Offen

1. **ElektroG:** Weg A, B oder C (3.1)?
2. **Passwort:** entschieden (`configesp`, 4.1); Test an echter Box Typ 2026 und Typ 2025 ausstehend.
3. Datenlogger (Raspberry Pi): eigene Erklärung später. [Optional]

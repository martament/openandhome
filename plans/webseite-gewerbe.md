# Plan: openandhome.de – Fokus auf gewerblichen Einsatz und digitale Souveränität

## Rahmenfestlungungen
Ehe wir die Webseite überarbeiten und auch die Quelltexte gelten folgende Festlegungen.

Wir benennen unsere Sensorboxen um
- Typ 2026 ist der primäre Sensor mit dem Esp32. Dieser ist für den gewerblichen Gebrauch. Mit LAN.
- Typ 2025 ist der sekundäre Sensore mit dem ESP8266. Nur mit WIFI

Wir ändern alle Bezeichnungen und alle Beschreibungen um in Typ 2026 und Typ 2025

- Gleich bleibt die Bestückung, Ausstattungsvarianten, Typ 2026 und 2025 sind im Store verfügbar. 
- Für Gewerbe adressieren wir aber nur den Typ 2026
- Manuell erzeugen wir die konformitätserlärung für beide Typen
- 

Auftrag 1 Konformitätserklärung:
- Mache mir einen Plan um für den Type 2025 und den Typ2026 die Konformitätserklärung für CE zu erstellen. Du kannst die vorhandenen nehmen und diese basieren auf den unterlagen zum Olimex esp32 und zum Wemos 8266. Erstelle die beiden erkläreungen und diese müssen den akteullen bestimmungen der Bundesnetzagentur standhalten. Du darfst dazu auch gerne im Netz recherchieren.

Auftrag 2: Erstelle eine Übersicht für die Konformitätserklärung über die neuesten Platinenversionen 1.9 für Typ2026 und für den Typen 2025 kenne ich die letzte Version nicht.

Auftrag 3: Erstelle eine Bauteilliste wie wir sie für die Konformitätserklärung benötigen. Du kannst als Anhalt die BOM von der Platine und die Bauteilliste von /home/martin/Projekte/openandhome/00 - 2026 - Neue Dokumente/Bauteilliste nehmen.




Stand: 20.11.2026 · Übersichtsplan, Umsetzung folgt später.
Grundlage: Live-Seite <https://openandhome.de> (WordPress 7.1.5, WooCommerce 11.3.1,
Theme Storefront), Hosting über Ansible-Rolle `ansible/roles/server-inet/wordpress`
(Instanz `openandhome`).

Ziel: Die Seite stellt die **Sensorbox Professional (LAN/PoE)** für Unternehmen, Behörden
und Hochschulen in den Vordergrund, der Datenlogger ergänzt sie. Kernbotschaft:
**digital souveräne Messtechnik – Hardware unter eigener Kontrolle, offen eingebunden in
eigene Systeme.** Der Privatkunden-Shop bleibt, rückt aber nach hinten.

## Entscheidungen (20.11.2026)

| Thema | Entscheidung |
|---|---|
| Referenzen | Vorerst **nur anonym** („eine Landesbehörde“, „ein Universitätsrechenzentrum“). |
| Angebot | Button **„Angebot anfragen“** öffnet eine Mail an info@openandhome.de mit vorformulierter Anfrage (`mailto:`), kein Formular-Plugin. |
| Umsatzsteuer | **Kleinunternehmer (§ 19 UStG)** – Preise sind Endpreise, keine Netto-/Brutto-Umschaltung. |
| Datenlogger | Bleibt, als **Ergänzung** zur Professional-Box. |
| Telefon/Ansprechpartner | **Nein**, Kontakt nur per Mail. |
| Englisch | **Entfällt vorerst**; englische Elemente werden entfernt. |

---

## 1. Ist-Analyse (Kurzfassung)

**Gut:** Startseite (12.10.2026) nennt Souveränität, Privat und Gewerbe sowie Monitoring-Systeme;
PoE-Produktseite ausführlich; Meta-/OG-Tags gepflegt; HTTPS/HSTS, Security-Header; keine
Google-Dienste eingebunden.

**Fehler:**

- F1 Kein Impressum (`/impressum` → 404, Footer nur Datenschutz).
- F2 Sichtbare Platzhalter auf der PoE-Seite („[… bitte ergänzen …]“).
- F3 Sitemap leer (Plugin `google-sitemap-generator`).
- F4 Keine Seiten Widerruf und Versand/Zahlung; AGB versteckt und nur für Verbraucher.
- F5 PoE-Box ohne Produktkategorie; CE-Erklärung nur auf Anfrage; ausverkauftes
  „Sonderangebot“ gelistet.
- F6 Menüpunkt „English“ = Google-Translate-Link (`http://`).

**Schwächen für Gewerbe:** keine Referenzen; Angebot nur über Kontaktseite; keine PDFs
(Datenblatt, Anleitung); Tonalität und Fotos privat; uneinheitliche Produktnamen
(„Professional“, „Premium Sensorbox“); `/index.php/` in allen URLs; mehrere H1.

---

## 2. Positionierung

**Hero (Entwurf):**

> **Messtechnik unter Ihrer Kontrolle.**
> Netzwerk-Sensorboxen für Serverraum, Technikraum und Labor – Open Source, ohne Cloud,
> per PoE angebunden und über offene Standards (Prometheus, JSON, MQTT, HTTP) in Ihr eigenes
> Monitoring integriert. Im Einsatz bei Behörden und Hochschulen.
>
> [Angebot anfragen] [Datenblatt (PDF)]

**Zielgruppen:** 1. IT-Betrieb in Behörden, Hochschulen, Forschung · 2. Unternehmen und
Systemhäuser · 3. Gebäude, Kirchen, Landwirtschaft · 4. Privat (eigener Bereich).

**Souveränitäts-Argumente (prüfbar):** keine Cloud, kein Konto, keine Telemetrie · keine
Auftragsverarbeitung (AVV) nötig · quelloffene Firmware (ESPEasy), Konfigurationen auf GitHub ·
Update/Wiederherstellung offline mit ohtoolbox · offene Standards statt Lock-in, kein Abo ·
Montage, 24-h-Test und Support in Deutschland · ehrlicher Sicherheitsleitfaden.

---

## 3. Phasen im Überblick

### Phase 0 – Sofort (Fehler und Pflichtangaben)

1. Impressum anlegen (GbR, Gesellschafter, Anschrift, Mail, Hinweis § 19 UStG), juristisch prüfen.
2. Platzhalter auf der PoE-Seite füllen (Sensortypen, Lieferzeit).
3. Sitemap reparieren (Core-Sitemap statt Plugin), in der Search Console einreichen.
4. Footer: Impressum · Datenschutz · AGB · Widerruf · Versand & Zahlung · Kontakt.
5. PoE-Box einer Kategorie zuordnen, ausverkauftes Sonderangebot ausblenden.
6. **Englisch entfernen:** Menüpunkt „English“ (Google Translate) aus beiden Menüs löschen.
7. Hinweis „Gemäß § 19 UStG wird keine Umsatzsteuer berechnet“ in Shop, Kasse und Rechnung
   prüfen bzw. ergänzen.

### Phase 1 – Startseite und Navigation

**Navigation:**

```
Lösungen ▾              Produkte ▾                     Referenzen   Wissen ▾        Über uns   Angebot anfragen
 - Serverraum & IT       - Sensorbox Professional                    - Dokumentation
 - Labor & Forschung       (LAN/PoE)                                 - Integration
 - Gebäude & Heizung     - Datenlogger (Ergänzung)                   - Praxis (Blog)
 - Lager & Kühlung       - Fühler & Zubehör                          - FAQ
 - Smart Home (privat)   - WLAN-Sensorbox (privat)
```

**Startseite:**

1. Hero mit Foto der Professional-Box, Buttons „Angebot anfragen“ und „Datenblatt (PDF)“.
2. Vertrauensleiste, anonym: „Im Einsatz bei Behörden, Hochschulen und Unternehmen“.
3. „Digitale Souveränität – konkret“: 4–6 Punkte mit Link zu GitHub.
4. „So binden Sie die Box ein“: Schema Box → Prometheus/Zabbix/MQTT → eigenes System.
5. Produktkacheln: Professional groß, Datenlogger als Ergänzung, Fühler/Zubehör;
   WLAN-Box klein „für Privatanwender“.
6. Praxisbeispiele (Kirchenheizung, Pufferspeicher, Getreide).
7. Abschluss-Block „Angebot anfragen“.

**Button „Angebot anfragen“** (Startseite, Produktseite, Menü) als `mailto:`-Link mit
vorbelegtem Betreff und Text. Die Mailadresse steht zusätzlich als Text daneben, weil
`mailto:` ohne eingerichtetes Mailprogramm (z. B. Webmail) nichts öffnet. Vorlage:

```
Betreff: Angebotsanfrage Sensorbox Professional

Guten Tag,

bitte senden Sie uns ein Angebot für:

Anzahl Sensorboxen:
Einsatzort (z. B. Serverraum, Labor, Lager):
Fühler je Box (Anzahl, Kabellänge):
Weitere Sensoren (Feuchte, Wasser/Kontakt, Display):
Stromversorgung (PoE / USB):
Einbindung in (z. B. Zabbix, Prometheus, MQTT):
Datenlogger gewünscht (ja/nein):
Gewünschter Liefertermin:

Rechnungsanschrift:
Organisation:
Ansprechpartner:
E-Mail:
Bestell-/Aktenzeichen (falls vorhanden):

Mit freundlichen Grüßen
```

(Im Link URL-kodiert: `mailto:info@openandhome.de?subject=…&body=…`, Zeilenumbrüche als `%0D%0A`.)

### Phase 2 – Inhalte für Gewerbe

1. Landingpage „Sensorbox Professional“ (Nutzen, Schnittstellen, Technik, Montage, Varianten,
   Downloads, Angebot-Button); Datenlogger dort als Ergänzung.
2. Downloads (PDF): Datenblatt, Anleitung (aus `docs/`), CE-Konformitätserklärung,
   Sicherheitsleitfaden.
3. Referenzen-Seite: 2–3 anonyme Kurz-Fallstudien (Ausgangslage – Lösung – Ergebnis).
4. Integrationsanleitungen: Zabbix, Prometheus/Grafana, CheckMK/Icinga, MQTT/Home Assistant;
   Vorlagen auf GitHub.
5. Seite „Für Behörden und Unternehmen“: Kauf auf Rechnung, Kleinunternehmer-Hinweis,
   Lieferzeit, Gewährleistung, Ersatzteile, Firmware-Pflege, Angebot-Button.
6. „Über uns“ neu: Team, Erfahrung bei Behörden und Hochschulen (anonym), Werte, Standort.
7. Sicherheitsleitfaden: eigenes VLAN, Admin-Passwort und IP-Bereich, Weboberfläche nur HTTP,
   keine ausgehenden Verbindungen ab Werk (NTP lokal, Internet nur als Fallback), Updates mit
   dokumentierten SHA256 über ohtoolbox, USB und PoE nie gleichzeitig.

### Phase 3 – Technik, SEO, Pflege

1. Permalinks ohne `/index.php/`, mit 301-Weiterleitungen (vorher Links in Dashboard-Footer,
   Readmes, Anleitungen prüfen).
2. Eine H1 je Seite; Schema.org `Organization`, `Product`, `FAQPage`.
3. Begriffe: „Temperaturüberwachung Serverraum“, „PoE Temperatursensor Prometheus“,
   „Zabbix Temperatursensor“, „Sensor ohne Cloud“.
4. Neue Produktfotos (Hutschiene, Rack, Anschlüsse), Logo als SVG.
5. Blog → „Praxis“, etwa ein Beitrag pro Quartal mit Schwerpunkt Gewerbe.
6. Einheitliche Produktnamen (Professional / WLAN-Sensorbox), „Premium Sensorbox“ ersetzen.
7. Datenschutzerklärung aktualisieren (ohne Drittanbieter kurz und klar).

### Phase 4 – Privatbereich

WLAN-Sensorbox, Display und Sets unter „Smart Home (privat)“ bündeln; Shop bleibt für beide
Zielgruppen, Startseite und Navigation führen zuerst zu Professional/Gewerbe.

---

## 4. Offen

- Welche Fallstudien (anonym) eignen sich, und welche Kennzahlen dürfen genannt werden?
- Umsetzung direkt im WordPress-Editor oder vorbereitete Block-HTML-Texte zum Einfügen?

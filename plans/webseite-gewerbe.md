# Plan: openandhome.de – Fokus auf gewerblichen Einsatz und digitale Souveränität

## Rahmenfestlungungen
Ehe wir die Webseite überarbeiten und auch die Quelltexte gelten folgende Festlegungen.

Wir benennen unsere Sensorboxen um
- Typ 2026 ist der primäre Sensor mit dem Esp32. Dieser ist für den gewerblichen Gebrauch. Mit LAN.
- Typ 2025 ist der sekundäre Sensore mit dem ESP8266. Nur mit WIFI

Wir ändern alle Bezeichnungen und alle Beschreibungen um in Typ 2026 und Typ 2025

- Gleich bleibt die Bestückung, Ausstattungsvarianten, Typ 2026 und 2025 sind im Store verfügbar. 
- Für Gewerbe adressieren wir aber nur den Typ 2026



Stand: 24.11.2026 (2. Fassung, nach Umbenennung und CE-Unterlagen) · Phase 0 umgesetzt, übrige Phasen geplant
(Stufenplan mit Status: Abschnitt 6).
Grundlage: Live-Seite <https://openandhome.de> (WordPress 7.1.5, WooCommerce 11.3.1,
Theme Storefront), Hosting über Ansible-Rolle `ansible/roles/server-inet/wordpress`
(Instanz `openandhome`).

Bezüge:

- [`umbenennung-typ2026-2025.md`](umbenennung-typ2026-2025.md) – Namen, Shop-Produkte (IDs), Artikelnummern, CE-Seite im Detail
- [`ce-konformitaet.md`](ce-konformitaet.md) – Pflichtangaben (RED, GPSR, CRA), Passwort-Festlegung
- CE-Mappe `00 - 2026 - Neue Dokumente/CE/` – Quellen für Erklärungen, Anleitungen, Sicherheitskontakt

Ziel: Die Seite stellt die **Sensorbox Typ 2026 (LAN/PoE)** für Unternehmen, Behörden
und Hochschulen in den Vordergrund, der Datenlogger ergänzt sie. Kernbotschaft:
**digital souveräne Messtechnik – Hardware unter eigener Kontrolle, offen eingebunden in
eigene Systeme.** Die **Sensorbox Typ 2025 (WLAN)** bleibt im Shop für Privatkunden, rückt aber nach hinten.

## Entscheidungen

| Thema | Entscheidung |
|---|---|
| Referenzen | **Keine Fallstudien vorhanden** – nur die anonyme Aussage „im Einsatz bei Behörden, Hochschulen und Unternehmen“; keine eigene Referenzen-Seite. |
| Angebot | Button **„Angebot anfragen“** öffnet eine Mail an info@openandhome.de mit vorformulierter Anfrage (`mailto:`), kein Formular-Plugin. |
| Umsatzsteuer | **Kleinunternehmer (§ 19 UStG)** – Preise sind Endpreise, keine Netto-/Brutto-Umschaltung. |
| Datenlogger | Bleibt, als **Ergänzung** zu Typ 2026 (und Typ 2025). |
| Telefon/Ansprechpartner | **Nein**, Kontakt nur per Mail. |
| Englisch | **Entfällt vorerst**; englische Elemente werden entfernt. |
| Namen | Nur noch **Sensorbox Typ 2026 (LAN/PoE)** und **Sensorbox Typ 2025 (WLAN)**, **ohne Übergangshinweis**, ab sofort. |
| Artikelnummern | Werden eingeführt (`OH-2026-…`, `OH-2025-…`, `OH-F-…`, Schema im Umbenennungsplan 4.2). |
| Fühler | **Bis zu 4 Fühler je Box**; Typ 2026 Standard mit 3, der vierte als Zubehör. |
| CE-Unterlagen | Öffentlich unter `/ce/`, `/ce/typ-2026`, `/ce/typ-2025` (Adressen stehen bereits in den Anleitungen). |
| Passwort | Ab Werk gesetzt (Wert siehe `ce-konformitaet.md`), Anleitung weist an, es bei Inbetriebnahme zu ändern. **Webseite und Kundenmails nennen keine Passwörter** (Festlegung 24.11.2026) – nur „ab Werk geschützt, bei Inbetriebnahme ändern, siehe Anleitung“. |
| WEEE | Vorerst ausgeklammert (siehe `ce-konformitaet.md`). |
| Sicherheitsmeldungen | Eigene Adresse **security@openandhome.de** (Postfach bzw. Weiterleitung einrichten). |
| Vierter Fühler Typ 2026 | Als **Zubehör** (Fühler-Produkte 2260, 2766–2769), keine eigene Variante. |
| Umsetzung | **Direkt im WordPress-Editor**, vorher **Sicherung** (Abschnitt 5). |

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
- F7 **Alte Produktnamen** überall (LAN Sensorbox PoE/Professional, WLAN/Premium Sensorbox, Standalone).
- F8 **Gedruckte Adressen `/ce/typ-2026|2025` laufen ins Leere** (Seiten fehlen, alle URLs mit `/index.php/`).
- F9 **GPSR-Pflichtangaben im Shop fehlen** (Hersteller mit Anschrift, Kennung, Warnhinweise, Anleitung).
- F10 Keine Meldeadresse für Sicherheitslücken (CRA-Meldepflicht seit 11.09.2026).

**Schwächen für Gewerbe:** keine Referenzen; Angebot nur über Kontaktseite; keine PDFs
(Datenblatt, Anleitung); Tonalität und Fotos privat; `/index.php/` in allen URLs; mehrere H1.

---

## 2. Positionierung

**Hero (Entwurf):**

> **Messtechnik unter Ihrer Kontrolle.**
> Die Sensorbox Typ 2026: Netzwerk-Sensorbox für Serverraum, Technikraum und Labor – Open Source,
> ohne Cloud, per PoE angebunden und über offene Standards (Prometheus, JSON, MQTT, HTTP) in Ihr
> eigenes Monitoring integriert. Im Einsatz bei Behörden und Hochschulen.
>
> [Angebot anfragen] [Datenblatt (PDF)] [CE-Unterlagen]

**Zielgruppen:** 1. IT-Betrieb in Behörden, Hochschulen, Forschung · 2. Unternehmen und
Systemhäuser · 3. Gebäude, Kirchen, Landwirtschaft · 4. Privat (Typ 2025, eigener Bereich).

**Souveränitäts-Argumente (prüfbar):** keine Cloud, kein Konto, keine Telemetrie · keine
Auftragsverarbeitung (AVV) nötig · quelloffene Firmware (ESPEasy), Konfigurationen auf GitHub ·
Update/Wiederherstellung offline mit ohtoolbox · offene Standards statt Lock-in, kein Abo ·
Montage, 24-h-Test und Support in Deutschland · **CE-Unterlagen öffentlich** · ehrlicher
Sicherheitsleitfaden mit Meldeadresse für Schwachstellen.

**Typen auf einen Blick** (Tabelle für Startseite und Produktseiten):

| | Sensorbox Typ 2026 (LAN/PoE) | Sensorbox Typ 2025 (WLAN) |
|---|---|---|
| Für | Gewerbe, Behörden, Hochschulen | Privat |
| Netzwerk | Ethernet mit PoE, WLAN als Rückfall | WLAN |
| Technik | ESP32 (Olimex ESP32-POE) | ESP8266 (D1 mini) |
| Fühler | bis zu 4 (Standard 3) | bis zu 4 |
| Zusätze | Feuchte, Wasser/Kontakt, Display | Feuchte, Display, Distanz |
| Kennung | 150x80 V1.9 | 79x59 V1.9 |
| Kauf | Angebot oder Shop | Shop |

---

## 3. Phasen im Überblick

Reihenfolge abgestimmt mit `umbenennung-typ2026-2025.md` Abschnitt 6: zuerst Pflicht und Rechtliches,
dann Namen im Shop, dann Startseite und Inhalte.

### Phase 0 – Sofort (Fehler und Pflichtangaben) – umgesetzt 20.11.2026

Sicherung vorher: `~/sicherungen-openandhome-webseite/openandhome-{db,app}-2026-11-20_2021.*` (lokal und auf
dem Server unter `~/sicherungen/`). Hinweis: Der WordPress-Container hat kein `mysqldump`; die Datenbank wird
im Container `wordpress-db-openandhome` mit `mariadb-dump` gesichert (Abschnitt 5 entsprechend).

1. ✔ Impressum (Seite 10359, `/index.php/impressum/`) veröffentlicht: Gesellschafter Martin Ament und Thomas
   Heinrichs (beide auch verantwortlich nach § 18 Abs. 2 MStV), im Footer an erster Stelle. [Empfohlen] juristisch prüfen.
2. ✔ Footer: Widget „Rechtliches“ (Menü 43) in Footer-Spalte 1: Impressum · Datenschutzerklärung · AGB · Widerrufsbelehrung ·
   Versand und Zahlung · Kontakt. CE-Unterlagen folgen (Phase 1).
   Neue Seiten: „Widerrufsbelehrung“ (10357, Text unverändert aus AGB § 6/7), „Versand und Zahlung“ (10358,
   aus den WooCommerce-Einstellungen: DE 4,99 €, EU 9 €, Abholung; Vorkasse, PayPal; 7 Werktage aus AGB § 4).
3. ✔ Sitemap: Plugin `google-sitemap-generator` deaktiviert, Yoast-Sitemap an (`/sitemap_index.xml`,
   `/sitemap.xml` leitet weiter). **Offen (ihr):** in der Search Console einreichen.
4. ✔ Menüpunkt „English“ (Google Translate) gelöscht.
5. ✔ § 19 UStG: Code-Snippet „Kleinunternehmer-Hinweis (§ 19 UStG)“ – Zusatz am Preis, Zeile in Warenkorb und
   Kasse, Satz in Bestellmails. AGB § 3 (1) „enthalten die gesetzliche Umsatzsteuer“ ersetzt durch „Endpreise,
   gemäß § 19 UStG keine Umsatzsteuer“ (Revision in WordPress). **Offen (ihr):** Rechnungen außerhalb des Shops prüfen.
6. ✔ Sonderangebot (ID 9879) auf „privat“.

### Phase 1 – CE-Seite und Weiterleitung (Voraussetzung: Erklärungen unterschrieben)

1. **Ansible** `server-inet/wordpress`: Weiterleitung `/ce/…` → `/index.php/ce/…` (`.htaccess`-Block nur
   für Instanz `openandhome`), damit die gedruckten Adressen sofort funktionieren.
2. Seite „CE-Unterlagen“ (`/ce/`) mit Unterseiten `typ-2026` und `typ-2025`. Inhalt je Typ:
   vollständige EU-Konformitätserklärung (PDF, unterschrieben), vereinfachte Erklärung als Text,
   Bedienungsanleitung (PDF, **Webseiten-Fassung** ohne Passwörter), Funkdaten (2,4 GHz; 19,5 dBm bzw. 20 dBm), Sicherheitshinweise,
   Hersteller mit Anschrift, Kennung und Gültigkeit, Firmware-Stand und Update-Weg.
   Details und was **nicht** veröffentlicht wird: Umbenennungsplan Abschnitt 5.
3. Abschnitt **„Sicherheitslücken melden“** auf `/ce/` (CRA): Meldeadresse **security@openandhome.de**,
   Ablauf aus CE-Mappe 16. Vorher Postfach bzw. Weiterleitung einrichten und testen.
4. [Optional] `/.well-known/security.txt` über die Ansible-Rolle (`Contact: mailto:security@openandhome.de`,
   Ablaufdatum, Link auf `/ce/`).
5. PDFs mit Datum im Namen hochladen; alte Fassungen behalten und als „ersetzt am …“ führen.

### Phase 2 – Shop umstellen (Namen, Kategorien, GPSR)

Produkt-IDs, neue Namen und Textänderungen: Umbenennungsplan Abschnitt 4. Kurz:

1. Kategorien neu: „Sensorbox Typ 2026 (LAN/PoE)“, „Sensorbox Typ 2025 (WLAN)“, „Fühler und Zubehör“,
   „Datenlogger“; alte Kategorien „Sensorbox“/„Temperatursensor“ auflösen.
2. Produktnamen und -texte auf Typ 2026/2025; Platzhalter der Typ-2026-Seite füllen (F2).
3. Fühler-Texte vereinheitlichen: **bis zu 4 Fühler je Box**; Typ 2026 mit 3 Fühlern, der vierte als
   **Zubehör** (Fühler-Produkte verlinken, „passt zu Sensorbox Typ 2026 und Typ 2025“).
4. Artikelnummern (SKU) eintragen.
5. **GPSR je Box-Produkt:** Hersteller mit Anschrift und Mail, Typ und Kennung, Warn- und
   Sicherheitshinweise, Link auf Anleitung (PDF, Webseiten-Fassung) und auf `/ce/typ-…`.
6. Hinweis bei beiden Boxen: „Die Einstellungen sind ab Werk durch ein Passwort geschützt – bitte bei der
   Inbetriebnahme ändern (siehe Bedienungsanleitung).“ **Ohne Passwort-Wert.**
7. Alte Produkt-Adressen nach der Umbenennung stichprobenartig prüfen (WordPress leitet weiter).

### Phase 3 – Startseite und Navigation

**Navigation:**

```
Lösungen ▾              Produkte ▾                          Wissen ▾        Über uns   Angebot anfragen
 - Serverraum & IT       - Sensorbox Typ 2026 (LAN/PoE)                  - Dokumentation
 - Labor & Forschung     - Datenlogger (Ergänzung)                        - Integration
 - Gebäude & Heizung     - Fühler & Zubehör                               - Sicherheit
 - Lager & Kühlung       - Sensorbox Typ 2025 (WLAN, privat)              - CE-Unterlagen
 - Smart Home (privat)                                                    - Praxis (Blog)
                                                                          - FAQ
```

**Startseite:**

1. Hero mit Foto der Sensorbox Typ 2026, Buttons „Angebot anfragen“, „Datenblatt (PDF)“, „CE-Unterlagen“.
2. Vertrauensleiste, anonym: „Im Einsatz bei Behörden, Hochschulen und Unternehmen“ (ohne Fallstudien).
3. „Digitale Souveränität – konkret“: 4–6 Punkte mit Link zu GitHub.
4. „So binden Sie die Box ein“: Schema Box → Prometheus/Zabbix/MQTT → eigenes System.
5. Produktkacheln: Typ 2026 groß, Datenlogger als Ergänzung, Fühler/Zubehör;
   Typ 2025 klein „für Privatanwender“.
6. Tabelle „Typen auf einen Blick“ (Abschnitt 2).
7. Praxisbeispiele (Kirchenheizung, Pufferspeicher, Getreide).
8. Abschluss-Block „Angebot anfragen“.

Alle übrigen Seiten (Über uns, FAQ, Kontakt) beim Überarbeiten auf Typ 2026/2025 umstellen; ältere
Blogbeiträge nicht umschreiben, nur Produktlinks auf die neuen Seiten setzen.

**Button „Angebot anfragen“** (Startseite, Typ-2026-Seite, Menü) als `mailto:`-Link mit
vorbelegtem Betreff und Text. Die Mailadresse steht zusätzlich als Text daneben, weil
`mailto:` ohne eingerichtetes Mailprogramm (z. B. Webmail) nichts öffnet. Vorlage:

```
Betreff: Angebotsanfrage Sensorbox Typ 2026

Guten Tag,

bitte senden Sie uns ein Angebot für:

Anzahl Sensorboxen Typ 2026:
Einsatzort (z. B. Serverraum, Labor, Lager):
Temperaturfühler je Box (Standard 3, vierter als Zubehör) und Kabellänge:
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

### Phase 4 – Inhalte für Gewerbe

1. Landingpage „Sensorbox Typ 2026“ (Nutzen, Schnittstellen, Technik, Montage, Varianten mit bis zu
   4 Fühlern, Downloads, Angebot-Button); Datenlogger dort als Ergänzung.
2. Downloads (PDF): Datenblatt Typ 2026, Anleitung Typ 2026 (Webseiten-Fassung aus `docs/`), Link auf `/ce/typ-2026`,
   Sicherheitsleitfaden.
3. ~~Referenzen-Seite~~ entfällt (keine Fallstudien). Stattdessen auf der Typ-2026-Seite typische
   Einsatzbereiche (Serverraum, Labor, Lager) ohne Kundennennung. Später nachholen, wenn Kunden zustimmen.
4. Integrationsanleitungen: Zabbix, Prometheus/Grafana, CheckMK/Icinga, MQTT/Home Assistant;
   Vorlagen auf GitHub. Hinweis: `/json` und `/metrics` sind ohne Anmeldung lesbar, Monitoring
   braucht kein Passwort.
5. Seite „Für Behörden und Unternehmen“: Kauf auf Rechnung, Kleinunternehmer-Hinweis,
   Lieferzeit, Gewährleistung, Ersatzteile, Firmware-Pflege, CE-Unterlagen, Angebot-Button.
   (Ersetzt die Referenzen-Seite als Vertrauensseite.)
6. „Über uns“ neu: Team, Erfahrung bei Behörden und Hochschulen (anonym), Werte, Standort.
7. Seite **Sicherheit** (Sicherheitsleitfaden): Passwort ab Werk **bei Inbetriebnahme ändern** (ohne Wert,
   Verweis auf die Anleitung); eigenes VLAN und erlaubter IP-Bereich; Weboberfläche nur HTTP; keine ausgehenden
   Verbindungen ab Werk (NTP lokal, Internet nur als Fallback); Updates mit dokumentierten SHA256
   über ohtoolbox; USB und PoE nie gleichzeitig (Typ 2026); Daten vor Rückgabe löschen;
   Sicherheitslücken an security@openandhome.de melden (Link `/ce/`).

### Phase 5 – Technik, SEO, Pflege

1. Permalinks ohne `/index.php/`, mit 301-Weiterleitungen (vorher Links in Dashboard-Footer,
   Readmes, Anleitungen prüfen). Die `/ce/`-Weiterleitung aus Phase 1 bleibt unschädlich.
2. Eine H1 je Seite; Schema.org `Organization`, `Product` (mit SKU), `FAQPage`.
3. Begriffe: „Temperaturüberwachung Serverraum“, „PoE Temperatursensor Prometheus“,
   „Zabbix Temperatursensor“, „Sensor ohne Cloud“.
4. Neue Produktfotos (Hutschiene, Rack, Anschlüsse, Etikett mit Kennung), Logo als SVG.
5. Blog → „Praxis“, etwa ein Beitrag pro Quartal mit Schwerpunkt Gewerbe.
6. Datenschutzerklärung aktualisieren (ohne Drittanbieter kurz und klar).

### Phase 6 – Privatbereich

Sensorbox Typ 2025, Display und Set unter „Smart Home (privat)“ bündeln; Shop bleibt für beide
Zielgruppen, Startseite und Navigation führen zuerst zu Typ 2026/Gewerbe.

---

## 4. Abhängigkeiten

| Schritt | braucht vorher |
|---|---|
| CE-Seite (Phase 1) | unterschriebene Erklärungen (CE-Mappe 01) als PDF, Anleitungen (Webseiten-Fassung) als PDF |
| Shop-Hinweis Passwort (Phase 2.6) | Test der Passwort-Funktion an einer echten Box (`ce-konformitaet.md`) |
| Produktfotos mit Etikett | neue Etiketten (`.lbx`, Umbenennungsplan Abschnitt 2) |
| Permalinks (Phase 5.1) | Prüfung der Links in Dashboard-Footer, Readmes, Anleitungen |

## 5. Sicherung vor jeder Bearbeitung

Umsetzung direkt im Editor, darum **vor jeder Arbeitssitzung** (und vor den Phasen 1, 2 und 5 unbedingt)
eine vollständige Sicherung von Datenbank und Dateien. Container laut Ansible-Rolle
`server-inet/wordpress` (Instanz `openandhome`): `wordpress-openandhome`, `wordpress-db-openandhome`;
Dateien unter `{{ dir_data }}/wordpress-openandhome/app`. wp-cli ist im Container (Wartungsskript).

```
# auf dem Server, Datum im Namen
D=$(date +%F_%H%M)
mkdir -p ~/sicherungen
sudo docker exec wordpress-db-openandhome sh -c 'mariadb-dump -uroot -p"$MARIADB_ROOT_PASSWORD" --single-transaction --databases wp-openandhome' | gzip > ~/sicherungen/openandhome-db-$D.sql.gz
sudo tar czf ~/sicherungen/openandhome-app-$D.tar.gz -C /mnt/datenstorage/data/wordpress-openandhome app
```

- Sicherung vom Server herunterladen und außerhalb aufbewahren; Inhalt kurz prüfen (`tar tzf`).
- Wiederherstellung: `app` zurückspielen, SQL mit `mariadb` im DB-Container einspielen.
- [Optional] Als Skript `wordpress_sicherung.sh` in die Ansible-Rolle aufnehmen.
- Zusätzlich vor Shop-Änderungen: WooCommerce → Produkte → Export (CSV) als schnelle Teilsicherung.

## 6. Stufenplan mit Status

| Stufe | Inhalt | Status |
|---|---|---|
| Phase 0 | Impressum, Footer „Rechtliches“, Widerruf, Versand/Zahlung, Sitemap, English weg, § 19 UStG, Sonderangebot privat | ✔ 20.11.2026 (Rest siehe 7.1) |
| Zwischenschritt | FAQ „Kann ich meinen Sensor aus dem Internet einsehen?“ (ufaq 9687) neu: VPN/WireGuard, FRITZ!-Anleitungen, Abruf per IP, keine Portfreigabe, ohne Passwort-Wert | ✔ 24.11.2026 |
| Phase 1 | CE-Seite `/ce/`, Weiterleitung per Ansible, Sicherheitslücken melden, security.txt | wartet auf unterschriebene Erklärungen und Postfach security@ |
| Phase 2 | Shop: Kategorien, Typ-Namen, SKU, 4 Fühler, GPSR, Passwort-Hinweis ohne Wert | geplant |
| Phase 3 | Startseite, Navigation, FAQ/Über uns/Kontakt auf Typ 2026/2025 | geplant |
| Phase 4 | Gewerbe-Inhalte, Seite „Für Behörden und Unternehmen“, Seite „Sicherheit“ | geplant |
| Phase 5 | Permalinks ohne `/index.php/`, Schema.org, Fotos, Blog, Datenschutzerklärung | geplant |
| Phase 6 | Privatbereich bündeln | geplant |

Sicherungen: 20.11.2026 (DB + Dateien, lokal und Server), 24.11.2026 (DB, Server `~/sicherungen/`).

## 7. Anmerkungen und offene Punkte

### 7.1 Für euch (Handarbeit)

- Search Console: <https://search.google.com/search-console> → Property `openandhome.de` (Domain, DNS-TXT) →
  Sitemaps → `sitemap_index.xml` senden; alte `sitemap.xml` entfernen. Bing: <https://www.bing.com/webmasters>
  (Import aus der Search Console).
- Testbestellung durchspielen: § 19-Hinweis in Warenkorb, Kasse und Bestellmail prüfen (nur Shopseite getestet).
- Rechnungen außerhalb des Shops auf den § 19-Hinweis prüfen.
- Impressum juristisch prüfen lassen; § 18 MStV nennt derzeit beide Gesellschafter – ggf. auf eine Person ändern.
- Postfach bzw. Weiterleitung security@openandhome.de einrichten und testen (vor Phase 1).
- Unterschriebene EU-Konformitätserklärungen als PDF (vor Phase 1).

### 7.2 Gefunden, noch nicht erledigt

- ✔ **Werks-Passwort in der Anleitung** (gelöst 24.11.2026): `tools/docs/anleitung.py --web` erzeugt je Typ eine
  **Webseiten-Fassung** (`docs/… - Typ 2026|2025 - Webseite.docx`) ohne Admin-Passwort und WLAN-Schlüssel – dort steht
  „siehe gedruckte Anleitung“, vorn ein Hinweis (gedruckte Anleitung in der Verpackung oder auf Anfrage per Mail).
  Sonst identisch. **Auf CE-Seite und Produktseiten nur diese Fassung** als PDF verlinken; die gedruckte Fassung
  liegt jeder Box bei.
- **Shop nennt noch alte Produktnamen** (z. B. 9743 „Temperatur- und Feuchtefühler inkl. Sensorbox mit Display“);
  Kunden kommen über diese Adressen. Bis Phase 2 in Antworten „heute Sensorbox Typ 2025“ schreiben.
- **FAQ allgemein:** weitere Einträge nennen Datenlogger-Einrichtung mit Controller-Werten, TeamViewer-Support
  (8132) und „Premium“-Begriffe – bei Phase 3 durchsehen. FAQ 9717 (Toolbox-Reset) ist aktuell.
- **Datenschutzerklärung** nennt als Betreiber „Ament-IT“ statt der GbR (Phase 5.6).
- **AGB** gelten nur für Verbraucher (F4); für Behörden/Unternehmen Kauf auf Rechnung ergänzen (Phase 4.5).
- Entwurf „Richtlinie für Rückerstattungen und Rückgaben“ (Seite 9912) liegt ungenutzt – löschen oder
  mit der Widerrufsseite zusammenführen.
- `robots.txt` enthält keine `Sitemap:`-Zeile – [Optional] in Yoast ergänzen.
- Sicherung: Der WordPress-Container hat kein `mysqldump`; immer über `wordpress-db-openandhome` sichern.
  Inhalte **nie** aus einer Datei aktualisieren, ohne vorher die Länge zu prüfen (am 24.11. kurz leere FAQ,
  sofort wiederhergestellt).

### 7.3 Kundenanfragen – Antwortvorlage „Zugriff von unterwegs“ (Typ 2025, privat)

Anlass: Anfrage 24.11.2026 (Privatkunde, FRITZ!Box 7490, Telekom-DSL, Abruf ohne Cloud per Browser von extern).
Erkenntnis für Phase 3/4: Diese Frage kommt wieder – FAQ 9687 ist dafür jetzt die Referenz; auf der Produktseite
Typ 2025 einen Satz „Abruf von unterwegs per VPN“ mit Link aufnehmen.

```
Betreff: AW: Netzwerkfähiger Temperatur- und Feuchtigkeitssensor – Abruf ohne Cloud

Sehr geehrte/r …,

vielen Dank für Ihre Anfrage und Ihr Interesse an unserer Sensorbox.

Ja, das ist mit dem Gerät möglich – ganz ohne Cloud und ohne eigene App.

Im eigenen WLAN
Die Sensorbox (heute „Sensorbox Typ 2025“, WLAN) verbindet sich mit Ihrer FRITZ!Box im 2,4-GHz-WLAN.
Die Messwerte rufen Sie im Browser auf: http://<IP-Adresse der Box>/openandhome.esp – die IP-Adresse
finden Sie in der FRITZ!Box unter „Heimnetz → Netzwerk“. Zusätzlich zeigt das Display die aktuellen
Werte an. Die Box sendet keine Daten ins Internet; die Firmware ist vollständig quelloffen (ESPEasy):
https://openandhome.de/index.php/ufaqs/ist-eure-komplette-firmware-auf-dem-geraet-open-source-oder-nur-die-basis-software-esp-easy/

Von unterwegs
Für den Zugriff von außen empfehlen wir eine VPN-Verbindung zu Ihrer FRITZ!Box. Die 7490 unterstützt
WireGuard (ab FRITZ!OS 7.50), sonst IPSec; mit einem Telekom-DSL-Anschluss funktioniert das in der Regel
problemlos. Auf Smartphone oder Laptop brauchen Sie nur den VPN-Client, z. B. die freie WireGuard-App –
eine Hersteller-App von uns ist nicht nötig. Ist das VPN aktiv, öffnen Sie dieselbe Adresse wie zu Hause.
Schritt für Schritt, mit Links zu den FRITZ!-Anleitungen:
https://openandhome.de/index.php/ufaqs/kann-ich-meinen-sensor-aus-dem-internet-einsehen/

Von einer Portfreigabe im Router raten wir ausdrücklich ab: Die Weboberfläche ist nicht verschlüsselt
(HTTP) und gehört nicht offen ins Internet.

Verlauf und Einbindung (optional)
Die Box zeigt die aktuellen Werte. Für Verläufe und Diagramme gibt es zwei Wege: unseren Datenlogger
(läuft ebenfalls lokal bei Ihnen und ist über dasselbe VPN erreichbar) oder die Einbindung über offene
Schnittstellen (MQTT, JSON, Prometheus) in ein eigenes System wie Home Assistant:
https://openandhome.de/index.php/ufaqs/ich-moechte-die-sensoren-in-mein-smarthome-einbinden-wie-laeuft-die-konfiguration/
https://openandhome.de/index.php/ufaqs/kann-ich-den-datenlogger-auch-nachtraeglich-ergaenzen/

Zugang
Die Einstellungen der Box sind ab Werk durch ein Passwort geschützt. Bitte ändern Sie es bei der
Inbetriebnahme; die Bedienungsanleitung beschreibt das Schritt für Schritt.

Bei Fragen melden Sie sich gern.

Mit freundlichen Grüßen
Martin Ament
Ament & Heinrichs OpenandHome GbR
info@openandhome.de
```

## 8. Offen (Entscheidungen)

- Fallstudien nachholen, sobald ein Kunde zustimmt.

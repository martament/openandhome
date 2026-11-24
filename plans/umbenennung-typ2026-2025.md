# Plan: Umbenennung der Sensorboxen in Typ 2026 und Typ 2025

Stand: 20.11.2026 · Plan, noch keine Umsetzung. Webseite und Shop werden hier **nur geplant**.
Bezüge: [`ce-konformitaet.md`](ce-konformitaet.md), [`webseite-gewerbe.md`](webseite-gewerbe.md).

## 1. Namensschema

| | Typ 2026 | Typ 2025 |
|---|---|---|
| Name (Shop, Anleitung, Erklärung) | **openandhome Sensorbox Typ 2026** | **openandhome Sensorbox Typ 2025** |
| Kurzform | Typ 2026 | Typ 2025 |
| Beiname (Untertitel, Shop) | LAN/PoE | WLAN |
| Kennung (Etikett, CE) | Typ 2026 · 150x80 V1.9 | Typ 2025 · 79x59 V1.9 |
| Technik | ESP32 (Olimex ESP32-POE Rev. M2) | ESP8266 (AZ-Delivery D1 mini) |
| Zielgruppe | Gewerbe (primär), auch privat | privat |
| Bisherige Namen (entfallen) | Sensorbox Professional, LAN Sensorbox PoE, Professionalbox | Sensorbox Standalone, WLAN Sensorbox, Premium Sensorbox/Premiumbox |

Regeln:

- In Texten für Kunden nur noch „Sensorbox Typ 2026“ bzw. „Typ 2025“, beim ersten Vorkommen mit Beiname
  („Sensorbox Typ 2026 (LAN/PoE)“).
- **Kein Übergangshinweis** auf die alten Namen (Festlegung 20.11.2026): überall nur noch Typ 2026 und Typ 2025.
- Ältere Geräte (Typ 2020, 2021.1, 2023.1, Sonderangebot 82×58×35 mm) behalten ihre Namen; sie werden nicht
  mehr verkauft.

**Technische Kennungen bleiben unverändert** (Ordner `configs/espeasy/professional|standalone`,
`oh_klassen.py` `name`, Manifest-Pfade, `anleitung.py --variante professional|standalone`). Grund: ausgelieferte
Toolbox-Versionen laden `tools/ohtoolbox/manifest.json` und die Dateien darin von GitHub `master`, und der
Dashboard-Footer verlinkt auf `…/master/…`. Eine Umbenennung der Ordner bräuchte eine Übergangszeit mit
beiden Pfaden – [Optional, später].

## 2. Unterlagen (ownCloud `openandhome/`)

| Datei / Ordner | Änderung | Status |
|---|---|---|
| `00 - 2026 - Neue Dokumente/CE/…` | bereits mit Typ 2026/2025 erstellt | ✔ |
| `…/2026 openandhome - Bedienungsanleitung - Professional.docx` (Ordner 00, Stand 16.11.) | durch neue Fassung aus dem Repo ersetzen, Name „2026 openandhome - Bedienungsanleitung - Typ 2026.docx“ | offen |
| `…/2025 openandhome - Bedienungsanleitung - Standalone.docx` | ebenso → „… - Typ 2025.docx“ | offen |
| `…/Konformitätserklärung-Professionalbox-2026.docx`, `…-Standalone Box-2025-1.docx` | ersetzt durch CE-Mappe; nach `15 - Konformität/Archiv/` verschieben | offen |
| `…/11_2026 - … Bauteilliste - Bestellliste 2026.xlsx` | Blattnamen „Professional-Netzwerk“ → „Typ 2026“, „Standalone-Wifi“ → „Typ 2025“; Titel „Bestellliste - Professional Temperatur Bauteile 2026“ → „Bestellliste Sensorbox Typ 2026“, „Bestelliste - Premium Standalone - Bauteile Typ 2025“ → „Bestellliste Sensorbox Typ 2025“ | ✔ 20.11. (Blätter „Typ 2026 LAN-PoE“, „Typ 2025 WLAN“, „Set Typ 2025 Datenlogger“) |
| `…/2026 - … Typ 2026 Aufdruck 36 mm.lbx`, `2025 - … Typ 2025 …lbx` | Etikett: „Sensorbox Typ 2026 · 150x80 V1.9“, CE, Hersteller mit Anschrift, Mülltonne (siehe CE-Mappe Dokument 03) | offen |
| `14 - Kunde Bedienungsanleitung`, `18 - Kundenbeschreibung Homepage`, `23 - Webseite` | Texte bei Gelegenheit anpassen; Altfassungen behalten | [Optional] |
| `03 - Zeichnungen/easyeda/150x80`, `79x59` | Platinenaufdruck bleibt; bei der nächsten Revision „Typ 2026“/„Typ 2025“ in den Bestückungsdruck aufnehmen | [Optional] |

## 3. Repository (`01 - Entwicklung/openandhome`)

| Datei | Änderung | Status |
|---|---|---|
| `tools/docs/anleitung.py` + `docs/*.docx` | Titel, Einleitung, Fließtexte Typ 2026/2025 ohne „bisher“; Dateien `docs/2026 openandhome - Bedienungsanleitung - Typ 2026.docx` / `- Typ 2025.docx` | ✔ 20.11. |
| `tools/ohtoolbox/bin/oh_toolbox.py`, `oh_flasher.py`, `tools/bin/oh_kunde.py`, `oh_server.py` | Anzeige „Sensorbox Typ 2026/2025 erkannt“, Warnung USB/PoE mit Typ 2026 | ✔ 20.11. |
| `tools/bin/espeasy_testbox.py`, `espeasy_autoconfig.py`, `espeasy_fsimage.py` | Ausgaben und Kommentare | ✔ 20.11. |
| `tools/bin/espeasy_download.py` + `readme_image.txt` | Kopfzeile „Firmware-Image Typ 2026/2025 …“ (Kopfzeile in beiden Dateien gleich mitgezogen) | ✔ 20.11. |
| `tools/ohtoolbox/README.md`, `RELEASE_EINLEITUNG.md` | Typ 2026/2025 | ✔ 20.11. |
| `README.md`, `AGENTS.md`, `tools/ohwerkstatt/README.md` | Begriffe und Abschnitt 4 „Geräteklassen“ | ✔ 20.11. |
| `server/stack/grafana/dashboards.py`, `boxsystem.json`, `server/AGENTS.md` | „ältere ESP8266-Boxen“ | ✔ 20.11. |
| `tools/bin/espeasy_testbox.py` (`erzeuge_dashboard`) | Dashboard zeigt „Sensorbox Typ 2026/2025“ | ✔ 20.11. |
| `plans/*.md` | laufende Pläne bei der nächsten Bearbeitung anpassen; erledigte Pläne nicht | – |

Danach: Manifest neu erzeugen (`python3 tools/bin/oh_klassen.py`) und prüfen, dass sich nichts ändert außer
Texten; Werkstatt und Toolbox einmal je Typ durchspielen.

## 4. Webshop (WooCommerce) – nur Plan

Umsetzung später im WordPress-Admin (Produkte → Bearbeiten). WordPress leitet geänderte Produkt-Slugs
automatisch weiter (`_wp_old_slug`); nach der Umstellung alte Adressen stichprobenartig prüfen.

### 4.1 Kategorien

| Neu | Inhalt |
|---|---|
| Sensorbox Typ 2026 (LAN/PoE) | 10159 |
| Sensorbox Typ 2025 (WLAN) | 8677, 9743, 9745 (Set) |
| Fühler und Zubehör | 2260, 2766–2769, 10231, 8682 |
| Datenlogger | 10051 |

Alte Kategorien „Sensorbox“ und „Temperatursensor“ auflösen. Die PoE-Box hat heute **keine** Kategorie.

### 4.2 Produkte

| ID | Heutiger Name | Neuer Name | Text ändern |
|---|---|---|---|
| 10159 | LAN Sensorbox PoE mit 3 Temperatursensoren (Professional, RJ45) | **Sensorbox Typ 2026 (LAN/PoE) mit 3 Temperaturfühlern** | „LAN Sensorbox PoE“ → „Sensorbox Typ 2026“; Platzhalter „[bitte ergänzen]“ füllen; Rev. M2/PoE-Klasse 0; Link CE-Unterlagen |
| 8677 | WLAN Sensorbox Temperatur für bis zu 4 Fühler (ohne Fühler, MQTT, Smart-Home-fähig) | **Sensorbox Typ 2025 (WLAN) für bis zu 4 Temperaturfühler** | Gehäusemaß 132,2 × 68,7 × 50,1 mm bleibt; Link CE-Unterlagen |
| 9743 | Temperatur- und Feuchtefühler inkl. Sensorbox mit Display (Wlan/Wifi MQTT Smarthomefähig) | **Sensorbox Typ 2025 (WLAN) mit Temperatur-/Feuchtefühler und Display** | wie oben |
| 9745 | Set: Temperatur- und Feuchtemessung mit Langzeitüberwachung | **Set: Sensorbox Typ 2025 mit Datenlogger (Temperatur und Feuchte)** | „Master Sensorbox“ → „Sensorbox Typ 2025“ |
| 10051 | Openandhome-Datenlogger | **openandhome Datenlogger für Sensorbox Typ 2026 und Typ 2025** | „als Ergänzung“ (siehe Webseiten-Plan) |
| 8682 | Infodisplay zur Anzeige weiterer Informationen | **OLED-Display für Sensorbox Typ 2026 und Typ 2025** | „Kann nur in Premiumbox verbaut werden“ → „für Typ 2026 und Typ 2025“ |
| 10231 | Wasser- und Kontaktsensor (Typ WLS-06) | bleibt | „Premium Sensorbox … oder Sensorbox Professional (Kabel/RJ45)“ → „Sensorbox Typ 2026 oder Typ 2025“ |
| 2260, 2766–2769 | Temperaturfühler 1/3/5/10/15 m (DS18B20) Wasserdicht | bleiben | „Sensorbox von Openandhome“ / „Premium Sensorbox“ → „Sensorbox Typ 2026 oder Typ 2025“; Satz „bis zu 2 … / bis zu 4 mit Premium“ (3 m) vereinheitlichen: bis zu 4 Fühler je Box (Typ 2026 und Typ 2025) |
| 9879 | Sensorbox vorgefertigt mit 1M Fühler … Sonderangebot (ausverkauft, altes Gehäuse 82×58×35) | – | ausblenden (Status „privat“), nicht umbenennen |

Zusätzlich je Box-Produkt (Typ 2026, Typ 2025, Set, Datenlogger):

- **Pflichtangaben GPSR im Shop:** Hersteller mit Anschrift und Mail, Typ/Kennung, Produktbild,
  Warn- und Sicherheitshinweise (aus der Anleitung), Link zur Bedienungsanleitung (PDF).
- Abschnitt „Konformität“ mit Link auf die CE-Seite des Typs (Abschnitt 5).
- Hinweis Kleinunternehmer (§ 19 UStG), siehe Webseiten-Plan.
- **Artikelnummern (SKU)** einführen (entschieden): `OH-2026-PoE-3F`, `OH-2025-WLAN`, `OH-2025-WLAN-TFD`, `OH-SET-2025`, `OH-LOG`, `OH-F-01/03/05/10/15`, `OH-WLS06`, `OH-OLED`.

### 4.3 Übrige Seiten

Startseite, Über uns, FAQ, Kontakt und Blogbeiträge nennen die alten Namen (z. B. Startseite „LAN Sensorbox PoE
(Professional)“, „WLAN Sensorbox Temperatur“; FAQ „Sensorbox Professional: Ziehen Sie …“). Anpassen zusammen mit
Phase 3 des Webseiten-Plans; ältere Blogbeiträge nicht umschreiben, nur Produktlinks auf die neuen Seiten setzen (kein
Übergangshinweis).

## 5. Seite „CE-Unterlagen“ – nur Plan

**Adressen** (stehen bereits in den Bedienungsanleitungen und der vereinfachten Erklärung):

- `https://openandhome.de/ce/` – Übersicht
- `https://openandhome.de/ce/typ-2026` und `https://openandhome.de/ce/typ-2025`

**Wichtig:** Die Seite nutzt heute Adressen mit `/index.php/…`. Damit die gedruckten Adressen funktionieren,
entweder (a) eine Weiterleitung `/ce/…` → `/index.php/ce/…` in der Ansible-Rolle
`server-inet/wordpress` (`.htaccess`-Block, nur für Instanz `openandhome`) oder (b) vorher die Permalinks ohne
`index.php` umstellen (Webseiten-Plan Phase 5). Empfehlung: (a) jetzt, (b) später – die Weiterleitung schadet
danach nicht.

**Aufbau:** WordPress-Seite „CE-Unterlagen“ (Slug `ce`) mit zwei Unterseiten `typ-2026` und `typ-2025`;
Link im Footer-Menü (neben Impressum, Datenschutz, AGB).

| Inhalt je Typ | Quelle | Veröffentlichen |
|---|---|---|
| Vollständige EU-Konformitätserklärung (unterschrieben, PDF) | CE-Mappe 01 | ja (Pflicht, RED Art. 10 Abs. 9) |
| Vereinfachte Erklärung (Text auf der Seite) | CE-Mappe 02 | ja |
| Bedienungsanleitung (PDF) | **Webseiten-Fassung** `docs/…Typ 2026/2025 - Webseite.docx` → PDF (ohne Passwörter; `anleitung.py --web`) | ja (GPSR) |
| Sicherheitshinweise, Funkdaten (Frequenzband, max. Sendeleistung) | Anleitung | ja |
| Hersteller mit Anschrift und Mail | – | ja |
| Kennung und Gültigkeit (Platinenversion, ab welchem Datum) | CE-Mappe 03 | ja |
| Aktueller Firmware-Stand und Update-Weg (ohtoolbox) | `readme_image.txt` | ja |
| Kontakt für Sicherheitsmeldungen (CRA) | CE-Mappe 16 | ja |
| Technische Dokumentation (Risikobeurteilung, Bauteilliste, Prüfungen, Gerber) | CE-Mappe 03–11 | **nein** – nur auf Anfrage von Behörden |
| Erklärungen älterer Typen (2020, 2023.1) | `15 - Konformität` | [Optional] als „Archiv“ |

PDFs über die Mediathek hochladen; Dateinamen mit Datum, z. B.
`EU-Konformitaetserklaerung_Sensorbox_Typ_2026_2026-12.pdf`. Bei jeder neuen Fassung alte Datei behalten
und auf der Seite als „ersetzt am …“ führen (Geräte im Feld verweisen auf den Stand ihres Kaufs).

## 6. Reihenfolge

1. Entscheidungen (Abschnitt 7).
2. Repository: Texte in Toolbox, Flasher, Werkstatt, Anleitung, READMEs; Manifest prüfen; Release.
3. Unterlagen: Bestellliste, Etiketten, alte Erklärungen archivieren, Anleitungen ersetzen.
4. CE-Erklärungen unterschreiben, PDFs erzeugen.
5. Webseite: Weiterleitung `/ce/` (Ansible), CE-Seiten anlegen, PDFs hochladen.
6. Shop: Kategorien, Produktnamen und -texte, GPSR-Angaben, Sonderangebot ausblenden.
7. Übrige Webseiten-Texte mit Phase 3 des Webseiten-Plans.

## 7. Entscheidungen (20.11.2026)

1. Kein Übergangshinweis auf die alten Namen – gilt **sofort** (Repository, Anleitungen, CE-Unterlagen und Bestellliste umgestellt am 20.11.2026).
2. **Artikelnummern (SKU) werden eingeführt** – Schema siehe 4.2 (`OH-2026-…`, `OH-2025-…`, `OH-F-…`).
3. **Typ im Dashboard:** ✔ umgesetzt – Kopfzeile „Sensorbox Typ 2026/2025 · openandhome Dashboard“ (wird beim Dashboard-Upload aus dem Firmware-Namen bestimmt; `header.txt` unverändert, damit ältere Toolboxen weiter funktionieren).
4. **Bis zu 4 Fühler je Box** (Typ 2026 und Typ 2025); Shop-Texte entsprechend, Typ 2026 Standard mit 3 Fühlern, der vierte als Zubehör (Fühler-Produkte), keine eigene Variante.

Bewusst unverändert: technische Kennungen in Kleinschreibung (Ordner `configs/espeasy/professional|standalone`, `--variante`), Dateinamen der Platinen-Exporte (`…SensorboxProfessional…`, Original in EasyEDA) und die Artikelbezeichnung des Gehäuselieferanten Sintron („Box Professional 150 90 60“).

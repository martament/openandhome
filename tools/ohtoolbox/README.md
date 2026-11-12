# openandhome-Toolbox und OH-Flasher

Ein Paket mit zwei Programmen für Ihre Sensorbox (**Standalone** und **Professional**):

- **Toolbox** – das Standardwerkzeug: WLAN, Gerätename, Zeitserver, Sensoren erkennen,
  Grundkonfiguration, Resets und Diagnose.
- **OH-Flasher** – Firmware aktualisieren und, als Notlösung, den Sensor komplett neu
  aufspielen.

Für den normalen Betrieb Ihrer Sensorbox brauchen Sie keines der beiden Programme.
Hilft beides nicht, senden Sie uns die Sensorbox – wir stellen den Auslieferungszustand wieder her.

FAQ: https://www.openandhome.de/index.php/2019/01/11/faq/

## Download

**https://github.com/martament/openandhome/releases/latest** – dort unter „Assets“
`ohtoolbox.zip` herunterladen.

Das Paket wird bei jeder Änderung automatisch neu gebaut; was sich geändert hat, steht in
den Release-Notes auf derselben Seite. Firmware und
Grundeinstellungen lädt das Programm beim Start aus dem Internet (immer der freigegebene
Stand); ohne Internet nimmt es die mitgelieferten Dateien.

## Vor dem Start

- ZIP entpacken und die Sensorbox per USB-Kabel mit dem Rechner verbinden.
- **Sensorbox Professional:** Ziehen Sie **vorher das Netzwerkkabel (PoE)** ab. USB und PoE
  dürfen nie gleichzeitig angeschlossen sein – die Box ist nicht galvanisch getrennt,
  angeschlossene Geräte können beschädigt werden. Die Box wird währenddessen über USB versorgt.
  Danach erst USB abziehen, dann das Netzwerkkabel wieder anstecken.

| | Windows | Linux |
|---|---|---|
| Toolbox | Doppelklick auf `start_toolbox.bat` | `./toolbox.sh` |
| OH-Flasher | Doppelklick auf `start_flasher.bat` | `./flasher.sh` |

Unter Linux wird Python 3 benötigt. Meldet das Programm „Kein Sensor gefunden“ oder
„Permission denied“, fehlen die Rechte für die serielle Schnittstelle:
`sudo usermod -aG dialout $USER`, danach einmal ab- und wieder anmelden.

## Toolbox (Standardwerkzeug)

Die Toolbox erkennt beim Start, ob eine Standalone- oder Professional-Box angeschlossen ist.

| Taste | Funktion |
|---|---|
| 1 | **WLAN-Zugangsdaten setzen** – mit Verbindungsprüfung. Klappt die Verbindung nicht, zeigt die Toolbox die WLANs, die der Sensor sieht, und fragt erneut. Bei Erfolg zeigt sie die Adresse des Dashboards. (Professional braucht normalerweise kein WLAN.) |
| 2 | Neustart |
| 3 | Einstellungen anzeigen (IP-Adresse, Name, WLAN) |
| 4 | Debugger – Ausgaben anzeigen und in `oh-debug.txt` speichern (für unseren Support) |
| 5 | WLAN-Daten löschen – danach öffnet der Sensor wieder sein eigenes WLAN „Sensorbox1“ |
| 6 | Reset DHCP – feste IP-Adresse aufheben (bei Professional auch für das Netzwerkkabel) |
| 7 | Admin-Passwort der Weboberfläche zurücksetzen |
| 8 | WLAN-Zugangspunkt des Sensors starten |
| 9 | IP-Filter zurücksetzen (bis zum Neustart), z. B. bei der Meldung „IP blocked“ |
| n | Zeitserver (NTP) setzen – z. B. Ihr Router, wenn Ihr Netz kein Internet hat |
| g | Gerätenamen ändern – bei mehreren Sensoren braucht jeder einen eigenen Namen |
| s | **Sensoren neu erkennen** – nach Tausch oder Erweiterung eines Fühlers; Einstellungen bleiben. Erkennt Fühler, Display und Kombifühler, wählt die Fühleradressen und erneuert Anzeige und Dashboard. Nicht erkennbare Sensoren (Wasser-, Abstandssensor) werden abgefragt. |
| k | **Grundkonfiguration wiederherstellen** – alle Einstellungen auf den Auslieferungszustand, danach Sensoren erkennen. Die Firmware bleibt. |

Für **s** und **k** muss der Sensor kurz im WLAN sein (die Toolbox fragt bei Bedarf danach).
Bei Professional werden diese WLAN-Daten danach wieder gelöscht.

## OH-Flasher

| Taste | Funktion |
|---|---|
| 1 | **Firmware aktualisieren** – aktueller freigegebener Stand, Einstellungen bleiben erhalten |
| 2 | **Sensor neu aufspielen und einrichten** (Notfall) – löscht den Sensor vollständig, spielt die aktuelle Firmware ein und richtet die Grundkonfiguration ein wie Toolbox-Menü **k**. Bei Professional wird zusätzlich der Netzwerkanschluss eingerichtet. |
| 3 | Debug – Ausgaben des Sensors anzeigen |

Es kann einige Minuten dauern, bis der Sensor wiederhergestellt ist.

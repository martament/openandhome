# openandhome-Toolbox (Standardwerkzeug)

Mit der Toolbox richten Sie Ihre Sensorbox über das USB-Kabel ein und beheben
die häufigsten Probleme – für **Standalone**- und **Professional**-Boxen.
Für den normalen Betrieb Ihrer Sensorbox brauchen Sie die Toolbox nicht.

Lässt sich ein Problem mit der Toolbox nicht lösen, gibt es als Notlösung den
[OH-Flasher](../oh-flasher/Readme.md). Hilft auch der nicht, senden Sie uns die
Sensorbox – wir stellen den Auslieferungszustand wieder her.

FAQ: https://www.openandhome.de/index.php/2019/01/11/faq/

## Vor dem Start

- Verbinden Sie die Sensorbox mit einem USB-Kabel mit Ihrem Rechner.
- **Sensorbox Professional:** Ziehen Sie **vorher das Netzwerkkabel (PoE)** ab.
  USB und PoE dürfen nie gleichzeitig angeschlossen sein – die Box ist nicht
  galvanisch getrennt, angeschlossene Geräte können beschädigt werden. Die Box
  wird während der Einstellung über USB versorgt. Danach erst USB abziehen,
  dann das Netzwerkkabel wieder anstecken.

Die Toolbox erkennt beim Start, ob eine Standalone- oder eine Professional-Box
angeschlossen ist, und zeigt das in der Kopfzeile an.

## Die Funktionen im Überblick

| Taste | Funktion |
|---|---|
| 1 | **WLAN-Zugangsdaten setzen** – Name (SSID) und Passwort Ihres WLANs (unsichtbare Eingabe, zur Sicherheit zweimal), optional ein zweites WLAN. Die Toolbox startet den Sensor neu und **prüft, ob er sich verbindet**. Klappt es nicht, zeigt sie die WLANs, die der Sensor sieht, und fragt erneut nach WLAN und Passwort. Bei Erfolg zeigt sie die Adresse des Dashboards. (Professional braucht normalerweise kein WLAN.) |
| 2 | **Neustart** des Sensors |
| 3 | **Einstellungen anzeigen** (IP-Adresse, Name, WLAN) |
| 4 | **Debugger** – Ausgaben des Sensors anzeigen und in `oh-debug.txt` speichern (für unseren Support) |
| 5 | **WLAN-Daten löschen** – danach öffnet der Sensor wieder sein eigenes WLAN „Sensorbox1“ |
| 6 | **Reset DHCP** – feste IP-Adresse aufheben (bei Professional auch für das Netzwerkkabel) |
| 7 | **Admin-Passwort zurücksetzen** (Weboberfläche) |
| 8 | **WLAN-Zugangspunkt starten** (eigenes WLAN des Sensors) |
| 9 | **IP-Filter zurücksetzen** – bis zum nächsten Neustart, z. B. wenn die Weboberfläche „IP blocked“ meldet |
| n | **Zeitserver (NTP) setzen** – z. B. die Adresse Ihres Routers, wenn Ihr Netz kein Internet hat |
| g | **Gerätenamen ändern** – bei mehreren Sensoren braucht jeder einen eigenen Namen |

Bei allen Befehlen wird zusätzlich der FlashWriteCounter des Sensors
zurückgesetzt; ein voller Zähler kann selbst eine Fehlerursache sein.

## Download

https://github.com/martament/openandhome/releases → `ohtoolbox.zip`

Das Archiv enthält eine PowerShell-Datei für Windows und ein Bash-Skript für Linux.

## Start unter Windows

Rechtsklick auf `win_ohtoolbox.ps1` → „Mit PowerShell ausführen“.

Blockiert Windows die Ausführung (Ausführungsrichtlinie), öffnen Sie eine
PowerShell im Ordner der Datei und starten Sie:

    powershell -ExecutionPolicy Bypass -File .\win_ohtoolbox.ps1

## Start unter Linux

Terminal im Ordner der Datei öffnen und starten:

    bash linux_ohtoolbox.sh

Meldet die Toolbox „Kein Sensor gefunden“ oder „Permission denied“, obwohl der
Sensor angeschlossen ist, fehlen Ihrem Benutzer die Rechte für die serielle
Schnittstelle. Fügen Sie ihn der Gruppe `dialout` hinzu und melden Sie sich
einmal ab und wieder an:

    sudo usermod -aG dialout $USER

Sie finden hier die Toolbox für den Sensor von Openandhome.



Für den bestimmungsgem. Betrieb unseres Sensors benötigen Sie diese Programme nicht.

Lesen Sie dazu bitte auch die FAQs auf unserer Homepage
# https://www.openandhome.de/index.php/2019/01/11/faq/
# https://www.openandhome.de/index.php/ufaqs/ich-moechte-die-konfiguration-aendern-ist-dies-moeglich/ 


Sie benötigen diese Programme nur, wenn bei Ihnen in der Konfiguration des Sensors etwas nicht funktioniert wie es sollte. Wir können nicht jede Änderung am Sensor mit unserem Support abdecken. Gleichwohl unterstützen wir mit unserem offenen Ansatz Sie bei Ihren Versuchen.

D.h. Sie können unseren Debugger versuchen und sollte der Ihre Problem nicht lösen, so können Sie uns jederzeit den Sensor zusenden und wir stellen den Auslieferungszustand wieder her.

# https://www.openandhome.de/index.php/ufaqs/ich-habe-ein-problem-mit-meinem-sensor-was-kann-ich-tun/ 

# openandhome-toolbox (Standardprogramm)

Die openandhome-toolbox ist ein Konsolenprogramm, mit dem Sie im Fehlerfall
mehrere Diagnose- und Reparaturmöglichkeiten haben und die WLAN-Zugangsdaten
des Sensors direkt über das USB-Kabel setzen können. Nutzen Sie dieses
Programm wann immer möglich.

Verbinden Sie vor dem Aufruf des Programms die Sensorbox mit einem
Micro-USB-Kabel mit Ihrem Rechner.

Hinweis: Bei fast allen Funktionen wird zusätzlich der FlashWriteCounter des
Sensors zurückgesetzt. Ein voller FlashWriteCounter kann selbst eine
Fehlerursache sein, daher geschieht dies automatisch im Hintergrund.

## Die Funktionen im Überblick

1. **WLAN-Zugangsdaten setzen (SSID/Key)** – Hier können Sie den Sensor in
   Ihr WLAN einbinden, ohne den Zugangspunkt-Modus zu verwenden. Sie werden
   nach der SSID (dem Namen Ihres WLANs) und dem WPA-Schlüssel gefragt; die
   Eingabe des Schlüssels ist dabei unsichtbar und wird zur Sicherheit
   zweimal abgefragt. Optional können Sie ein zweites WLAN als Fallback
   hinterlegen. Nach dem Senden der Daten empfiehlt sich der angebotene
   Neustart, damit sich der Sensor direkt mit dem neuen WLAN verbindet.
2. **Neustart (Reboot)** – Startet den Sensor neu. Nützlich z. B. nach dem
   Ändern von Einstellungen oder wenn sich der Sensor nicht mehr verbindet.
3. **Einstellungen anzeigen (Settings)** – Zeigt die aktuellen Einstellungen
   des Sensors an.
4. **Debugger** – Schreibt die Ausgaben des Sensors in die Datei
   oh-debug.txt und zeigt sie gleichzeitig an. Beenden mit STRG+C.
5. **Reset Wifi** – Setzt die WLAN-Zugangsdaten zurück. Sie müssen den
   Sensor danach erneut in Ihr WLAN einbinden – am einfachsten direkt über
   Menüpunkt 1 oder alternativ über den Zugangspunkt-Modus (Punkt 8).
6. **Reset DHCP** – Hebt eine statische IP-Adresse des Sensors auf, die
   IP wird danach wieder automatisch per DHCP bezogen. Hier bitte kurz
   warten.
7. **Reset Admin Password** – Setzt ein eventuell vergebenes
   Admin-Passwort der Weboberfläche zurück.
8. **Start AP-Mode** – Startet den WLAN-Zugangspunkt des Sensors. Verbinden
   Sie sich anschließend wie in der Anleitung beschrieben mit dem Sensor.
9. **Reset IP-Filtering** – Setzt die Client-IP-Filterung des Sensors für
   die aktuelle Session (bis zum nächsten Neustart) zurück.

## Download

Sie können die Toolbox hier herunterladen:
https://github.com/martament/openandhome/releases => ohtoolbox.zip

Das Archiv enthält eine PowerShell-Datei für Windows und ein Bash-Skript
für Linux. Beide müssen aus einer PowerShell bzw. einem Terminal heraus
aufgerufen werden.

## Start unter Windows

Rechtsklick auf win_ohtoolbox.ps1 => "Mit PowerShell ausführen".

Falls Windows die Ausführung mit einem Hinweis auf die Ausführungsrichtlinie
(Execution Policy) blockiert, öffnen Sie eine PowerShell im Ordner der Datei
und starten Sie das Programm mit:

    powershell -ExecutionPolicy Bypass -File .\win_ohtoolbox.ps1

## Start unter Linux

Öffnen Sie ein Terminal im Ordner der Datei und starten Sie:

    bash linux_ohtoolbox.sh

Falls die Meldung "Kein Sensor gefunden" oder ein Berechtigungsfehler
(Permission denied) erscheint, obwohl der Sensor angeschlossen ist, fehlen
Ihrem Benutzer vermutlich die Rechte für die serielle Schnittstelle. Fügen
Sie Ihren Benutzer der Gruppe "dialout" hinzu und melden Sie sich danach
einmal ab und wieder an:

    sudo usermod -aG dialout $USER

Alternativ können Sie das Skript einmalig mit sudo starten:

    sudo bash linux_ohtoolbox.sh


2. Toolbox kann das Problem nicht lösen

Sollten Sie mit dem Debugger Ihr Problem nicht lösen können, so sollten Sie den Sensor an uns zurück schicken. Wir können Ihnen den Sensor in den Auslieferungszustand zurück versetzen.


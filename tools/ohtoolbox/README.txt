Sie finden hier die Toolbox für den Sensor von Openandhome.



Für den bestimmungsgem. Betrieb unseres Sensors benötigen Sie diese Programme nicht.

Lesen Sie dazu bitte auch die FAQs auf unserer Homepage
# https://www.openandhome.de/index.php/2019/01/11/faq/
# https://www.openandhome.de/index.php/ufaqs/ich-moechte-die-konfiguration-aendern-ist-dies-moeglich/ 


Sie benötigen diese Programme nur, wenn bei Ihnen in der Konfiguration des Sensors etwas nicht funktioniert wie es sollte. Wir können nicht jede Änderung am Sensor mit unserem Support abdecken. Gleichwohl unterstützen wir mit unserem offenen Ansatz Sie bei Ihren Versuchen.

D.h. Sie können unseren Debugger versuchen und sollte der Ihre Problem nicht lösen, so können Sie uns jederzeit den Sensor zusenden und wir stellen den Auslieferungszustand wieder her.

# https://www.openandhome.de/index.php/ufaqs/ich-habe-ein-problem-mit-meinem-sensor-was-kann-ich-tun/ 

1. openandhome-toolbox (Standardprogramm)
Dies ist ein Programm für die Konsole mit dem Sie im Fehlerfall mehrere Möglichkeiten haben. Sie sollten dieses Programm wann immer möglich nutzen.
Bei jedem der Befehler wird auch der FlashWriteCounter des Sensors zurück gesetzt. Dies kann auch eine Fehlerursache sein.

Verbinden Sie vor dem Aufruf des Programms die Sensorbox mit einem Micro-USB-Kabel mit Ihrem Rechner.

# **ResetWifi** hier koennen Sie die Wifizugangsdaten zuruecksetzen. Sie muessen den Sensor danach erneut in Ihr WLAN einbinden.
# **Einstellungen** hier koennen Sie die aktuellen Einstellungen des Sensors anzeigen lassen.
# **Debugger** hier koennen Sie die Ausgaben des Sensors in eine Datei schreiben und anzeigen lassen.
# **ResetDHCP** hier  koennen Sie eine statische IP Ihres Sensors aufheben. Hier bitte kurz warten. 
# **ResetAdmin** hier koennen Sie ein evtl. vergebenenes Adminpasswort zuruecksetzen.
# **StartAPMode** hier koennen Sie den WLAN-Zugangspunkt des Sensors starten und sich wie in der Anleitung beschrieben mit dem Sensor verbinden.
# **ResetIPFiltering** hier koennen Sie die Client-IP-Filterung des Sensors für die aktuelle Session zurücksetzen

Sie können die Toolbox unter https://github.com/martament/openandhome/releases => ohtoolbox.zip herunterladen.

Das Programm ist eine Powershelldatei oder ein Linuxskript. Diese müssen Sie aus einer  Powershell oder einem Terminal heraus aufrufen. 

Windows: Rechte Maustaste win_ohtoolbox.ps1 und öffnen mit Powershell.
Linux: bash linux_ohtoolbox.sh


2. Toolbox kann das Problem nicht lösen

Sollten Sie mit dem Debugger Ihr Problem nicht lösen können, so sollten Sie den Sensor an uns zurück schicken. Wir können Ihnen den Sensor in den Auslieferungszustand zurück versetzen.


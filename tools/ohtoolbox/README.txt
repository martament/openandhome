Sie finden hier den Debugger für den Sensor von Openandhome.



Für den bestimmungsgem. Betrieb unseres Sensors benötigen Sie dieses Programme nicht.

Lesen Sie dazu bitte auch die FAQs auf unserer Homepage
# https://www.openandhome.de/index.php/2019/01/11/faq/
# https://www.openandhome.de/index.php/ufaqs/ich-moechte-die-konfiguration-aendern-ist-dies-moeglich/ 


Sie benötigen diese Programme nur, wenn bei Ihnen in der Konfiguration des Sensors etwas nicht funktioniert wie es sollte. Wir können nicht jede Änderung am Sensor mit unserem Support abdecken. Gleichwohl unterstützen wir mit unserem offenen Ansatz Sie bei Ihren Versuchen.

D.h. Sie können unseren Debugger versuchen und sollte der Ihre Problem nicht lösen, so können Sie uns jederzeit den Sensor zusenden und wir stellen den Auslieferungszustand wieder her.

# https://www.openandhome.de/index.php/ufaqs/ich-habe-ein-problem-mit-meinem-sensor-was-kann-ich-tun/ 

1. openandhome-debugger.exe (Standardprogramm)
Dies ist ein grafisches Programm mit dem Sie im Fehlerfall mehrere Möglichkeiten haben. Sie sollten dieses Programm wann immer möglich nutzen.
Bei jedem der Befehler wird auch der FlashWriteCounter des Sensors zurück gesetzt. Dies kann auch eine Fehlerursache sein.

Verbinden Sie vor dem Aufruf des Programms die Sensorbox mit einem Micro-USB-Kabel mit Ihrem Rechner.

# **Debugger** hier koennen Sie die Ausgaben des Sensors in eine Datei schreiben und anzeigen lassen.
# **ResetDHCP** hier  koennen Sie eine statische IP Ihres Sensors aufheben. Hier bitte kurz warten. 
# **ResetWifi** hier koennen Sie die Wifizugangsdaten zuruecksetzen. Sie muessen den Sensor danach erneut in Ihr WLAN einbinden.
# **ResetAdmin** hier koennen Sie ein evtl. vergebenenes Adminpasswort zuruecksetzen.
# **StartAPMode** hier koennen Sie den WLAN-Zugangspunkt des Sensors starten und sich wie in der Anleitung beschrieben mit dem Sensor verbinden.
# **ResetIPFiltering** hier koennen Sie die Client-IP-Filterung des Sensors für die aktuelle Session zurücksetzen

Sie können den Debugger unter https://github.com/martament/openandhome/releases => ohtoolbox.zip herunterladen.

Das Programm ist eine kompilierte Powershelldatei. Daher wird diese von manchen Virenscannern fälschlicherweise als Bedrohung definiert. Sollten Sie damit ein Problem haben, so finden Sie die zugehörige openandhome-debugger.ps1 im Ordern bin ebenfalls zum Download. Diese ist funktionsgleich der Exe, allerdings müssen Sie diese aus einer  Powershell Administratorenrechten heraus aufrufen. 


2. Debugger kann das Problem nicht lösen

Sollten Sie mit dem Debugger Ihr Problem nicht lösen können, so steht ihnen noch der oh-flasher zur Verfügung. Diesen bitte nur auf Anweisung unseres Supports verwenden.
Mit dem Flasher können Sie Ihren Sensor vollständig zurücksetzen und unsere Konfiguration automatisiert wieder einspielen.

Sie können den OH-Flasher unter https://github.com/martament/openandhome/releases => oh-flasher.zip herunterladen.


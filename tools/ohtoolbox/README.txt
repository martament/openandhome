Sie finden hier mehrere Programme für den Sensor von Openandhome.



Für den bestimmungsgem. Betrieb unseres Sensors benötigen Sie diese Programme nicht.

Lesen Sie dazu bitte auch die FAQs auf unserer Homepage
# https://www.openandhome.de/index.php/2019/01/11/faq/
# https://www.openandhome.de/index.php/ufaqs/ich-moechte-die-konfiguration-aendern-ist-dies-moeglich/ 


Sie benötigen diese Programme nur, wenn bei Ihnen in der Konfiguration des Sensors etwas nicht funktioniert wie es sollte. Wir können nicht jede Änderung am Sensor mit unserem Support abdecken. Gleichwohl unterstützen wir mit unserem offenen Ansatz Sie bei Ihren Versuchen.

D.h. Sie können unseren Debugger versuchen und sollte der Ihre Problem nicht lösen, so können Sie uns jederzeit den Sensor zusenden und wir stellen den Ausliefgerungszustand wieder her.

# https://www.openandhome.de/index.php/ufaqs/ich-habe-ein-problem-mit-meinem-sensor-was-kann-ich-tun/ 

1. openandhome-debugger.exe (Standardprogramm)
Dies ist ein grafisches Programm mit dem Sie im Fehlerfall mehrere Möglichkeiten haben. Sie sollten dieses Programm wann immer möglich nutzen.

#  **Debugger** hier koennen Sie die Ausgaben des Sensors in eine Datei schreiben und anzeigen lassen.
#  **ResetDHCP** hier  koennen Sie eine statische IP Ihres Sensors aufheben. Hier bitte kurz warten. 
# **ResetWifi** hier koennen Sie die Wifizugangsdaten zuruecksetzen. Sie muessen den Sensor danach erneut in Ihr WLAN einbinden.
# **ResetAdmin** hier koennen Sie ein evtl. vergebenenes Adminpasswort zuruecksetzen.

2. reset_openandhome.bat (obsolet)

Dies ist der Vorgängerer des grafischen Debuggers. 

Achten Sie bitte darauf, dass die Datei SerialSend.exe bei Windows im gleichen Verzeichnis ist.
Ebenso muss der Sensor mit dem Rechner über USB verbunden sein.

Mit dem Programm reset_openandhome.bat können Sie die Einstellungen des Sensors auf den Auslieferungszustand zurück setzen. 
Es werden die WIFI-Zugangsdaten und das Zugangspasswort auf den Auslieferungszustand gesetzt. 

3. full_reset.bat (Nur im Notfall)

Dieses Tool bitte nur im Notfall benutzen.

Mit diesem Programm können Sie den Sensor vollständig zurück setzen. Es werden alle Einstellungen des Sensor gelöscht. Der Sensor ist dann auch nicht mehr im Auslieferungszustand, sondern auch diese Einstellungen werden gelöscht.

Der Sensor wird auf die bei der Kompilierung eingestellten Werte zurück gesetzt.

Sie müssen den Sensor danach von Grund auf neu konfigurieren.
Eine Anleitung dazu finden Sie in https://www.openandhome.de/index.php/ufaqs/waere-es-moeglich-mir-die-daten-fuer-die-grundfiguration-zukommen-zu-lassen/ 



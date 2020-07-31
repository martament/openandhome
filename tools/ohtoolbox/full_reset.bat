@echo "Achtung dieses Skript löscht alle Einstellungen des Sensors..." 
@echo "Versuchen Sie immer zuerst das Skript reset_openandhome.bat" 
@echo "" 
@echo "Sie muessen den Sensor danach erneut von Grund auf konfigurieren." 
@echo "" 
@echo "Achten Sie drauf, dass sich die Datei SerialSend.exe im gleichen Verzeichnis befindet." 
@echo "Der Sensor muss mit dem Rechner über USB verbunden sein." 
@echo "" 
@echo "..." 
@echo "Sie sollten genau wissen was Sie tun." 
@echo "..." 
@echo "..." 
@echo "Druecken Sie eine beliebige Taste . . ." 
pause
SerialSend.exe /baudrate 115200 /closedelay 500 /hex "Reset\r\n" 
@echo "Druecken Sie eine beliebige Taste . . ." 
pause
SerialSend.exe /baudrate 115200  /closedelay 500 /hex "reboot\r\n"
@echo "" 
@echo "Wenn das Skript keinen Fehler zeigt, dann koennen Sie den Sensor erneut einrichten."
@echo "https://www.openandhome.de/index.php/ufaqs/waere-es-moeglich-mir-die-daten-fuer-die-grundfiguration-zukommen-zu-lassen/"
@echo "Druecken Sie eine beliebige Taste . . ." 
pause


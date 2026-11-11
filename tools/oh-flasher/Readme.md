Hier finden Sie den OH-Flasher.

Mit diesem können Sie die Firmware und die Einstellungen unseres Temperatursensors
wiederherstellen. Den Flasher bitte nur auf Anweisung unseres Supports verwenden.

Ablauf:
- Laden Sie den OH-Flasher unter https://github.com/martament/openandhome/releases
  => oh-flasher.zip herunter und entpacken Sie die Datei.
- Schließen Sie den Sensor per USB an Ihren Rechner an.
- Wechseln Sie in das Verzeichnis oh-flasher und starten Sie die start_flasher.bat
  mit einem Doppelklick.

Auswahl im Flasher:
- **1 Sensor neu aufsetzen** – der Sensor wird vollständig gelöscht und neu eingerichtet.
  Der Flasher lädt dafür den aktuellen, von uns freigegebenen Stand aus dem Internet
  (ohne Internet nimmt er die mitgelieferten Dateien).
  - Geben Sie den Namen und das Passwort Ihres WLANs ein. Dann erkennt der Flasher
    die angeschlossenen Fühler, das Display und weitere Sensoren selbst und richtet
    alles ein. Am Ende zeigt er die Adresse, unter der Ihr Sensor erreichbar ist.
  - Fühler, die sich nicht automatisch erkennen lassen (z. B. Abstandssensor),
    fragt der Flasher ab.
- **2 Nur Firmware aktualisieren** – Ihre Einstellungen bleiben erhalten.
- **3 Debug** – zeigt die Ausgaben des Sensors (für unseren Support).

Es kann einige Minuten dauern, bis der Sensor wiederhergestellt ist.
Die Oberfläche des Sensors erreichen Sie danach unter der angezeigten Adresse
oder unter http://Sensorbox1.

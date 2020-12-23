Hier finden Sie die Dateien für den OH-Flasher.

Mit diesem können Sie die Firmware und die Einstellungen unseres Temperatursensores wieder herstellen. 

Den Flasher bitte nur auf Anweisung unsere Supports verwenden.



Ablauf:
- Sie können den OH-Flasher unter https://github.com/martament/openandhome/releases => oh-flasher.zip herunterladen.
- Entpacken Sie die oh-flasher.zip
- wechseln Sie in das Verzeichnis oh-flasher und starten die die start_flasher.bat mit einem Doppelklick.

- Aktion auswählen
- Dies wird im Normalfall [L] für die vollständige Löschung und Wiederherstellung des Sensors sein
<img src="https://raw.githubusercontent.com/martament/openandhome/master/images/oh-flasher/flasher1.PNG">

- Es kann bis zu mehreren Minuten dauern bis der Sensor wiederhergestellt ist.

- Dann die Anzahl der an Ihrem Temperaturfühler verbauten Sensoren auswählen.

<img src="https://raw.githubusercontent.com/martament/openandhome/master/images/oh-flasher/flasher2.PNG">

- Fenster schließen mit [RETURN]

<img src="https://raw.githubusercontent.com/martament/openandhome/master/images/oh-flasher/flasher3.PNG">

- Sensor gem. Anleitung in das WLAN einbinden oder mit dem WLAN des Sensors gem. Anleitung verbinden
- Rufen Sie die Oberfläche des Sensors mit http://Temperatursensor-0 oder http://Temperatursensor oder http://192.168.4.1 auf
- Gehen Sie auf den Reiter Devices und wählen Sie den Button Edit beim ersten Sensor

<img src="https://raw.githubusercontent.com/martament/openandhome/master/images/oh-flasher/flasher4.PNG">

- Wählen Sie bei Deviceaddress die Adresse Ihres Sensors aus. 

<img src="https://raw.githubusercontent.com/martament/openandhome/master/images/oh-flasher/flasher5.PNG">

- Wiederholen Sie den Vorgang für jeden Ihrer Sensoren. Achten Sie dabei darauf, dass bei jedem Sensor eine andere Deviceaddress gemeldet ist.

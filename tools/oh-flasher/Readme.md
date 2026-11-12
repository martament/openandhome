# OH-Flasher (Notlösung)

Der OH-Flasher stellt die Firmware und die Grundeinstellungen Ihrer Sensorbox
wieder her. **Er ist nur eine Notlösung**: Nutzen Sie zuerst die
[openandhome-Toolbox](../ohtoolbox/README.md) – sie ist das Standardwerkzeug für
WLAN, Name, Zeitserver und die meisten Probleme. Den Flasher bitte möglichst nur
auf Anweisung unseres Supports verwenden.

Der Flasher funktioniert für **Standalone**- und **Professional**-Boxen und lädt
den aktuellen, von uns freigegebenen Stand aus dem Internet (ohne Internet die
mitgelieferten Dateien). Für die Einrichtung muss sich die Sensorbox kurz mit
Ihrem WLAN verbinden.

## Vor dem Start

- Laden Sie den OH-Flasher unter https://github.com/martament/openandhome/releases
  → `oh-flasher.zip` herunter und entpacken Sie die Datei.
- Schließen Sie die Sensorbox per USB an Ihren Rechner an.
- **Sensorbox Professional:** Ziehen Sie **vorher das Netzwerkkabel (PoE)** ab.
  USB und PoE dürfen nie gleichzeitig angeschlossen sein – die Box ist nicht
  galvanisch getrennt, angeschlossene Geräte können beschädigt werden.
- Starten Sie im Ordner `oh-flasher` die Datei `start_flasher.bat` mit einem Doppelklick.

## Auswahl im Flasher

| Taste | Funktion |
|---|---|
| 1 | **Sensoren neu erkennen** – Einstellungen bleiben erhalten. Nach dem Tausch oder Hinzufügen eines Fühlers erkennt der Flasher Fühler, Display und Kombifühler, wählt die Fühleradressen und erneuert Anzeige und Dashboard. Fühler, die sich nicht automatisch erkennen lassen (z. B. Wasser- oder Abstandssensor), fragt er ab. |
| 2 | **Sensor neu aufsetzen** – der Sensor wird vollständig gelöscht und mit Firmware und Grundeinstellungen neu eingerichtet; danach erkennt der Flasher die Fühler wie bei 1. Bei Professional wird zusätzlich der Netzwerkanschluss eingerichtet, und die WLAN-Daten werden am Ende wieder gelöscht. |
| 3 | **Nur Firmware aktualisieren** – nur Standalone, Einstellungen bleiben erhalten |
| 4 | **Debug** – Ausgaben des Sensors anzeigen (für unseren Support) |

Geben Sie bei 1 und 2 den Namen und das Passwort Ihres WLANs ein. Kann sich der
Sensor nicht verbinden, zeigt der Flasher die sichtbaren WLANs und fragt erneut.

**Nach dem Flashen:**
- Standalone: Der Flasher zeigt die Adresse Ihres Sensors (Dashboard: `http://<Adresse>/openandhome.esp`).
- Professional: Erst das USB-Kabel abziehen, **danach** das Netzwerkkabel anstecken.
  Die IP-Adresse zeigt das Display bzw. Ihr Router (Gerät „Sensorbox1“).

Es kann einige Minuten dauern, bis der Sensor wiederhergestellt ist.

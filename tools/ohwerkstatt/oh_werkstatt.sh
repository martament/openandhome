#!/bin/bash
# Openandhome Werkstatt-Tool (nur Linux, nur intern - nicht an Kunden ausliefern).
# Kundenfunktionen (WLAN setzen, Reset Wifi, AP-Mode ...) bleiben in
# tools/ohtoolbox/bin/linux_ohtoolbox.sh. Ablauf siehe plans/espeasy-fertig-images.md, Abschnitt 6.

# --- KONFIGURATION ---
BAUD=115200
SYSLOG_TEST_IP="192.168.9.4"
REPO="$(cd "$(dirname "$(readlink -f "$0")")/../.." && pwd)"
BIN="$REPO/tools/bin"
PORT=""
BOX_IP=""

# --- FUNKTIONEN ---
show_header() {
    clear
    echo -e "\e[35m====================================\e[0m"
    echo -e "\e[35m    Openandhome - Werkstatt (Linux)\e[0m"
    echo -e "\e[35m====================================\e[0m\n"
}

weiter() {
    read -p "Zurück zum Menü mit Enter..."
}

# Serieller Port wird erst gesucht, wenn eine Funktion ihn braucht
find_port() {
    [ -n "$PORT" ] && [ -e "$PORT" ] && return 0
    PORT=$(ls /dev/ttyUSB* /dev/ttyACM* 2>/dev/null | head -n 1)
    if [ -z "$PORT" ]; then
        echo -e "\e[31mKein Sensor am USB gefunden.\e[0m"
        return 1
    fi
    stty -F "$PORT" "$BAUD" cs8 -cstopb -parenb -echo raw
    echo -e "\e[32mSensor an Port: $PORT\e[0m"
}

send_serial() {
    find_port || return 1
    # Leerzeile verwirft Datenmüll im Eingabepuffer des Sensors
    printf '\n' > "$PORT"
    sleep 0.3
    echo "ResetFlashWriteCounter" > "$PORT"
    sleep 0.3
    for cmd in "$@"; do
        echo "$cmd" > "$PORT"
        echo " -> $cmd"
        sleep 0.3
    done
}

# Liest die Antwort des Sensors für ein paar Sekunden mit
read_serial() {
    timeout "${1:-5}s" cat "$PORT"
}

# Standardweg ist USB: IP der Box aus "Settings" lesen (WLAN-Key wird nicht angezeigt)
usb_box_ip() {
    find_port >/dev/null || return 1
    local ausgabe
    ausgabe=$( { read_serial 3 & sleep 0.3; printf '\n' > "$PORT"; sleep 0.3; echo "Settings" > "$PORT"; wait; } | tr -d '\r')
    local ip
    # Neuere Firmware stellt einen Zeitstempel voran ("24.920 : >  IP Address : ...")
    ip=$(sed -n 's/.*IP Address *: *\([0-9.]*\).*/\1/p' <<< "$ausgabe" | head -n 1)
    [ -n "$ip" ] && [ "$ip" != "0.0.0.0" ] && BOX_IP="$ip"
}

ask_box_ip() {
    local eingabe
    [ -z "$BOX_IP" ] && usb_box_ip && echo -e "\e[32mIP per USB gelesen: $BOX_IP\e[0m"
    read -p "IP der Box [${BOX_IP:-keine}]: " eingabe
    BOX_IP="${eingabe:-$BOX_IP}"
    [ -n "$BOX_IP" ]
}

set_name() {
    echo -e "\n\e[36m--- Gerätename und Unit setzen ---\e[0m"
    echo "Jede Testbox braucht einen eindeutigen Namen (MQTT %sysname%, Syslog)."
    read -p "Name (z. B. Sensorbox13): " name
    read -p "Unit-Nummer (z. B. 13): " unit
    if [ -z "$name" ] || ! [[ "$unit" =~ ^[0-9]+$ ]]; then
        echo -e "\e[31mName leer oder Unit keine Zahl. Abbruch.\e[0m"
        weiter
        return
    fi
    send_serial "Name,$name" "Unit,$unit" "Save" && echo -e "\e[32mGesetzt.\e[0m"
    weiter
}

onewire_scan() {
    echo -e "\n\e[36m--- 1-Wire-Scan (DS18B20-Adressen) ---\e[0m"
    echo "Tipp: Fühler einzeln anstecken und nach jedem Fühler scannen,"
    echo "die Reihenfolge ergibt Fuehler1..N (Plan Abschnitt 8)."
    read -p "GPIO des 1-Wire-Busses: " gpio
    if ! [[ "$gpio" =~ ^[0-9]+$ ]]; then
        echo -e "\e[31mGPIO muss eine Zahl sein.\e[0m"
        weiter
        return
    fi
    send_serial "OWScan,$gpio" || { weiter; return; }
    echo -e "\e[90mAntwort des Sensors:\e[0m"
    read_serial 4 | tee -a ow-scan.txt
    echo -e "\n\e[90m(auch in ow-scan.txt gespeichert)\e[0m"
    weiter
}

autoconfig() {
    echo -e "\n\e[36m--- Sensoren erkennen und Tasks einschalten ---\e[0m"
    echo "Scannt I2C (Display, HTU21D, AM2320, BMx280) und 1-Wire (DS18B20) per USB."
    find_port || { weiter; return; }
    ask_box_ip || { echo "Keine IP angegeben."; weiter; return; }
    python3 "$BIN/espeasy_autoconfig.py" --port "$PORT" --host "$BOX_IP" || { weiter; return; }

    echo -e "\nNicht erkennbare Sensoren (z. B. HCSR04, Wassersensor) bleiben unverändert."
    read -p "Davon einschalten (Tasknamen, Leerzeichen getrennt, leer = keine): " -a an
    read -p "Davon ausschalten (Tasknamen, leer = keine): " -a aus
    read -p "Änderungen jetzt schreiben? (j/n): " ok
    if [[ "$ok" =~ ^[jJyY]$ ]]; then
        python3 "$BIN/espeasy_autoconfig.py" --port "$PORT" --host "$BOX_IP" \
            ${an:+--an "${an[@]}"} ${aus:+--aus "${aus[@]}"} --anwenden
    fi
    weiter
}

syslog() {
    local aktion=$1
    echo -e "\n\e[36m--- Syslog $aktion (HTTP /advanced) ---\e[0m"
    ask_box_ip || { echo "Keine IP angegeben."; weiter; return; }
    python3 "$BIN/espeasy_syslog.py" "$BOX_IP" "$aktion" --ip "$SYSLOG_TEST_IP"
    weiter
}

teardown() {
    echo -e "\n\e[36m--- Teardown nach dem 24h-Test ---\e[0m"
    echo "1. Syslog aus (HTTP)   2. WLAN-Daten löschen (seriell, nur WLAN-Boxen)"
    echo "3. Admin-Passwort löschen   4. Save + Reboot"
    ask_box_ip || { echo "Keine IP angegeben."; weiter; return; }
    read -p "Teardown für $BOX_IP jetzt starten? (j/n): " ok
    [[ "$ok" =~ ^[jJyY]$ ]] || { echo "Abgebrochen."; weiter; return; }

    if ! python3 "$BIN/espeasy_syslog.py" "$BOX_IP" aus; then
        echo -e "\e[31mSyslog konnte nicht abgeschaltet werden - Teardown abgebrochen.\e[0m"
        weiter
        return
    fi

    local cmds=("password")
    read -p "WLAN-Box (SSIDs löschen)? (j/n): " wlan
    if [[ "$wlan" =~ ^[jJyY]$ ]]; then
        cmds+=("WifiSSID ssid" "WifiKey wpakey" "WifiSSID2 ssid" "WifiKey2 wpakey")
    fi
    send_serial "${cmds[@]}" "Save" "Reboot" || { weiter; return; }
    echo -e "\e[32mTeardown gesendet.\e[0m Prüfen: kein Syslog-Traffic mehr, AP öffnet sich (WLAN-Box)."
    echo "Ergebnis und Testdatum in readme_image.txt bzw. readme.txt eintragen."
    weiter
}

check_config() {
    echo -e "\n\e[36m--- config.dat / Backup-Tar prüfen ---\e[0m"
    read -e -p "Datei(en): " -a dateien
    [ ${#dateien[@]} -gt 0 ] && python3 "$BIN/espeasy_configcheck.py" "${dateien[@]}"
    weiter
}

download_images() {
    echo -e "\n\e[36m--- Fertig-Images laden (nur Branch devel) ---\e[0m"
    read -p "Release-Tag (leer = neuestes): " tag
    python3 "$BIN/espeasy_download.py" ${tag:+--tag "$tag"}
    weiter
}

monitor() {
    find_port || { weiter; return; }
    echo -e "\e[90mSerielle Ausgabe, schreibt oh-monitor.txt. Beenden mit STRG+C.\e[0m"
    trap 'trap - INT; return' INT
    tee -a oh-monitor.txt < "$PORT"
}

# --- HAUPTPROGRAMM ---
while true; do
    show_header
    echo -e "USB: ${PORT:-\e[90m(noch nicht gesucht)\e[0m}   Box-IP: ${BOX_IP:-\e[90m(keine)\e[0m}"
    echo "------------------------------------"
    echo "1) Gerätename/Unit setzen          (seriell)"
    echo "2) 1-Wire-Scan DS18B20             (seriell)"
    echo "3) Syslog AN  ($SYSLOG_TEST_IP)     (HTTP)"
    echo "4) Syslog AUS                      (HTTP)"
    echo "5) Syslog-Status                   (HTTP)"
    echo "6) Teardown nach 24h-Test          (HTTP + seriell)"
    echo "7) config.dat / Backup-Tar prüfen"
    echo "8) Fertig-Images laden             (Branch devel)"
    echo "9) Serieller Monitor"
    echo "a) Sensoren erkennen, Tasks einschalten (USB + HTTP)"
    echo "------------------------------------"
    echo "WLAN setzen: tools/ohtoolbox/bin/linux_ohtoolbox.sh (Punkt 1)"
    echo "q) Beenden"
    echo ""

    read -p "Ihre Wahl: " choice || exit 0
    case $choice in
        1) set_name ;;
        2) onewire_scan ;;
        3) syslog an ;;
        4) syslog aus ;;
        5) syslog status ;;
        6) teardown ;;
        7) check_config ;;
        8) download_images ;;
        9) monitor ;;
        a|A) autoconfig ;;
        q|Q) exit 0 ;;
        *) echo -e "\e[31mUngültige Wahl\e[0m"; sleep 1 ;;
    esac
done

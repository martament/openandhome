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
    if [ ! -w "$PORT" ]; then
        echo -e "\e[31mKeine Rechte auf $PORT.\e[0m sudo usermod -aG dialout $USER (danach neu anmelden)"
        PORT=""
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

# Ruft den Testablauf auf (tools/bin/espeasy_testbox.py), USB-Port wird mitgegeben
testbox() {
    find_port || { weiter; return; }
    python3 "$BIN/espeasy_testbox.py" "$@" --port "$PORT"
    # Nach Flash/Reboot kann sich die IP geändert haben
    BOX_IP=""
    weiter
}

test_starten() {
    echo -e "\n\e[36m--- Box aufsetzen und 24h-Test starten ---\e[0m"
    echo "Sicherung -> Flashen -> WLAN -> Basis-config.dat -> Testname/Zugriff ->"
    echo "Sensoren erkennen -> Dashboard -> Werte prüfen -> Syslog an ($SYSLOG_TEST_IP)"
    read -p "Ohne Flashen (Box hat schon das aktuelle Image)? (j/n) [n]: " ohne
    if [[ "$ohne" =~ ^[jJyY]$ ]]; then
        testbox aufsetzen --ohne-flash --syslog-ip "$SYSLOG_TEST_IP"
    else
        testbox aufsetzen --syslog-ip "$SYSLOG_TEST_IP"
    fi
}

test_beenden() {
    echo -e "\n\e[36m--- Test beenden ---\e[0m"
    echo "Werte prüfen -> Syslog aus -> Name Sensorbox1/Unit 0 -> Zugriff 192.168.x"
    read -p "WLAN-Daten danach löschen wie esp_resetap (nur WLAN-Boxen)? (j/n) [n]: " wlan
    if [[ "$wlan" =~ ^[jJyY]$ ]]; then
        testbox beenden --wlan-reset
    else
        testbox beenden --ohne-wlan-reset
    fi
}

set_name() {
    echo -e "\n\e[36m--- Gerätename und Unit setzen ---\e[0m"
    echo "Im Test: Testbox<Unit>, bei Auslieferung: Sensorbox1 / Unit 0."
    read -p "Name: " name
    read -p "Unit-Nummer: " unit
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
    read -p "GPIO des 1-Wire-Busses [0]: " gpio
    gpio=${gpio:-0}
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
    echo -e "\n\e[36m--- Syslog (HTTP /advanced) ---\e[0m"
    read -p "an / aus / status [status]: " aktion
    aktion=${aktion:-status}
    [[ "$aktion" =~ ^(an|aus|status)$ ]] || { echo "Ungültig."; weiter; return; }
    ask_box_ip || { echo "Keine IP angegeben."; weiter; return; }
    python3 "$BIN/espeasy_syslog.py" "$BOX_IP" "$aktion" --ip "$SYSLOG_TEST_IP"
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
    echo -e "\e[1;33mTest\e[0m"
    echo "1) Box aufsetzen und 24h-Test starten"
    echo "2) Test prüfen (Werte + Dashboard)"
    echo "3) Test beenden (Syslog aus, Sensorbox1, opt. WLAN-Reset)"
    echo "------------------------------------"
    echo -e "\e[1;33mEinzelschritte\e[0m"
    echo "4) Sensoren erkennen, Tasks einschalten"
    echo "5) Dashboard erzeugen und hochladen"
    echo "6) Gerätename/Unit setzen"
    echo "7) 1-Wire-Scan DS18B20"
    echo "8) Syslog an/aus/Status"
    echo "9) config.dat / Backup-Tar prüfen"
    echo "i) Fertig-Images laden (Branch devel)"
    echo "m) Serieller Monitor"
    echo "------------------------------------"
    echo "WLAN setzen: tools/ohtoolbox/bin/linux_ohtoolbox.sh (Punkt 1)"
    echo "q) Beenden"
    echo ""

    read -p "Ihre Wahl: " choice || exit 0
    case $choice in
        1) test_starten ;;
        2) testbox pruefen ;;
        3) test_beenden ;;
        4) autoconfig ;;
        5) testbox dashboard ;;
        6) set_name ;;
        7) onewire_scan ;;
        8) syslog ;;
        9) check_config ;;
        i|I) download_images ;;
        m|M) monitor ;;
        q|Q) exit 0 ;;
        *) echo -e "\e[31mUngültige Wahl\e[0m"; sleep 1 ;;
    esac
done

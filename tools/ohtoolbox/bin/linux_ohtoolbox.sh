#!/bin/bash
# --- KONFIGURATION ---
# Sucht nach gängigen USB-Seriell Treibern (ttyUSB0, ttyACM0 etc.)
BAUD=115200

# --- FUNKTIONEN ---
show_header() {
    clear
    echo -e "\e[36m====================================\e[0m"
    echo -e "\e[36m    Openandhome - Multi-Tool v2.4 (Linux)\e[0m"
    echo -e "\e[36m====================================\e[0m\n"
}

find_port() {
    # Sucht nach dem ersten verfügbaren USB-Seriell Port
    PORT=$(ls /dev/ttyUSB* /dev/ttyACM* 2>/dev/null | head -n 1)

    if [ -z "$PORT" ]; then
        echo -e "\e[31mCRITICAL ERROR: Kein Sensor gefunden!\e[0m"
        echo "Bitte stellen Sie sicher, dass der Sensor angeschlossen ist."
        read -p "Drücken Sie Enter zum Beenden..."
        exit 1
    fi
    echo -e "\e[32mSensor gefunden an Port: $PORT\e[0m"
}

# Konfiguriert den Port (entspricht dem Öffnen in PowerShell)
setup_port() {
    stty -F "$PORT" "$BAUD" cs8 -cstopb -parenb -echo raw
}

send_commands() {
    local label=$1
    shift
    local cmds=("$@")

    echo -e "\n\e[33mFühre aus: $label\e[0m"
    setup_port

    # Befehle senden
    echo "ResetFlashWriteCounter" > "$PORT"
    sleep 0.3
    for cmd in "${cmds[@]}"; do
        echo "$cmd" > "$PORT"
        echo " -> $cmd"
        sleep 0.3
    done
    echo "Save" > "$PORT"

    echo -e "\e[32mErfolgreich abgeschlossen.\e[0m"
    read -p "Zurück zum Menü mit Enter..."
}

show_settings() {
    echo -e "\n\e[36m--- Aktuelle Einstellungen ---\e[0m"
    setup_port
    echo "ResetFlashWriteCounter" > "$PORT"
    sleep 0.1
    echo "Settings" > "$PORT"

    echo -e "\e[90mLese Daten (STRG+C für Menü)...\e[0m\n"
    # Liest den Port aus
    timeout 5s cat "$PORT" || echo -e "\nZeitüberschreitung oder Abbruch."
    read -p "Weiter mit Enter..."
}

invoke_debugger() {
    echo -e "\n\e[36m--- Debugging aktiv ---\e[0m"
    echo -e "\e[90mSchreibe in oh-debug.txt. Beenden mit STRG+C.\e[0m\n"
    echo "--- Debug Log Start: $(date) ---" > oh-debug.txt

    setup_port
    echo "ResetFlashWriteCounter" > "$PORT"
    echo "Settings" > "$PORT"

    # Port lesen und gleichzeitig in Datei und Konsole schreiben
    tee -a oh-debug.txt < "$PORT"
}

set_wifi() {
    echo -e "\n\e[36m--- WLAN-Zugangsdaten setzen ---\e[0m"

    read -p "WLAN-SSID: " wifi_ssid
    if [ -z "$wifi_ssid" ]; then
        echo -e "\e[31mSSID darf nicht leer sein. Abbruch.\e[0m"
        read -p "Zurück zum Menü mit Enter..."
        return
    fi

    # -s = verdeckte Eingabe des Passworts
    read -s -p "WPA-Key (Eingabe unsichtbar): " wifi_key
    echo ""
    read -s -p "WPA-Key wiederholen: " wifi_key_confirm
    echo ""

    if [ "$wifi_key" != "$wifi_key_confirm" ]; then
        echo -e "\e[31mDie Passwörter stimmen nicht überein. Abbruch.\e[0m"
        read -p "Zurück zum Menü mit Enter..."
        return
    fi

    # Optional: zweites Netz (Fallback) abfragen
    local use_fallback=""
    read -p "Zweites WLAN (Fallback) konfigurieren? (j/n): " use_fallback

    local wifi_ssid2=""
    local wifi_key2=""
    if [[ "$use_fallback" =~ ^[jJyY]$ ]]; then
        read -p "Fallback-SSID: " wifi_ssid2
        if [ -n "$wifi_ssid2" ]; then
            read -s -p "Fallback WPA-Key (Eingabe unsichtbar): " wifi_key2
            echo ""
        fi
    fi

    echo ""
    echo -e "SSID:          \e[32m$wifi_ssid\e[0m"
    if [ -n "$wifi_ssid2" ]; then
        echo -e "Fallback-SSID: \e[32m$wifi_ssid2\e[0m"
    fi
    read -p "Daten jetzt an den Sensor senden? (j/n): " confirm
    if [[ ! "$confirm" =~ ^[jJyY]$ ]]; then
        echo "Abgebrochen."
        read -p "Zurück zum Menü mit Enter..."
        return
    fi

    # Befehlsliste aufbauen.
    # Anführungszeichen um SSID/Key, damit Leerzeichen und Kommas
    # laut ESPEasy-Doku korrekt verarbeitet werden.
    local cmds=(
        "WifiSSID,\"$wifi_ssid\""
        "WifiKey,\"$wifi_key\""
    )
    if [ -n "$wifi_ssid2" ]; then
        cmds+=(
            "WifiSSID2,\"$wifi_ssid2\""
            "WifiKey2,\"$wifi_key2\""
        )
    fi

    send_commands "WLAN-Daten setzen" "${cmds[@]}"

    # WifiConnect greift laut Praxisberichten nicht immer zuverlässig,
    # daher optionaler Reboot als sichere Variante.
    read -p "Gerät jetzt neu verbinden/rebooten? (j/n): " reboot_choice
    if [[ "$reboot_choice" =~ ^[jJyY]$ ]]; then
        do_reboot
    fi
}

do_reboot() {
    echo -e "\n\e[33mSende Reboot-Befehl...\e[0m"
    setup_port
    echo "Reboot" > "$PORT"
    echo -e "\e[32mGerät startet neu.\e[0m"
    read -p "Zurück zum Menü mit Enter..."
}

# --- HAUPTPROGRAMM ---
find_port
while true; do
    show_header
    echo -e "\e[32mVerbunden mit: $PORT\e[0m"
    echo "------------------------------------"
    echo -e "1) \e[1;33mWLAN-Zugangsdaten setzen (SSID/Key)\e[0m"
    echo "2) Neustart (Reboot)"
    echo "3) Einstellungen anzeigen (Settings)"
    echo "4) Debugger (Output lesen & speichern)"
    echo "5) Reset Wifi (SSID/Key löschen)"
    echo "6) Reset DHCP (Statische IP löschen)"
    echo "7) Reset Admin Password"
    echo "8) Start AP-Mode"
    echo "9) Reset IP-Filtering"
    echo "------------------------------------"
    echo "q) Beenden"
    echo ""

    read -p "Ihre Wahl: " choice
    case $choice in
        1) set_wifi ;;
        2) do_reboot ;;
        3) show_settings ;;
        4) invoke_debugger ;;
        5) send_commands "Reset Wifi" "WifiSSID ssid" "WifiKey wpakey" "WifiSSID2 ssid" "WifiKey2 wpakey" ;;
        6) send_commands "Reset DHCP" "IP 0.0.0.0" ;;
        7) send_commands "Reset Admin" "password" ;;
        8) send_commands "Start AP-Mode" "WifiAPMode" ;;
        9) send_commands "Reset IP-Filtering" "ClearAccessBlock" ;;
        q|Q) exit 0 ;;
        *) echo -e "\e[31mUngültige Wahl\e[0m"; sleep 1 ;;
    esac
done

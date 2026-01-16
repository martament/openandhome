#!/bin/bash

# --- KONFIGURATION ---
# Sucht nach gängigen USB-Seriell Treibern (ttyUSB0, ttyACM0 etc.)
BAUD=115200

# --- FUNKTIONEN ---

show_header() {
    clear
    echo -e "\e[36m====================================\e[0m"
    echo -e "\e[36m    Openandhome - Multi-Tool v2.2 (Linux)\e[0m"
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
    echo "ResetFlashWriteCounter" > "$PORT" > "$PORT"
    echo "Settings" > "$PORT"
    
    # Port lesen und gleichzeitig in Datei und Konsole schreiben
    tee -a oh-debug.txt < "$PORT"
}

# --- HAUPTPROGRAMM ---

find_port

while true; do
    show_header
    echo -e "\e[32mVerbunden mit: $PORT\e[0m"
    echo "------------------------------------"
    echo "1) Reset Wifi (SSID/Key löschen)"
    echo "2) Einstellungen anzeigen (Settings)"
    echo "3) Debugger (Output lesen & speichern)"
    echo "4) Reset DHCP (Statische IP löschen)"
    echo "5) Reset Admin Password"
    echo "6) Start AP-Mode"
    echo "7) Reset IP-Filtering"
    echo "------------------------------------"
    echo "q) Beenden"
    echo ""
    
    read -p "Ihre Wahl: " choice

    case $choice in
        1) send_commands "Reset Wifi" "WifiSSID ssid" "WifiKey wpakey" "WifiSSID2 ssid" "WifiKey2 wpakey" ;;
        2) show_settings ;;
        3) invoke_debugger ;;
        4) send_commands "Reset DHCP" "IP 0.0.0.0" ;;
        5) send_commands "Reset Admin" "password" ;;
        6) send_commands "Start AP-Mode" "WifiAPMode" ;;
        7) send_commands "Reset IP-Filtering" "ClearAccessBlock" ;;
        q|Q) exit 0 ;;
        *) echo -e "\e[31mUngültige Wahl\e[0m"; sleep 1 ;;
    esac
done

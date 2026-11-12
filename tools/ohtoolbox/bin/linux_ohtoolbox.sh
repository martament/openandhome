#!/bin/bash
# --- KONFIGURATION ---
# Sucht nach gängigen USB-Seriell Treibern (ttyUSB0, ttyACM0 etc.)
BAUD=115200

# --- FUNKTIONEN ---
show_header() {
    clear
    echo -e "\e[36m====================================\e[0m"
    echo -e "\e[36m    Openandhome - Toolbox v3.0 (Linux)\e[0m"
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

# Sendet Befehle und gibt die Antwort des Sensors aus (ohne Farbcodes).
# Aufruf: send_read <Sekunden> <Befehl> [Befehl ...]
send_read() {
    local sekunden=$1
    shift
    setup_port
    {
        timeout "${sekunden}s" cat "$PORT" &
        sleep 0.3
        printf '\n' > "$PORT"
        sleep 0.3
        for cmd in "$@"; do
            echo "$cmd" > "$PORT"
            sleep 0.3
        done
        wait
    } | tr -d '\r' | sed 's/\x1b\[[0-9;]*m//g'
}

# Standalone (ESP8266, WLAN) oder Professional (ESP32, Netzwerkkabel/PoE)
detect_box() {
    local antwort
    antwort=$(send_read 2 'logentry,%sysbuild_filename%')
    case "$antwort" in
        *ESP32*) BOX="Professional" ;;
        *ESP8266*) BOX="Standalone" ;;
        *) BOX="unbekannt" ;;
    esac
}

box_ip() {
    send_read 2 "Settings" | sed -n 's/.*IP Address *: *\([0-9.]*\).*/\1/p' | grep -v '^0\.0\.0\.0$' | head -n 1
}

# Sichtbare WLANs: "dBm<TAB>Name", staerkstes je Name, sortiert nach Signal
wlan_liste() {
    send_read 8 "WifiScan" \
        | sed -n 's/.*WIFI : [0-9]*: \(.*\) [0-9A-Fa-f:]\{17\} Ch:[0-9]* (\(-\{0,1\}[0-9]*\)dBm).*/\2\t\1/p' \
        | grep -v $'\t#Hidden#$' | sort -t$'\t' -k1,1nr | awk -F'\t' '!gesehen[$2]++'
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
    if [ "$BOX" = "Professional" ]; then
        echo -e "\e[33mHinweis: Die Sensorbox Professional arbeitet mit dem Netzwerkkabel (PoE). WLAN brauchen Sie nur,\e[0m"
        echo -e "\e[33mwenn Sie die Box ohne Netzwerkkabel betreiben wollen.\e[0m"
        read -p "Trotzdem WLAN setzen? (j/n): " trotzdem
        [[ "$trotzdem" =~ ^[jJyY]$ ]] || return
    fi

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

    while true; do
        echo -e "\n\e[33mSende WLAN-Daten und starte den Sensor neu ...\e[0m"
        send_read 1 "${cmds[@]}" "Save" "Reboot" > /dev/null
        echo -n "Warte auf die Verbindung (bis zu 60 Sekunden) "
        local ip=""
        for i in $(seq 12); do
            sleep 3
            echo -n "."
            ip=$(box_ip)
            [ -n "$ip" ] && break
        done
        if [ -n "$ip" ]; then
            echo -e "\n\e[32mVerbunden. Ihr Sensor ist erreichbar unter: http://$ip/openandhome.esp\e[0m"
            read -p "Zurück zum Menü mit Enter..."
            return
        fi
        echo -e "\n\e[31mDer Sensor kann sich nicht mit '$wifi_ssid' verbinden.\e[0m Sichtbare WLANs:"
        local -a netze=()
        local nr=0
        while IFS=$'\t' read -r dbm name; do
            nr=$((nr + 1))
            netze+=("$name")
            printf "  %2d) %-32s %s dBm\n" "$nr" "$name" "$dbm"
        done < <(wlan_liste)
        if printf '%s\n' "${netze[@]}" | grep -qxF "$wifi_ssid"; then
            echo -e "  \e[33m('$wifi_ssid' ist sichtbar - vermutlich ist das Passwort falsch)\e[0m"
        fi
        read -p "Nummer oder WLAN-Name (Enter = gleiches WLAN, q = Abbruch): " wahl
        [ "$wahl" = "q" ] && return
        if [[ "$wahl" =~ ^[0-9]+$ ]] && [ "$wahl" -ge 1 ] && [ "$wahl" -le "${#netze[@]}" ]; then
            wifi_ssid="${netze[$((wahl - 1))]}"
        elif [ -n "$wahl" ]; then
            wifi_ssid="$wahl"
        fi
        read -s -p "Passwort für '$wifi_ssid' (Eingabe unsichtbar): " wifi_key
        echo ""
        cmds=("WifiSSID,\"$wifi_ssid\"" "WifiKey,\"$wifi_key\"")
    done
}

set_name() {
    echo -e "\n\e[36m--- Gerätename ändern ---\e[0m"
    echo "Bei mehreren Sensoren braucht jeder einen eigenen Namen (z. B. Keller, Heizung)."
    read -p "Neuer Name (Buchstaben, Ziffern, - und _; leer = Abbruch): " name
    if ! [[ "$name" =~ ^[A-Za-z0-9_-]{1,24}$ ]]; then
        echo "Abgebrochen."
        read -p "Zurück zum Menü mit Enter..."
        return
    fi
    send_commands "Gerätename setzen" "Name,$name"
}

set_ntp() {
    echo -e "\n\e[36m--- Zeitserver (NTP) setzen ---\e[0m"
    echo "Standard ist de.pool.ntp.org (Internet). Ohne Internet z. B. die Adresse Ihres Routers"
    echo "(FRITZ!Box: 192.168.178.1) eintragen."
    read -p "NTP-Server (leer = Abbruch): " ntp
    if [ -z "$ntp" ] || ! [[ "$ntp" =~ ^[A-Za-z0-9.-]+$ ]]; then
        echo "Abgebrochen."
        read -p "Zurück zum Menü mit Enter..."
        return
    fi
    send_commands "NTP-Server setzen" "NTPHost,$ntp"
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
echo "Erkenne Sensorbox ..."
detect_box
if [ "$BOX" = "Professional" ]; then
    echo -e "\n\e[33mSensorbox Professional erkannt.\e[0m"
    echo -e "\e[31mACHTUNG: USB und Netzwerkkabel (PoE) nie gleichzeitig anschließen!\e[0m"
    echo -e "\e[31mZiehen Sie das Netzwerkkabel ab, bevor Sie fortfahren.\e[0m"
    read -p "Weiter mit Enter"
fi
while true; do
    show_header
    echo -e "\e[32mVerbunden mit: $PORT  -  Sensorbox $BOX\e[0m"
    if [ "$BOX" = "Professional" ]; then
        echo -e "\e[31mACHTUNG: Netzwerkkabel (PoE) muss abgezogen sein, solange USB steckt!\e[0m"
    fi
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
    echo "n) Zeitserver (NTP) setzen"
    echo "g) Gerätename ändern"
    echo "------------------------------------"
    echo "q) Beenden"
    echo ""

    read -p "Ihre Wahl: " choice || exit 0
    case $choice in
        1) set_wifi ;;
        2) do_reboot ;;
        3) show_settings ;;
        4) invoke_debugger ;;
        5) send_commands "Reset Wifi" "WifiSSID ssid" "WifiKey wpakey" "WifiSSID2 ssid" "WifiKey2 wpakey" ;;
        6) if [ "$BOX" = "Professional" ]; then send_commands "Reset DHCP" "IP 0.0.0.0" "ethip,0.0.0.0"; else send_commands "Reset DHCP" "IP 0.0.0.0"; fi ;;
        7) send_commands "Reset Admin" "password" ;;
        8) send_commands "Start AP-Mode" "WifiAPMode" ;;
        9) send_commands "Reset IP-Filtering" "ClearAccessBlock" ;;
        n|N) set_ntp ;;
        g|G) set_name ;;
        q|Q) exit 0 ;;
        *) echo -e "\e[31mUngültige Wahl\e[0m"; sleep 1 ;;
    esac
done

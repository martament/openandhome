# --- TITEL ---
function Show-Header {
    Clear-Host
    Write-Host "====================================" -ForegroundColor Cyan
    Write-Host "    Openandhome - Toolbox v3.0" -ForegroundColor Cyan
    Write-Host "====================================`n" -ForegroundColor Cyan
}

# --- KONFIGURATION ---
$deviceNameFilter = "*USB-SERIAL*" 
$baudRate = 115200 

Show-Header

# --- 1. PORT AUTOMATISCH FINDEN & PRÜFEN ---
Write-Host "Suche Gerät ($deviceNameFilter)..." -ForegroundColor Gray

$dev = Get-PnpDevice -PresentOnly | Where-Object { $_.FriendlyName -match "COM\d+" -and $_.FriendlyName -like $deviceNameFilter } | Select-Object -First 1

if (-not $dev) {
    Write-Host "`nCRITICAL ERROR: Kein Sensor gefunden!" -ForegroundColor Red
    Write-Host "Bitte stellen Sie sicher, dass der Sensor angeschlossen ist." -ForegroundColor White
    Write-Host "`nDrücken Sie Enter zum Beenden..."
    Read-Host
    exit
}

$COM = [regex]::match($dev.FriendlyName, 'COM\d+').Value
Write-Host "Sensor gefunden an Port: $COM" -ForegroundColor Green
Start-Sleep -Milliseconds 500

# --- FUNKTIONEN ---

function Open-Port {
    try {
        $p = New-Object System.IO.Ports.SerialPort $COM, $baudRate, "None", 8, "One"
        # WICHTIG: DTR/RTS aktivieren. Linux (stty) und Terminalprogramme wie
        # PuTTY setzen diese Steuerleitungen beim Öffnen automatisch - .NET
        # SerialPort NICHT. Ohne DTR/RTS senden viele USB-Seriell-Adapter
        # (CH340/CP2102) keine Daten an den PC => Debugausgabe bleibt leer.
        $p.DtrEnable = $true
        $p.RtsEnable = $true
        $p.Encoding  = [System.Text.Encoding]::UTF8
        $p.Open()
        $p.DiscardOutBuffer()
        return $p
    } catch {
        Write-Host "`nFEHLER: Port $COM ist belegt!" -ForegroundColor Red
        Write-Host "Schließen Sie andere Programme (z.B. Arduino IDE)." -ForegroundColor White
        Read-Host "Drücken Sie Enter..."
        exit
    }
}

# Sendet Befehle und liefert die Antwort des Sensors als Text (ohne Farbcodes)
function Send-AndRead($commands, $seconds = 2) {
    $port = Open-Port
    try {
        Start-Sleep -Milliseconds 1500
        $port.DiscardInBuffer()
        $port.WriteLine("")
        Start-Sleep -Milliseconds 300
        foreach ($cmd in $commands) {
            $port.WriteLine($cmd)
            Start-Sleep -Milliseconds 300
        }
        $text = ""
        $ende = (Get-Date).AddSeconds($seconds)
        while ((Get-Date) -lt $ende) {
            if ($port.BytesToRead -gt 0) { $text += $port.ReadExisting() }
            Start-Sleep -Milliseconds 100
        }
        return ($text -replace "\x1b\[[0-9;]*m", "")
    } finally {
        if ($port) { $port.Close() }
    }
}

# Standalone (ESP8266, WLAN) oder Professional (ESP32, Netzwerkkabel/PoE)
function Get-BoxTyp {
    $text = Send-AndRead @('logentry,%sysbuild_filename%') 2
    if ($text -match "ESP32") { return "Professional" }
    if ($text -match "ESP8266") { return "Standalone" }
    return "unbekannt"
}

function Get-BoxIp {
    $text = Send-AndRead @("Settings") 2
    $m = [regex]::Match($text, "IP Address\s*:\s*([\d.]+)")
    if ($m.Success -and $m.Groups[1].Value -ne "0.0.0.0") { return $m.Groups[1].Value }
    return $null
}

# Sichtbare WLANs (staerkstes je Name), sortiert nach Signal
function Get-WlanListe {
    $text = Send-AndRead @("WifiScan") 8
    $netze = @{}
    foreach ($m in [regex]::Matches($text, "WIFI : \d+: (.+?) [0-9A-Fa-f:]{17} Ch:(\d+) \((-?\d+)dBm\)")) {
        $name = $m.Groups[1].Value
        $dbm = [int]$m.Groups[3].Value
        if ($name -ne "#Hidden#" -and (-not $netze.ContainsKey($name) -or $dbm -gt $netze[$name])) {
            $netze[$name] = $dbm
        }
    }
    return $netze.GetEnumerator() | Sort-Object Value -Descending
}

function Show-Settings {
    Write-Host "`n--- Aktuelle Einstellungen ---" -ForegroundColor Cyan
    Write-Host "Beenden mit STRG+C.`n" -ForegroundColor Gray
    $port = Open-Port
    try {
        # Das Öffnen des Ports kann den Sensor über DTR/RTS kurz neu starten
        Start-Sleep -Milliseconds 1500
        $port.DiscardInBuffer()
        $port.WriteLine("ResetFlashWriteCounter")
        Start-Sleep -Milliseconds 100
        $port.WriteLine("Settings")
        while ($Host.UI.RawUI.KeyAvailable) {
            $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
        }
        Write-Host "Lese Daten (Beliebige Taste für Menü)...`n" -ForegroundColor Gray
        while (-not $Host.UI.RawUI.KeyAvailable) {
            if ($port.BytesToRead -gt 0) {
                Write-Host $port.ReadExisting() -NoNewline
            }
            Start-Sleep -Milliseconds 50
        }
        $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
    } finally {
        if ($port) { $port.Close() }
    }
}

function Invoke-Debugger {
    Write-Host "`n--- Debugging aktiv ---" -ForegroundColor Cyan
    $logFile = Join-Path (Get-Location) "oh-debug.txt"
    Write-Host "Schreibe in $logFile" -ForegroundColor Gray
    Write-Host "Beenden mit beliebiger Taste.`n" -ForegroundColor Gray
    "--- Debug Log Start: $(Get-Date) ---" | Out-File -FilePath $logFile -Encoding utf8

    $port = Open-Port
    try {
        # Das Öffnen des Ports kann den Sensor über DTR/RTS kurz neu starten -
        # daher etwas warten, damit die Befehle nicht im Boot verloren gehen
        Start-Sleep -Milliseconds 1500
        $port.DiscardInBuffer()
        $port.WriteLine("ResetFlashWriteCounter")
        $port.WriteLine("Settings")
        # Evtl. noch anstehende Tasten (z.B. Enter vom Menü) verwerfen
        while ($Host.UI.RawUI.KeyAvailable) {
            $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
        }
        # Solange keine Taste gedrückt wurde: Port auslesen,
        # in Datei schreiben und gleichzeitig anzeigen
        while (-not $Host.UI.RawUI.KeyAvailable) {
            if ($port.BytesToRead -gt 0) {
                $data = $port.ReadExisting()
                $data | Out-File -FilePath $logFile -Append -Encoding utf8 -NoNewline
                Write-Host $data -NoNewline
            }
            Start-Sleep -Milliseconds 50
        }
        $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
    } finally {
        if ($port) { $port.Close() }
        Write-Host "`nAufzeichnung beendet. Log gespeichert unter:" -ForegroundColor Yellow
        Write-Host $logFile -ForegroundColor Green
        Read-Host "Zurück zum Menü mit Enter..."
    }
}

function Send-Commands($label, $commands) {
    Write-Host "`nFühre aus: $label" -ForegroundColor Yellow
    $port = Open-Port
    try {
        # Kurze Wartezeit, falls das Öffnen des Ports den Sensor neu startet
        Start-Sleep -Milliseconds 1500
        $port.WriteLine("ResetFlashWriteCounter")
        Start-Sleep -Milliseconds 300
        foreach ($cmd in $commands) {
            $port.WriteLine($cmd)
            Write-Host " -> $cmd"
            Start-Sleep -Milliseconds 300
        }
        $port.WriteLine("Save")
        Write-Host "Erfolgreich abgeschlossen." -ForegroundColor Green
    } finally {
        if ($port) { $port.Close() }
        Write-Host "`nZurück zum Menü mit Enter..."
        Read-Host
    }
}

function Set-Ntp {
    Write-Host "`n--- Zeitserver (NTP) setzen ---" -ForegroundColor Cyan
    Write-Host "Standard ist de.pool.ntp.org (Internet). Ohne Internet z. B. die Adresse Ihres Routers"
    Write-Host "(FRITZ!Box: 192.168.178.1) eintragen."
    $ntp = Read-Host "NTP-Server (leer = Abbruch)"
    if (-not $ntp -or $ntp -notmatch '^[A-Za-z0-9.-]+$') {
        Write-Host "Abgebrochen."
        Read-Host "Zurück zum Menü mit Enter..."
        return
    }
    Send-Commands "NTP-Server setzen" @("NTPHost,$ntp")
}

function Invoke-Reboot {
    Write-Host "`nSende Reboot-Befehl..." -ForegroundColor Yellow
    $port = Open-Port
    try {
        $port.WriteLine("Reboot")
        Write-Host "Gerät startet neu." -ForegroundColor Green
    } finally {
        if ($port) { $port.Close() }
        Write-Host "`nZurück zum Menü mit Enter..."
        Read-Host
    }
}

# Hilfsfunktion: SecureString in Klartext umwandeln (für verdeckte Passworteingabe)
function ConvertFrom-SecureToPlain($secure) {
    return [System.Net.NetworkCredential]::new("", $secure).Password
}

function Set-Wifi {
    Write-Host "`n--- WLAN-Zugangsdaten setzen ---" -ForegroundColor Cyan
    if ($script:BoxTyp -eq "Professional") {
        Write-Host "Hinweis: Die Sensorbox Professional arbeitet mit dem Netzwerkkabel (PoE). WLAN brauchen Sie nur," -ForegroundColor Yellow
        Write-Host "wenn Sie die Box ohne Netzwerkkabel betreiben wollen." -ForegroundColor Yellow
        if ((Read-Host "Trotzdem WLAN setzen? (j/n)") -notmatch '^[jJyY]$') { return }
    }

    $wifiSsid = Read-Host "WLAN-SSID"
    if ([string]::IsNullOrWhiteSpace($wifiSsid)) {
        Write-Host "SSID darf nicht leer sein. Abbruch." -ForegroundColor Red
        Read-Host "Zurück zum Menü mit Enter..."
        return
    }

    # Verdeckte Eingabe des Passworts
    $secureKey        = Read-Host "WPA-Key (Eingabe unsichtbar)" -AsSecureString
    $secureKeyConfirm = Read-Host "WPA-Key wiederholen" -AsSecureString
    $wifiKey        = ConvertFrom-SecureToPlain $secureKey
    $wifiKeyConfirm = ConvertFrom-SecureToPlain $secureKeyConfirm

    if ($wifiKey -cne $wifiKeyConfirm) {
        Write-Host "Die Passwörter stimmen nicht überein. Abbruch." -ForegroundColor Red
        Read-Host "Zurück zum Menü mit Enter..."
        return
    }

    # Optional: zweites Netz (Fallback) abfragen
    $wifiSsid2 = ""
    $wifiKey2  = ""
    $useFallback = Read-Host "Zweites WLAN (Fallback) konfigurieren? (j/n)"
    if ($useFallback -match '^[jJyY]$') {
        $wifiSsid2 = Read-Host "Fallback-SSID"
        if (-not [string]::IsNullOrWhiteSpace($wifiSsid2)) {
            $secureKey2 = Read-Host "Fallback WPA-Key (Eingabe unsichtbar)" -AsSecureString
            $wifiKey2 = ConvertFrom-SecureToPlain $secureKey2
        } else {
            $wifiSsid2 = ""
        }
    }

    Write-Host ""
    Write-Host "SSID:          " -NoNewline; Write-Host $wifiSsid -ForegroundColor Green
    if ($wifiSsid2) {
        Write-Host "Fallback-SSID: " -NoNewline; Write-Host $wifiSsid2 -ForegroundColor Green
    }
    $confirm = Read-Host "Daten jetzt an den Sensor senden? (j/n)"
    if ($confirm -notmatch '^[jJyY]$') {
        Write-Host "Abgebrochen."
        Read-Host "Zurück zum Menü mit Enter..."
        return
    }

    # Befehlsliste aufbauen.
    # Anführungszeichen um SSID/Key, damit Leerzeichen und Kommas
    # laut ESPEasy-Doku korrekt verarbeitet werden.
    $cmds = @(
        ('WifiSSID,"{0}"' -f $wifiSsid),
        ('WifiKey,"{0}"'  -f $wifiKey)
    )
    if ($wifiSsid2) {
        $cmds += @(
            ('WifiSSID2,"{0}"' -f $wifiSsid2),
            ('WifiKey2,"{0}"'  -f $wifiKey2)
        )
    }

    while ($true) {
        Write-Host "`nSende WLAN-Daten und starte den Sensor neu ..." -ForegroundColor Yellow
        $null = Send-AndRead ($cmds + @("Save", "Reboot")) 1
        Write-Host "Warte auf die Verbindung (bis zu 60 Sekunden) " -NoNewline
        $ip = $null
        for ($i = 0; $i -lt 12 -and -not $ip; $i++) {
            Start-Sleep -Seconds 3
            Write-Host "." -NoNewline
            $ip = Get-BoxIp
        }
        if ($ip) {
            Write-Host "`nVerbunden. Ihr Sensor ist erreichbar unter: http://$ip/openandhome.esp" -ForegroundColor Green
            Read-Host "Zurück zum Menü mit Enter..."
            return
        }
        Write-Host "`nDer Sensor kann sich nicht mit '$wifiSsid' verbinden." -ForegroundColor Red
        Write-Host "Sichtbare WLANs:"
        $netze = @(Get-WlanListe)
        for ($i = 0; $i -lt $netze.Count; $i++) {
            Write-Host ("  {0,2}) {1,-32} {2} dBm" -f ($i + 1), $netze[$i].Key, $netze[$i].Value)
        }
        if ($netze | Where-Object { $_.Key -eq $wifiSsid }) {
            Write-Host "  ('$wifiSsid' ist sichtbar - vermutlich ist das Passwort falsch)" -ForegroundColor Yellow
        }
        $wahl = Read-Host "Nummer oder WLAN-Name (Enter = gleiches WLAN, q = Abbruch)"
        if ($wahl -eq "q") { return }
        if ($wahl -match '^\d+$' -and [int]$wahl -ge 1 -and [int]$wahl -le $netze.Count) {
            $wifiSsid = $netze[[int]$wahl - 1].Key
        } elseif ($wahl) {
            $wifiSsid = $wahl
        }
        $wifiKey = ConvertFrom-SecureToPlain (Read-Host "Passwort für '$wifiSsid' (unsichtbar)" -AsSecureString)
        $cmds = @(('WifiSSID,"{0}"' -f $wifiSsid), ('WifiKey,"{0}"' -f $wifiKey))
    }
}

function Set-Name {
    Write-Host "`n--- Gerätename ändern ---" -ForegroundColor Cyan
    Write-Host "Bei mehreren Sensoren braucht jeder einen eigenen Namen (z. B. Keller, Heizung)."
    $name = Read-Host "Neuer Name (Buchstaben, Ziffern, - und _; leer = Abbruch)"
    if (-not $name -or $name -notmatch '^[A-Za-z0-9_-]{1,24}$') {
        Write-Host "Abgebrochen."
        Read-Host "Zurück zum Menü mit Enter..."
        return
    }
    Send-Commands "Gerätename setzen" @("Name,$name")
    Write-Host "Nach einem Neustart ist der Sensor unter http://$name/openandhome.esp erreichbar (je nach Router)."
}

# --- SENSORBOX ERKENNEN ---
Write-Host "Erkenne Sensorbox ..." -ForegroundColor Gray
$script:BoxTyp = Get-BoxTyp
if ($script:BoxTyp -eq "Professional") {
    Write-Host "`nSensorbox Professional erkannt." -ForegroundColor Yellow
    Write-Host "ACHTUNG: USB und Netzwerkkabel (PoE) nie gleichzeitig anschließen!" -ForegroundColor Red
    Write-Host "Ziehen Sie das Netzwerkkabel ab, bevor Sie fortfahren." -ForegroundColor Red
    Read-Host "Weiter mit Enter"
}

# --- HAUPT-SCHLEIFE (TEXT-MENÜ) ---
$running = $true
while ($running) {
    Show-Header
    Write-Host "Verbunden mit: $COM  -  Sensorbox $script:BoxTyp" -ForegroundColor Green
    if ($script:BoxTyp -eq "Professional") {
        Write-Host "ACHTUNG: Netzwerkkabel (PoE) muss abgezogen sein, solange USB steckt!" -ForegroundColor Red
    }
    Write-Host "------------------------------------"
    Write-Host "1) " -NoNewline; Write-Host "WLAN-Zugangsdaten setzen (SSID/Key)" -ForegroundColor Yellow
    Write-Host "2) Neustart (Reboot)"
    Write-Host "3) Einstellungen anzeigen (Settings)"
    Write-Host "4) Debugger (Output lesen & speichern)"
    Write-Host "5) Reset Wifi (SSID/Key löschen)"
    Write-Host "6) Reset DHCP (Statische IP löschen)"
    Write-Host "7) Reset Admin Password"
    Write-Host "8) Start AP-Mode"
    Write-Host "9) Reset IP-Filtering"
    Write-Host "N) Zeitserver (NTP) setzen"
    Write-Host "G) Gerätename ändern"
    Write-Host "------------------------------------"
    Write-Host "Q) Beenden"
    Write-Host ""
    
    $choice = Read-Host "Ihre Wahl"

    switch ($choice) {
        "1" { Set-Wifi }
        "2" { Invoke-Reboot }
        "3" { Show-Settings }
        "4" { Invoke-Debugger }
        "5" { Send-Commands "Reset Wifi" @("WifiSSID ssid", "WifiKey wpakey", "WifiSSID2 ssid", "WifiKey2 wpakey") }
        "6" { if ($script:BoxTyp -eq "Professional") { Send-Commands "Reset DHCP" @("IP 0.0.0.0", "ethip,0.0.0.0") } else { Send-Commands "Reset DHCP" @("IP 0.0.0.0") } }
        "7" { Send-Commands "Reset Admin" @("password") }
        "8" { Send-Commands "Start AP-Mode" @("WifiAPMode") }
        "9" { Send-Commands "Reset IP-Filtering" @("ClearAccessBlock") }
        "g" { Set-Name }
        "G" { Set-Name }
        "n" { Set-Ntp }
        "N" { Set-Ntp }
        "q" { $running = $false }
        "Q" { $running = $false }
    }
}

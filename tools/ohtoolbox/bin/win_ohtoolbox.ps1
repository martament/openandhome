# --- TITEL ---
function Show-Header {
    Clear-Host
    Write-Host "====================================" -ForegroundColor Cyan
    Write-Host "    Openandhome - Multi-Tool v2.4" -ForegroundColor Cyan
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
        $p.Open()
        return $p
    } catch {
        Write-Host "`nFEHLER: Port $COM ist belegt!" -ForegroundColor Red
        Write-Host "Schließen Sie andere Programme (z.B. Arduino IDE)." -ForegroundColor White
        Read-Host "Drücken Sie Enter..."
        exit
    }
}

function Show-Settings {
    Write-Host "`n--- Aktuelle Einstellungen ---" -ForegroundColor Cyan
    Write-Host "Beenden mit STRG+C.`n" -ForegroundColor Gray
    $port = Open-Port
    try {
        $port.WriteLine("ResetFlashWriteCounter")
        Start-Sleep -Milliseconds 100
        $port.WriteLine("Settings")
        
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
    Write-Host "Schreibe in oh-debug.txt. Beenden mit STRG+C.`n" -ForegroundColor Gray
    "--- Debug Log Start: $(Get-Date) ---" | Out-File -FilePath .\oh-debug.txt
    
    $port = Open-Port
    try {
        $port.WriteLine("ResetFlashWriteCounter")
        $port.WriteLine("Settings")
        while ($port.IsOpen) {
            if ($port.BytesToRead -gt 0) {
                $line = $port.ReadLine()
                $line | Out-File -FilePath .\oh-debug.txt -Append
                Write-Host $line
            }
            Start-Sleep -Milliseconds 10
        }
    } catch [System.Management.Automation.PipelineStoppedException] {
        Write-Host "`nAufzeichnung beendet." -ForegroundColor Yellow
    } finally {
        if ($port) { $port.Close() }
        if (Test-Path .\oh-debug.txt) { Get-Content .\oh-debug.txt | Out-GridView -Title "Debug Resultate" }
    }
}

function Send-Commands($label, $commands) {
    Write-Host "`nFühre aus: $label" -ForegroundColor Yellow
    $port = Open-Port
    try {
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

    Send-Commands "WLAN-Daten setzen" $cmds

    # WifiConnect greift laut Praxisberichten nicht immer zuverlässig,
    # daher optionaler Reboot als sichere Variante.
    $rebootChoice = Read-Host "Gerät jetzt neu verbinden/rebooten? (j/n)"
    if ($rebootChoice -match '^[jJyY]$') {
        Invoke-Reboot
    }
}

# --- HAUPT-SCHLEIFE (TEXT-MENÜ) ---
$running = $true
while ($running) {
    Show-Header
    Write-Host "Verbunden mit: $COM" -ForegroundColor Green
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
        "6" { Send-Commands "Reset DHCP" @("IP 0.0.0.0") }
        "7" { Send-Commands "Reset Admin" @("password") }
        "8" { Send-Commands "Start AP-Mode" @("WifiAPMode") }
        "9" { Send-Commands "Reset IP-Filtering" @("ClearAccessBlock") }
        "q" { $running = $false }
        "Q" { $running = $false }
    }
}

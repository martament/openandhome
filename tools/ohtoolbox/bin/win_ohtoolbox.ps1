# --- TITEL ---
function Show-Header {
    Clear-Host
    Write-Host "====================================" -ForegroundColor Cyan
    Write-Host "    Openandhome - Multi-Tool v2.2" -ForegroundColor Cyan
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

# --- HAUPT-SCHLEIFE (TEXT-MENÜ) ---
$running = $true
while ($running) {
    Show-Header
    Write-Host "Verbunden mit: $COM" -ForegroundColor Green
    Write-Host "------------------------------------"
    Write-Host "1) Reset Wifi (SSID/Key löschen)"
    Write-Host "2) Einstellungen anzeigen (Settings)"
    Write-Host "3) Debugger (Output lesen & speichern)"
    Write-Host "4) Reset DHCP (Statische IP löschen)"
    Write-Host "5) Reset Admin Password"
    Write-Host "6) Start AP-Mode"
    Write-Host "7) Reset IP-Filtering"
    Write-Host "------------------------------------"
    Write-Host "Q) Beenden"
    Write-Host ""
    
    $choice = Read-Host "Ihre Wahl"

    switch ($choice) {
        "1" { Send-Commands "Reset Wifi" @("WifiSSID ssid", "WifiKey wpakey", "WifiSSID2 ssid", "WifiKey2 wpakey") }
        "2" { Show-Settings }
        "3" { Invoke-Debugger }
        "4" { Send-Commands "Reset DHCP" @("IP 0.0.0.0") }
        "5" { Send-Commands "Reset Admin" @("password") }
        "6" { Send-Commands "Start AP-Mode" @("WifiAPMode") }
        "7" { Send-Commands "Reset IP-Filtering" @("ClearAccessBlock") }
        "q" { $running = $false }
        "Q" { $running = $false }
    }
}
# --- TITEL AUSGABE ---
Clear-Host
Write-Host "====================================" -ForegroundColor Cyan
Write-Host "    Openandhome - Debugger" -ForegroundColor Cyan
Write-Host "   Zeigt die Debugausgaben der Sensorbox" -ForegroundColor Cyan
Write-Host "====================================`n" -ForegroundColor Cyan

# --- KONFIGURATION ---
$deviceNameFilter = "*USB-SERIAL*" 
$baudRate = 115200

$commands = @(
    "Settings"
)

# --- 1. PORT AUTOMATISCH FINDEN ---
$dev = Get-PnpDevice -PresentOnly | Where-Object { $_.FriendlyName -match "COM\d+" -and $_.FriendlyName -like $deviceNameFilter } | Select-Object -First 1

if (-not $dev) {
    Write-Host "FEHLER: Kein Gerät mit Filter '$deviceNameFilter' gefunden." -ForegroundColor Red
    return
}

$portName = [regex]::match($dev.FriendlyName, 'COM\d+').Value
$port = New-Object System.IO.Ports.SerialPort($portName, $baudRate, "None", 8, "One")

try {
    $port.Open()
    Write-Host "Verbunden mit $portName bei $baudRate Baud.`n" -ForegroundColor Green

    # --- 2. BEFEHLE SENDEN ---
    foreach ($cmd in $commands) {
        Write-Host "Sende: $cmd" -ForegroundColor Yellow
        $port.WriteLine($cmd)
        Start-Sleep -Milliseconds 200
    }

    Write-Host "`n--- Lese Modus aktiv ---" -ForegroundColor Cyan
    Write-Host "Beenden mit Taste 'A' oder STRG+C.`n" -ForegroundColor Gray

    # --- 3. FORTLAUFEND LESEN & AUF EINGABE PRÜFEN ---
    while ($port.IsOpen) {
        # Daten vom Port lesen
        if ($port.BytesToRead -gt 0) {
            $data = $port.ReadExisting()
            Write-Host $data -NoNewline
        }

        # Prüfen ob Taste 'A' gedrückt wurde
        if ($Host.UI.RawUI.KeyAvailable) {
            $key = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
            if ($key.Character -eq 'a' -or $key.Character -eq 'A') {
                Write-Host "`n`nTaste 'A' erkannt. Beende..." -ForegroundColor Yellow
                break 
            }
        }

        Start-Sleep -Milliseconds 20 
    }

} catch [System.Management.Automation.PipelineStoppedException] {
    # Dieser Block fängt STRG+C spezifisch ab, falls nötig
    Write-Host "`n`nAbbruch durch Benutzer (STRG+C)." -ForegroundColor Yellow
} catch {
    Write-Host "`nFehler: $($_.Exception.Message)" -ForegroundColor Red
} finally {
    # Dieser Teil wird IMMER ausgeführt, auch bei STRG+C
    if ($port -and $port.IsOpen) {
        $port.Close()
        $port.Dispose()
        Write-Host "`nVerbindung sicher getrennt und Port geschlossen." -ForegroundColor Red
    }
}
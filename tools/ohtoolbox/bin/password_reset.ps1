# --- KONFIGURATION ---
$deviceNameFilter = "*USB-SERIAL*" # Suchbegriff für dein Gerät (z.B. *Arduino*, *FTDI*)
$baudRate = 115200

# Die Befehle, die gesendet werden sollen
$commands = @(
    "wifissid,ssid",
    "wifissid2,ssid",
    "wifikey,ssid",
    "wifikey2,ssid",
    "save",
    "Settings",
    "reboot"
)

# --- 1. PORT AUTOMATISCH FINDEN ---
Write-Host "Suche nach Gerät..." -ForegroundColor Cyan
$dev = Get-PnpDevice -PresentOnly | Where-Object { $_.FriendlyName -like $deviceNameFilter } | Select-Object -First 1

if (-not $dev) {
    Write-Error "Kein passendes Gerät mit dem Namen '$deviceNameFilter' gefunden."
    return
}

# COM-Port aus dem Namen extrahieren (z.B. "COM3")
$portName = [regex]::match($dev.FriendlyName, 'COM\d+').Value
Write-Host "Gerät gefunden an: $portName" -ForegroundColor Green

# --- 2. VERBINDUNG AUFBAUEN UND SENDEN ---
$port = New-Object System.IO.Ports.SerialPort($portName, $baudRate, "None", 8, "One")

try {
    $port.Open()
    Write-Host "Verbindung geöffnet. Sende Befehle..." -ForegroundColor Yellow

    foreach ($cmd in $commands) {
        Write-Host "Sende: $cmd"
        $port.WriteLine($cmd)
        
        # Kurze Pause, damit das Gerät den Befehl verarbeiten kann
        Start-Sleep -Milliseconds 300 
        
        # Antwort vom Gerät (falls vorhanden) auslesen
        if ($port.BytesToRead -gt 0) {
            $resp = $port.ReadExisting()
            Write-Host "Antwort: $resp" -ForegroundColor Gray
        }
    }

    Write-Host "Passwort wurde zurück gesetzt!" -ForegroundColor Green

} catch {
    Write-Error "Fehler beim Senden: $($_.Exception.Message)"
} finally {
    if ($port -and $port.IsOpen) {
        $port.Close()
        Write-Host "Verbindung geschlossen."
    }
}
$COMS = [System.IO.Ports.SerialPort]::getportnames()


foreach ($comport in $COMS) {
    $COM = $comport
}

$msg = "Stellen Sie sicher, dass der Sensor am Rechner vor dem Start des Debuggers angeschlossen ist." + 
"$([System.Environment]::NewLine)$([System.Environment]::NewLine)Mit **Debugger** koennen Sie die Ausgaben des Sensors in eine Datei schreiben und anzeigen lassen. Achtung es werden auch WIFI-Zugangsdaten geschrieben. Diese evtl. loeschen." +
"$([System.Environment]::NewLine)$([System.Environment]::NewLine)Mit **ResetDHCP** koennen Sie eine statische IP Ihres Sensors aufheben. Hier bitte kurz warten. " +
"$([System.Environment]::NewLine)$([System.Environment]::NewLine)Mit **ResetWifi** koennen Sie die Wifizugangsdaten zuruecksetzen. Sie muessen den Sensor danach erneut in Ihr WLAN einbinden." +
"$([System.Environment]::NewLine)$([System.Environment]::NewLine)Mit **ResetAdmin** koennen Sie ein evtl. vergebenenes Adminpasswort zuruecksetzen." +
"$([System.Environment]::NewLine)$([System.Environment]::NewLine)Mit **StartAPMode** koennen Sie den WLAN-Zugangspunkt des Sensors starten und sich wie in der Anleitung beschrieben mit dem Sensor verbinden." +
"$([System.Environment]::NewLine)$([System.Environment]::NewLine)Mit **ResetIpFiltering** koennen Sie die Client-IP-Filterung fuer die aktuelle Session deaktiveren."  


function read-com {
    [System.Windows.Forms.MessageBox]::Show("Es werden die Debugausgaben des Sensors in die Datei oh-debug.txt im aktuellen Verzeichnis geschrieben. Trennen Sie den Sensor vom Rechner um die Aufzeichnung zu beenden. Die dann erscheinende Fehlermeldung koennen Sie ignorieren. In der Datei sind auch die WIFI-Zugangsdaten. Loeschen Sie evtl. das Passwort vor dem Versand aus der Datei.","Debugging",0)
    $text = 'Wir schreiben die Ausgabe des Sensors in die Datei oh-debug.txt.'
    $text | Out-File -FilePath .\oh-debug.txt
    Get-Date | Out-File -FilePath .\oh-debug.txt -Append -NoNewline
    $port= new-Object System.IO.Ports.SerialPort $COM,115000,None,8,one
    $port.Open()
    Sleep -Milliseconds 1000
    $port.WriteLine("reboot")
    Sleep -Milliseconds 3000
    $port.WriteLine("ResetFlashWriteCounter")
    Sleep -Milliseconds 3000
    $port.WriteLine("Settings")
    do {
        $line = $port.ReadLine()
        $line | Format-Table |Out-File -FilePath .\oh-debug.txt -Append -NoNewline
        #Write-Host $line # Do stuff here
    }
    while ($port.IsOpen)
    Get-Content .\oh-debug.txt | Out-GridView
}

function write-dhcp {
    $port= new-Object System.IO.Ports.SerialPort $COM,115000,None,8,one
    $port.Open()
    Sleep -Milliseconds 300
    $port.WriteLine("ResetFlashWriteCounter")
    Sleep -Milliseconds 300
    $port.WriteLine("IP 0.0.0.0")
    $port.WriteLine("Save")
    Sleep -Milliseconds 300
    $port.Close()
}

function reset-wifi {
    $port= new-Object System.IO.Ports.SerialPort $COM,115000,None,8,one
    $port.Open()
    Sleep -Milliseconds 300
    $port.WriteLine("ResetFlashWriteCounter")
    Sleep -Milliseconds 300
    $port.WriteLine("WifiSSID ssid")
    Sleep -Milliseconds 300
    $port.WriteLine("WifiKey wpakey")
    Sleep -Milliseconds 300
    $port.WriteLine("WifiSSID2 ssid")
    Sleep -Milliseconds 300
    $port.WriteLine("WifiKey2 wpakey")
    Sleep -Milliseconds 300
    $port.WriteLine("Save")
    Sleep -Milliseconds 300
}

function reset-password {
    $port= new-Object System.IO.Ports.SerialPort $COM,115000,None,8,one
    $port.Open()
    Sleep -Milliseconds 300
    $port.WriteLine("ResetFlashWriteCounter")
    Sleep -Milliseconds 300
    $port.WriteLine("password")
    Sleep -Milliseconds 300
    $port.WriteLine("Save")
    Sleep -Milliseconds 300
    $port.Close()
}

function start-apmode {
    $port= new-Object System.IO.Ports.SerialPort $COM,115000,None,8,one
    $port.Open()
    Sleep -Milliseconds 300
    $port.WriteLine("ResetFlashWriteCounter")
    Sleep -Milliseconds 300
    $port.WriteLine("WifiAPMode")
    Sleep -Milliseconds 300
    $port.WriteLine("Save")
    Sleep -Milliseconds 300
    $port.Close()
}

function reset-ipfilter {
    $port= new-Object System.IO.Ports.SerialPort $COM,115000,None,8,one
    $port.Open()
    Sleep -Milliseconds 300
    $port.WriteLine("ResetFlashWriteCounter")
    Sleep -Milliseconds 300
    $port.WriteLine("ClearAccessBlock")
    Sleep -Milliseconds 300
    $port.WriteLine("Save")
    Sleep -Milliseconds 300
    $port.Close()
}

$Title = "Openandhome-Debugger"

  
$options = [System.Management.Automation.Host.ChoiceDescription[]] @("&Debugger", "&ResetDHCP", "&ResetWifi", "&ResetAdmin","&StartAPMode", "&ResetIPFiltering","&Abbrechen")
[int]$defaultchoice = 6
$opt = $host.UI.PromptForChoice($Title , $msg , $Options,$defaultchoice)
switch($opt)
{
0 { read-com }
1 { write-dhcp }
2 { reset-wifi }
3 { reset-password }
4 { start-apmode }
5 { reset-ipfilter }
6 { Write-Host "Good Bye!!!" -ForegroundColor Green}
}

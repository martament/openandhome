$COMS = [System.IO.Ports.SerialPort]::getportnames()

#Wir nehmen immer den höchsten, also zuletzt angeschlossenen COM-Port
foreach ($comport in $COMS) {
    $COM = $comport
}

#Aktuelle Version ist nur in Python verfügbar. Daher mit Python Portable
$flash_cmd=".\pythonportable\python.exe .\pythonportable\Lib\site-packages\esptool.py --port " + $COM + " --baud 115200 write_flash --flash_mode dout --flash_size 4MB --flash_freq 40m 0x00000 "
$flash_cfg=".\pythonportable\python.exe .\pythonportable\Lib\site-packages\esptool.py --port " + $COM + " --baud 115200 write_flash 0x300000 "
$flash_erase=".\pythonportable\python.exe .\pythonportable\Lib\site-packages\esptool.py --port " + $COM + " --baud 115200 erase_flash  "

#Firmwares
$firmware_stable="..\firmware\openandhome_stable.bin"
$firmware_blank="..\firmware\blank_4MB.bin"

function update {
	 Write-Host "$([System.Environment]::NewLine)Sensor wird geupdated. Einstellungen bleiben erhalten.$([System.Environment]::NewLine)" -ForegroundColor Green
       $str = $flash_cmd + $firmware_stable
	Invoke-Expression $str

}
function upgrade {
	  Write-Host "$([System.Environment]::NewLine)Loesche den Sensor vollstaendig.$([System.Environment]::NewLine)" -ForegroundColor Green
         $str = $flash_cmd + $firmware_blank
	  Invoke-Expression $str
	  Sleep -Milliseconds 2000
	  Invoke-Expression $flash_erase
	  Sleep -Milliseconds 2000
	  Write-Host "$([System.Environment]::NewLine)Schreibe die Firmware auf den Sensor.$([System.Environment]::NewLine)" -ForegroundColor Green
         $str = $flash_cmd + $firmware_stable
	  Invoke-Expression $str
	  Sleep -Milliseconds 3000
	 write_config
}

function write_config {
	  Write-Host "$([System.Environment]::NewLine)Konfiguriere den Sensor.$([System.Environment]::NewLine)" -ForegroundColor Green
	$Title_conf = "Anzahl der Sensoren"
	$msg_conf = "Waehlen Sie die Anzahl Ihrer Sensoren." + 
	"Es wird dann die Konfiguration für Ihre Anzahl der Sensoren auf den Temperatursensor geschrieben.$([System.Environment]::NewLine)" 

	$options_conf = [System.Management.Automation.Host.ChoiceDescription[]] @("&1_Sensor", "&2_Sensoren", "&3_Sensoren", "&4_Sensoren", "&5=Wassersensor")
	[int]$defaultchoice = 0
	$opt_conf = $host.UI.PromptForChoice($Title_conf , $msg_conf , $options_conf,$defaultchoice)
	switch($opt_conf)
		{
		0 { $sensors=1}
		1 { $sensors=2 }
		2 { $sensors=3 }
		3 { $sensors=4}
		4 { $sensors=6}
	}

         $str = $flash_cfg + "..\firmware\" + $sensors + "_spiffs1M.bin"
  	 Invoke-Expression $str
	 Sleep -Milliseconds 1000	

	 $port= new-Object System.IO.Ports.SerialPort $COM,115000,None,8,one
	 $port.Open()
	 Sleep -Milliseconds 1000
	 $port.WriteLine("reboot")
	 Sleep -Milliseconds 3000
	 $port.WriteLine("ResetFlashWriteCounter")
	 Sleep -Milliseconds 500
        $port.Close()



	 Write-Host ""
	 Write-Host "Binden Sie nun den Sensor wie in der Anleitung beschrieben in Ihr WLAN ein."  -ForegroundColor Green
	 Write-Host ""
	 Write-Host "Sie müssen in der Oberfläche des Sensors noch unter Devices bei den einzelnen Sensoren die Device-Adresse auswählen."  -ForegroundColor Green
	 Write-Host ""
}

function debug {

    $port= new-Object System.IO.Ports.SerialPort $COM,115000,None,8,one
    $port.Open()
    Sleep -Milliseconds 1000
    $port.WriteLine("reboot")
    Sleep -Milliseconds 2000
    $port.WriteLine("ResetFlashWriteCounter")
    Sleep -Milliseconds 500
    $port.WriteLine("Settings")
    do {
        $line = $port.ReadLine()
        Write-Host $line # Do stuff here
    }
    while ($port.IsOpen)
}

Write-Host "*********************************************************************************************"
Write-Host "Stellen Sie sicher, dass der Sensor am Rechner vor dem Start des Flashers angeschlossen ist." 
Write-Host "*********************************************************************************************"
Write-Host "**Update**"   -BackgroundColor white -ForegroundColor Blue -NoNewline; Write-Host " => Hier koennen Sie die Firmware einspielen ohne die Konfiguration zu löschen." 
Write-Host "**Loeschen_und_Upgrade**"   -BackgroundColor white -ForegroundColor Blue -NoNewline; Write-Host " => Hier  koennen Sie den Sensor vollstaendig zurueck setzen. "
Write-Host "Es wird der Speicher geloescht, die Firmware und die Konfiguration eingespielt." 
Write-Host "**Debug**"   -BackgroundColor white -ForegroundColor Blue -NoNewline; Write-Host " => Hier koennen Sie die Ausgaben des Sensors lesen. Zum Beenden trennen Sie den Sensor vom Rechner."
Write-Host "*********************************************************************************************"
$Title = "Geben Sie den Buchstaben fuer Ihre Auswahl ein:"
$options = [System.Management.Automation.Host.ChoiceDescription[]] @("&Update", "&Loeschen_und_Upgrade", "&Debug", "&Abbrechen")
[int]$defaultchoice = 3
$opt = $host.UI.PromptForChoice($Title , $msg , $Options,$defaultchoice)
switch($opt)
{
0 { update }
1 { upgrade }
2 { debug }
3 { Write-Host "Good Bye!!!" -ForegroundColor Green}
}

# Startet den openandhome-Flasher. Die Logik steckt in oh_flasher.py
# (mitgeliefertes Python mit esptool und pyserial).
Set-Location $PSScriptRoot
& .\pythonportable\python.exe .\oh_flasher.py @args

echo off
cd bin
PowerShell -NoProfile -ExecutionPolicy Bypass -Command "& './openandhome-flasher.ps1'"
set /p asd="Beliebige Taste zum Beenden druecken"
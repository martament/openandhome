#!/bin/sh
# Skript to build the docs from Word
soffice --headless --convert-to pdf Openandhome_Bedienungsanleitung_Temperatursensor.pdf ../../../../14\ -\ Kunde\ Bedienungsanleitung/2019\ openandhome\ -\ Temperatur\ Bedienungsanleitung.docx
soffice --headless --convert-to pdf Openandhome_Bedienungsanleitung_Entfernungssensor.pdf ../../../../14\ -\ Kunde\ Bedienungsanleitung/2019\ openandhome\ -\ Entfernung\ Bedienungsanleitung.docx
#Move to Target
mv '2019 openandhome - Temperatur Bedienungsanleitung.pdf' ../../docs/'openandhome - Temperatur Bedienungsanleitung.pdf'
mv '2019 openandhome - Entfernung Bedienungsanleitung.pdf' ../../docs/'openandhome - Entfernung Bedienungsanleitung.pdf'

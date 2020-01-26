#!/bin/sh
# Skript to build the docs from Word
soffice --headless --convert-to pdf Openandhome_Bedienungsanleitung_Temperatursensor.pdf '../../../../14\ -\ Kunde\ Bedienungsanleitung/2020\ openandhome\ -\ Temperatur\ Bedienungsanleitung.docx'
#Move to Target
mv '2020 openandhome - Temperatur Bedienungsanleitung.pdf' ../../docs/'openandhome - Temperatur Bedienungsanleitung.pdf'

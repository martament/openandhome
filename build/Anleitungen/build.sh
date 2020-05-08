#!/bin/sh
# Skript to build the docs from Word
cur_dir=$PWD
cd ../../../../14\ -\ Kunde\ Bedienungsanleitung
pwd
soffice --headless --convert-to pdf Openandhome_Bedienungsanleitung_Temperatursensor.pdf '2020 openandhome - Temperatur Bedienungsanleitung.docx'
#Move to Target
mv '2020 openandhome - Temperatur Bedienungsanleitung.pdf' '../01 - Entwicklung/openandhome/docs/openandhome - Temperatur Bedienungsanleitung.pdf'
pwd
cd "$cur_dir"

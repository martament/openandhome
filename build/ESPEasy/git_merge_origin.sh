#! /bin/bash
my_pfad="ESPEasy"

echo Mache das Git-Update
echo
echo "Sichere unsere Dateien nach myfiles"
echo 
 
cp -v $my_pfad/.gitignore myfiles/.gitignore$my_pfad
#cp -v $my_pfad/platformio.ini myfiles/platformio.ini$my_pfad
cp -v $my_pfad/src/Custom.h myfiles/Custom.h$my_pfad
cd $my_pfad
#Setze auf die Version aus dem Repo zurück
#git reset --hard espeasy-fork/f-standalone-webserver
echo "Hole meinen Branch"
git pull espeasy-fork f-standalone-webserver
echo "Hole Änderungen vom Original"
git pull origin HEAD
echo "Wir verwenden den folgenden Branch"
git config --get remote.origin.url
git branch
echo
echo "Schicke gemergete Änderungen an den Branch"
 git push espeasy-fork f-standalone-webserver
cd ..
#cp -v myfiles/.gitignore$my_pfad ./$my_pfad/.gitignore
#cp -v myfiles/platformio.ini$my_pfad ./$my_pfad/platformio.ini
#cp -v myfiles/Custom.h$my_pfad ./$my_pfad/src/Custom.h

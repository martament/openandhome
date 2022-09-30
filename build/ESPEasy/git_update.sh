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
git reset --hard
git fetch
git pull
#
echo
echo "**************************************"
latesttag=$(git describe --tags --abbrev=0)
echo "Der aktuellste Tag ist ${latesttag}"
echo "**************************************"
echo 
echo "Wir verwenden den folgenden Branch"
git config --get remote.origin.url
git branch
echo
echo "Gehe zum letzen Tag zurück und setze meine Buildparameter"
git reset --hard $latesttag
cd ..
cp -v myfiles/.gitignore$my_pfad ./$my_pfad/.gitignore
#cp -v myfiles/platformio.ini$my_pfad ./$my_pfad/platformio.ini
cp -v myfiles/Custom.h$my_pfad ./$my_pfad/src/Custom.h

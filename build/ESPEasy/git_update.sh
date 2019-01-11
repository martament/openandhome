#! /bin/bash
if [[ $1 == "20" ]]
then
 my_pfad="ESPEasy_20"
else
 my_pfad="ESPEasy_mega"
fi

echo Mache das Git-Update
echo
echo "Sichere unsere Dateien nach myfiles"
echo 
 
cp -v $my_pfad/.gitignore myfiles/.gitignore$my_pfad
cp -v $my_pfad/platformio.ini myfiles/platformio.ini$my_pfad
cp -v $my_pfad/src/Custom.h myfiles/Custom.h$my_pfad
cd $my_pfad
git reset --hard
git pull
echo "Wir verwenden den folgenden Branch"
git config --get remote.origin.url
git branch
cd ..
cp -v myfiles/.gitignore$my_pfad ./$my_pfad/.gitignore
#cp -v myfiles/platformio.ini$my_pfad ./$my_pfad/platformio.ini
cp -v myfiles/Custom.h$mypfad ./$my_pfad/src/Custom.h

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
echo "Sichere die configs als Patch"
git checkout f-standalone-webserver 
git format-patch origin/mega -o ../myfiles
#git reset --hard
#reset hard nicht nötig. Habe mit git checkout -b f-standalone-webserver und git branch -u origin/mega 
#den Branch so erstellt, dass er meine Änderungen hat und dem Remote-Mega folgt.
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
echo "Gehe zum letzen Tag zurück und wende meine Patch an"
git reset --hard $latesttag
git am ../myfiles/0001-Patch-to-use-the-AP-Mode-as-daily-driver.patch
cd ..
cp -v myfiles/.gitignore$my_pfad ./$my_pfad/.gitignore
#cp -v myfiles/platformio.ini$my_pfad ./$my_pfad/platformio.ini
cp -v myfiles/Custom.h$my_pfad ./$my_pfad/src/Custom.h

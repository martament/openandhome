#! /bin/bash
echo Mache das Git-Update
echo
cd Tasmota
git reset --hard
git pull
echo "Wir verwenden den folgenden Branch"
git config --get remote.origin.url
git branch
cd ..

#!/bin/bash
echo "Installin PIP3-------"
sudo apt install python3-pip
echo "Installing Setuptools---------"
pip3 install setuptools
echo "Installing IBKR API--------------"
sudo python3 setup.py install
echo "Installig Required packages"
pip3 install -r requirements.txt
echo "Installing PyAutoGuy for TWS login"
python3 -m pip install pyautogui
sudo apt-get install scrot
sudo apt-get install python3-tk
sudo apt-get install python3-dev
echo "Doing executable files..."
cd ..
chmod u+x linux_start_all.sh
chmod u+x linux_watch_dog.sh
echo "Installing TWS if it is in Downloads-----"
cd ~/Downloads
chmod u+x tws-latest-linux-x64.sh
./tws-latest-linux-x64.sh
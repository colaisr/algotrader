#!/bin/bash
echo "Installin PIP3-------"
sudo apt install python3-pip
echo "Installing Setuptools---------"
pip3 install setuptools
echo "Installing IBKR API--------------"
python3 setup.py install
echo "Installig Required packages"
pip3 install -r requirements.txt
echo "Installing Xdotools for TWS login"
sudo apt-get install xdotool
echo "Installing TWS if it is in Downloads-----"
cd ~/Downloads
chmod u+x tws-latest-linux-x64.sh
./tws-latest-linux-x64.sh
#!/bin/bash
sudo apt install python3-pip
pip3 install setuptools
python3 setup.py install
pip3 install -r requirements.txt
sudo apt-get install xdotool
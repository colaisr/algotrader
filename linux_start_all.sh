#!/bin/bash
cd $(dirname $0)
sudo chmod +x Scripts/linux_twsRestartScript.sh
Scripts/linux_twsRestartScript.sh
python3 Main.py

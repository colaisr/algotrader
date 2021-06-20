#!/bin/bash
echo "Restarting TWS"
/root/Jts/tws start&
echo "TWS started"
sleep 60
echo "finished waiting"
python3 tws_cred_login.py
echo "Finished login to TWS"
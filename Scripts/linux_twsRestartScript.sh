#!/bin/bash
echo "Restarting TWS"
/home/su/Jts/tws start&
echo "TWS started"
sleep 60
echo "finished waiting"
python3 Scripts/tws_cred_login.py
echo "Finished login to TWS"
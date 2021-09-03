#!/bin/bash
echo "Closing TWS if open"
killall java
sleep 1
echo "Restarting TWS"
/home/su/Jts/tws start&
echo "TWS started"
sleep 10
echo "finished waiting"
python3 Scripts/tws_cred_login.py
echo "Finished login to TWS"
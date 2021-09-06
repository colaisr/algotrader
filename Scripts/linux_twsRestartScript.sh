#!/bin/bash
echo "Closing TWS if open"
killall java
sleep 1
echo "Restarting TWS"
/home/su/Jts/ibgateway/981/ibgateway start&
echo "TWS started"
sleep 30
echo "finished waiting"
python3 Scripts/tws_cred_login.py
echo "Finished login to TWS"
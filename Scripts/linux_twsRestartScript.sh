#!/bin/bash
echo "Restarting TWS"
/root/Jts/tws start&
echo "TWS started"
sleep 10
echo "finished waiting"
xdotool type colak1982
sleep 2
xdotool key Tab
sleep 2
xdotool type klk5489103
xdotool key Return
echo "Finished login to TWS"
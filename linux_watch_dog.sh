#!/bin/bash
#make-run.sh
#make sure a process is always running.

export DISPLAY=:0 #needed if you are running a simple gui app.

process=traderproc
makerun="/sbin/shutdown -r"

if ps ax | grep -v grep | grep $process > /dev/null
then
    exit
else
    $makerun &
fi

exit
#!/bin/bash

echo "Preparing for restart"

cd ~/cern2016/dpbcontrols

echo "Stop data acquisition"
./build/bin/SyncStopCern2016 -xml etc/ipbus_cern16_phase1.xml

echo "Reset timestamp"
./build/bin/SyncStartCern2016 -xml etc/ipbus_cern16_phase1.xml

echo "Please remember to execute SyncRestart only AFTER Starting FLESNET"

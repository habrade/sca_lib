#!/bin/bash

echo "Preparing for restart"

cd ~/cern2016/dpbcontrols

echo "Stop data acquisition"
./build/bin/SyncStopCern2016 -xml etc/ipbus_cern16_phase1.xml

sleep 5

echo "Preparing gDPB part of the setup for reconfiguration"
./build/bin/StartCern2016 -xml etc/ipbus_cern16_gdpb.xml
./build/bin/SyncStartCern2016 -xml etc/ipbus_cern16_gdpb.xml
./build/bin/SyncRestartCern2016 -xml etc/ipbus_cern16_gdpb.xml

echo "Apply configuration to gDPBs only"
./flim_gdpb_conf.sh

echo "Reset timestamp for all"
./build/bin/SyncStartCern2016 -xml etc/ipbus_cern16_phase1.xml

echo "Hope you change the settings BEFORE running this script!!!"
echo "Please remember to execute SyncRestart only AFTER Starting FLESNET"

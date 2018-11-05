#!/bin/bash

echo "Start preparing for configuration"

echo "Synchronize timing system"
cd ~/cern2016/ts_gm
./bin/ndpb_cern2016_ts_sys_start.exe

echo "Prepare configuration"
cd ~/cern2016/dpbcontrols
./build/bin/StartCern2016 -xml etc/ipbus_cern16_ndpb.xml
./build/bin/SyncStartCern2016 -xml etc/ipbus_cern16_ndpb.xml
./build/bin/SyncRestartCern2016 -xml etc/ipbus_cern16_ndpb.xml

echo "Please now execute the configuration scripts for the front-ends (all nDPBs) before starting the acquisition"

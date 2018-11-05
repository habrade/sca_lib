#!/bin/bash

echo "Start preparing for configuration"

echo "Synchronize timing system"
cd ~/cern2016/ts_gm
./bin/cern2016_ts_sys_start.exe --connection_file="file://cfg/cern16_gdpb_sys_connections_hw.xml"

echo "Prepare configuration"
cd ~/cern2016/dpbcontrols
./build/bin/StartCern2016 -xml etc/ipbus_cern16_gdpb.xml
./build/bin/SyncStartCern2016 -xml etc/ipbus_cern16_gdpb.xml
./build/bin/SyncRestartCern2016 -xml etc/ipbus_cern16_gdpb.xml

echo "Apply configuration"
./flim_gdpb_conf.sh

echo "Re-synchronize boards"
./build/bin/SyncStartCern2016 -xml etc/ipbus_cern16_gdpb.xml

echo "Ready to start FLESNET (gDPBs only)"

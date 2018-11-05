#!/bin/bash

echo "Start preparing for configuration for eTOF@STAR 2017 tests"

echo "Prepare configuration"
cd /opt/cbmsoft/dpbcontrols/
./build/bin/StartCern2016 -xml etc/ipbus_star17_gdpb.xml
./build/bin/SyncStartCern2016 -xml etc/ipbus_star17_gdpb.xml
./build/bin/SyncRestartCern2016 -xml etc/ipbus_star17_gdpb.xml

echo "Apply configuration"
#./flim_gdpb_conf.sh
./build/bin/gdpbCli @etc/config/flim_star_g104.gdpb

echo "Re-synchronize boards"
./build/bin/SyncStartCern2016 -xml etc/ipbus_star17_gdpb.xml

echo "Ready to start FLESNET for eTOF@STAR 2017 tests"

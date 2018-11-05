#!/bin/bash

echo "Preparing for restart"

cd /opt/cbmsoft/dpbcontrols/

#echo "Stop data acquisition"
#./build/bin/SyncStopCern2016 -xml etc/ipbus_star17_gdpb.xml

echo "Reload gDPB configuration"
./build/bin/SyncStartCern2016 -xml etc/ipbus_star17_gdpb.xml
./build/bin/SyncRestartCern2016 -xml etc/ipbus_star17_gdpb.xml
#./flim_gdpb_conf.sh
./build/bin/gdpbCli @etc/config/flim_star_g104.gdpb

echo "Reset timestamp"
./build/bin/SyncStartCern2016 -xml etc/ipbus_star17_gdpb.xml

echo "Please remember to execute SyncRestart only AFTER Starting FLESNET"

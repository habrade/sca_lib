#!/bin/bash

echo "Preparing for restart"

cd /opt/cbmsoft/dpbcontrols/

echo "Stop data acquisition"
./build/bin/SyncStopCern2016 -xml etc/ipbus_star17_gdpb.xml

echo "Reset timestamp"
./build/bin/SyncStartCern2016 -xml etc/ipbus_star17_gdpb.xml

echo "Please remember to execute SyncRestart only AFTER Starting FLESNET"

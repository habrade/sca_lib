#!/bin/bash
#
## Script starting all the pieces needed to readout eTOF@STAR data and
## send events to the STAR DAQ
#

# Printout date for log file
echo "----------------------------------"
date 

cd /home/cbm-star/logs

# First start the IPBUS control_hub.
/opt/cbmsoft/dpbcontrols/start_controlhub.sh

echo "Starting Config ..."

# Then load the gDPB and GET4 config
cd /home/cbm-star/logs
/opt/cbmsoft/dpbcontrols/init_star2017.sh 2>&1 > /home/cbm-star/logs/init_star2017.log

echo "Config Done ..."

# Then start the readout script in background mode
cd /home/cbm-star/src/flesnet/build
nohup /home/cbm-star/src/flesnet/build/readout > /dev/null &

echo "FLESNET started ..."

# Finally enable the data readout when flesnet is ready
## Wait until we find the line in the log showing that the compute node is ready
###tail -f /home/cbm-star/src/flesnet/build/flesnet_in0.log | while read LOGLINE
CNREADY=`grep -c "connection to input nodes established" /home/cbm-star/src/flesnet/build/flesnet_cn.log`
while [ 1 -ne ${CNREADY} ]
do
   sleep 1
   CNREADY=`grep -c "connection to input nodes established" /home/cbm-star/src/flesnet/build/flesnet_cn.log`
   echo "CNREADY is " ${CNREADY}
###   [[ "${LOGLINE}" == *"flib server started and running"* ]] && pkill -P $$ tail
done
echo "FLESNET Compute Node ready ..."
## Wait until we find the line in the log showing that the input no is ready
INREADY=`grep -c "connection to compute nodes established" /home/cbm-star/src/flesnet/build/flesnet_in0.log`
while [ 1 -ne ${INREADY} ]
do
   sleep 1
   INREADY=`grep -c "connection to compute nodes established" /home/cbm-star/src/flesnet/build/flesnet_in0.log`
   echo "INREADY is " ${INREADY}
###   [[ "${LOGLINE}" == *"flib server started and running"* ]] && pkill -P $$ tail
done
echo "FLESNET Input Node ready ..."

## wait 4s to be sure
sleep 4
## Send the SyncRestart command
cd /opt/cbmsoft/dpbcontrols/
./build/bin/SyncRestartCern2016 -xml etc/ipbus_star17_gdpb.xml 2>&1 > /home/cbm-star/logs/SyncRestart.log


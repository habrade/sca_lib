#!/bin/bash

echo "Start config of gDPB 115"
./build/bin/gdpbCli @etc/config/cdaq_g115.gdpb
echo "Config of gDPB 115 done"

echo "Start config of gDPB 116"
./build/bin/gdpbCli @etc/config/cdaq_g116.gdpb
echo "Config of gDPB 116 done"

echo "Start config of gDPB 113"
./build/bin/gdpbCli @etc/config/cdaq_g113.gdpb
echo "Config of gDPB 113 done"

echo "Start config of gDPB 102"
./build/bin/gdpbCli @etc/config/cdaq_g102.gdpb
echo "Config of gDPB 102 done"

echo "Start config of gDPB 103"
./build/bin/gdpbCli @etc/config/cdaq_g103.gdpb
echo "Config of gDPB 103 done"

echo "Start config of gDPB 110"
./build/bin/gdpbCli @etc/config/cdaq_g110.gdpb
echo "Config of gDPB 110 done"

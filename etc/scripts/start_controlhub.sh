#!/bin/bash
#
## Script doing the login for IPbus and then starting the control_hub
#

source /opt/cbmsoft/ipbuslogin.sh

# If already ON, do nothing.
controlhub_start 2>&1 > /home/cbm-star/logs/controlhub_start.log

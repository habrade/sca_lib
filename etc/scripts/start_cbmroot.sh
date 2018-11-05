#!/bin/bash
#
## Script doing the login for CBMROOT adn starting it
## with redirection of the output to the ~/logs folder
#

source ~/bin/cbmrootlogin
root -l -q -b MonitorStar2017.C

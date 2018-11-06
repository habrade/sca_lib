#!/usr/bin/python

import sys
import time

sys.path.append('./lib')
import sca_defs
import scaAdc

if __name__ == '__main__':

    sca_dev = scaAdc.ScaAdc()

    # Reset Chip
    sca_dev.send_reset()
    # Connect SCA chip
    sca_dev.send_connect()

    # Read Chip ID
    sca_dev.readScaId()

    while True:
        sca_dev.wSel(6)
        print("ADC Ch 6 = %x") %sca_dev.startConv()
        print("OFS = %x") %sca_dev.rOfs()
        sca_dev.wSel(31)
        print("SCA Temp  = %x") %sca_dev.startConv()
        print("OFS = %x") %sca_dev.rOfs()

        time.sleep(1)

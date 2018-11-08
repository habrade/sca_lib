#!/usr/bin/python

import sys
import time

sys.path.append('./lib')
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
        for i in range(32):
            sca_dev.wSel(i)
            print("ADC Ch %d = %x" % (i, sca_dev.startConv()))
        time.sleep(1)

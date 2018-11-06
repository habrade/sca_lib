#!/usr/bin/python

import sys
import time

sys.path.append('./lib')
import sca_defs
import scaGpio

if __name__ == '__main__':

    sca_dev = scaGpio.ScaGpio()

    # Reset Chip
    sca_dev.send_reset()
    # Connect SCA chip
    sca_dev.send_connect()

    sca_dev.readScaId()

    # Enable GPIO
    print("Enable GPIO")
    sca_dev.enableGPIO()

    # GPIO Direction Set
    sca_dev.setDirection(0xffffffff)

    # GPIO Direction READ
    print("Direction = "), hex(sca_dev.getDirection())

    sca_dev.testGPIO(0x00000000)
    sca_dev.testGPIO(0xffffffff)


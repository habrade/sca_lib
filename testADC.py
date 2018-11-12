#!/usr/bin/python

import sys
import time

sys.path.append('./lib')
import sca_adc

if __name__ == '__main__':

    sca_dev = sca_adc.ScaAdc()

    # Reset Chip
    sca_dev.send_reset()
    # Connect SCA chip
    sca_dev.send_connect()

    # Read Chip ID
    sca_dev.read_sca_id()

    while True:
        for i in range(32):
            sca_dev.w_sel(i)
            print("ADC Ch %d = %x" % (i, sca_dev.start_conv()))
        time.sleep(1)

#!/usr/bin/env python
import time

from lib.gdpb import Gdpb
from lib.sca_defs import *

if __name__ == '__main__':
    afck_num = 66
    sca_dev = Gdpb(afck_num)

    # Reset Chip
    sca_dev.send_reset()
    # Connect SCA chip
    sca_dev.send_connect()

    sca_dev.enable_chn(SCA_CH_ADC, True)
    # Read Chip ID
    while True:
        sca_id = sca_dev.read_sca_id()
        time.sleep(1)

#!/usr/bin/env python
import sys
import time

from lib.gdpb import Gdpb
from lib.sca_defs import *

if __name__ == '__main__':

    if len(sys.argv) == 3:
        afck_num = int(sys.argv[1])
        link = int(sys.argv[2])
    else:
        print("Usage:  ./readScaId.py board_num link_num")
        sys.exit(1)

    sca_dev = Gdpb(afck_num, link)

    # Reset Chip
    sca_dev.send_reset()
    # Connect SCA chip
    sca_dev.send_connect()

    sca_dev.enable_chn(SCA_CH_ADC, True)
    # Read Chip ID
    while True:
        sca_id = sca_dev.read_sca_id()
        time.sleep(1)

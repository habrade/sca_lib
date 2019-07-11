#!/usr/bin/env python
import logging
import time

from lib.sca_defs import *
from lib.gdpb import Gdpb

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


class TestReadId(Gdpb):
    def __init__(self, afck_num):
        super(TestReadId, self).__init__(afck_num)


if __name__ == '__main__':
    sca_dev = TestReadId(66)

    # Reset Chip
    sca_dev.send_reset()
    # Connect SCA chip
    sca_dev.send_connect()

    sca_dev.enable_chn(SCA_CH_ADC, True)
    # Read Chip ID
    while True:
        sca_id = sca_dev.read_sca_id()
        time.sleep(1)

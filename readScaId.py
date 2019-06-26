#!/usr/bin/env python
import logging
import pvaccess
import time

from lib import sca
from lib.sca_defs import *

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


if __name__ == '__main__':
    sca_dev = sca.Sca()

    # Reset Chip
    sca_dev.send_reset()
    # Connect SCA chip
    sca_dev.send_connect()

    sca_dev.enable_chn(SCA_CH_ADC, True)
    # Read Chip ID
    while True:
        sca_id = sca_dev.read_sca_id()

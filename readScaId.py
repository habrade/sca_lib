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

sca_dev = sca.Sca()

# Read Chip ID
while True:
    sca_id = sca_dev.read_sca_id()
    time.sleep(1)

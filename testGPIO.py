#!/usr/bin/env python
import sys
import time
import logging

import pvaccess

from lib import sca_defs
from lib import sca_gpio

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

if __name__ == '__main__':
    sca_dev = sca_gpio.ScaGpio(version=2)

    # Reset Chip
    sca_dev.send_reset()
    # Connect SCA chip
    sca_dev.send_connect()

    # Read Chip ID
    sca_id = sca_dev.read_sca_id()
    log.info("SCA ID = %x" % sca_id)

    # Enable GPIO
    sca_dev.enable_chn(sca_defs.SCA_CH_GPIO, True)

    PREFIX = "labtest:"
    ch_name_direction_set = PREFIX + "SCA:GPIO:DIRECTION:SET"
    ca_name_direction_get = PREFIX + "SCA:GPIO:DIRECTION:GET"
    ca_name_pinout_get = PREFIX + "SCA:GPIO:PINOUT:GET"
    ca_name_pinout_set = PREFIX + "SCA:GPIO:PINOUT:SET"
    ca_name_pinin_get = PREFIX + "SCA:GPIO:PININ:GET"

    while True:
        # GPIO Direction Set
        ca_ch = pvaccess.Channel(ch_name_direction_set)
        direction_set = int(ca_ch.get().getDouble())
        log.debug("GPIO Direction Set to %x" % direction_set)
        sca_dev.set_direction(direction_set)

        # GPIO Direction READ
        ca_ch = pvaccess.Channel(ca_name_direction_get)
        direction_get = sca_dev.get_direction()
        log.debug("GPIO Direction Get =  %x" % direction_get)
        ca_ch.put(int(direction_get))

        # GPIO PinOut Set
        ca_ch = pvaccess.Channel(ca_name_pinout_set)
        pinout_set = int(ca_ch.get().getDouble())
        log.debug("GPIO PINOUT Set to %x" % pinout_set)
        sca_dev.write_pin_out(pinout_set)

        # GPIO PinOut READ
        ca_ch = pvaccess.Channel(ca_name_pinout_get)
        pinout_get = sca_dev.read_pin_out()
        log.debug("GPIO PINOUT Get =  %x" % pinout_get)
        ca_ch.put(int(pinout_get))

        # GPIO PinIn READ
        ca_ch = pvaccess.Channel(ca_name_pinin_get)
        pinin_get = sca_dev.read_pin_in()
        log.debug("GPIO PININ Get =  %x" % pinin_get)
        ca_ch.put(int(pinin_get))

        time.sleep(1)

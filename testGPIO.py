#!/usr/bin/env python
import logging

import pvaccess

from lib import sca_defs
from lib.gdpb import Gdpb

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

if __name__ == '__main__':
    afck_num = 66
    link = 0
    sca_dev = Gdpb(afck_num, link)

    # Reset Chip
    sca_dev.send_reset()
    # Connect SCA chip
    sca_dev.send_connect()

    # Enable GPIO
    sca_dev.enable_chn(sca_defs.SCA_CH_GPIO, True)

    PREFIX = "labtest:Gdpb:%d:SCA:" % afck_num
    ca_name_direction_set_1_half = PREFIX + "GPIO:CH_31_16:DIRECTION:SET"
    ca_name_direction_get_1_half = PREFIX + "GPIO:CH_31_16:DIRECTION:GET"
    ca_name_pinout_get_1_half = PREFIX + "GPIO:CH_31_16:PINOUT:GET"
    ca_name_pinout_set_1_half = PREFIX + "GPIO:CH_31_16:PINOUT:SET"
    ca_name_pinin_get_1_half = PREFIX + "GPIO:CH_31_16:PININ:GET"
    ca_name_direction_set_2_half = PREFIX + "GPIO:CH_15_0:DIRECTION:SET"
    ca_name_direction_get_2_half = PREFIX + "GPIO:CH_15_0:DIRECTION:GET"
    ca_name_pinout_get_2_half = PREFIX + "GPIO:CH_15_0:PINOUT:GET"
    ca_name_pinout_set_2_half = PREFIX + "GPIO:CH_15_0:PINOUT:SET"
    ca_name_pinin_get_2_half = PREFIX + "GPIO:CH_15_0:PININ:GET"

    while True:
        # GPIO Direction Set
        ca_ch_1 = pvaccess.Channel(ca_name_direction_set_1_half)
        ca_ch_2 = pvaccess.Channel(ca_name_direction_set_2_half)
        direction_set_1 = ca_ch_1.get().getInt()
        direction_set_2 = ca_ch_2.get().getInt()
        direction_set = (direction_set_1 << 16) + direction_set_2
        log.debug("GPIO Direction Set to %#x" % direction_set)
        sca_dev.set_direction(direction_set)

        # GPIO Direction READ
        ca_ch_1 = pvaccess.Channel(ca_name_direction_get_1_half)
        ca_ch_2 = pvaccess.Channel(ca_name_direction_get_2_half)
        direction_get = sca_dev.get_direction()
        log.debug("GPIO Direction Get =  %#x" % direction_get)
        ca_ch_1.putInt(direction_get >> 16)
        ca_ch_2.putInt(direction_get & 0xFFFF)

        # GPIO PinOut Set
        ca_ch_1 = pvaccess.Channel(ca_name_pinout_set_1_half)
        ca_ch_2 = pvaccess.Channel(ca_name_pinout_set_2_half)
        pinout_set_1 = ca_ch_1.get().getInt()
        pinout_set_2 = ca_ch_2.get().getInt()
        pinout_set = (pinout_set_1 << 16) + pinout_set_2
        log.debug("GPIO PINOUT Set to %#x" % pinout_set)
        sca_dev.write_pin_out(pinout_set)

        # GPIO PinOut READ
        ca_ch_1 = pvaccess.Channel(ca_name_pinout_get_1_half)
        ca_ch_2 = pvaccess.Channel(ca_name_pinout_get_2_half)
        pinout_get = sca_dev.read_pin_out()
        log.debug("GPIO PINOUT Get =  %#x" % pinout_get)
        ca_ch_1.putInt(pinout_get >> 16)
        ca_ch_2.putInt(pinout_get & 0xFFFF)

        # GPIO PinIn READ
        ca_ch_1 = pvaccess.Channel(ca_name_pinin_get_1_half)
        ca_ch_2 = pvaccess.Channel(ca_name_pinin_get_2_half)
        pinin_get = sca_dev.read_pin_in()
        log.debug("GPIO PININ Get =  %#x" % pinin_get)
        ca_ch_1.putInt(pinin_get >> 16)
        ca_ch_2.putInt(pinin_get & 0xFFFF)

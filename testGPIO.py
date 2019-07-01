#!/usr/bin/env python
import logging
import subprocess

import pvaccess

from lib import sca_defs
from lib.gdpb import Gdpb

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


class TestGPIO(Gdpb):
    def __init__(self):
        Gdpb.__init__(self)
        self.gpio_dev = self.sca_modules[0].sca_gpio


if __name__ == '__main__':

    # run softIocPVA
    subprocess.Popen(["./runIoc.sh"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

    test_gpio = TestGPIO()
    sca_dev = test_gpio.gpio_dev

    # Reset Chip
    sca_dev.send_reset()
    # Connect SCA chip
    sca_dev.send_connect()

    # Enable GPIO
    sca_dev.enable_chn(sca_defs.SCA_CH_GPIO, True)

    PREFIX = "labtest:SCA:0:"
    ca_name_direction_set = PREFIX + "GPIO:DIRECTION:SET"
    ca_name_direction_get = PREFIX + "GPIO:DIRECTION:GET"
    ca_name_pinout_get = PREFIX + "GPIO:PINOUT:GET"
    ca_name_pinout_set = PREFIX + "GPIO:PINOUT:SET"
    ca_name_pinin_get = PREFIX + "GPIO:PININ:GET"

    while True:
        # GPIO Direction Set
        ca_ch = pvaccess.Channel(ca_name_direction_set)
        direction_set = ca_ch.get().getInt()
        log.debug("GPIO Direction Set to %#x" % direction_set)
        sca_dev.set_direction(direction_set)

        # GPIO Direction READ
        ca_ch = pvaccess.Channel(ca_name_direction_get)
        direction_get = sca_dev.get_direction()
        log.debug("GPIO Direction Get =  %#x" % direction_get)
        ca_ch.putInt(direction_get)

        # GPIO PinOut Set
        ca_ch = pvaccess.Channel(ca_name_pinout_set)
        pinout_set = ca_ch.get().getInt()
        log.debug("GPIO PINOUT Set to %#x" % pinout_set)
        sca_dev.write_pin_out(pinout_set)

        # GPIO PinOut READ
        ca_ch = pvaccess.Channel(ca_name_pinout_get)
        pinout_get = sca_dev.read_pin_out()
        log.debug("GPIO PINOUT Get =  %#x" % pinout_get)
        ca_ch.putInt(pinout_get)

        # GPIO PinIn READ
        ca_ch = pvaccess.Channel(ca_name_pinin_get)
        pinin_get = sca_dev.read_pin_in()
        log.debug("GPIO PININ Get =  %#x" % pinin_get)
        ca_ch.putInt(pinin_get)

#!/usr/bin/env python
import logging
import sys

import pvaccess

from lib.gdpb import Gdpb
from lib.sca_defs import *

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

if __name__ == '__main__':
    if len(sys.argv) == 3:
        afck_num = int(sys.argv[1])
        link = int(sys.argv[2])
    else:
        print("Usage:  ./readScaId.py board_num link_num")
        sys.exit(1)

    testGdpb = Gdpb(afck_num, link)

    # Reset SCA
    testGdpb.send_reset()
    # Connect SCA chip
    testGdpb.send_connect()

    # Enable I2C ch. 0
    testGdpb.enable_chn(SCA_CH_I2C0, True)
    testGdpb.set_frq(SCA_I2C_SPEED_100)
    testGdpb.set_mode(SCA_I2C_MODE_OPEN_DRAIN)

    # reset bme280
    testGdpb.rst_dev()

    PREFIX = "labtest:Gdpb:%d:SCA:%d:" % (afck_num, link)
    degrees_ch = pvaccess.Channel(PREFIX + "BME280:Temperature")
    hectopascals_ch = pvaccess.Channel(PREFIX + "BME280:Pressure")
    humidity_ch = pvaccess.Channel(PREFIX + "BME280:Humidity")

    # check BME280 ID
    if testGdpb.read_id() != 0x60:
        log.error("BME280's ID is not right, should be 0x60 after reset")

    # read Temp, Pressure, Humidity
    while True:
        degrees = testGdpb.read_temperature()
        pascals = testGdpb.read_pressure()
        hectopascals = pascals / 100
        humidity = testGdpb.read_humidity()

        # Data put to epics channel
        degrees_ch.putDouble(degrees)
        hectopascals_ch.putDouble(hectopascals)
        humidity_ch.putDouble(humidity)

        log.debug("Temp = %f deg C" % degrees)
        log.debug("Pressure = %f hPa" % hectopascals)
        log.debug("Humidity = %f %%" % humidity)

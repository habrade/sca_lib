#!/usr/bin/env python
import logging
import subprocess

import pvaccess

from lib.gdpb import Gdpb
from lib.sca_defs import *

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


class TestBme280(Gdpb):
    def __init__(self):
        Gdpb.__init__(self, scaNum=2)
        self.bme280_dev = self.sca_modules[1].bme280


if __name__ == '__main__':
    # run softIocPVA
    subprocess.Popen(["./runIoc.sh"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

    test_bme280 = TestBme280()
    sensor = test_bme280.bme280_dev

    # Reset SCA
    sensor.send_reset()
    # Connect SCA chip
    sensor.send_connect()

    # Enable I2C ch. 0
    sensor.enable_chn(SCA_CH_I2C0, True)
    sensor.set_frq(SCA_I2C_SPEED_100)
    sensor.set_mode(SCA_I2C_MODE_OPEN_DRAIN)

    # reset bme280
    sensor.rst_dev()

    PREFIX = "labtest:SCA:0:"
    degrees_ch = pvaccess.Channel(PREFIX + "BME280:Temperature")
    hectopascals_ch = pvaccess.Channel(PREFIX + "BME280:Pressure")
    humidity_ch = pvaccess.Channel(PREFIX + "BME280:Humidity")

    # check BME280 ID
    if sensor.read_id() != 0x60:
        log.error("BME280's ID is not right, should be 0x60 after reset")

    # read Temp, Pressure, Humidity
    while True:
        degrees = sensor.read_temperature()
        pascals = sensor.read_pressure()
        hectopascals = pascals / 100
        humidity = sensor.read_humidity()

        # Data put to epics channel
        degrees_ch.putDouble(degrees)
        hectopascals_ch.putDouble(hectopascals)
        humidity_ch.putDouble(humidity)

        log.debug("Temp = %f deg C" % degrees)
        log.debug("Pressure = %f hPa" % hectopascals)
        log.debug("Humidity = %f %%" % humidity)

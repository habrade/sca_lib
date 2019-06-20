#!/usr/bin/env python
import logging
import pvaccess
import time
import sys  # For sys.argv and sys.exit

from lib.sca_defs import *
from lib.bme280_defs import *
from lib import bme280

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

if __name__ == '__main__':
    sensor = bme280.BME280(t_mode=BME280_OSAMPLE_8,
                           p_mode=BME280_OSAMPLE_8, h_mode=BME280_OSAMPLE_8)
    # Reset SCA
    sensor.send_reset()
    # Connect SCA chip
    sensor.send_connect()

    log.info("SCA ID = %x", sensor.read_sca_id())

    # Enable I2C ch. 0
    sensor.enable_chn(SCA_CH_I2C0, True)
    sensor.set_frq(SCA_I2C_SPEED_100)
    sensor.set_mode(SCA_I2C_MODE_OPEN_DRAIN)

    # reset bme280
    sensor.rst_dev()

    PREFIX = "labtest:"

    # check BME280 ID
    if sensor.read_id() != 0x60:
        log.error("BME280's ID is not right, should be 0x60 after reset")

    # read Temp, Pressure, Humidity
    while True:
        degrees_ch = pvaccess.Channel(PREFIX + "BME280:Temperature")
        hectopascals_ch = pvaccess.Channel(PREFIX + "BME280:Pressure")
        humidity_ch = pvaccess.Channel(PREFIX + "BME280:Humidity")

        degrees = sensor.read_temperature()
        pascals = sensor.read_pressure()
        hectopascals = pascals / 100
        humidity = sensor.read_humidity()

        degrees_ch.putDouble(degrees)
        hectopascals_ch.putDouble(hectopascals)
        humidity_ch.putDouble(humidity)

        print 'Temp      = {0:0.3f} deg C'.format(degrees)
        print 'Pressure  = {0:0.2f} hPa'.format(hectopascals)
        print 'Humidity  = {0:0.2f} %'.format(humidity)
        time.sleep(0.04)

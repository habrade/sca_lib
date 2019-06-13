#!/usr/bin/python
import logging
import pvaccess
import time
import sys  # For sys.argv and sys.exit

sys.path.append('./lib')
import sca_defs

import bme280
import bme280_defs

log = logging.getLogger(__name__)

if __name__ == '__main__':
    sensor = bme280.BME280(t_mode=bme280_defs.BME280_OSAMPLE_8, p_mode=bme280_defs.BME280_OSAMPLE_8,
                           h_mode=bme280_defs.BME280_OSAMPLE_8)
    # Reset SCA
    sensor.SCA._send_reset()
    # Connect SCA chip
    sensor.SCA._send_connect()

    log.info("SCA ID = %x", sensor.SCA._read_sca_id())

    # Enable I2C ch. 0
    sensor.SCA._enable_chn(sca_defs.SCA_CH_I2C0)
    sensor.I2C.set_frq(sca_defs.SCA_CH_I2C0, sca_defs.SCA_I2C_SPEED_100)
    sensor.I2c.set_mode(sca_defs.SCA_CH_I2C0, sca_defs.SCA_I2C_MODE_OPEN_DRAIN)

    # reset bme280
    sensor.BME280.rst_dev()

    # check BME280 ID
    if sensor.BME280.read_id() != 0x60:
        log.error("BME280's ID is not right, should be 0x60 after reset")

    # read Temp, Pressure, Humidity
    while True:
        degrees = sensor.read_temperature()
        pascals = sensor.read_pressure()
        hectopascals = pascals / 100
        humidity = sensor.read_humidity()

        print 'Temp      = {0:0.3f} deg C'.format(degrees)
        print 'Pressure  = {0:0.2f} hPa'.format(hectopascals)
        print 'Humidity  = {0:0.2f} %'.format(humidity)
        time.sleep(0.04)

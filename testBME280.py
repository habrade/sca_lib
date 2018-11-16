#!/usr/bin/python

import sys  # For sys.argv and sys.exit

sys.path.append('./lib')
import sca_defs

import bme280
import bme280_defs


def rst_device(sca_dev):
    sca_dev.send_command(sca_defs.SCA_CH_I2C0, 0x40, 0xE0B60000)
    sca_dev.send_command(sca_defs.SCA_CH_I2C0, 0xDA, 0x77000000)
    sca_dev.send_command(sca_defs.SCA_CH_I2C0, 0x41, 0x00000000)


def dev_init(sca_dev):
    rst_device()
    sca_dev.set_frq(sca_defs.SCA_CH_I2C0, sca_defs.SCA_I2C_SPEED_100)
    sca_dev.set_mode(sca_defs.SCA_CH_I2C0, sca_defs.SCA_I2C_MODE_OPEN_DRAIN)
    sca_dev.nrByte(sca_defs.SCA_CH_I2C0, 2)


if __name__ == '__main__':
    sensor = bme280.BME280(t_mode=bme280_defs.BME280_OSAMPLE_8, p_mode=bme280_defs.BME280_OSAMPLE_8,
                           h_mode=bme280_defs.BME280_OSAMPLE_8)
    # Reset SCA
    sensor.SCA.send_reset()
    # Connect SCA chip
    sensor.SCA.send_connect()

    print "SCA ID = %x" % sensor.SCA.read_sca_id()

    # Enable I2C ch. 0
    sensor.enable_chn(sca_defs.SCA_CH_I2C0)

    # send reset
    rst_device(sca_dev)

    degrees = sensor.read_temperature()
    pascals = sensor.read_pressure()
    hectopascals = pascals / 100
    humidity = sensor.read_humidity()

    print 'Temp      = {0:0.3f} deg C'.format(degrees)
    print 'Pressure  = {0:0.2f} hPa'.format(hectopascals)
    print 'Humidity  = {0:0.2f} %'.format(humidity)

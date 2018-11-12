#!/usr/bin/python

import sys  # For sys.argv and sys.exit

sys.path.append('./lib')
import sca_i2c
import sca_defs


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
    sca_dev = sca_i2c.ScaI2c()
    # Reset Chip
    sca_dev.send_reset()
    # Connect SCA chip
    sca_dev.send_connect()

    chipId = sca_dev.read_sca_id()
    print "SCA ID = %x" % chipId

    # Enable I2C ch. 0
    sca_dev.enable_chn(sca_defs.SCA_CH_I2C0)

    # BME280 I2C addr
    addr = 0x77

    # send reset
    rst_device(sca_dev)

    # read ID
    sca_dev.send_command(sca_defs.SCA_CH_I2C0, 0x82, 0x77D00000)
    sca_dev.send_command(sca_defs.SCA_CH_I2C0, 0x86, 0x77000000)

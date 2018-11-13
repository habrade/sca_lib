#!/usr/bin/python

import sys

sys.path.append('./lib')
import sca_defs
import sca_gpio

if __name__ == '__main__':
    sca_dev = sca_gpio.ScaGpio()

    # Reset Chip
    sca_dev.send_reset()
    # Connect SCA chip
    sca_dev.send_connect()

    sca_dev.read_sca_id()

    # Enable GPIO
    sca_dev.enable_chn(sca_defs.SCA_CH_GPIO, True)

    # GPIO Direction Set
    sca_dev.set_direction(0xffffffff)

    # GPIO Direction READ
    print("Direction = "), hex(sca_dev.get_direction())

    sca_dev.test_gpio(0x00000000)
    sca_dev.test_gpio(0xffffffff)

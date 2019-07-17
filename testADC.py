#!/usr/bin/env python
import time
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
        log.debug("Usage:  ./readScaId.py board_num link_num")
        sys.exit(1)

    sca_dev = Gdpb(afck_num, link)

    # Reset Chip
    sca_dev.send_reset()
    # Connect SCA chip
    sca_dev.send_connect()

    # Enable ADC channel
    sca_dev.enable_chn(SCA_CH_ADC, True)

    # sca_dev.w_gain(2125)

    PREFIX = "labtest:Gdpb:%d:SCA:%d:" % (afck_num, link)
    while True:
        # read adc channels for 0 31
        for i in range(32):
            sca_dev.w_sel(i)
            sca_dev.start_conv()
            time.sleep(0.001)
            adc_value = sca_dev.r_data()
            adc_ofs = sca_dev.r_ofs()
            adc_raw = sca_dev.r_raw()
            adc_gain = sca_dev.r_gain()
            ch_name = PREFIX + "ADC:CH:" + str(i)
            if i == 31:
                # not vert accurate number to caluate the internal temprature, the manual doesn't give a formular.
                internal_temp = float(720 - adc_raw) / 5
                log.debug("ADC Ch %d = %d \t Temp = %f" % (31, adc_value, internal_temp))
                ca_ch = pvaccess.Channel(ch_name)
                ca_ch.putDouble(internal_temp)
            else:
                # read internal tenperature sensor
                volt_value = 1000*float(adc_value * SCA_ADC_VREF) / (2 ** 12)
                log.debug("ADC Ch %d =  %d \t Volt = %f mV \t RAW = %d \t OFS = %d \t Gain = %d" % (i, adc_value, volt_value, adc_raw, adc_ofs, adc_gain))
                ca_ch = pvaccess.Channel(ch_name)
                ca_ch.putDouble(volt_value)
        
        time.sleep(1)

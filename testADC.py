#!/usr/bin/env python
import pvaccess
import time

from lib.gdpb import Gdpb
from lib.sca_defs import *


class TestADC(Gdpb):
    def __init__(self):
        Gdpb.__init__(self)
        self.adc_dev = self.sca_modules[0].adc


# ioc channels' prefix
PREFIX = "labtest:SCA:0:"

if __name__ == '__main__':
    SCA_ADC_VREF = 1.5

    test_adc = TestADC()
    sca_dev = test_adc.sca_modules[0].adc

    # Reset Chip
    sca_dev.send_reset()
    # Connect SCA chip
    sca_dev.send_connect()

    # Enable ADC channel
    sca_dev.enable_chn(SCA_CH_ADC, True)

    while True:
        # read adc channels for 0 31
        for i in range(32):
            sca_dev.w_sel(i)
            sca_dev.start_conv()
            time.sleep(0.001)
            adc_value = sca_dev.r_data()
            ch_name = PREFIX + "ADC:CH:" + str(i)
            if i == 31:
                # not vert accurate number to caluate the internal temprature, the manual doesn't give a formular.
                internal_temp = float(720 - adc_value) / 5
                # print("ADC Ch %d = %#x \t Temp = %f" % (31, adc_value, internal_temp))
                ca_ch = pvaccess.Channel(ch_name)
                ca_ch.putDouble(internal_temp)
            else:
                # read internal tenperature sensor
                volt_value = float(adc_value * SCA_ADC_VREF) / (2 ** 12)
                # print("ADC Ch %d =  %#x \t Volt = %f" % (i, adc_value, volt_value))
                ca_ch = pvaccess.Channel(ch_name)
                ca_ch.putDouble(volt_value)


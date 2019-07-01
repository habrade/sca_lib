#!/usr/bin/env python
import subprocess

import pvaccess

from lib.gdpb import Gdpb
from lib.sca_defs import *


class TestADC(Gdpb):
    def __init__(self):
        Gdpb.__init__(self)
        self.adc_dev = self.sca_modules[0].adc


# ioc channels' prefix
PREFIX = "labtest:SCA:0:"

if __name__ == '__main__':

    # run softIocPVA
    subprocess.Popen(["./runIoc.sh"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

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
        for i in range(31):
            sca_dev.w_sel(i)
            sca_dev.start_conv()
            adc_value = sca_dev.r_data()
            volt_value = float(adc_value * SCA_ADC_VREF) / (2 ** 12)
            print("ADC Ch %d =  %#x \t Volt = %f" % (i, adc_value, volt_value))
            ch_name = PREFIX + "ADC:CH:" + str(i)
            ca_ch = pvaccess.Channel(ch_name)
            ca_ch.putDouble(volt_value)

        # read internal tenperature sensor
        sca_dev.w_sel(31)
        sca_dev.start_conv()
        adc_value = sca_dev.r_data()
        internal_temp = float(720 - adc_value) / 5
        print("ADC Ch %d = %#x \t Temp = %f" % (31, adc_value, internal_temp))
        ch_name = PREFIX + "ADC:CH:" + str(31)
        ca_ch = pvaccess.Channel(ch_name)
        # not vert accurate number to caluate the internal temprature, the manual doesn't give a formular.
        ca_ch.putDouble(internal_temp)

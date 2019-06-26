#!/usr/bin/env python
import sys
import time
import pvaccess

from lib.sca_defs import *
from lib import sca_adc

# ioc channels' prefix
PREFIX = "labtest:SCA:"
# ADC channels' name
ca_adc_vref = pvaccess.Channel(PREFIX + "ADC:VREF")

if __name__ == '__main__':

    sca_dev = sca_adc.ScaAdc()

    # Reset Chip
    sca_dev.send_reset()
    # Connect SCA chip
    sca_dev.send_connect()

    # Enable ADC channel
    sca_dev.enable_chn(SCA_CH_ADC, True)

    while True:
        vref = ca_adc_vref.get().getDouble()
        print("vref: %f" % vref)
        # read adc channels for 0 31
        for i in range(31):
            sca_dev.w_sel(i)
            sca_dev.start_conv()
            adc_value = sca_dev.r_data()
            volt_value = float(adc_value*vref)/(2**12)
            print("ADC Ch %d =  %#x Volt = %f" % (i, adc_value, volt_value))
            ch_name = PREFIX + "ADC:CH:" + str(i)
            ca_ch = pvaccess.Channel(ch_name)
            ca_ch.putDouble(volt_value)

        # read internal tenperature sensor
        sca_dev.w_sel(31)
        sca_dev.start_conv()
        adc_value = sca_dev.r_data()
        internal_temp = float(-adc_value)/5
        # print("ADC Ch %d = %#x Temp = %f" % (31, adc_value, internal_temp))
        ch_name = PREFIX + "ADC:CH:" + str(31)
        ca_ch = pvaccess.Channel(ch_name)
        # not vert accurate number to caluate the internal temprature, the manual doesn't give a formular.
        ca_ch.putDouble(internal_temp)

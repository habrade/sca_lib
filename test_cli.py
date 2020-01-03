#!/usr/bin/env python2
import sys
import time

from lib.gdpb import Gdpb
from lib.sca_defs import *


class ScaAttribute():
    def __init__(self):
        self.id = None

        self.gpio_direc = None
        self.gpio_pin_in = None

        self.adc = []

        self.temperature = None
        self.hectopascals = None
        self.pressure = None


def main():
    if len(sys.argv) == 3:
        afck_num = int(sys.argv[1])
        link = int(sys.argv[2])
    else:
        print("Usage:  ./test_cli.py board_num link_num")
        sys.exit(1)

    test_gdpb = Gdpb(afck_num, link)

    # Reset SCA
    test_gdpb.scaModule.send_reset()
    # Connect SCA chip
    test_gdpb.scaModule.send_connect()

    # Enable ADC
    test_gdpb.scaModule.enable_chn(SCA_CH_ADC, True)
    # Enable GPIO
    test_gdpb.scaModule.enable_chn(SCA_CH_GPIO, True)
    # Enable I2c
    test_gdpb.scaModule.enable_chn(SCA_CH_I2C0, True)
    test_gdpb.scaModule.enable_chn(SCA_CH_I2C1, True)
    # Initial BME280
    test_gdpb.scaModule._initial_sensor()

    scaAttr = ScaAttribute()

    while True:
        # Read Chip ID
        scaAttr.id = test_gdpb.scaModule.read_sca_id()
        print("SCA ID = {0:#x}".format(scaAttr.id))

        # Read GPIO direction and pin in
        scaAttr.gpio_direc = test_gdpb.scaModule.get_direction()
        print("GPIO Direction = {0:#x}".format(scaAttr.gpio_direc))
        scaAttr.gpio_pin_in = test_gdpb.scaModule.read_pin_in()
        print("GPIO PIN IN = {0:#x}".format(scaAttr.gpio_pin_in))

        # READ ADCfor i in range(32):
        for i in range(32):
            test_gdpb.scaModule.w_sel(i)
            adc_value = test_gdpb.scaModule.start_conv()
            time.sleep(0.1)
            adc_ofs = test_gdpb.scaModule.r_ofs()
            adc_raw = test_gdpb.scaModule.r_raw()
            adc_gain = test_gdpb.scaModule.r_gain()
            volt_value = 1000 * float(adc_value * SCA_ADC_VREF) / (2 ** 12)
            if i == 31:
                # not vert accurate number to caluate the internal temprature, the manual doesn't give a formular.
                internal_temp = float(716 - volt_value) / 1.82
                print("ADC Ch {0:d} = {1:d} \t Temp = {2:.2f} deg C".format(31, adc_value, internal_temp))
            else:
                # read internal tenperature sensor
                print(
                    "ADC Ch {0:d} =  {1:d} \t Volt = {2:f} mV \t RAW = {3:d} \t OFS = {4:d} \t Gain = {5:d} \t".format(
                        i, adc_value, volt_value, adc_raw, adc_ofs, adc_gain))

        # BME280
        offset_t = -6.5
        factor_h = 2.173
        offset_h = 3.246
        do_cali = True
        if do_cali:
            scaAttr.temperature = test_gdpb.scaModule.read_temperature() + offset_t
            scaAttr.humidity = test_gdpb.scaModule.read_humidity() * factor_h + offset_h
        else:
            scaAttr.temperature = test_gdpb.scaModule.read_temperature()
            scaAttr.humidity = test_gdpb.scaModule.read_humidity()

        scaAttr.pressure = test_gdpb.scaModule.read_pressure() / 100
        print("BME280 Temperature = {0:.2f} deg C".format(scaAttr.temperature))
        print("BME280 Pressure = {0:.2f} hPa".format(scaAttr.pressure))
        print("BME280 Humidity = {0:.2f} %%".format(scaAttr.humidity))


if __name__ == "__main__":
    main()

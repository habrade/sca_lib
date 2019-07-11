#!/usr/bin/env python
import functools
import logging
import threading
import time

import pvaccess

from lib.gdpb import Gdpb
from lib.sca_defs import *

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)


class ScaSrv(Gdpb):
    def __init__(self, afck_num):
        super(ScaSrv, self).__init__(afck_num)

        self.__scaNum = 1

        self.ca_sca_id = []
        self.ca_gpio_direction_set_ch_31_16 = []
        self.ca_gpio_direction_get_ch_31_16 = []
        self.ca_gpio_pinout_set_ch_31_16 = []
        self.ca_gpio_pinout_get_ch_31_16 = []
        self.ca_gpio_pinin_get_ch_31_16 = []
        self.ca_gpio_direction_set_ch_15_0 = []
        self.ca_gpio_direction_get_ch_15_0 = []
        self.ca_gpio_pinout_set_ch_15_0 = []
        self.ca_gpio_pinout_get_ch_15_0 = []
        self.ca_gpio_pinin_get_ch_15_0 = []
        self.ca_bme280_degrees = []
        self.ca_bme280_hectopascals = []
        self.ca_bme280_humidity = []
        self.ca_adc_channels = []

        self.create_pv_channels()
        self.read_sca_modules_ids()
        self.create_threads()

    def read_sca_modules_ids(self):
        for index in range(self.__scaNum):
            # Initial SCA chip
            sca_dev = self.gdpb.sca_modules[index].sca_asic
            # Reset Chip
            sca_dev.send_reset()
            # Connect SCA chip
            sca_dev.send_connect()
            # read SCA ID
            sca_dev.enable_chn(SCA_CH_ADC, True)
            sca_id = sca_dev.read_sca_id()
            # put to epics channel
            self.ca_sca_id[index].putInt(sca_id)
            del sca_dev

    def create_pv_channels(self):
        for index in range(self.__scaNum):
            # ioc channels' prefix
            self.__PREFIX = "labtest:SCA:%d:" % index
            # SCA ID channel's name
            self.ca_sca_id.append(pvaccess.Channel(self.__PREFIX + "ID"))
            # GPIO channels' name
            self.ca_gpio_direction_set_ch_31_16.append(pvaccess.Channel(self.__PREFIX + "GPIO:CH_31_16:DIRECTION:SET"))
            self.ca_gpio_direction_get_ch_31_16.append(pvaccess.Channel(self.__PREFIX + "GPIO:CH_31_16:DIRECTION:GET"))
            self.ca_gpio_pinout_set_ch_31_16.append(pvaccess.Channel(self.__PREFIX + "GPIO:CH_31_16:PINOUT:SET"))
            self.ca_gpio_pinout_get_ch_31_16.append(pvaccess.Channel(self.__PREFIX + "GPIO:CH_31_16:PINOUT:GET"))
            self.ca_gpio_pinin_get_ch_31_16.append(pvaccess.Channel(self.__PREFIX + "GPIO:CH_31_16:PININ:GET"))
            self.ca_gpio_direction_set_ch_15_0.append(pvaccess.Channel(self.__PREFIX + "GPIO:CH_15_0:DIRECTION:SET"))
            self.ca_gpio_direction_get_ch_15_0.append(pvaccess.Channel(self.__PREFIX + "GPIO:CH_15_0:DIRECTION:GET"))
            self.ca_gpio_pinout_set_ch_15_0.append(pvaccess.Channel(self.__PREFIX + "GPIO:CH_15_0:PINOUT:SET"))
            self.ca_gpio_pinout_get_ch_15_0.append(pvaccess.Channel(self.__PREFIX + "GPIO:CH_15_0:PINOUT:GET"))
            self.ca_gpio_pinin_get_ch_15_0.append(pvaccess.Channel(self.__PREFIX + "GPIO:CH_15_0:PININ:GET"))
            # BME280 channels' name
            self.ca_bme280_degrees.append(pvaccess.Channel(self.__PREFIX + "BME280:Temperature"))
            self.ca_bme280_hectopascals.append(pvaccess.Channel(self.__PREFIX + "BME280:Pressure"))
            self.ca_bme280_humidity.append(pvaccess.Channel(self.__PREFIX + "BME280:Humidity"))

            for ch_index in range(32):
                self.ca_adc_channels.append(pvaccess.Channel(self.__PREFIX + "ADC:CH:" + str(ch_index)))

    def create_threads(self):
        for sca_index in range(self.__scaNum):
            num_threads = 2
            threads = []
            for index_t in range(num_threads):
                if index_t == 0:
                    thread_function = functools.partial(self.GPIO_thread_func, sca_index)
                elif index_t == 1:
                    thread_function = functools.partial(self.ADC_thread_func, sca_index)
                elif index_t == 2:
                    thread_function = functools.partial(self.BME280_thread_func, sca_index)

                t = threading.Thread(target=thread_function, args=())
                t.daemon = True
                threads.append(t)

            for thread in threads:
                thread.start()
            for thread in threads:
                thread.join()

    def GPIO_thread_func(self, sca_index):
        sca_dev = self.gdpb.sca_modules[sca_index].gpio
        sca_dev.enable_chn(SCA_CH_GPIO, True)
        while True:
            # GPIO Direction Set
            direction_set_1 = self.ca_gpio_direction_set_ch_31_16[sca_index].get().getInt()
            direction_set_2 = self.ca_gpio_direction_set_ch_15_0[sca_index].get().getInt()
            direction_set = (direction_set_1 << 16) + direction_set_2
            log.debug("GPIO Direction Set to %#x" % direction_set)
            sca_dev.set_direction(direction_set)
            time.sleep(0.01)
            # GPIO Direction Get
            direction_get = sca_dev.get_direction()
            log.debug("GPIO Direction Get =  %#x" % direction_get)
            self.ca_gpio_direction_get_ch_31_16[sca_index].putUShort(direction_get >> 16)
            self.ca_gpio_direction_get_ch_15_0[sca_index].putUShort(direction_get & 0xFFFF)
            time.sleep(0.01)
            # GPIO PinOut Set
            pinout_set_1 = self.ca_gpio_pinout_set_ch_31_16[sca_index].get().getInt()
            pinout_set_2 = self.ca_gpio_pinout_set_ch_15_0[sca_index].get().getInt()
            pinout_set = (pinout_set_1 << 16) + pinout_set_2
            log.debug("GPIO PINOUT Set to %#x" % pinout_set)
            sca_dev.write_pin_out(pinout_set)
            time.sleep(0.01)
            # GPIO PinOut Get
            pinout_get = sca_dev.read_pin_out()
            log.debug("GPIO PINOUT Get =  %#x" % pinout_get)
            self.ca_gpio_pinout_get_ch_31_16[sca_index].putUShort(pinout_get >> 16)
            self.ca_gpio_pinout_get_ch_15_0[sca_index].putUShort(pinout_get & 0xFFFF)
            time.sleep(0.01)
            # GPIO PinIn Get
            pinin_get = sca_dev.read_pin_in()
            log.debug("GPIO PININ Get =  %#x" % pinin_get)
            self.ca_gpio_pinin_get_ch_31_16[sca_index].putUShort(pinin_get >> 16)
            self.ca_gpio_pinin_get_ch_15_0[sca_index].putUShort(pinin_get & 0xFFFF)

    def ADC_thread_func(self, sca_index):
        sca_dev = self.gdpb.sca_modules[sca_index].adc
        sca_dev.enable_chn(SCA_CH_ADC, True)
        while True:
            # read adc channels for 0 32
            for i in range(32):
                sca_dev.w_sel(i)
                sca_dev.start_conv()
                time.sleep(0.01)
                adc_value = sca_dev.r_data()
                # read internal tenperature sensor
                if i == 31:
                    internal_temp = (725 - adc_value) / 2
                    log.debug("ADC Ch %d = %#x Temp = %f" % (i, adc_value, internal_temp))
                    # not vert accurate number to caluate the internal temprature, the manual doesn't give a formular.
                    self.ca_adc_channels[i].putDouble(internal_temp)
                else:
                    volt_value = float(adc_value * SCA_ADC_VREF) / (2 ** 12)
                    log.debug("ADC Ch %d =  %#x Volt = %f" % (i, adc_value, volt_value))
                    self.ca_adc_channels[i].putDouble(volt_value)

    def BME280_thread_func(self, sca_index):
        sensor = self.gdpb.sca_modules[sca_index].bme280
        # Enable I2C ch. 0
        sensor.enable_chn(SCA_CH_I2C0, True)
        sensor.set_frq(SCA_I2C_SPEED_100)
        sensor.set_mode(SCA_I2C_MODE_OPEN_DRAIN)
        # reset bme280
        sensor.rst_dev()
        # check BME280 ID
        if sensor.read_id() != 0x60:
            log.error("BME280's ID is not right, should be 0x60 after reset")
        while True:
            degrees = sensor.read_temperature()
            pascals = sensor.read_pressure()
            hectopascals = pascals / 100
            humidity = sensor.read_humidity()
            # Data put to epics channel
            self.ca_bme280_degrees[sca_index].putDouble(degrees)
            self.ca_bme280_hectopascals[sca_index].putDouble(hectopascals)
            self.ca_bme280_humidity[sca_index].putDouble(humidity)
            log.debug("Temp = %f deg C" % degrees)
            log.debug("Pressure = %f hPa" % hectopascals)
            log.debug("Humidity = %f %%" % humidity)


if __name__ == '__main__':
    scaSrv = ScaSrv(66)

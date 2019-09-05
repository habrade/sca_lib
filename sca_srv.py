#!/usr/bin/env python
import logging
import threading
import time
import sys

import pvaccess

from lib.gdpb import Gdpb
from lib.sca_defs import *

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

__author__ = "Sheng Dong"
__email__ = "habrade@gmail.com"


class ScaSrv(Gdpb):
    def __init__(self, afck_num, link):
        super(ScaSrv, self).__init__(afck_num, link)

        self.__afck_num = afck_num
        self.__link = link

        # Reset SCA
        self.send_reset()
        # Connect SCA chip
        self.send_connect()
        # Enable ADC
        self.enable_chn(SCA_CH_ADC, True)
        # Enable GPIO
        self.enable_chn(SCA_CH_GPIO, True)
        # Initial BME280
        self.enable_chn(SCA_CH_I2C0, True)
        self.enable_chn(SCA_CH_I2C1, True)
        self._initial_sensor()

        self.__PREFIX = "labtest:Gdpb:%d:SCA:%d:" % (self.__afck_num, self.__link)

        self.ca_sca_id = pvaccess.Channel(self.__PREFIX + "ID")
        self.ca_gpio_direction_set_ch_31_16 = pvaccess.Channel(self.__PREFIX + "GPIO:CH_31_16:DIRECTION:SET")
        self.ca_gpio_direction_get_ch_31_16 = pvaccess.Channel(self.__PREFIX + "GPIO:CH_31_16:DIRECTION:GET")
        self.ca_gpio_pinout_set_ch_31_16 = pvaccess.Channel(self.__PREFIX + "GPIO:CH_31_16:PINOUT:SET")
        self.ca_gpio_pinout_get_ch_31_16 = pvaccess.Channel(self.__PREFIX + "GPIO:CH_31_16:PINOUT:GET")
        self.ca_gpio_pinin_get_ch_31_16 = pvaccess.Channel(self.__PREFIX + "GPIO:CH_31_16:PININ:GET")
        self.ca_gpio_direction_set_ch_15_0 = pvaccess.Channel(self.__PREFIX + "GPIO:CH_15_0:DIRECTION:SET")
        self.ca_gpio_direction_get_ch_15_0 = pvaccess.Channel(self.__PREFIX + "GPIO:CH_15_0:DIRECTION:GET")
        self.ca_gpio_pinout_set_ch_15_0 = pvaccess.Channel(self.__PREFIX + "GPIO:CH_15_0:PINOUT:SET")
        self.ca_gpio_pinout_get_ch_15_0 = pvaccess.Channel(self.__PREFIX + "GPIO:CH_15_0:PINOUT:GET")
        self.ca_gpio_pinin_get_ch_15_0 = pvaccess.Channel(self.__PREFIX + "GPIO:CH_15_0:PININ:GET")
        self.ca_bme280_degrees = pvaccess.Channel(self.__PREFIX + "BME280:Temperature")
        self.ca_bme280_hectopascals = pvaccess.Channel(self.__PREFIX + "BME280:Pressure")
        self.ca_bme280_humidity = pvaccess.Channel(self.__PREFIX + "BME280:Humidity")
        self.ca_adc_channels = []
        for ch_index in range(32):
            self.ca_adc_channels.append(pvaccess.Channel(self.__PREFIX + "ADC:CH:" + str(ch_index)))

        # self.create_threads()

    def read_sca_modules_ids(self):
        sca_id = self.read_sca_id()
        log.debug("SCA ID: {0:#x}".format(sca_id))
        # put to epics channel
        self.ca_sca_id.putInt(sca_id)

    def create_threads(self):
        num_threads = 3
        threads = []
        for index_t in range(num_threads):
            if index_t == 0:
                thread_function = self.gpio_thread_func
            elif index_t == 1:
                thread_function = self.adc_thread_func
            elif index_t == 2:
                thread_function = self.bme280_thread_func

            t = threading.Thread(target=thread_function, args=())
            t.daemon = True
            threads.append(t)

        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()

    def gpio_thread_func(self):
        # GPIO Direction Set
        direction_set_1 = self.ca_gpio_direction_set_ch_31_16.get().getInt()
        direction_set_2 = self.ca_gpio_direction_set_ch_15_0.get().getInt()
        direction_set = (direction_set_1 << 16) + direction_set_2
        log.debug("GPIO Direction Set to %#x" % direction_set)
        self.set_direction(direction_set)
        time.sleep(0.01)
        # GPIO Direction Get
        direction_get = self.get_direction()
        log.debug("GPIO Direction Get =  %#x" % direction_get)
        self.ca_gpio_direction_get_ch_31_16.putUShort(direction_get >> 16)
        self.ca_gpio_direction_get_ch_15_0.putUShort(direction_get & 0xFFFF)
        time.sleep(0.01)
        # GPIO PinOut Set
        pinout_set_1 = self.ca_gpio_pinout_set_ch_31_16.get().getInt()
        pinout_set_2 = self.ca_gpio_pinout_set_ch_15_0.get().getInt()
        pinout_set = (pinout_set_1 << 16) + pinout_set_2
        log.debug("GPIO PINOUT Set to %#x" % pinout_set)
        self.write_pin_out(pinout_set)
        time.sleep(0.01)
        # GPIO PinOut Get
        pinout_get = self.read_pin_out()
        log.debug("GPIO PINOUT Get =  %#x" % pinout_get)
        self.ca_gpio_pinout_get_ch_31_16.putUShort(pinout_get >> 16)
        self.ca_gpio_pinout_get_ch_15_0.putUShort(pinout_get & 0xFFFF)
        time.sleep(0.01)
        # GPIO PinIn Get
        pinin_get = self.read_pin_in()
        log.debug("GPIO PININ Get =  %#x" % pinin_get)
        self.ca_gpio_pinin_get_ch_31_16.putUShort(pinin_get >> 16)
        self.ca_gpio_pinin_get_ch_15_0.putUShort(pinin_get & 0xFFFF)

    def adc_thread_func(self):
        # read adc channels for 0 32
        for i in range(32):
            self.w_sel(i)
            adc_value = self.start_conv()
            volt_value = float(1000 * adc_value * SCA_ADC_VREF) / (2 ** 12 - 1)
            # The maximum conversation rate is 3.5KHz(2.857ms)
            time.sleep(5 / 1000)
            # read internal tenperature sensor
            if i == 31:
                internal_temp = (716 - volt_value) / 1.82
                log.debug("ADC Ch %d \t Temp = %.2f deg C" % (i, internal_temp))
                # not vert accurate number to caluate the internal temprature, the manual doesn't give a formular.
                self.ca_adc_channels[i].putDouble(internal_temp)
            elif i == 9:
                log.debug("ADC Ch %d \t Volt = %.2f mV" % (i, volt_value))
                # put the real value which should be displayed, because of the ADC input limitation(1V)
                self.ca_adc_channels[i].putDouble(volt_value / 10)
            elif 1 <= i <= 8:
                log.debug("ADC Ch %d \t Volt = %.2f mV" % (i, volt_value))
                # put the real value which should be displayed, because of the ADC input limitation(1V)
                self.ca_adc_channels[i].putDouble(volt_value / 100)
            else:
                log.debug("ADC Ch %d \t Volt = %.2f mV" % (i, volt_value))
                # put the real value which should be displayed, because of the ADC input limitation(1V)
                self.ca_adc_channels[i].putDouble(volt_value)

    def bme280_thread_func(self):
        offset_t = -4.5
        factor_h = 2.173
        offset_h = 3.246
        degrees = self.read_temperature() + offset_t
        # degrees = self.read_temperature()
        pascals = self.read_pressure()
        hectopascals = pascals / 100
        humidity = self.read_humidity() * factor_h + offset_h
        # humidity = self.read_humidity()
        # Data put to epics channel
        self.ca_bme280_degrees.putDouble(degrees)
        self.ca_bme280_hectopascals.putDouble(hectopascals)
        self.ca_bme280_humidity.putDouble(humidity)
        log.debug("Temp = %.2f deg C" % degrees)
        log.debug("Pressure = %.2f hPa" % hectopascals)
        log.debug("Humidity = %.2f %%" % humidity)


if __name__ == '__main__':
    afck_num_lists = [67]
    links_per_gdpb = 2
    scaSrv_lists = []

    for afck_num in afck_num_lists:
        for link in range(links_per_gdpb):
            scaSrv_lists.append(ScaSrv(afck_num, link))
            scaSrv_lists[link].read_sca_modules_ids()

    while True:
        for scaSrv in scaSrv_lists:
            scaSrv.gpio_thread_func()
            scaSrv.adc_thread_func()
            # time.sleep(1)
            scaSrv.bme280_thread_func()

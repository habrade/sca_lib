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
        # Enable I2C ch. 0
        self.enable_chn(SCA_CH_I2C0, True)
        self.set_frq(SCA_I2C_SPEED_1000)
        self.set_mode(SCA_I2C_MODE_OPEN_DRAIN)

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

        self.read_sca_modules_ids()
        # self.create_threads()

    def read_sca_modules_ids(self):
        # read SCA ID
        self.enable_chn(SCA_CH_ADC, True)
        sca_id = self.read_sca_id()
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
        # while True:
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
        # while True:
        # read adc channels for 0 32
        for i in range(32):
            self.w_sel(i)
            adc_value = self.start_conv()
            volt_value = float(1000 * adc_value * SCA_ADC_VREF) / (2 ** 12 - 1)
            time.sleep(0.001)
            # read internal tenperature sensor
            if i == 31:
                internal_temp = (716 - volt_value) / 1.82
                log.debug("adc ch %d = %#x temp = %.2f deg C" % (i, adc_value, internal_temp))
                # not vert accurate number to caluate the internal temprature, the manual doesn't give a formular.
                self.ca_adc_channels[i].putDouble(internal_temp)
            else:
                log.debug("ADC Ch %d =  %#x Volt = %.2f mV" % (i, adc_value, volt_value))
                self.ca_adc_channels[i].putDouble(volt_value)

    def bme280_thread_func(self):
        # while True
        # time.sleep(1)
        offset_t = -6.5
        factor_h = 1
        offset_h = 0
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
    if len(sys.argv) == 3:
        afck_num = int(sys.argv[1])
        link = int(sys.argv[2])
    else:
        print("Usage:  ./readScaId.py board_num link_num")
        sys.exit(1)

    scaSrv = ScaSrv(afck_num, link)
    while True:
        # scaSrv.gpio_thread_func()
        # scaSrv.adc_thread_func()
        scaSrv.bme280_thread_func()

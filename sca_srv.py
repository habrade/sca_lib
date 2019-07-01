#!/usr/bin/env python
import logging
import threading
import functools

import pvaccess

from lib.gdpb import Gdpb
from lib.sca_defs import *

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


class ScaSrv():
    def __init__(self, scaNum=1):
        # run softIocPVA
        # subprocess.Popen(["./runIoc.sh"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

        self.__scaNum = scaNum
        self.gdpb = Gdpb(self.__scaNum)
        self.__SCA_ADC_VREF = 1.5

        self.ca_sca_id = []
        self.ca_gpio_direction_set_1_half = []
        self.ca_gpio_direction_get_1_half = []
        self.ca_gpio_pinout_set_1_half = []
        self.ca_gpio_pinout_get_1_half = []
        self.ca_gpio_pinin_get_1_half = []
        self.ca_gpio_direction_set_2_half = []
        self.ca_gpio_direction_get_2_half = []
        self.ca_gpio_pinout_set_2_half = []
        self.ca_gpio_pinout_get_2_half = []
        self.ca_gpio_pinin_get_2_half = []
        self.ca_bme280_degrees = []
        self.ca_bme280_hectopascals = []
        self.ca_bme280_humidity = []

        for index in range(self.__scaNum):
            # ioc channels' prefix
            self.__PREFIX = "labtest:SCA:%d:" % index
            # SCA ID channel's name
            self.ca_sca_id.append(pvaccess.Channel(self.__PREFIX + "ID"))
            # GPIO channels' name
            self.ca_gpio_direction_set_1_half.append(pvaccess.Channel(self.__PREFIX + "GPIO:CH_31_16:DIRECTION:SET"))
            self.ca_gpio_direction_get_1_half.append(pvaccess.Channel(self.__PREFIX + "GPIO:CH_31_16:DIRECTION:GET"))
            self.ca_gpio_pinout_set_1_half.append(pvaccess.Channel(self.__PREFIX + "GPIO:CH_31_16:PINOUT:SET"))
            self.ca_gpio_pinout_get_1_half.append(pvaccess.Channel(self.__PREFIX + "GPIO:CH_31_16:PINOUT:GET"))
            self.ca_gpio_pinin_get_1_half.append(pvaccess.Channel(self.__PREFIX + "GPIO:CH_31_16:PININ:GET"))
            self.ca_gpio_direction_set_2_half.append(pvaccess.Channel(self.__PREFIX + "GPIO:CH_15_0:DIRECTION:SET"))
            self.ca_gpio_direction_get_2_half.append(pvaccess.Channel(self.__PREFIX + "GPIO:CH_15_0:DIRECTION:GET"))
            self.ca_gpio_pinout_set_2_half.append(pvaccess.Channel(self.__PREFIX + "GPIO:CH_15_0:PINOUT:SET"))
            self.ca_gpio_pinout_get_2_half.append(pvaccess.Channel(self.__PREFIX + "GPIO:CH_15_0:PINOUT:GET"))
            self.ca_gpio_pinin_get_2_half.append(pvaccess.Channel(self.__PREFIX + "GPIO:CH_15_0:PININ:GET"))
            # BME280 channels' name
            self.ca_bme280_degrees.append(pvaccess.Channel(self.__PREFIX + "BME280:Temperature"))
            self.ca_bme280_hectopascals.append(pvaccess.Channel(self.__PREFIX + "BME280:Pressure"))
            self.ca_bme280_humidity.append(pvaccess.Channel(self.__PREFIX + "BME280:Humidity"))

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

            num_threads = 2
            threads = []
            for index_t in range(num_threads):
                if index_t == 0:
                    thread_function = functools.partial(self.GPIO_thread_func, index)
                elif index_t == 1:
                    thread_function = functools.partial(self.ADC_thread_func, index)
                elif index_t == 2:
                    thread_function = functools.partial(self.BME280_thread_func, index)

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
            direction_set_1 = self.ca_gpio_direction_set_1_half[sca_index].get().getInt()
            direction_set_2 = self.ca_gpio_direction_set_2_half[sca_index].get().getInt()
            direction_set = (direction_set_1 << 16) + direction_set_2
            log.debug("GPIO Direction Set to %#x" % direction_set)
            sca_dev.set_direction(direction_set)

            # GPIO Direction Get
            direction_get = sca_dev.get_direction()
            log.debug("GPIO Direction Get =  %#x" % direction_get)
            self.ca_gpio_direction_get_1_half[sca_index].putInt(direction_get >> 16)
            self.ca_gpio_direction_get_2_half[sca_index].putInt(direction_get & 0xFF)

            # GPIO PinOut Set
            pinout_set_1 = self.ca_gpio_pinout_set_1_half[sca_index].get().getInt()
            pinout_set_2 = self.ca_gpio_pinout_set_2_half[sca_index].get().getInt()
            pinout_set = (pinout_set_1 << 16) + pinout_set_2
            log.debug("GPIO PINOUT Set to %#x" % pinout_set)
            sca_dev.write_pin_out(pinout_set)

            # GPIO PinOut Get
            pinout_get = sca_dev.read_pin_out()
            log.debug("GPIO PINOUT Get =  %#x" % pinout_get)
            self.ca_gpio_pinout_get_1_half[sca_index].putInt(pinout_get >> 16)
            self.ca_gpio_pinout_get_2_half[sca_index].putInt(pinout_get & 0xFF)

            # GPIO PinIn Get
            pinin_get = sca_dev.read_pin_in()
            log.debug("GPIO PININ Get =  %#x" % pinin_get)
            self.ca_gpio_pinin_get_1_half[sca_index].putInt(pinin_get >> 16)
            self.ca_gpio_pinin_get_2_half[sca_index].putInt(pinin_get & 0xFF)
        del sca_dev

    def ADC_thread_func(self, sca_index):
        sca_dev = self.gdpb.sca_modules[sca_index].adc
        sca_dev.enable_chn(SCA_CH_ADC, True)
        while True:
            # vref = ca_adc_vref.get().getDouble()
            # read adc channels for 0 31
            for i in range(31):
                sca_dev.w_sel(i)
                sca_dev.start_conv()
                adc_value = sca_dev.r_data()
                volt_value = float(adc_value * self.__SCA_ADC_VREF) / (2 ** 12)
                log.debug("ADC Ch %d =  %#x Volt = %f" %
                          (i, adc_value, volt_value))

                ch_name = self.__PREFIX + "ADC:CH:" + str(i)
                ca_ch = pvaccess.Channel(ch_name)
                ca_ch.putDouble(volt_value)
            # read internal tenperature sensor
            sca_dev.w_sel(31)
            sca_dev.start_conv()
            adc_value = sca_dev.r_data()
            internal_temp = (725 - adc_value) / 2
            log.debug("ADC Ch %d = %#x Temp = %f" % (31, adc_value, internal_temp))
            ch_name = self.__PREFIX + "ADC:CH:" + str(31)
            ca_ch = pvaccess.Channel(ch_name)
            # not vert accurate number to caluate the internal temprature, the manual doesn't give a formular.
            ca_ch.putDouble(internal_temp)
        del sca_dev

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
        del sensor


if __name__ == '__main__':
    scaSrv = ScaSrv(1)

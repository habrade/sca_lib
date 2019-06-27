#!/usr/bin/env python
import logging
import threading

import pvaccess

from lib import bme280
from lib import sca
from lib import sca_adc
from lib import sca_gpio
from lib.bme280_defs import *
from lib.sca_defs import *

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


class ScaSrv():
    def __init__(self, scaNum):

        self.__SCA_ADC_VREF = 1.5

        # ioc channels' prefix
        self.__PREFIX = "labtest:SCA:" + scaNum + ":"
        # SCA ID channel's name
        self.ca_sca_id = pvaccess.Channel(self.__PREFIX + "ID")
        # GPIO channels' name
        self.ca_gpio_direction_set = pvaccess.Channel(self.__PREFIX + "GPIO:DIRECTION:SET")
        self.ca_gpio_direction_get = pvaccess.Channel(self.__PREFIX + "GPIO:DIRECTION:GET")
        self.ca_gpio_pinout_set = pvaccess.Channel(self.__PREFIX + "GPIO:PINOUT:SET")
        self.ca_gpio_pinout_get = pvaccess.Channel(self.__PREFIX + "GPIO:PINOUT:GET")
        self.ca_gpio_pinin_get = pvaccess.Channel(self.__PREFIX + "GPIO:PININ:GET")
        # BME280 channels' name
        self.ca_bme280_degrees = pvaccess.Channel(self.__PREFIX + "BME280:Temperature")
        self.ca_bme280_hectopascals = pvaccess.Channel(self.__PREFIX + "BME280:Pressure")
        self.ca_bme280_humidity = pvaccess.Channel(self.__PREFIX + "BME280:Humidity")
        # ADC channels' name
        self.ca_adc_vref = pvaccess.Channel(self.__PREFIX + "ADC:VREF")

        # Initial SCA chip
        sca_dev = sca.Sca()
        # Reset Chip
        sca_dev.send_reset()
        # Connect SCA chip
        sca_dev.send_connect()

        threads = []
        for index in range(3):
            if index == 0:
                thread_function = self.readID_thread_func
            elif index == 1:
                thread_function = self.GPIO_thread_func
            elif index == 2:
                thread_function = self.ADC_thread_func
            elif index == 3:
                thread_function = self.BME280_thread_func

            t = threading.Thread(target=thread_function, args=())
            t.daemon = True
            threads.append(t)

        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()

    def readID_thread_func(self):
        sca_dev = sca.Sca()
        sca_dev.enable_chn(SCA_CH_ADC, True)
        while True:
            # read SCA ID
            sca_id = sca_dev.read_sca_id()
            # put to epics channel
            self.ca_sca_id.putInt(int(sca_id))

    def GPIO_thread_func(self):
        sca_dev = sca_gpio.ScaGpio()
        sca_dev.enable_chn(SCA_CH_GPIO, True)
        while True:
            # GPIO Direction Set
            direction_set = int(self.ca_gpio_direction_set.get().getInt())
            log.debug("GPIO Direction Set to %#x" % direction_set)
            sca_dev.set_direction(direction_set)
            # GPIO Direction READ
            direction_get = sca_dev.get_direction()
            log.debug("GPIO Direction Get =  %#x" % direction_get)
            self.ca_gpio_direction_get.putInt(int(direction_get))
            # GPIO PinOut Set
            pinout_set = int(self.ca_gpio_pinout_set.get().getInt())
            log.debug("GPIO PINOUT Set to %#x" % pinout_set)
            sca_dev.write_pin_out(pinout_set)
            # GPIO PinOut READ
            pinout_get = sca_dev.read_pin_out()
            log.debug("GPIO PINOUT Get =  %#x" % pinout_get)
            self.ca_gpio_pinout_get.putInt(int(pinout_get))
            # GPIO PinIn READ
            pinin_get = sca_dev.read_pin_in()
            log.debug("GPIO PININ Get =  %#x" % pinin_get)
            self.ca_gpio_pinin_get.putInt(int(pinin_get))

    def ADC_thread_func(self):
        sca_dev = sca_adc.ScaAdc()
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

    def BME280_thread_func(self):
        sensor = bme280.BME280(t_mode=BME280_OSAMPLE_8, p_mode=BME280_OSAMPLE_8,
                               h_mode=BME280_OSAMPLE_8)
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
            self.ca_bme280_degrees.putDouble(degrees)
            self.ca_bme280_hectopascals.putDouble(hectopascals)
            self.ca_bme280_humidity.putDouble(humidity)

            log.debug("Temp = %f deg C" % degrees)
            log.debug("Pressure = %f hPa" % hectopascals)
            log.debug("Humidity = %f %%" % humidity)


if __name__ == '__main__':
    scaSrv = ScaSrv(0)

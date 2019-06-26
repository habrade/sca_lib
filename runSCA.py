#!/usr/bin/env python
import sys
import time
import pvaccess
import logging
import threading

from lib import sca
from lib import sca_gpio
from lib import sca_adc
from lib import bme280

from lib.sca_defs import *
from lib.bme280_defs import *

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


# ioc channels' prefix
PREFIX = "labtest:SCA:"
# SCA ID channel's name
ca_sca_id = pvaccess.Channel(PREFIX + "ID")
# GPIO channels' name
ca_gpio_direction_set = pvaccess.Channel(PREFIX + "GPIO:DIRECTION:SET")
ca_gpio_direction_get = pvaccess.Channel(PREFIX + "GPIO:DIRECTION:GET")
ca_gpio_pinout_set = pvaccess.Channel(PREFIX + "GPIO:PINOUT:SET")
ca_gpio_pinout_get = pvaccess.Channel(PREFIX + "GPIO:PINOUT:GET")
ca_gpio_pinin_get = pvaccess.Channel(PREFIX + "GPIO:PININ:GET")
# BME280 channels' name
ca_bme280_degrees = pvaccess.Channel(PREFIX + "BME280:Temperature")
ca_bme280_hectopascals = pvaccess.Channel(PREFIX + "BME280:Pressure")
ca_bme280_humidity = pvaccess.Channel(PREFIX + "BME280:Humidity")
# ADC channels' name
ca_adc_vref = pvaccess.Channel(PREFIX + "ADC:VREF")


def readID_thread_func():
    sca_dev = sca.Sca()
    sca_dev.enable_chn(SCA_CH_ADC, True)
    while True:
        # read SCA ID
        sca_id = sca_dev.read_sca_id()
        log.info("SCA ID = %x" % sca_id)

        # put to epics channel
        ca_sca_id.put(int(sca_id))

        time.sleep(2)


def GPIO_thread_func():
    sca_dev = sca_gpio.ScaGpio()
    while True:
        # GPIO Direction Set
        direction_set = int(ca_gpio_direction_set.get().getDouble())
        log.debug("GPIO Direction Set to %x" % direction_set)
        sca_dev.set_direction(direction_set)

        # GPIO Direction READ
        direction_get = sca_dev.get_direction()
        log.debug("GPIO Direction Get =  %x" % direction_get)
        ca_gpio_direction_get.put(int(direction_get))

        # GPIO PinOut Set
        pinout_set = int(ca_gpio_pinout_set.get().getDouble())
        log.debug("GPIO PINOUT Set to %x" % pinout_set)
        sca_dev.write_pin_out(pinout_set)

        # GPIO PinOut READ
        pinout_get = sca_dev.read_pin_out()
        log.debug("GPIO PINOUT Get =  %x" % pinout_get)
        ca_gpio_pinout_get.put(int(pinout_get))

        # GPIO PinIn READ
        pinin_get = sca_dev.read_pin_in()
        log.debug("GPIO PININ Get =  %x" % pinin_get)
        ca_gpio_pinin_get.put(int(pinin_get))

        time.sleep(1)


def ADC_thread_func():
    sca_dev = sca_adc.ScaAdc()
    sca_dev.enable_chn(SCA_CH_ADC, True)
    while True:
        vref = ca_adc_vref.get().getDouble()
        # read adc channels for 0 31
        for i in range(31):
            sca_dev.w_sel(i)
            sca_dev.r_data()
            adc_value = sca_dev.start_conv()
            log.debug("ADC Ch %d = %x" % (i, adc_value))
            volt_value = adc_value*vref/(2**12)

            ch_name = PREFIX + "ADC:CH:" + str(i)
            ca_ch = pvaccess.Channel(ch_name)
            ca_ch.putDouble(volt_value)
            time.sleep(0.1)

        # read internal tenperature sensor
        sca_dev.w_sel(31)
        sca_dev.r_data()
        adc_value = sca_dev.start_conv()
        ch_name = PREFIX + "ADC:CH:" + str(31)
        ca_ch = pvaccess.Channel(ch_name)
        # not vert accurate number to caluate the internal temprature, the manual doesn't give a formular.
        internal_temp = (725-adc_value)/2
        ca_ch.putDouble(internal_temp)


def BME280_thread_func():
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
        ca_bme280_degrees.putDouble(degrees)
        ca_bme280_hectopascals.putDouble(hectopascals)
        ca_bme280_humidity.putDouble(humidity)

        log.debug("Temp = %f deg C" % degrees)
        log.debug("Pressure = %f hPa" % hectopascals)
        log.debug("Humidity = %f %%" % humidity)

        time.sleep(1)


if __name__ == '__main__':

    sca_dev = sca.Sca()

    # Reset Chip
    sca_dev.send_reset()
    # Connect SCA chip
    sca_dev.send_connect()

    threads = []
    for index in range(4):
        if index == 0:
            thread_function = readID_thread_func
        elif index == 1:
            thread_function = GPIO_thread_func
        elif index == 2:
            thread_function = ADC_thread_func
        elif index == 3:
            thread_function = BME280_thread_func

        t = threading.Thread(target=thread_function, args=())
        t.daemon = False
        threads.append(t)

    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()

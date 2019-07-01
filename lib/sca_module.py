from bme280 import BME280
from sca_adc import ScaAdc
from sca_gpio import ScaGpio


class ScaModule(object):
    def __init__(self, hw):
        self.sca_adc = ScaAdc(hw)
        self.sca_gpio = ScaGpio(hw)
        # self.bme280 = BME280(hw)

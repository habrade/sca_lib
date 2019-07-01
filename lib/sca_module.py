from bme280 import Bme280
from sca_adc import ScaAdc
from sca_gpio import ScaGpio
from sca import Sca


class ScaModule(object):
    def __init__(self, hw):
        self.sca_asic = Sca(hw)
        self.adc = ScaAdc(hw)
        self.gpio = ScaGpio(hw)
        # self.bme280 = Bme280(hw=hw)

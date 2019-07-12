from sca_adc import ScaAdc
from sca_gpio import ScaGpio
from bme280 import Bme280


class ScaModule(ScaAdc, ScaGpio, Bme280):
    def __init__(self, hw, link):
        super(ScaModule, self).__init__(hw, link)

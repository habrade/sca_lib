from sca_adc import ScaAdc
from sca_gpio import ScaGpio
from bme280 import Bme280


class ScaModule(ScaAdc, ScaGpio):
    def __init__(self, hw):
        super(ScaModule, self).__init__(hw)

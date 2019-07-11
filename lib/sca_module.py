from sca_adc import ScaAdc
from sca_gpio import ScaGpio


class ScaModule(ScaAdc, ScaGpio):
    def __init__(self, hw):
        super(ScaModule, self).__init__(hw)

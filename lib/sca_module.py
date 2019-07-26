import logging

from bme280 import Bme280
from sca_adc import ScaAdc
from sca_gpio import ScaGpio

logging.basicConfig(level=logging.INFO, format='%(asctime)s  %(name)s  %(levelname)s  %(message)s')
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

__author__ = "Sheng Dong"
__email__ = "habrade@gmail.com"

class ScaModule(ScaAdc, ScaGpio, Bme280):
    def __init__(self, hw, link):
        super(ScaModule, self).__init__(hw, link)

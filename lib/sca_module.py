import logging

from bme280 import Bme280
from sca_adc import ScaAdc
from sca_asic import ScaAsic
from sca_defs import *
from sca_gpio import ScaGpio
from sca_i2c import ScaI2c

logging.basicConfig(level=logging.INFO, format='%(asctime)s  %(name)s  %(levelname)s  %(message)s')
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

__author__ = "Sheng Dong"
__email__ = "s.dong@mails.ccnu.edu.cn"


class ScaModule(object):
    def __init__(self, hw, link):
        super(ScaModule, self).__init__(link)

        self.ScaAsic = ScaAsic(hw, link)

        self.ScaAdc = ScaAdc(self.ScaAsic)
        self.ScaGpio = ScaGpio(self.ScaAsic)
        self.ScaI2c = ScaI2c(self.ScaAsic, SCA_CH_I2C1)

        self.Bme280_ = Bme280(self.ScaI2c)

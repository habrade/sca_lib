import logging

from sca import Sca
from sca_defs import *

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s  %(name)s  %(levelname)s  %(message)s')
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

__author__ = "Sheng Dong"
__email__ = "habrade@gmail.com"


class ScaGpio(Sca):

    def __init__(self, link):
        super(ScaGpio, self).__init__(link)
        self.__link = link

    def set_direction(self, directions):
        """GPIO Direction Set, 1->output mode, 0->input mode"""
        return self.send_command(SCA_CH_GPIO, SCA_GPIO_W_DIRECTION, directions)

    def get_direction(self):
        if self.send_command(SCA_CH_GPIO, SCA_GPIO_R_DIRECTION, 0):
            return self.get_reg_value("rxData%d" % self.__link)
        else:
            log.error("get_direction: Sca command error")

    def write_pin_out(self, pins):
        return self.send_command(SCA_CH_GPIO, SCA_GPIO_W_DATAOUT, pins)

    def read_pin_out(self):
        if self.send_command(SCA_CH_GPIO, SCA_GPIO_R_DATAOUT, 0):
            return self.get_reg_value("rxData%d" % self.__link)
        else:
            log.error("read_pin_out: Sca command error")

    def read_pin_in(self):
        if self.send_command(SCA_CH_GPIO, SCA_GPIO_R_DATAIN, 0):
            return self.get_reg_value("rxData%d" % self.__link)
        else:
            log.error("read_pin_in: Sca command error")

    def get_pins_bit_value(self, pins_index):
        if pins_index < 0 or pins_index > 31:
            log.error("get_pins_bit_value: Invalid pin number")
        else:
            return self.read_pin_out() & (1 << pins_index)

    def set_pins_bit_value(self, pins_index, set_value):
        if pins_index < 0 or pins_index > 31:
            log.error("set_pins_bit_value: Invalid pin number")
        else:
            pins = self.read_pin_out()
            pins &= ~(1 << pins_index)
            if set_value:
                pins |= 1 << pins_index
            self.write_pin_out(pins)

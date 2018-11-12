import sys

sys.path.append('./')

import sca
import sca_defs


class ScaGpio(sca.Sca):

    def enable_gpio(self):
        self.send_command(sca_defs.SCA_CH_CTRL, sca_defs.SCA_CTRL_W_CRB, sca_defs.SCA_CTRL_CRB_ENGPIO)

    def set_direction(self, directions):
        """GPIO Direction Set, 1->output mode, 0->input mode"""
        self.send_command(sca_defs.SCA_CH_GPIO, sca_defs.SCA_GPIO_W_DIRECTION, directions)

    def get_direction(self):
        self.send_command(sca_defs.SCA_CH_GPIO, sca_defs.SCA_GPIO_R_DIRECTION, 0)
        return self.get_reg_value("rxData")

    def set_gpio(self, pins):
        self.send_command(sca_defs.SCA_CH_GPIO, sca_defs.SCA_GPIO_W_DATAOUT, pins)

    def get_gpio(self):
        self.send_command(sca_defs.SCA_CH_GPIO, sca_defs.SCA_GPIO_R_DATAOUT, 0)
        return self.get_reg_value("rxData")

    def test_gpio(self, pins):
        debug = 1
        print "set GPIO value: %x" % pins
        self.send_command(sca_defs.SCA_CH_GPIO, sca_defs.SCA_GPIO_W_DATAOUT, pins)
        if debug:
            print "Get GPIO value"
        self.send_command(sca_defs.SCA_CH_GPIO, sca_defs.SCA_GPIO_R_DATAOUT, 0)
        print "GPIO = %x" % self.get_reg_value("rxData")
        if self.get_reg_value("rxData") == pins:
            print "pass!"
        else:
            raise ValueError('oops!')

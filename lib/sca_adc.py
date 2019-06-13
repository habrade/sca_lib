import sys

import sca
import sca_defs
from sca_defs import *


class ScaAdc(sca.Sca):

    def __init__(self):
        sca.Sca.__init__(self, version=1)

    def enable_adc(self):
        self.send_command(SCA_CH_CTRL, SCA_CTRL_W_CRD, SCA_CTRL_CRD_ENADC)

    def start_conv(self):
        self.send_command(SCA_CH_ADC, SCA_ADC_GO, 1)
        return self.get_reg_value("rxData")

    def w_sel(self, sel):
        self.send_command(SCA_CH_ADC, SCA_ADC_W_MUX, sel)

    def r_sel(self):
        self.send_command(SCA_CH_ADC, SCA_ADC_R_MUX, 0)
        return self.get_reg_value("rxData")

    def w_curr(self, curr):
        self.send_command(SCA_CH_ADC, SCA_ADC_W_CURR, curr)

    def r_curr(self):
        self.send_command(SCA_CH_ADC, SCA_ADC_R_CURR, 0)
        return self.get_reg_value("rxData")

    def w_gain(self, gain):
        self.send_command(SCA_CH_ADC, SCA_ADC_W_GAIN, gain)

    def r_gain(self):
        self.send_command(SCA_CH_ADC, SCA_ADC_R_GAIN, 0)
        return self.get_reg_value("rxData")

    def r_raw(self):
        self.send_command(SCA_CH_ADC, SCA_ADC_R_RAW, 0)
        return self.get_reg_value("rxData")

    def r_data(self):
        self.send_command(SCA_CH_ADC, SCA_ADC_R_DATA, 0)
        return self.get_reg_value("rxData")

    def r_ofs(self):
        self.send_command(SCA_CH_ADC, SCA_ADC_R_OFS, 0)
        return self.get_reg_value("rxData")

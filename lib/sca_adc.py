import logging

from sca import Sca
from sca_defs import *

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s  %(name)s  %(levelname)s  %(message)s')
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


class ScaAdc(Sca):

    def __init__(self, hw):
        super(ScaAdc, self).__init__(hw)

    def enable_adc(self):
        self.send_command(SCA_CH_CTRL, SCA_CTRL_W_CRD, SCA_CTRL_CRD_ENADC)

    def start_conv(self):
        if self._version == 0x02:
            self.send_command(SCA_CH_ADC, SCA_ADC_GO, 1)
        elif self._version == 0x01:
            self.send_command(SCA_CH_ADC, SCAV1_ADC_GO, 1)

        return self.get_reg_value("rxData") & 0b111111111111

    def w_sel(self, sel):
        if self._version == 0x02:
            self.send_command(SCA_CH_ADC, SCA_ADC_W_MUX, sel)
        elif self._version == 0x01:
            self.send_command(SCA_CH_ADC, SCAV1_ADC_W_INSEL, sel)

    def r_sel(self):
        if self._version == 0x02:
            self.send_command(SCA_CH_ADC, SCA_ADC_R_MUX, 0)
        elif self._version == 0x01:
            self.send_command(SCA_CH_ADC, SCAV1_ADC_R_INSEL, 0)

        return self.get_reg_value("rxData")

    def w_curr(self, curr):
        if self._version == 0x02:
            self.send_command(SCA_CH_ADC, SCA_ADC_W_CURR, curr)
        elif self._version == 0x01:
            self.send_command(SCA_CH_ADC, SCAV1_ADC_W_CUREN, curr)

    def r_curr(self):
        if self._version == 0x02:
            self.send_command(SCA_CH_ADC, SCA_ADC_R_CURR, 0)
        elif self._version == 0x01:
            self.send_command(SCA_CH_ADC, SCAV1_ADC_R_CUREN, 0)

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
        if self._version == 0x02:
            self.send_command(SCA_CH_ADC, SCA_ADC_R_DATA, 0)
        elif self._version == 0x01:
            self.send_command(SCA_CH_ADC, SCAV1_ADC_R_DATA, 0)

        return self.get_reg_value("rxData")

    def r_ofs(self):
        self.send_command(SCA_CH_ADC, SCA_ADC_R_OFS, 0)
        return self.get_reg_value("rxData")

import logging

from sca import Sca
from sca_defs import *

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s  %(name)s  %(levelname)s  %(message)s')
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


class ScaAdc(Sca):

    def __init__(self, hw, link):
        super(ScaAdc, self).__init__(hw, link)
        self.__link = link

    def enable_adc(self):
        return self.send_command(SCA_CH_CTRL, SCA_CTRL_W_CRD, SCA_CTRL_CRD_ENADC)

    def start_conv(self):
        ret_val = []
        if self._version == 0x02:
            ret_val.append(self.send_command(SCA_CH_ADC, SCA_ADC_GO, 1))
        elif self._version == 0x01:
            ret_val.append(self.send_command(SCA_CH_ADC, SCAV1_ADC_GO, 1))

        if False in ret_val:
            log.error("Sca command error")
        else:
            adc = self.get_reg_value("rxData%d" % self.__link) & 0xFFF
            return adc

    def w_sel(self, sel):
        assert 0 <= sel << 31
        if self._version == 0x02:
            return self.send_command(SCA_CH_ADC, SCA_ADC_W_MUX, sel)
        elif self._version == 0x01:
            return self.send_command(SCA_CH_ADC, SCAV1_ADC_W_INSEL, sel)

    def r_sel(self):
        ret_val = []
        if self._version == 0x02:
            ret_val.append(self.send_command(SCA_CH_ADC, SCA_ADC_R_MUX, 0))
        elif self._version == 0x01:
            ret_val.append(self.send_command(SCA_CH_ADC, SCAV1_ADC_R_INSEL, 0))

        if False in ret_val:
            log.error("Sca command error")
        else:
            sel = self.get_reg_value("rxData%d" % self.__link)
            assert 0 <= sel << 31
            return sel

    def w_curr(self, curr):
        if self._version == 0x02:
            return self.send_command(SCA_CH_ADC, SCA_ADC_W_CURR, curr)
        elif self._version == 0x01:
            return self.send_command(SCA_CH_ADC, SCAV1_ADC_W_CUREN, curr)

    def r_curr(self):
        ret_val = []
        if self._version == 0x02:
            ret_val.append(self.send_command(SCA_CH_ADC, SCA_ADC_R_CURR, 0))
        elif self._version == 0x01:
            ret_val.append(self.send_command(SCA_CH_ADC, SCAV1_ADC_R_CUREN, 0))

        if False in ret_val:
            log.error("Sca command error")
        else:
            return self.get_reg_value("rxData%d" % self.__link)

    def w_gain(self, gain):
        return self.send_command(SCA_CH_ADC, SCA_ADC_W_GAIN, gain)

    def r_gain(self):
        if self.send_command(SCA_CH_ADC, SCA_ADC_R_GAIN, 0):
            return self.get_reg_value("rxData%d" % self.__link) & 0xFFFF
        else:
            log.error("Sca command error")

    def r_raw(self):
        if self.send_command(SCA_CH_ADC, SCA_ADC_R_RAW, 0):
            return self.get_reg_value("rxData%d" % self.__link) & 0xFFF
        else:
            log.error("Sca command error")

    def r_data(self):
        ret_val = []
        if self._version == 0x02:
            ret_val.append(self.send_command(SCA_CH_ADC, SCA_ADC_R_DATA, 0))
        elif self._version == 0x01:
            ret_val.append(self.send_command(SCA_CH_ADC, SCAV1_ADC_R_DATA, 0))

        if False in ret_val:
            log.error("Sca command error")
        else:
            return self.get_reg_value("rxData%d" % self.__link) & 0xFFF

    def r_ofs(self):
        if self.send_command(SCA_CH_ADC, SCA_ADC_R_OFS, 0):
            return self.get_reg_value("rxData%d" % self.__link) & 0xFFF
        else:
            log.error("Sca command error")

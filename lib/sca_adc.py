import logging

from sca_defs import *

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s  %(name)s  %(levelname)s  %(message)s')
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

__author__ = "Sheng Dong"
__email__ = "s.dong@mails.ccnu.edu.cn"


class ScaAdc(object):

    def __init__(self, sca_asic):
        super(ScaAdc, self).__init__()
        self._ScaAsic = sca_asic

    def enable_adc(self):
        return self._ScaAsic.send_command(SCA_CH_CTRL, SCA_CTRL_W_CRD, SCA_CTRL_CRD_ENADC)

    def start_conv(self):
        cmd = SCA_ADC_GO
        if self._ScaAsic.version == 0x01:
            cmd = SCAV1_ADC_GO

        if self._ScaAsic.send_command(SCA_CH_ADC, cmd, 1):
            return self._ScaAsic.get_reg_value("rxData%d" % self._ScaAsic.__link) & 0xFFF
        else:
            log.error("start_conv: Sca command error")
            return -1

    def w_sel(self, sel):
        assert 0 <= sel << 31
        cmd = SCA_ADC_W_MUX
        if self._ScaAsic.version == 0x01:
            cmd = SCAV1_ADC_W_INSEL
        return self._ScaAsic.send_command(SCA_CH_ADC, cmd, sel)

    def r_sel(self):
        cmd = SCA_ADC_R_MUX
        if self._ScaAsic.version == 0x01:
            cmd = SCAV1_ADC_R_INSEL

        if self._ScaAsic.send_command(SCA_CH_ADC, cmd, 0):
            sel = self._ScaAsic.get_reg_value("rxData%d" % self._ScaAsic.__link)
            assert 0 <= sel << 31
            return sel
        else:
            log.error("r_sel: Sca command error")
            return -1

    def w_curr(self, curr):
        cmd = SCA_ADC_W_CURR
        if self._ScaAsic.version == 0x01:
            cmd = SCAV1_ADC_W_CUREN
        return self._ScaAsic.send_command(SCA_CH_ADC, cmd, curr)

    def r_curr(self):
        cmd = SCA_ADC_R_CURR
        if self._ScaAsic.version == 0x01:
            cmd = SCAV1_ADC_R_CUREN

        if self._ScaAsic.send_command(SCA_CH_ADC, cmd, 0):
            return self._ScaAsic.get_reg_value("rxData%d" % self._ScaAsic.__link)
        else:
            log.error("r_curr: Sca command error")
            return -1

    def w_gain(self, gain):
        return self._ScaAsic.send_command(SCA_CH_ADC, SCA_ADC_W_GAIN, gain)

    def r_gain(self):
        if self._ScaAsic.send_command(SCA_CH_ADC, SCA_ADC_R_GAIN, 0):
            return self._ScaAsic.get_reg_value("rxData%d" % self._ScaAsic.__link) & 0xFFFF
        else:
            log.error("r_gain: Sca command error")
            return -1

    def r_raw(self):
        if self._ScaAsic.send_command(SCA_CH_ADC, SCA_ADC_R_RAW, 0):
            return self._ScaAsic.get_reg_value("rxData%d" % self._ScaAsic.__link) & 0xFFF
        else:
            log.error("r_raw: Sca command error")
            return -1

    def r_data(self):
        cmd = SCA_ADC_R_DATA
        if self._ScaAsic.version == 0x01:
            cmd = SCAV1_ADC_R_DATA

        if self._ScaAsic.send_command(SCA_CH_ADC, cmd, 0):
            return self._ScaAsic.get_reg_value("rxData%d" % self._ScaAsic.__link) & 0xFFF
        else:
            log.error("r_data: Sca command error")
            return -1

    def r_ofs(self):
        if self._ScaAsic.send_command(SCA_CH_ADC, SCA_ADC_R_OFS, 0):
            return self._ScaAsic.get_reg_value("rxData%d" % self._ScaAsic.__link) & 0xFFF
        else:
            log.error("r_ofs: Sca command error")
            return -1

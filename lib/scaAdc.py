import sys

sys.path.append('./')

import sca
import sca_defs


class ScaAdc(sca.Sca):

    def enbableAdc(self):
        self.send_command(sca_defs.SCA_CH_CTRL, sca_defs.SCA_CTRL_W_CRD, sca_defs.SCA_CTRL_CRD_ENADC)

    def startConv(self):
        self.send_command(sca_defs.SCA_CH_ADC, sca_defs.SCA_ADC_GO, 1)
        return self.getRegValue("rxData")

    def wSel(self, sel):
        self.send_command(sca_defs.SCA_CH_ADC, sca_defs.SCA_ADC_W_MUX, sel)

    def rSel(self):
        self.send_command(sca_defs.SCA_CH_ADC, sca_defs.SCA_ADC_R_MUX, 0)
        return self.getRegValue("rxData")

    def wCurr(self, curr):
        self.send_command(sca_defs.SCA_CH_ADC, sca_defs.SCA_ADC_W_CURR, curr)

    def rCurr(self):
        self.send_command(sca_defs.SCA_CH_ADC, sca_defs.SCA_ADC_R_CURR, 0)
        return self.getRegValue("rxData")

    def wGain(self, gain):
        self.send_command(sca_defs.SCA_CH_ADC, sca_defs.SCA_ADC_W_GAIN, gain)

    def rGain(self):
        self.send_command(sca_defs.SCA_CH_ADC, sca_defs.SCA_ADC_R_GAIN, 0)
        return self.getRegValue("rxData")

    def rRaw(self):
        self.send_command(sca_defs.SCA_CH_ADC, sca_defs.SCA_ADC_R_RAW, 0)
        return self.getRegValue("rxData")

    def rData(self):
        self.send_command(sca_defs.SCA_CH_ADC, sca_defs.SCA_ADC_R_DATA, 0)
        return self.getRegValue("rxData")

    def rOfs(self):
        self.send_command(sca_defs.SCA_CH_ADC, sca_defs.SCA_ADC_R_OFS, 0)
        return self.getRegValue("rxData")

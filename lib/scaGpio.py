import sys

sys.path.append('./')

import sca
import sca_defs


class ScaGpio(sca.Sca):

    def enableGPIO(self):
        self.send_command(sca_defs.SCA_CH_CTRL, sca_defs.SCA_CTRL_W_CRB, sca_defs.SCA_CTRL_CRB_ENGPIO)

    def setDirection(self, directions):
        # GPIO Direction Set, 1->output mode, 0->input mode
        self.send_command(sca_defs.SCA_CH_GPIO, sca_defs.SCA_GPIO_W_DIRECTION, directions)

    def getDirection(self):
        self.send_command(sca_defs.SCA_CH_GPIO, sca_defs.SCA_GPIO_R_DIRECTION, 0)
        return self.getRegValue("rxData")

    def setGPIO(self, pins):
        self.send_command(sca_defs.SCA_CH_GPIO, sca_defs.SCA_GPIO_W_DATAOUT, pins)

    def getGPIO(self):
        self.send_command(sca_defs.SCA_CH_GPIO, sca_defs.SCA_GPIO_R_DATAOUT, 0)
        return self.getRegValue("rxData")

    def testGPIO(self, pins):
        debug = 1
        print("set GPIO value: %x") % pins
        self.send_command(sca_defs.SCA_CH_GPIO, sca_defs.SCA_GPIO_W_DATAOUT, pins)
        if debug:
            print("Get GPIO value")
        self.send_command(sca_defs.SCA_CH_GPIO, sca_defs.SCA_GPIO_R_DATAOUT, 0)
        print("GPIO = "), hex(self.getRegValue("rxData"))
        if self.getRegValue("rxData") == pins:
            print("pass!")
        else:
            raise ValueError('oops!')

import sys

sys.path.append('./')

import sca
import sca_defs


class ScaI2c(sca.Sca):

    def wCtrlReg(self, chn, val):
        self.send_command(chn, sca_defs.SCA_I2C_W_CTRL, val << 24)

    def rCtrlReg(self, chn):
        self.send_command(chn, sca_defs.SCA_I2C_W_CTRL, 0)
        return self.getRegValue("rxData") >> 24

    def rStatus(self, chn):
        self.send_command(chn, sca_defs.SCA_I2C_R_STATUS, 0)
        return self.getRegValue("rxData") >> 24

    def wMask(self, chn, val):
        self.send_command(chn, sca_defs.SCA_I2C_W_MASK, val << 24)

    def rMask(self, chn):
        self.send_command(chn, sca_defs.SCA_I2C_R_MASK, 0)
        return self.getRegValue("rxData") >> 24

    def wData0(self, chn, data):
        self.send_command(chn, sca_defs.SCA_I2C_W_DATA0, data)

    def wData1(self, chn, data):
        self.send_command(chn, sca_defs.SCA_I2C_W_DATA1, data)

    def wData2(self, chn, data):
        self.send_command(chn, sca_defs.SCA_I2C_W_DATA2, data)

    def wData3(self, chn, data):
        self.send_command(chn, sca_defs.SCA_I2C_W_DATA3, data)

    def rData0(self, chn):
        self.send_command(chn, sca_defs.SCA_I2C_R_DATA0, 0)
        return self.getRegValue("rxData")

    def rData1(self, chn):
        self.send_command(chn, sca_defs.SCA_I2C_R_DATA1, 0)
        return self.getRegValue("rxData")

    def rData2(self, chn):
        self.send_command(chn, sca_defs.SCA_I2C_R_DATA2, 0)
        return self.getRegValue("rxData")

    def rData3(self, chn):
        self.send_command(chn, sca_defs.SCA_I2C_R_DATA3, 0)
        return self.getRegValue("rxData")

    def s_7b_w(self, chn, addr, data):
        temp = addr << 24 + data << 16
        self.send_command(chn, sca_defs.SCA_I2C_S_7B_W, temp)
        status = self.getRegValue("rxData") >> 24
        return status

    def s_7b_r(self, chn, addr):
        self.send_command(chn, sca_defs.SCA_I2C_S_7B_R, addr << 24)
        # Return status + data
        return self.getRegValue("rxData") >> 16

    def s_10b_w(self, chn, addr, data):
        temp = addr << 16 + data << 8
        self.send_command(chn, sca_defs.SCA_I2C_S_10B_W, temp)
        status = self.getRegValue("rxData") >> 24
        return status

    def s_10b_r(self, chn, addr):
        self.send_command(chn, sca_defs.SCA_I2C_S_10B_R, addr << 16)
        # Return status + data
        return self.getRegValue("rxData") >> 16

    def m_7b_w(self, chn, addr):
        self.send_command(chn, sca_defs.SCA_I2C_M_7B_W, addr << 24)
        status = self.getRegValue("rxData") >> 24
        return status

    def m_7b_r(self, chn, addr):
        self.send_command(chn, sca_defs.SCA_I2C_M_7B_R, addr << 24)
        status = self.getRegValue("rxData") >> 24
        return status

    def m_10b_w(self, chn, addr):
        self.send_command(chn, sca_defs.SCA_I2C_M_10B_W, addr << 24)
        status = self.getRegValue("rxData") >> 24
        return status

    def m_10b_r(self, chn, addr):
        self.send_command(chn, sca_defs.SCA_I2C_M_10B_R, addr << 24)
        status = self.getRegValue("rxData") >> 24
        return status

    def setFrq(self, chn, frq):
        frq_list = [sca_defs.SCA_I2C_SPEED_100, sca_defs.SCA_I2C_SPEED_200, sca_defs.SCA_I2C_SPEED_400,
                    sca_defs.SCA_I2C_SPEED_1000]
        ctrl_reg = self.rCtrlReg(chn)
        if frq in frq_list:
            frq_reg = frq
        else:
            frq_reg = ctrl_reg & 0x03

        new_ctrl = (ctrl_reg & 0b11111100) | frq_reg
        self.send_command(chn, sca_defs.SCA_I2C_W_CTRL, new_ctrl << 24)

    def setMode(self, chn, mode):
        mode_list = [sca_defs.SCA_I2C_MODE_OPEN_DRAIN, sca_defs.SCA_I2C_MODE_CMOS]
        current_reg = self.rCtrlReg(chn)
        if mode in mode_list:
            new_reg = (mode << 7) | (current_reg & 0x7f)
            self.send_command(chn, sca_defs.SCA_I2C_W_CTRL, new_reg << 24)
        else:
            raise Exception("Channel out of range")


    def setTransByteLength(self, chn, nr):
        current_reg = self.rCtrlReg(chn)
        if nr in range(1, 17):
            new_reg = (nr << 2) | (current_reg & 0x83)
            self.send_command(chn, sca_defs.SCA_I2C_W_CTRL, new_reg << 24)
        else:
            raise Exception("Channel out of range")


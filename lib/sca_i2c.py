import logging
import sys

sys.path.append('./')

import sca
import sca_defs


class ScaI2c(sca.Sca):

    def __init__(self, chn):
        sca.Sca.__init__()
        self.__chn = chn
        self.__log = logging.getLogger(__name__)

    def w_ctrl_reg(self, val):
        self.send_command(self.__chn, sca_defs.SCA_I2C_W_CTRL, val << 24)

    def r_ctrl_reg(self):
        self.send_command(self.__chn, sca_defs.SCA_I2C_W_CTRL, 0)
        return self.get_reg_value("rxData") >> 24

    def r_status(self):
        self.send_command(self.__chn, sca_defs.SCA_I2C_R_STATUS, 0)
        return self.get_reg_value("rxData") >> 24

    def w_mask(self, val):
        self.send_command(self.__chn, sca_defs.SCA_I2C_W_MASK, val << 24)

    def r_mask(self):
        self.send_command(self.__chn, sca_defs.SCA_I2C_R_MASK, 0)
        return self.get_reg_value("rxData") >> 24

    def w_data0(self, data):
        self.send_command(self.__chn, sca_defs.SCA_I2C_W_DATA0, data)

    def w_data1(self, data):
        self.send_command(self.__chn, sca_defs.SCA_I2C_W_DATA1, data)

    def w_data2(self, data):
        self.send_command(self.__chn, sca_defs.SCA_I2C_W_DATA2, data)

    def w_data3(self, data):
        self.send_command(self.__chn, sca_defs.SCA_I2C_W_DATA3, data)

    def r_data0(self):
        self.send_command(self.__chn, sca_defs.SCA_I2C_R_DATA0, 0)
        return self.get_reg_value("rxData")

    def r_data1(self):
        self.send_command(self.__chn, sca_defs.SCA_I2C_R_DATA1, 0)
        return self.get_reg_value("rxData")

    def r_data2(self):
        self.send_command(self.__chn, sca_defs.SCA_I2C_R_DATA2, 0)
        return self.get_reg_value("rxData")

    def r_data3(self):
        self.send_command(self.__chn, sca_defs.SCA_I2C_R_DATA3, 0)
        return self.get_reg_value("rxData")

    def s_7b_w(self, addr, data):
        temp = addr << 24 + data << 16
        self.send_command(self.__chn, sca_defs.SCA_I2C_S_7B_W, temp)
        status = self.get_reg_value("rxData") >> 24
        if status == 0x04:
            return status
        else:
            self.__log.error("Error happened at this I2C write transaction, check status")

    def s_7b_r(self, addr):
        self.send_command(self.__chn, sca_defs.SCA_I2C_S_7B_R, addr << 24)
        # temp =  status + data
        temp = self.get_reg_value("rxData") >> 16
        status = (temp & 0xff00) >> 8
        data = (temp & 0x00ff)
        if status == 0x04:
            return data
        else:
            self.__log.error("Error happened at this I2C read transaction, check status")

    def s_10b_w(self, addr, data):
        temp = addr << 16 + data << 8
        self.send_command(self.__chn, sca_defs.SCA_I2C_S_10B_W, temp)
        status = self.get_reg_value("rxData") >> 24
        if status == 0x04:
            return status
        else:
            self.__log.error("Error happened at this I2C write transaction, check status")
        return status

    def s_10b_r(self, addr):
        self.send_command(self.__chn, sca_defs.SCA_I2C_S_10B_R, addr << 16)
        # Return status + data
        temp = self.get_reg_value("rxData") >> 16
        status = (temp & 0xff00) >> 8
        data = (temp & 0x00ff)
        if status == 0x04:
            return data
        else:
            self.__log.error("Error happened at this I2C read transaction, check status")
        return self.get_reg_value("rxData") >> 16

    def m_7b_w(self, addr):
        self.send_command(self.__chn, sca_defs.SCA_I2C_M_7B_W, addr << 24)
        status = self.get_reg_value("rxData") >> 24
        return status

    def m_7b_r(self, addr):
        self.send_command(self.__chn, sca_defs.SCA_I2C_M_7B_R, addr << 24)
        status = self.get_reg_value("rxData") >> 24
        return status

    def m_10b_w(self, addr):
        self.send_command(self.__chn, sca_defs.SCA_I2C_M_10B_W, addr << 24)
        status = self.get_reg_value("rxData") >> 24
        return status

    def m_10b_r(self, addr):
        self.send_command(self.__chn, sca_defs.SCA_I2C_M_10B_R, addr << 24)
        status = self.get_reg_value("rxData") >> 24
        return status

    def set_frq(self, frq):
        frq_list = [sca_defs.SCA_I2C_SPEED_100, sca_defs.SCA_I2C_SPEED_200, sca_defs.SCA_I2C_SPEED_400,
                    sca_defs.SCA_I2C_SPEED_1000]
        current_reg = self.r_ctrl_reg()
        if frq in frq_list:
            new_reg = (frq << 0) | (current_reg & 0xfc)
            self.send_command(self.__chn, sca_defs.SCA_I2C_W_CTRL, new_reg << 24)
        else:
            raise Exception("Frequency out of index")

    def set_mode(self, mode):
        mode_list = [sca_defs.SCA_I2C_MODE_OPEN_DRAIN, sca_defs.SCA_I2C_MODE_CMOS]
        current_reg = self.r_ctrl_reg()
        if mode in mode_list:
            new_reg = (mode << 7) | (current_reg & 0x7f)
            self.send_command(self.__chn, sca_defs.SCA_I2C_W_CTRL, new_reg << 24)
        else:
            raise Exception("Mode out of index")

    def set_trans_byte_length(self, nr):
        current_reg = self.r_ctrl_reg()
        if nr in range(1, 17):
            new_reg = (nr << 2) | (current_reg & 0x83)
            self.send_command(self.__chn, sca_defs.SCA_I2C_W_CTRL, new_reg << 24)
        else:
            raise Exception("Channel out of range")

    def set_data_reg(self, data):
        if (len(data) > 16) or (len(data) < 1):
            raise Exception("Too less data")
        else:
            if len(data) > 12:
                self.send_command(self.__chn, sca_defs.SCA_I2C_W_DATA3, data[12:16])
            if len(data) > 8:
                self.send_command(self.__chn, sca_defs.SCA_I2C_W_DATA3, data[8:12])
            if len(data) > 4:
                self.send_command(self.__chn, sca_defs.SCA_I2C_W_DATA3, data[4:8])
            self.send_command(self.__chn, sca_defs.SCA_I2C_W_DATA3, data[0:4])

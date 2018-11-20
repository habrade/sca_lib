import logging
import sys

sys.path.append('./')

import sca
import sca_defs


class ScaI2c(sca.Sca):

    def __init__(self, chn):
        sca.Sca.__init__()
        self.__chn = chn
        self._log = logging.getLogger(__name__)

    def _parse_status(self, status):
        """Return 0 on success or positive value on error"""
        if status & (0x1 << 2):
            # log.debug("SCA I2C transaction status SUCCESS")
            pass
        elif status & (0x1 << 3):
            self._log.warn("SCA I2C transaction LEVERR - SDA pulled to GND")
        elif status & (0x1 << 5):
            self._log.warn("SCA I2C transaction INVOM - invalid command")
        elif status & (0x1 << 6):
            self._log.warn("SCA I2C transaction NOACK - no acknowledge from slave")
        return status & 0x68

    def w_ctrl_reg(self, val):
        self._send_command(self.__chn, sca_defs.SCA_I2C_W_CTRL, val << 24)

    def r_ctrl_reg(self):
        self._send_command(self.__chn, sca_defs.SCA_I2C_W_CTRL, 0)
        return self._get_reg_value("rxData") >> 24

    def r_status(self):
        self._send_command(self.__chn, sca_defs.SCA_I2C_R_STATUS, 0)
        return self._get_reg_value("rxData") >> 24

    def w_mask(self, val):
        self._send_command(self.__chn, sca_defs.SCA_I2C_W_MASK, val << 24)

    def r_mask(self):
        self._send_command(self.__chn, sca_defs.SCA_I2C_R_MASK, 0)
        return self._get_reg_value("rxData") >> 24

    def w_data0(self, data):
        self._send_command(self.__chn, sca_defs.SCA_I2C_W_DATA0, data)

    def w_data1(self, data):
        self._send_command(self.__chn, sca_defs.SCA_I2C_W_DATA1, data)

    def w_data2(self, data):
        self._send_command(self.__chn, sca_defs.SCA_I2C_W_DATA2, data)

    def w_data3(self, data):
        self._send_command(self.__chn, sca_defs.SCA_I2C_W_DATA3, data)

    def r_data0(self):
        self._send_command(self.__chn, sca_defs.SCA_I2C_R_DATA0, 0)
        return self._get_reg_value("rxData")

    def r_data1(self):
        self._send_command(self.__chn, sca_defs.SCA_I2C_R_DATA1, 0)
        return self._get_reg_value("rxData")

    def r_data2(self):
        self._send_command(self.__chn, sca_defs.SCA_I2C_R_DATA2, 0)
        return self._get_reg_value("rxData")

    def r_data3(self):
        self._send_command(self.__chn, sca_defs.SCA_I2C_R_DATA3, 0)
        return self._get_reg_value("rxData")

    def s_7b_w(self, addr, data):
        temp = addr << 24 + data << 16
        self._send_command(self.__chn, sca_defs.SCA_I2C_S_7B_W, temp)
        status = self._get_reg_value("rxData") >> 24
        return self._parse_status(status)

    def s_7b_r(self, addr):
        self._send_command(self.__chn, sca_defs.SCA_I2C_S_7B_R, addr << 24)
        # temp =  status + data
        temp = self._get_reg_value("rxData") >> 16
        status = (temp & 0xff00) >> 8
        data = (temp & 0xff)
        if self._parse_status(status) == 0:
            return data
        else:
            self._log.error("Error happened at this I2C read transaction, check status")

    def s_10b_w(self, addr, data):
        temp = addr << 16 + data << 8
        self._send_command(self.__chn, sca_defs.SCA_I2C_S_10B_W, temp)
        status = self._get_reg_value("rxData") >> 24
        if status == 0x04:
            return True
        else:
            self._log.error("Error happened at this I2C write transaction, check status")
        return status

    def s_10b_r(self, addr):
        self._send_command(self.__chn, sca_defs.SCA_I2C_S_10B_R, addr << 16)
        # Return status + data
        temp = self._get_reg_value("rxData") >> 16
        status = (temp & 0xff00) >> 8
        data = (temp & 0x00ff)
        if status == 0x04:
            return data
        else:
            self._log.error("Error happened at this I2C read transaction, check status")
        return self._get_reg_value("rxData") >> 16

    def m_7b_w(self, addr):
        self._send_command(self.__chn, sca_defs.SCA_I2C_M_7B_W, addr << 24)
        status = self._get_reg_value("rxData") >> 24
        if status == 0x04:
            return True
        else:
            self._log.error("Error happened at this I2C write transaction, check status")

    def m_7b_r(self, addr):
        self._send_command(self.__chn, sca_defs.SCA_I2C_M_7B_R, addr << 24)
        status = self._get_reg_value("rxData") >> 24
        if self._parse_status(status) == 0:
            return True
        else:
            self._log.error("Error happened at this I2C read transaction, check status")

    def m_10b_w(self, addr):
        self._send_command(self.__chn, sca_defs.SCA_I2C_M_10B_W, addr << 24)
        status = self._get_reg_value("rxData") >> 24
        if status == 0x04:
            return True
        else:
            self._log.error("Error happened at this I2C read transaction, check status")

    def m_10b_r(self, addr):
        self._send_command(self.__chn, sca_defs.SCA_I2C_M_10B_R, addr << 24)
        status = self._get_reg_value("rxData") >> 24
        return status

    def set_frq(self, frq):
        frq_list = [sca_defs.SCA_I2C_SPEED_100, sca_defs.SCA_I2C_SPEED_200, sca_defs.SCA_I2C_SPEED_400,
                    sca_defs.SCA_I2C_SPEED_1000]
        current_reg = self.r_ctrl_reg()
        if frq in frq_list:
            new_reg = (frq << 0) | (current_reg & 0xfc)
            self._send_command(self.__chn, sca_defs.SCA_I2C_W_CTRL, new_reg << 24)
        else:
            raise Exception("Frequency out of index")

    def set_mode(self, mode):
        mode_list = [sca_defs.SCA_I2C_MODE_OPEN_DRAIN, sca_defs.SCA_I2C_MODE_CMOS]
        current_reg = self.r_ctrl_reg()
        if mode in mode_list:
            new_reg = (mode << 7) | (current_reg & 0x7f)
            self._send_command(self.__chn, sca_defs.SCA_I2C_W_CTRL, new_reg << 24)
        else:
            raise Exception("Mode out of index")

    def set_trans_byte_length(self, nr_bytes):
        current_reg = self.r_ctrl_reg()
        if nr_bytes in range(1, 17):
            new_reg = (nr_bytes << 2) | (current_reg & 0x83)
            self._send_command(self.__chn, sca_defs.SCA_I2C_W_CTRL, new_reg << 24)
        else:
            raise Exception("Channel out of range")

    def set_data_reg(self, data):
        if (len(data) > 16) or (len(data) < 1):
            raise Exception("Too less data")
        else:
            if len(data) > 12:
                self._send_command(self.__chn, sca_defs.SCA_I2C_W_DATA3, data[12:16])
            if len(data) > 8:
                self._send_command(self.__chn, sca_defs.SCA_I2C_W_DATA2, data[8:12])
            if len(data) > 4:
                self._send_command(self.__chn, sca_defs.SCA_I2C_W_DATA1, data[4:8])
            self._send_command(self.__chn, sca_defs.SCA_I2C_W_DATA0, data[0:4])

    def get_data_reg(self, nr_bytes):
        data = []
        if (nr_bytes > 16) or (nr_bytes < 1):
            self._log.error("Bytes of data should be from 1 to 16")
        else:
            data[0:4] = self._send_command(self.__chn, sca_defs.SCA_I2C_R_DATA0, 0)
            if nr_bytes > 4:
                data[4:8] = self._send_command(self.__chn, sca_defs.SCA_I2C_R_DATA1, 0)
            if nr_bytes > 8:
                data[8:12] = self._send_command(self.__chn, sca_defs.SCA_I2C_R_DATA2, 0)
            if nr_bytes > 12:
                data[12:16] = self._send_command(self.__chn, sca_defs.SCA_I2C_R_DATA3, 0)
            return data

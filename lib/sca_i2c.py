import logging
import struct

from sca import Sca
from sca_defs import *

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s  %(name)s  %(levelname)s  %(message)s')
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


class ScaI2c(Sca):

    def __init__(self, hw, link, chn):
        super(ScaI2c, self).__init__(hw, link)
        self.__chn = chn
        self.__link = link

    @staticmethod
    def _parse_status(status):
        """Return 0 on success or positive value on error"""
        if status & (0x1 << 2):
            log.debug("SCA I2C transaction status SUCCESS")
            pass
        elif status & (0x1 << 3):
            log.warn("SCA I2C transaction LEVERR - SDA pulled to GND")
        elif status & (0x1 << 5):
            log.warn("SCA I2C transaction INVOM - invalid command")
        elif status & (0x1 << 6):
            log.warn("SCA I2C transaction NOACK - no acknowledge from slave")
        return status & 0x68

    def w_ctrl_reg(self, val):
        self.send_command(self.__chn, SCA_I2C_W_CTRL, val << 24)

    def r_ctrl_reg(self):
        self.send_command(self.__chn, SCA_I2C_W_CTRL, 0)
        return self.get_reg_value("rxData%d" % self.__link) >> 24

    def r_status(self):
        self.send_command(self.__chn, SCA_I2C_R_STATUS, 0)
        return self.get_reg_value("rxData%d" % self.__link) >> 24

    def w_mask(self, val):
        self.send_command(self.__chn, SCA_I2C_W_MASK, val << 24)

    def r_mask(self):
        self.send_command(self.__chn, SCA_I2C_R_MASK, 0)
        return self.get_reg_value("rxData%d" % self.__link) >> 24

    def w_data0(self, data):
        self.send_command(self.__chn, SCA_I2C_W_DATA0, data)

    def w_data1(self, data):
        self.send_command(self.__chn, SCA_I2C_W_DATA1, data)

    def w_data2(self, data):
        self.send_command(self.__chn, SCA_I2C_W_DATA2, data)

    def w_data3(self, data):
        self.send_command(self.__chn, SCA_I2C_W_DATA3, data)

    def r_data0(self):
        self.send_command(self.__chn, SCA_I2C_R_DATA0, 0)
        return self.get_reg_value("rxData%d" % self.__link)

    def r_data1(self):
        self.send_command(self.__chn, SCA_I2C_R_DATA1, 0)
        return self.get_reg_value("rxData%d" % self.__link)

    def r_data2(self):
        self.send_command(self.__chn, SCA_I2C_R_DATA2, 0)
        return self.get_reg_value("rxData%d" % self.__link)

    def r_data3(self):
        self.send_command(self.__chn, SCA_I2C_R_DATA3, 0)
        return self.get_reg_value("rxData%d" % self.__link)

    def s_7b_w(self, addr, data):
        temp = (addr << 24) + (data << 16)
        self.send_command(self.__chn, SCA_I2C_S_7B_W, temp)
        status = self.get_reg_value("rxData%d" % self.__link) >> 24
        return self._parse_status(status)

    def s_7b_r(self, addr):
        self.send_command(self.__chn, SCA_I2C_S_7B_R, addr << 24)
        # temp =  status + data
        temp = self.get_reg_value("rxData%d" % self.__link) >> 16
        status = (temp & 0xff00) >> 8
        data = (temp & 0xff)
        if self._parse_status(status) == 0:
            return data
        else:
            log.error("Error happened at this I2C read transaction, check status")

    def s_10b_w(self, addr, data):
        temp = (addr << 16) + (data << 8)
        self.send_command(self.__chn, SCA_I2C_S_10B_W, temp)
        status = self.get_reg_value("rxData%d" % self.__link) >> 24
        if status == 0x04:
            return True
        else:
            log.error("Error happened at this I2C write transaction, check status")
        return status

    def s_10b_r(self, addr):
        self.send_command(self.__chn, SCA_I2C_S_10B_R, addr << 16)
        # Return status + data
        temp = self.get_reg_value("rxData%d" % self.__link) >> 16
        status = (temp & 0xff00) >> 8
        data = (temp & 0x00ff)
        if status == 0x04:
            return data
        else:
            log.error("Error happened at this I2C read transaction, check status")
        return self.get_reg_value("rxData%d" % self.__link) >> 16

    def m_7b_w(self, addr):
        self.send_command(self.__chn, SCA_I2C_M_7B_W, addr << 24)
        status = self.get_reg_value("rxData%d" % self.__link) >> 24
        if status == 0x04:
            return True
        else:
            log.error("Error happened at this I2C write transaction, check status")

    def m_7b_r(self, addr):
        self.send_command(self.__chn, SCA_I2C_M_7B_R, addr << 24)
        status = self.get_reg_value("rxData%d" % self.__link) >> 24
        if self._parse_status(status) == 0:
            return True
        else:
            log.error("Error happened at this I2C read transaction, check status")

    def m_10b_w(self, addr):
        self.send_command(self.__chn, SCA_I2C_M_10B_W, addr << 24)
        status = self.get_reg_value("rxData%d" % self.__link) >> 24
        if status == 0x04:
            return True
        else:
            log.error("Error happened at this I2C read transaction, check status")

    def m_10b_r(self, addr):
        self.send_command(self.__chn, SCA_I2C_M_10B_R, addr << 24)
        status = self.get_reg_value("rxData%d" % self.__link) >> 24
        return status

    def set_frq(self, frq):
        frq_list = [SCA_I2C_SPEED_100, SCA_I2C_SPEED_200, SCA_I2C_SPEED_400,
                    SCA_I2C_SPEED_1000]
        current_reg = self.r_ctrl_reg()
        if frq in frq_list:
            new_reg = (frq << 0) | (current_reg & 0xfc)
            self.send_command(self.__chn, SCA_I2C_W_CTRL, new_reg << 24)
        else:
            raise Exception("Frequency out of index")

    def set_mode(self, mode):
        mode_list = [SCA_I2C_MODE_OPEN_DRAIN, SCA_I2C_MODE_CMOS]
        current_reg = self.r_ctrl_reg()
        if mode in mode_list:
            new_reg = (mode << 7) | (current_reg & 0x7f)
            self.send_command(self.__chn, SCA_I2C_W_CTRL, new_reg << 24)
        else:
            raise Exception("Mode out of index")

    def set_trans_byte_length(self, nr_bytes):
        current_reg = self.r_ctrl_reg()
        if nr_bytes in range(1, 17):
            new_reg = (nr_bytes << 2) | (current_reg & 0x83)
            self.send_command(self.__chn, SCA_I2C_W_CTRL, new_reg << 24)
        else:
            raise Exception("Channel out of range")

    def set_data_reg(self, data):
        if (len(data) > 16) or (len(data) < 1):
            raise Exception("Data lenth should between 1 and 16")
        else:
            data_temp = bytearray(16)
            data_temp[0:len(data)] = data
            # log.debug("data = %x" % data)
            print data_temp
            print len(data_temp)
            if len(data) > 12:
                self.send_command(self.__chn, SCA_I2C_W_DATA3, struct.unpack('>I', data_temp[12:16])[0])
            if len(data) > 8:
                self.send_command(self.__chn, SCA_I2C_W_DATA2, struct.unpack('>I', data_temp[8:12])[0])
            if len(data) > 4:
                self.send_command(self.__chn, SCA_I2C_W_DATA1, struct.unpack('>I', data_temp[4:8])[0])
            self.send_command(self.__chn, SCA_I2C_W_DATA0, struct.unpack('>I', data_temp[0:4])[0])

    def get_data_reg(self, nr_bytes):
        data = bytearray(16)
        if (nr_bytes > 16) or (nr_bytes < 1):
            log.error("Bytes of data should be from 1 to 16")
        else:
            self.send_command(self.__chn, SCA_I2C_R_DATA0, 0)
            data0 = self.get_reg_value("rxData%d" % self.__link)
            data[0:4] = struct.pack('>I', data0)

            if nr_bytes > 4:
                self.send_command(self.__chn, SCA_I2C_R_DATA1, 0)
                data1 = self.get_reg_value("rxData%d" % self.__link)
                data[4:8] = struct.pack('>I', data1)

            if nr_bytes > 8:
                self.send_command(self.__chn, SCA_I2C_R_DATA2, 0)
                data2 = self.get_reg_value("rxData%d" % self.__link)
                data[8:12] = struct.pack('>I', data2)

            if nr_bytes > 12:
                self.send_command(self.__chn, SCA_I2C_R_DATA3, 0)
                data3 = self.get_reg_value("rxData%d" % self.__link)
                data[12:16] = struct.pack('>I', data3)

            return data[0:nr_bytes]

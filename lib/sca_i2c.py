import logging
import struct

from sca_defs import *

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s  %(name)s  %(levelname)s  %(message)s')
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

__author__ = "Sheng Dong"
__email__ = "s.dong@mails.ccnu.edu.cn"


class ScaI2c(object):

    def __init__(self, sca_asic, chn):
        super(ScaI2c, self).__init__()
        self.__chn = chn
        self._ScaAsic = sca_asic
        self._ScaAsic.enable_chn(self.__chn, True)
        self._ctrl_reg = self.r_ctrl_reg()

    @staticmethod
    def _parse_status(status):
        """Return 0 on success or positive value on error"""
        if status & (0x1 << 2):
            pass
        elif status & (0x1 << 3):
            log.warn("SCA I2C transaction LEVERR - SDA pulled to GND")
        elif status & (0x1 << 5):
            log.warn("SCA I2C transaction INVOM - invalid command")
        elif status & (0x1 << 6):
            log.warn("SCA I2C transaction NOACK - no acknowledge from slave")
        return status & 0x68

    def w_ctrl_reg(self, val):
        return self._ScaAsic.send_command(self.__chn, SCA_I2C_W_CTRL, val << 24)

    def r_ctrl_reg(self):
        if self._ScaAsic.send_command(self.__chn, SCA_I2C_R_CTRL, 0):
            ctrl_reg = self._ScaAsic.get_reg_value("rxData%d" % self._ScaAsic.__link) >> 24
            return ctrl_reg
        else:
            log.error("r_ctrl_reg: SCA command error!")
            return -1

    def r_status(self):
        if self._ScaAsic.send_command(self.__chn, SCA_I2C_R_STATUS, 0):
            return self._ScaAsic.get_reg_value("rxData%d" % self._ScaAsic.__link) >> 24
        else:
            log.error("r_status: SCA command error!")
            return -1

    def w_mask(self, val):
        return self._ScaAsic.send_command(self.__chn, SCA_I2C_W_MASK, val << 24)

    def r_mask(self):
        if self._ScaAsic.send_command(self.__chn, SCA_I2C_R_MASK, 0):
            return self._ScaAsic.get_reg_value("rxData%d" % self._ScaAsic.__link) >> 24
        else:
            log.error("r_mask: SCA command error!")
            return -1

    def w_data0(self, data):
        log.debug("Write DATA0: %x" % data)
        return self._ScaAsic.send_command(self.__chn, SCA_I2C_W_DATA0, data)

    def w_data1(self, data):
        log.debug("Write DATA1: %x" % data)
        return self._ScaAsic.send_command(self.__chn, SCA_I2C_W_DATA1, data)

    def w_data2(self, data):
        log.debug("Write DATA2: %x" % data)
        return self._ScaAsic.send_command(self.__chn, SCA_I2C_W_DATA2, data)

    def w_data3(self, data):
        log.debug("Write DATA3: %x" % data)
        return self._ScaAsic.send_command(self.__chn, SCA_I2C_W_DATA3, data)

    def r_data0(self):
        data0 = 0
        if self._ScaAsic.send_command(self.__chn, SCA_I2C_R_DATA0, 0):
            try:
                data0 = self._ScaAsic.get_reg_value("rxData%d" % self._ScaAsic.__link)
                log.debug("Read DATA0 = %#x" % data0)
            except TypeError:
                pass
        else:
            log.error("r_data0: SCA command error!")
        return data0

    def r_data1(self):
        data1 = 0
        if self._ScaAsic.send_command(self.__chn, SCA_I2C_R_DATA1, 0):
            try:
                data1 = self._ScaAsic.get_reg_value("rxData%d" % self._ScaAsic.__link)
                log.debug("Read DATA1 = %#x" % data1)
            except TypeError:
                pass
        else:
            log.error("r_data1: SCA command error!")
        return data1

    def r_data2(self):
        data2 = 0
        if self._ScaAsic.send_command(self.__chn, SCA_I2C_R_DATA2, 0):
            try:
                data2 = self._ScaAsic.get_reg_value("rxData%d" % self._ScaAsic.__link)
                log.debug("Read DATA2 = %#x" % data2)
            except TypeError:
                pass
        else:
            log.error("r_data2: SCA command error!")
        return data2

    def r_data3(self):
        data3 = 0
        if self._ScaAsic.send_command(self.__chn, SCA_I2C_R_DATA3, 0):
            try:
                data3 = self._ScaAsic.get_reg_value("rxData%d" % self._ScaAsic.__link)
                log.debug("Read DATA3 = %#x" % data3)
            except TypeError:
                pass
        else:
            log.error("r_data3: SCA command error!")
        return data3

    def s_7b_w(self, addr, data):
        temp = (addr << 24) + (data << 16)
        log.debug("s_7b_w send data: %#x" % data)
        if self._ScaAsic.send_command(self.__chn, SCA_I2C_S_7B_W, temp):
            status = self._ScaAsic.get_reg_value("rxData%d" % self._ScaAsic.__link) >> 24
            return self._parse_status(status)
        else:
            log.error("s_7b_w: SCA command error!")

    def s_7b_r(self, addr):
        if self._ScaAsic.send_command(self.__chn, SCA_I2C_S_7B_R, addr << 24):
            # temp =  status + data
            temp = self._ScaAsic.get_reg_value("rxData%d" % self._ScaAsic.__link) >> 16
            status = (temp & 0xff00) >> 8
            data = (temp & 0xff)
            if self._parse_status(status) == 0:
                log.debug("s_7b_r: %#02x" % data)
                return data
            else:
                log.error("s_7b_r: Error happened at this I2C read transaction, check status")
        else:
            log.error("s_7b_r: SCA command error!")

    def s_10b_w(self, addr, data):
        temp = (addr << 16) + (data << 8)
        if self._ScaAsic.send_command(self.__chn, SCA_I2C_S_10B_W, temp):
            status = self._ScaAsic.get_reg_value("rxData%d" % self._ScaAsic.__link) >> 24
            return self._parse_status(status)
        else:
            log.error("s_10b_w: SCA command error!")

    def s_10b_r(self, addr):
        if self._ScaAsic.send_command(self.__chn, SCA_I2C_S_10B_R, addr << 16):
            # Return status + data
            temp = self._ScaAsic.get_reg_value("rxData%d" % self._ScaAsic.__link) >> 16
            status = (temp & 0xff00) >> 8
            data = (temp & 0x00ff)
            if status == 0x04:
                return data
            else:
                log.error("s_10b_r: Error happened at this I2C read transaction, check status")
            return self._ScaAsic.get_reg_value("rxData%d" % self._ScaAsic.__link) >> 16
        else:
            log.error("s_10b_r: SCA command error!")

    def m_7b_w(self, addr):
        if self._ScaAsic.send_command(self.__chn, SCA_I2C_M_7B_W, addr << 24):
            status = self._ScaAsic.get_reg_value("rxData%d" % self._ScaAsic.__link) >> 24
            if self._parse_status(status) == 0:
                return True
            else:
                log.error("m_7b_w: Error happened at this I2C write transaction, check status")
                return False
        else:
            log.error("m_7b_w: SCA command error!")
            return False

    def m_7b_r(self, addr):
        log.debug("Multi read(7 bits I2C) starting...")
        if self._ScaAsic.send_command(self.__chn, SCA_I2C_M_7B_R, addr << 24):
            status = self._ScaAsic.get_reg_value("rxData%d" % self._ScaAsic.__link) >> 24
            if self._parse_status(status) == 0:
                return True
            else:
                log.error("m_7b_r: Error happened at this I2C read transaction, check status")
                return False
        else:
            log.error("m_7b_r: SCA command error!")
            return False

    def m_10b_w(self, addr):
        if self._ScaAsic.send_command(self.__chn, SCA_I2C_M_10B_W, addr << 24):
            status = self._ScaAsic.get_reg_value("rxData%d" % self._ScaAsic.__link) >> 24
            if self._parse_status(status) == 0:
                return True
            else:
                log.error("m_10b_w: Error happened at this I2C read transaction, check status")
                return False
        else:
            log.error("m_10b_w: SCA command error!")
            return False

    def m_10b_r(self, addr):
        if self._ScaAsic.send_command(self.__chn, SCA_I2C_M_10B_R, addr << 24):
            status = self._ScaAsic.get_reg_value("rxData%d" % self._ScaAsic.__link) >> 24
            if self._parse_status(status) == 0:
                return True
            else:
                log.error("m_10b_r: Error happened at this I2C read transaction, check status")
                return False
        else:
            log.error("m_10b_r: SCA command error!")
            return False

    def set_frq(self, frq):
        frq_list = [SCA_I2C_SPEED_100, SCA_I2C_SPEED_200, SCA_I2C_SPEED_400,
                    SCA_I2C_SPEED_1000]
        if frq in frq_list:
            log.debug("set_frq: Control reg in set frq, Old: %#x" % self._ctrl_reg)
            self._ctrl_reg = (frq << 0) | (self._ctrl_reg & 0xfc)
            log.debug("set_frq: Control reg in set frq, New: %#x" % self._ctrl_reg)
            return self._ScaAsic.send_command(self.__chn, SCA_I2C_W_CTRL, self._ctrl_reg << 24)
        else:
            raise Exception("set_frq: Frequency out of index")

    def set_mode(self, mode):
        mode_list = [SCA_I2C_MODE_OPEN_DRAIN, SCA_I2C_MODE_CMOS]
        if mode in mode_list:
            log.debug("set_mode: Control reg in set mode, Old: %#x" % self._ctrl_reg)
            self._ctrl_reg = (mode << 7) | (self._ctrl_reg & 0x7f)
            log.debug("set_mode: Control reg in set mode, New: %#x" % self._ctrl_reg)
            return self._ScaAsic.send_command(self.__chn, SCA_I2C_W_CTRL, self._ctrl_reg << 24)
        else:
            raise Exception("set_mode: Mode out of index")

    def set_trans_byte_length(self, nr_bytes):
        log.debug("Set data number to be transferred: %d" % nr_bytes)
        if nr_bytes in range(1, 17):
            log.debug("set_trans_byte_length: Old ctrl_reg: %#x" % self._ctrl_reg)
            self._ctrl_reg = (nr_bytes << 2) | (self._ctrl_reg & 0x83)
            log.debug("set_trans_byte_length: New ctrl_reg: %#x" % self._ctrl_reg)
            return self._ScaAsic.send_command(self.__chn, SCA_I2C_W_CTRL, self._ctrl_reg << 24)
        else:
            raise Exception("set_trans_byte_length: Number of Bytes out of range, should be 1 to 16")

    def set_data_reg(self, data):
        if (len(data) > 16) or (len(data) < 1):
            raise Exception("set_data_reg: Data lenth should between 1 and 16")
        else:
            data_temp = bytearray(16)
            data_temp[0:len(data)] = data
            # log.debug("data = %x" % data)
            try:
                if len(data) > 12:
                    self._ScaAsic.send_command(self.__chn, SCA_I2C_W_DATA3, struct.unpack('>I', data_temp[12:16])[0])
                if len(data) > 8:
                    self._ScaAsic.send_command(self.__chn, SCA_I2C_W_DATA2, struct.unpack('>I', data_temp[8:12])[0])
                if len(data) > 4:
                    self._ScaAsic.send_command(self.__chn, SCA_I2C_W_DATA1, struct.unpack('>I', data_temp[4:8])[0])
                self._ScaAsic.send_command(self.__chn, SCA_I2C_W_DATA0, struct.unpack('>I', data_temp[0:4])[0])

                return True
            except TypeError:
                return False

    def get_data_reg(self, nr_bytes):
        log.debug("get_data_reg, number: %d" % nr_bytes)
        data = bytearray(nr_bytes)
        if (nr_bytes > 16) or (nr_bytes < 1):
            log.error("Bytes of data should be from 1 to 16")
        else:
            data3 = self.r_data3()
            log.debug("data3: %#04x" % data3)
            data[0:4] = struct.pack('>I', data3)

            if nr_bytes > 4:
                data2 = self.r_data2()
                log.debug("data2: %#04x" % data2)
                data[4:8] = struct.pack('>I', data2)

            if nr_bytes > 8:
                data1 = self.r_data1()
                log.debug("data1: %#04x" % data1)
                data[8:12] = struct.pack('>I', data1)

            if nr_bytes > 12:
                data0 = self.r_data0()
                log.debug("data0: %#04x" % data0)
                data[12:16] = struct.pack('>I', data0)

            # log.debug("get_data_reg: ")
            # print binascii.hexlify(data)
            return data

    def write_raw8(self, slave_addr, value):
        """Write an 8-bit value on the bus (without register)."""
        log.debug("Write %#02x on the bus (without register)" % value)
        return self.s_7b_w(slave_addr, value)

    def write_reg(self, slave_addr, register, value):
        """Write an 8-bit value to the specified register."""
        log.debug("Write %#02x to register %#02x" % (value, register))
        data = [register, value & 0xFF]
        return self.write_block(slave_addr, data)

    def write16(self, slave_addr, register, value):
        """Write a 16-bit value to the specified register."""
        log.debug("Write %#04x to register pair %#02x, %#02x" % (value, register, register + 1))
        value = value & 0xFFFF
        data = (register << 24) | (((value >> 8) & 0xff) << 16) | ((register + 1) << 8) | (value & 0xff)
        return self.write_block(slave_addr, data)

    def read_u8(self, slave_addr, register):
        """To be able to read registers, first the register must be sent in write mode"""
        self.write_raw8(slave_addr, register)
        try:
            result = self.s_7b_r(slave_addr)
            log.debug("read_u8: %#02x" % result)
            return result
        except TypeError:
            log.error("read u8 failed!")

    def read_s8(self, slave_addr, register):
        """Read a signed byte from the specified register."""
        try:
            result = self.read_u8(slave_addr, register)
            if result > 127:
                result -= 256
            log.debug("read_s8: %#02x  %d" % (result, result))
            return result
        except TypeError:
            log.error("read s8 failed!")

    def read_u16(self, slave_addr, register, little_endian=True):
        """Read an unsigned 16-bit value from the specified register, with the
        specified endianness (default little endian, or least significant byte
        first)."""
        # result_bytes = self._read_block(register, 2)
        result_array = self.read_block(slave_addr, register, 2)
        result = (result_array[1] << 8) + result_array[0]
        # result = (((resultLE & 0xFF) << 8) | ((resultLE >> 8) & 0xFF)) & 0xFFFF
        # Swap bytes if using big endian because read_word_data assumes little
        # endian on ARM (little endian) systems.
        if not little_endian:
            result = ((result << 8) & 0xFF00) + (result >> 8)
        log.debug("Read 0x%04X from register pair %#02x, %#02x", result, register, register + 1)
        return result

    def read_s16(self, slave_addr, register, little_endian=True):
        """Read a signed 16-bit value from the specified register, with the specified endianness
        (default little endian, or least significant byte first)."""
        result = self.read_u16(slave_addr, register, little_endian)
        if result > 32767:
            result -= 65536
        log.debug("read_s16: %#04x %d" % (result, result))
        return result

    def read_u16le(self, slave_addr, register):
        """Read an unsigned 16-bit value from the specified register, in little endian byte order."""
        return self.read_u16(slave_addr, register, little_endian=True)

    def read_u16be(self, slave_addr, register):
        """Read an unsigned 16-bit value from the specified register, in big
        endian byte order."""
        return self.read_u16(slave_addr, register, little_endian=False)

    def read_s16le(self, slave_addr, register):
        """Read a signed 16-bit value from the specified register, in little endian byte order."""
        return self.read_s16(slave_addr, register, little_endian=True)

    def read_s16be(self, slave_addr, register):
        """Read a signed 16-bit value from the specified register, in big
        endian byte order."""
        return self.read_s16(slave_addr, register, little_endian=False)

    def write_block(self, slave_addr, value):
        nr_bytes = len(value)
        log.debug("write_block: length =%d" % nr_bytes)
        self.set_trans_byte_length(nr_bytes)
        self.set_data_reg(value)
        return self.m_7b_w(slave_addr)

    def read_block(self, slave_addr, register, nr_bytes):
        log.debug("read_block, reg:%#x number:%d" % (register, nr_bytes))
        self.set_trans_byte_length(nr_bytes)
        assert 1 <= nr_bytes <= 16
        self.s_7b_w(slave_addr, register)
        self.m_7b_r(slave_addr)
        data_block = self.get_data_reg(nr_bytes)
        return data_block

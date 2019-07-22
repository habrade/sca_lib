import binascii
import logging
import struct

from sca import Sca
from sca_defs import *

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s  %(name)s  %(levelname)s  %(message)s')
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


class ScaI2c(Sca):

    def __init__(self, hw, link, chn=SCA_CH_I2C0):
        super(ScaI2c, self).__init__(hw, link)
        self.__chn = chn
        self.__link = link
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
        self.send_command(self.__chn, SCA_I2C_W_CTRL, val << 24)

    def r_ctrl_reg(self):
        self.send_command(self.__chn, SCA_I2C_R_CTRL, 0)
        self._ctrl_reg = self.get_reg_value("rxData%d" % self.__link) >> 24
        return self._ctrl_reg

    def r_status(self):
        self.send_command(self.__chn, SCA_I2C_R_STATUS, 0)
        return self.get_reg_value("rxData%d" % self.__link) >> 24

    def w_mask(self, val):
        self.send_command(self.__chn, SCA_I2C_W_MASK, val << 24)

    def r_mask(self):
        self.send_command(self.__chn, SCA_I2C_R_MASK, 0)
        return self.get_reg_value("rxData%d" % self.__link) >> 24

    def w_data0(self, data):
        log.debug("Write DATA0: %x" % data)
        self.send_command(self.__chn, SCA_I2C_W_DATA0, data)

    def w_data1(self, data):
        log.debug("Write DATA1: %x" % data)
        self.send_command(self.__chn, SCA_I2C_W_DATA1, data)

    def w_data2(self, data):
        log.debug("Write DATA2: %x" % data)
        self.send_command(self.__chn, SCA_I2C_W_DATA2, data)

    def w_data3(self, data):
        log.debug("Write DATA3: %x" % data)
        self.send_command(self.__chn, SCA_I2C_W_DATA3, data)

    def r_data0(self):
        self.send_command(self.__chn, SCA_I2C_R_DATA0, 0)
        data0 = self.get_reg_value("rxData%d" % self.__link)
        log.debug("Read DATA0 = %#x" % data0)
        return data0

    def r_data1(self):
        self.send_command(self.__chn, SCA_I2C_R_DATA1, 0)
        data1 = self.get_reg_value("rxData%d" % self.__link)
        log.debug("Read DATA1 = %#x" % data1)
        return data1

    def r_data2(self):
        self.send_command(self.__chn, SCA_I2C_R_DATA2, 0)
        data2 = self.get_reg_value("rxData%d" % self.__link)
        log.debug("Read DATA2 = %#x" % data2)
        return data2

    def r_data3(self):
        self.send_command(self.__chn, SCA_I2C_R_DATA3, 0)
        data3 = self.get_reg_value("rxData%d" % self.__link)
        log.debug("Read DATA3 = %#x" % data3)
        return data3

    def s_7b_w(self, addr, data):
        temp = (addr << 24) + (data << 16)
        log.debug("s_7b_w send data: %#x" % data)
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
            log.debug("s_7b_r: %#02x" % data)
            return data
        else:
            log.error("Error happened at this I2C read transaction, check status")

    def s_10b_w(self, addr, data):
        temp = (addr << 16) + (data << 8)
        self.send_command(self.__chn, SCA_I2C_S_10B_W, temp)
        status = self.get_reg_value("rxData%d" % self.__link) >> 24
        return self._parse_status(status)

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
        if self._parse_status(status) == 0:
            return True
        else:
            log.error("Error happened at this I2C write transaction, check status")

    def m_7b_r(self, addr):
        log.debug("Multi read(7 bits I2C) starting...")
        self.send_command(self.__chn, SCA_I2C_M_7B_R, addr << 24)
        status = self.get_reg_value("rxData%d" % self.__link) >> 24
        if self._parse_status(status) == 0:
            return True
        else:
            log.error("Error happened at this I2C read transaction, check status")

    def m_10b_w(self, addr):
        self.send_command(self.__chn, SCA_I2C_M_10B_W, addr << 24)
        status = self.get_reg_value("rxData%d" % self.__link) >> 24
        if self._parse_status(status) == 0:
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
        if frq in frq_list:
            self._ctrl_reg = (frq << 0) | (self._ctrl_reg & 0xfc)
            self.send_command(self.__chn, SCA_I2C_W_CTRL, self._ctrl_reg << 24)
        else:
            raise Exception("Frequency out of index")

    def set_mode(self, mode):
        mode_list = [SCA_I2C_MODE_OPEN_DRAIN, SCA_I2C_MODE_CMOS]
        if mode in mode_list:
            self._ctrl_reg = (mode << 7) | (self._ctrl_reg & 0x7f)
            self.send_command(self.__chn, SCA_I2C_W_CTRL, self._ctrl_reg << 24)
        else:
            raise Exception("Mode out of index")

    def set_trans_byte_length(self, nr_bytes):
        log.debug("Set data number to be transferred: %d" % nr_bytes)
        log.debug("Old ctrl_reg: %#x" % self._ctrl_reg)
        if nr_bytes in range(1, 17):
            self._ctrl_reg = (nr_bytes << 2) | (self._ctrl_reg & 0x83)
            log.debug("New ctrl_reg: %#x" % self._ctrl_reg)
            self.send_command(self.__chn, SCA_I2C_W_CTRL, self._ctrl_reg << 24)
        else:
            raise Exception("Number of Bytes out of range, should be 1 to 16")

    def set_data_reg(self, data):
        if (len(data) > 16) or (len(data) < 1):
            raise Exception("Data lenth should between 1 and 16")
        else:
            data_temp = bytearray(16)
            data_temp[0:len(data)] = data
            # log.debug("data = %x" % data)
            if len(data) > 12:
                self.send_command(self.__chn, SCA_I2C_W_DATA3, struct.unpack('>I', data_temp[12:16])[0])
            if len(data) > 8:
                self.send_command(self.__chn, SCA_I2C_W_DATA2, struct.unpack('>I', data_temp[8:12])[0])
            if len(data) > 4:
                self.send_command(self.__chn, SCA_I2C_W_DATA1, struct.unpack('>I', data_temp[4:8])[0])
            self.send_command(self.__chn, SCA_I2C_W_DATA0, struct.unpack('>I', data_temp[0:4])[0])

    def get_data_reg(self, nr_bytes):
        log.debug("get_data_reg, number: %d" % nr_bytes)
        data = bytearray(nr_bytes)
        if (nr_bytes > 16) or (nr_bytes < 1):
            log.error("Bytes of data should be from 1 to 16")
        else:
            if self.r_data3():
                data3 = self.get_reg_value("rxData%d" % self.__link)
                log.debug("data3: %#04x" % data3)
                data[0:4] = struct.pack('>I', data3)

            if nr_bytes > 4:
                if self.r_data2():
                    data2 = self.get_reg_value("rxData%d" % self.__link)
                    log.debug("data2: %#04x" % data2)
                    data[4:8] = struct.pack('>I', data2)

            if nr_bytes > 8:
                if self.r_data1():
                    data1 = self.get_reg_value("rxData%d" % self.__link)
                    log.debug("data1: %#04x" % data1)
                    data[8:12] = struct.pack('>I', data1)

            if nr_bytes > 12:
                if self.r_data0():
                    data0 = self.get_reg_value("rxData%d" % self.__link)
                    log.debug("data0: %#04x" % data0)
                    data[12:16] = struct.pack('>I', data0)

            log.debug("get_data_reg: ")
            print binascii.hexlify(data)
            for b in data:
                print hex(b)
            return data

    def _write_raw8(self, slave_addr, value):
        """Write an 8-bit value on the bus (without register)."""
        log.debug("Write %#02x on the bus (without register)" % value)
        return self.s_7b_w(slave_addr, value)

    def _write_reg(self, slave_addr, register, value):
        """Write an 8-bit value to the specified register."""
        log.debug("Write %#02x to register %#02x" % (value, register))
        data = [register, value & 0xFF]
        return self._write_block(slave_addr, data)

    def _write16(self, slave_addr, register, value):
        """Write a 16-bit value to the specified register."""
        log.debug("Write %#04x to register pair %#02x, %#02x" % (value, register, register + 1))
        value = value & 0xFFFF
        data = (register << 24) | (((value >> 8) & 0xff) << 16) | ((register + 1) << 8) | (value & 0xff)
        self._write_block(slave_addr, data)

    def _read_u8(self, slave_addr, register):
        """To be able to read registers, first the register must be sent in write mode"""
        self._write_raw8(slave_addr, register)
        result = self.s_7b_r(slave_addr)
        log.debug("read_u8: %#02x" % result)
        return result

    def _read_s8(self, slave_addr, register):
        """Read a signed byte from the specified register."""
        result = self._read_u8(slave_addr, register)
        if result > 127:
            result -= 256
        log.debug("read_s8: %#02x  %d" % (result, result))
        return result

    def _read_u16(self, slave_addr, register, little_endian=True):
        """Read an unsigned 16-bit value from the specified register, with the
        specified endianness (default little endian, or least significant byte
        first)."""
        # result_bytes = self._read_block(register, 2)
        result_array = self._read_block(slave_addr, register, 2)
        result = (result_array[1] << 8) + result_array[0]
        # result = (((resultLE & 0xFF) << 8) | ((resultLE >> 8) & 0xFF)) & 0xFFFF
        # Swap bytes if using big endian because read_word_data assumes little
        # endian on ARM (little endian) systems.
        if not little_endian:
            result = ((result << 8) & 0xFF00) + (result >> 8)
        log.debug("Read 0x%04X from register pair %#02x, %#02x", result, register, register + 1)
        return result

    def _read_s16(self, slave_addr, register, little_endian=True):
        """Read a signed 16-bit value from the specified register, with the specified endianness
        (default little endian, or least significant byte first)."""
        result = self._read_u16(slave_addr, register, little_endian)
        if result > 32767:
            result -= 65536
        log.debug("read_s16: %#04x %d" % (result, result))
        return result

    def _read_u16LE(self, slave_addr, register):
        """Read an unsigned 16-bit value from the specified register, in little endian byte order."""
        return self._read_u16(slave_addr, register, little_endian=True)

    def _read_u16BE(self, slave_addr, register):
        """Read an unsigned 16-bit value from the specified register, in big
        endian byte order."""
        return self._read_u16(slave_addr, register, little_endian=False)

    def _read_s16LE(self, slave_addr, register):
        """Read a signed 16-bit value from the specified register, in little endian byte order."""
        return self._read_s16(slave_addr, register, little_endian=True)

    def _read_s16BE(self, slave_addr, register):
        """Read a signed 16-bit value from the specified register, in big
        endian byte order."""
        return self._read_s16(slave_addr, register, little_endian=False)

    def _write_block(self, slave_addr, value):
        nr_bytes = len(value)
        log.debug("write_block: length =%d" % nr_bytes)
        self.set_trans_byte_length(nr_bytes)
        self.set_data_reg(value)
        return self.m_7b_w(slave_addr)

    def _read_block(self, slave_addr, register, nr_bytes):
        log.debug("read_block, reg:%#x number:%d" % (register, nr_bytes))
        self.set_trans_byte_length(nr_bytes)
        assert 1 <= nr_bytes <= 16
        data_block = bytearray(nr_bytes)
        self.s_7b_w(slave_addr, register)
        self.m_7b_r(slave_addr)
        data_block = self.get_data_reg(nr_bytes)
        return data_block

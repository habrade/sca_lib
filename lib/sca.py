import logging

from sca_defs import *

logging.basicConfig(level=logging.INFO, format='%(asctime)s  %(name)s  %(levelname)s  %(message)s')
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

__author__ = "Sheng Dong"
__email__ = "habrade@gmail.com"


# define Python user-defined exceptions
class Error(Exception):
    """Base class for other exceptions"""
    pass


class ScaGenericError(Error):
    """Raised when the sca command get error"""
    print("SCA command error: Generic error flag")


class ScaInvalidChannelError(Error):
    """Raised when the sca command get error"""
    print("SCA command error: Invalid channel request")


class ScaInvalidCommandError(Error):
    """Raised when the sca command get error"""
    print("SCA command error: Invalid command request")


class ScaInvalidTransactionNumberError(Error):
    """Raised when the sca command get error"""
    print("SCA command error: Invalid transaction number request")


class ScaInvalidLengthError(Error):
    """Raised when the sca command get error"""
    print("SCA command error: Invalid Length")


class ScaChannelDisableError(Error):
    """Raised when the sca command get error"""
    print("SCA command error: Channel not enable")


class ScaChannelBusyError(Error):
    """Raised when the sca command get error"""
    print("SCA command error: Channel currently busy")


class ScaChannelCommandInTreatmentError(Error):
    """Raised when the sca command get error"""
    print("SCA command error: Command in treatment")


class Sca(object):
    def __init__(self, link=0):
        self.__sca_addr = 0x00
        self.__trans_id = 0x01

        self._version = SCA_VERSION
        self.__link = link

    def set_hw(self, hw):
        self.__hw = hw

    def send_command(self, channel, command, data):
        node = self.__hw.getNode("GBT-SCA.txAddr%d" % self.__link)
        node.write(self.__sca_addr)
        node = self.__hw.getNode("GBT-SCA.txTransID%d" % self.__link)
        node.write(self.__trans_id)

        self.__trans_id += 1
        if self.__trans_id == 0xff:  # 0x0 and 0xFF are reserved IDs
            self.__trans_id = 1

        node = self.__hw.getNode("GBT-SCA.txChn%d" % self.__link)
        node.write(channel)
        node = self.__hw.getNode("GBT-SCA.txCmd%d" % self.__link)
        node.write(command)
        node = self.__hw.getNode("GBT-SCA.txData%d" % self.__link)
        node.write(data)
        # start_transaction
        node = self.__hw.getNode("GBT-SCA.sendCmd%d" % self.__link)
        node.write(1)
        node.write(0)
        self.__hw.dispatch()

        log.debug("Link: %d" % self.__link)
        log.debug("    txTransID = %#02x\t" % self.get_reg_value("txTransID%d" % self.__link))
        log.debug("    rxTransID = %#02x\t" % self.get_reg_value("rxTransID%d" % self.__link))
        log.debug("    txChn = %#02x\t" % self.get_reg_value("txChn%d" % self.__link))
        log.debug("    rxChn = %#02x\t" % self.get_reg_value("rxChn%d" % self.__link))
        log.debug("    txCmd = %#02x\t" % self.get_reg_value("txCmd%d" % self.__link))
        log.debug("    rxAddr = %#02x\t" % self.get_reg_value("rxAddr%d" % self.__link))
        log.debug("    txData = %#08x\t" % self.get_reg_value("txData%d" % self.__link))
        log.debug("    rxData = %#08x\t" % self.get_reg_value("rxData%d" % self.__link))
        log.debug("    rxCtrl = %#02x\t" % self.get_reg_value("rxCtrl%d" % self.__link))
        log.debug("    rxLen = %#02x\t" % self.get_reg_value("rxLen%d" % self.__link))
        log.debug("    rxErr = %#1x\t" % self.get_reg_value("rxErr%d" % self.__link))

        rxErr = self.get_reg_value("rxErr%d" % self.__link)
        if rxErr == 0:
            return True
        else:
            try:
                self.check_error(rxErr)
            finally:
                return False

    def send_reset(self):
        node = self.__hw.getNode("GBT-SCA.rst%d" % self.__link)
        node.write(0)
        node.write(1)
        node.write(0)
        self.__hw.dispatch()

    def send_connect(self):
        node = self.__hw.getNode("GBT-SCA.connect%d" % self.__link)
        node.write(0)
        node.write(1)
        node.write(0)
        self.__hw.dispatch()

    def get_reg_value(self, reg_name):
        node_name = "GBT-SCA." + reg_name
        node = self.__hw.getNode(node_name)
        reg_val = node.read()
        self.__hw.dispatch()
        return reg_val.value()

    @staticmethod
    def check_error(err_code):
        if err_code & (0x1 << 0):
            raise ScaGenericError
        elif err_code & (0x1 << 1):
            raise ScaInvalidChannelError
        elif err_code & (0x1 << 2):
            raise ScaInvalidCommandError
        elif err_code & (0x1 << 3):
            raise ScaInvalidTransactionNumberError
        elif err_code & (0x1 << 4):
            raise ScaInvalidLengthError
        elif err_code & (0x1 << 5):
            raise ScaChannelDisableError
        elif err_code & (0x1 << 6):
            raise ScaChannelBusyError
        elif err_code & (0x1 << 7):
            raise ScaChannelCommandInTreatmentError
        else:
            pass

    def read_sca_id(self):
        sca_id = 0x000000

        readID_cmd = SCA_CTRL_R_ID_V2
        if self._version == 0x01:
            readID_cmd = SCA_CTRL_R_ID_V1

        if self.send_command(SCA_CH_ADC, readID_cmd, SCA_CTRL_DATA_R_ID):
            sca_id = self.get_reg_value("rxData%d" % self.__link)
            log.debug("Link = %d \t SCA Version = %#02x \t SCA ID = %#06x" %
                      (self.__link, self._version, sca_id))
        else:
            log.error("read_sca_id: SCA command error")
        return sca_id

    @staticmethod
    def get_node_control_cmd(chn, for_write):
        if (chn >= 1) and (chn <= 7):
            if for_write:
                return SCA_CTRL_W_CRB
            else:
                return SCA_CTRL_R_CRB
        elif (chn >= 8) and (chn <= 15):
            if for_write:
                return SCA_CTRL_W_CRC
            else:
                return SCA_CTRL_R_CRC
        elif (chn >= 16) and (chn <= 21):
            if for_write:
                return SCA_CTRL_W_CRD
            else:
                return SCA_CTRL_R_CRD
        else:
            raise Exception("get_node_control_cmd: Channel out of range")

    def get_chn_enabled(self, chn):
        if (chn >= 1) and (chn <= 31):
            read_cmd = self.get_node_control_cmd(chn, False)
            if self.send_command(SCA_CH_CTRL, read_cmd, 0):
                mask = self.get_reg_value("rxData%d" % self.__link) >> 24
                log.debug("Link = %d \t Channel Mask = %#02x" % (self.__link, mask))
                bit = chn & 0x07
                return mask & (1 << bit)
            else:
                log.error("get_chn_enabled: SCA command error")
        else:
            raise Exception("Link = %d \t Channel out of range" % self.__link)

    def enable_chn(self, chn, enabled):
        if (chn >= 1) and (chn <= 31):
            ret_send_cmd = True
            read_cmd = self.get_node_control_cmd(chn, False)
            ret_send_cmd &= self.send_command(SCA_CH_CTRL, read_cmd, 0)
            mask = self.get_reg_value("rxData%d" % self.__link) >> 24
            log.debug("Link = %d \t Channel Mask = %#02x" % (self.__link, mask))
            bit = chn & 0x07
            if enabled:
                mask |= 1 << bit
            else:
                mask &= ~(1 << bit)
            log.debug("Link = %d \t Channel new Mask = %#02x" % (self.__link, mask))
            write_cmd = self.get_node_control_cmd(chn, True)
            ret_send_cmd &= self.send_command(SCA_CH_CTRL, write_cmd, mask << 24)
            return ret_send_cmd
        else:
            raise Exception("enable_chn: Link = %d \t Channel out of range" % self.__link)

    def enable_all_channels(self):
        return (self.enable_chn(SCA_CH_SPI, True) &
                self.enable_chn(SCA_CH_GPIO, True) &
                self.enable_chn(SCA_CH_I2C0, True) &
                self.enable_chn(SCA_CH_I2C1, True) &
                self.enable_chn(SCA_CH_I2C2, True) &
                self.enable_chn(SCA_CH_I2C3, True) &
                self.enable_chn(SCA_CH_I2C4, True) &
                self.enable_chn(SCA_CH_I2C5, True) &
                self.enable_chn(SCA_CH_I2C6, True) &
                self.enable_chn(SCA_CH_I2C7, True) &
                self.enable_chn(SCA_CH_I2C8, True) &
                self.enable_chn(SCA_CH_I2C9, True) &
                self.enable_chn(SCA_CH_I2CA, True) &
                self.enable_chn(SCA_CH_I2CB, True) &
                self.enable_chn(SCA_CH_I2CC, True) &
                self.enable_chn(SCA_CH_I2CD, True) &
                self.enable_chn(SCA_CH_I2CE, True) &
                self.enable_chn(SCA_CH_I2CF, True) &
                self.enable_chn(SCA_CH_JTAG, True) &
                self.enable_chn(SCA_CH_ADC, True) &
                self.enable_chn(SCA_CH_DAC, True))

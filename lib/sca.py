import logging
import sys

import uhal

from sca_defs import *

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)


class Sca(object):
    """
    SCA basic methods
    """

    def __init__(self, sca_addr=0x00, connectionFilePath="../dpbcontrols/etc/ipbus_lab66_gdpb_gbtx.xml",
                 deviceId="C0S00_gdpb066" 
                 ):
        self.__SCA_ADDR = sca_addr
        self.__trans_id = 0x01

        self.__connectionFilePath = connectionFilePath
        self.__deviceId = deviceId
        self._version = SCA_VERSION
        # Creating the HwInterface
        self.__connectionMgr = uhal.ConnectionManager(
            "file://" + self.__connectionFilePath)
        self.__hw = self.__connectionMgr.getDevice(self.__deviceId)

    def send_command(self, channel, command, data):
        node = self.__hw.getNode("GBT-SCA.txAddr")
        node.write(self.__SCA_ADDR)
        node = self.__hw.getNode("GBT-SCA.txTransID")
        node.write(self.__trans_id)

        self.__trans_id += 1
        if self.__trans_id == 0xff:  # 0x0 and 0xFF are reserved IDs
            self.__trans_id = 1

        node = self.__hw.getNode("GBT-SCA.txChn")
        node.write(channel)
        node = self.__hw.getNode("GBT-SCA.txCmd")
        node.write(command)
        node = self.__hw.getNode("GBT-SCA.txData")
        node.write(data)
        # start_transaction
        node = self.__hw.getNode("GBT-SCA.sendCmd")
        node.write(1)
        node.write(0)
        self.__hw.dispatch()

        log.debug("    txTransID = %x\t" % self.get_reg_value("txTransID"))
        log.debug("    rxTransID = %x\n" % self.get_reg_value("rxTransID"))
        log.debug("    txChn = %x\t" % self.get_reg_value("txChn"))
        log.debug("    rxChn = %x\n" % self.get_reg_value("rxChn"))
        log.debug("    txCmd = %x\t" % self.get_reg_value("txCmd"))
        log.debug("    rxAddr = %x\n" % self.get_reg_value("rxAddr"))
        log.debug("    txData = %x\t" % self.get_reg_value("txData"))
        log.debug("    rxData = %x\n" % self.get_reg_value("rxData"))
        log.debug(" \t")
        log.debug("    rxCtrl = %x\n" % self.get_reg_value("rxCtrl"))
        log.debug(" \t")
        log.debug("    rxLen = %x\n" % self.get_reg_value("rxLen"))
        log.debug(" \t")
        log.debug("    rxErr = %x\n" % self.get_reg_value("rxErr"))

        rxErr = self.get_reg_value("rxErr")
        if rxErr != 0x00:
            # raise Exception("ERROR! SCA rxErr Code: 0x%02x" % rxErr)
            log.error("ERROR! SCA rxErr Code: 0x%02x" % rxErr)

    def send_reset(self):
        node = self.__hw.getNode("GBT-SCA.rst")
        node.write(0)
        node.write(1)
        node.write(0)
        self.__hw.dispatch()

    def send_connect(self):
        node = self.__hw.getNode("GBT-SCA.connect")
        node.write(0)
        node.write(1)
        node.write(0)
        self.__hw.dispatch()

    def get_reg_value(self, reg_name):
        node_name = "GBT-SCA." + reg_name
        node = self.__hw.getNode(node_name)
        reg_val = node.read()
        self.__hw.dispatch()
        return reg_val

    def check_error(self):
        node_name = "GBT-SCA.rx_flag"
        node = self.__hw.getNode(node_name)
        rx_flag = node.read()

        node_name = "GBT-SCA.rxErr"
        node = self.__hw.getNode(node_name)
        err_val = node.read()

        self.__hw.dispatch()

        while rx_flag == 1:
            return err_val

    def read_sca_id(self):
        if self._version == 0x01:
            self.send_command(SCA_CH_ADC, SCA_CTRL_R_ID_V1, SCA_CTRL_DATA_R_ID)
        else:
            self.send_command(SCA_CH_ADC, SCA_CTRL_R_ID_V2, SCA_CTRL_DATA_R_ID)

        log.info("SCA Version = %d" % self._version)
        sca_id = self.get_reg_value("rxData")
        log.info("SCA ID = 0x%06x" % sca_id)
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
            raise Exception("Channel out of range")

    def get_chn_enabled(self, chn):
        if (chn >= 1) and (chn <= 31):
            read_cmd = self.get_node_control_cmd(chn, False)
            self.send_command(SCA_CH_CTRL, read_cmd, 0)
            mask = self.get_reg_value("rxData") >> 24
            log.debug("Channel Mask = %02x" % mask)
            bit = chn & 0x07
            return mask & (1 << bit)
        else:
            raise Exception("Channel out of range")

    def enable_chn(self, chn, enabled):
        if (chn >= 1) and (chn <= 31):
            read_cmd = self.get_node_control_cmd(chn, False)
            self.send_command(SCA_CH_CTRL, read_cmd, 0)
            mask = self.get_reg_value("rxData") >> 24
            log.debug("Channel Mask = %02x" % mask)
            bit = chn & 0x07
            if enabled:
                mask |= 1 << bit
            else:
                mask &= ~(1 << bit)
            log.debug("Channel new Mask = %02x" % mask)
            write_cmd = self.get_node_control_cmd(chn, True)
            self.send_command(SCA_CH_CTRL, write_cmd, mask << 24)
        else:
            raise Exception("Channel out of range")

    def enable_all_channels(self):
        self.enable_chn(SCA_CH_SPI, True)
        self.enable_chn(SCA_CH_GPIO, True)
        self.enable_chn(SCA_CH_I2C0, True)
        self.enable_chn(SCA_CH_I2C1, True)
        self.enable_chn(SCA_CH_I2C2, True)
        self.enable_chn(SCA_CH_I2C3, True)
        self.enable_chn(SCA_CH_I2C4, True)
        self.enable_chn(SCA_CH_I2C5, True)
        self.enable_chn(SCA_CH_I2C6, True)
        self.enable_chn(SCA_CH_I2C7, True)
        self.enable_chn(SCA_CH_I2C8, True)
        self.enable_chn(SCA_CH_I2C9, True)
        self.enable_chn(SCA_CH_I2CA, True)
        self.enable_chn(SCA_CH_I2CB, True)
        self.enable_chn(SCA_CH_I2CC, True)
        self.enable_chn(SCA_CH_I2CD, True)
        self.enable_chn(SCA_CH_I2CE, True)
        self.enable_chn(SCA_CH_I2CF, True)
        self.enable_chn(SCA_CH_JTAG, True)
        self.enable_chn(SCA_CH_ADC, True)
        self.enable_chn(SCA_CH_DAC, True)

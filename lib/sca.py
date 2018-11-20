import logging
import sys

import uhal

import sca_defs

sys.path.append('./')

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


class Sca(object):
    """
    SCA basic methods
    """

    def __init__(self, sca_addr=0x00, connectionFilePath="etc/ipbus_lab202_gdpb_gbtx.xml", deviceId="C0S00_gdpb202",
                 debug=0):
        self.__SCA_ADDR = sca_addr
        self.__trans_id = 0x01
        self.__debug = debug

        self.__connectionFilePath = connectionFilePath
        self.__deviceId = "C0S00_gdpb202"
        # Creating the HwInterface
        self.__connectionMgr = uhal.ConnectionManager("file://" + self.__connectionFilePath)
        self.__hw = self.__connectionMgr.getDevice(deviceId)

    def _send_command(self, channel, command, data):
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

        if self.__debug:
            log.debug("    txTransID = %x\t" % self._get_reg_value("txTransID"))
            log.debug("    rxTransID = %x\n" % self._get_reg_value("rxTransID"))
            log.debug("    txChn = %x\t" % self._get_reg_value("txChn"))
            log.debug("    rxChn = %x\n" % self._get_reg_value("rxChn"))
            log.debug("    txCmd = %x\t" % self._get_reg_value("txCmd"))
            log.debug("    rxAddr = %x\n" % self._get_reg_value("rxAddr"))
            log.debug("    txData = %x\t" % self._get_reg_value("txData"))
            log.debug("    rxData = %x\n" % self._get_reg_value("rxData"))
            log.debug(" \t")
            log.debug("    rxCtrl = %x\n" % self._get_reg_value("rxCtrl"))
            log.debug(" \t")
            log.debug("    rxLen = %x\n" % self._get_reg_value("rxLen"))
            log.debug(" \t")
            log.debug("    rxErr = %x\n" % self._get_reg_value("rxErr"))

        # while True:
        #    if self.checkErr(self.__hw) == 0x00:
        #       break

    def _send_reset(self):
        node = self.__hw.getNode("GBT-SCA.rst")
        node.write(0)
        node.write(1)
        node.write(0)
        self.__hw.dispatch()

    def _send_connect(self):
        node = self.__hw.getNode("GBT-SCA.connect")
        node.write(0)
        node.write(1)
        node.write(0)
        self.__hw.dispatch()

    def _get_reg_value(self, reg_name):
        node_name = "GBT-SCA." + reg_name
        node = self.__hw.getNode(node_name)
        reg_val = node.read()
        self.__hw.dispatch()
        return reg_val

    def _check_error(self):
        node_name = "GBT-SCA.rx_flag"
        node = self.__hw.getNode(node_name)
        rx_flag = node.read()

        node_name = "GBT-SCA.rxErr"
        node = self.__hw.getNode(node_name)
        err_val = node.read()

        self.__hw.dispatch()

        while rx_flag == 1:
            return err_val

    def _read_sca_id(self):
        """Enable ADC channel, must do this before read chip ID"""
        self._send_command(sca_defs.SCA_CH_CTRL, sca_defs.SCA_CTRL_W_CRD, sca_defs.SCA_CTRL_CRD_ENADC)
        self._send_command(sca_defs.SCA_CH_ADC, sca_defs.SCA_CTRL_R_ID_V2, sca_defs.SCA_CTRL_DATA_R_ID)
        sca_id = self._get_reg_value("rxData")
        log.info("SCA ID = %x" % sca_id)
        return sca_id

    @staticmethod
    def get_node_control_cmd(chn, for_write):
        if (chn >= 1) and (chn <= 7):
            if for_write:
                return sca_defs.SCA_CTRL_W_CRB
            else:
                return sca_defs.SCA_CTRL_R_CRB
        elif (chn >= 8) and (chn <= 15):
            if for_write:
                return sca_defs.SCA_CTRL_W_CRC
            else:
                return sca_defs.SCA_CTRL_R_CRC
        elif (chn >= 16) and (chn <= 21):
            if for_write:
                return sca_defs.SCA_CTRL_W_CRD
            else:
                return sca_defs.SCA_CTRL_R_CRD
        else:
            raise Exception("Channel out of range")

    def _get_chn_enabled(self, chn):
        if (chn >= 1) and (chn <= 31):
            read_cmd = self.get_node_control_cmd(chn, False)
            self._send_command(sca_defs.SCA_CH_CTRL, read_cmd, 0)
            mask = self._get_reg_value("rxData") >> 24
            bit = chn & 0x07
            return mask & (1 << bit)
        else:
            raise Exception("Channel out of range")

    def _enable_chn(self, chn, enabled):
        read_cmd = self.get_node_control_cmd(chn, False)
        self._send_command(sca_defs.SCA_CH_CTRL, read_cmd, 0)
        mask = self._get_reg_value("rxData") >> 24
        bit = chn & 0x07
        if enabled:
            mask |= 1 << bit
        else:
            mask &= ~(1 << bit)
        write_cmd = self.get_node_control_cmd(chn, True)
        self._send_command(sca_defs.SCA_CH_CTRL, write_cmd, mask)

    def _enable_all_channels(self):
        self._enable_chn(sca_defs.SCA_CH_SPI, True)
        self._enable_chn(sca_defs.SCA_CH_GPIO, True)
        self._enable_chn(sca_defs.SCA_CH_I2C0, True)
        self._enable_chn(sca_defs.SCA_CH_I2C1, True)
        self._enable_chn(sca_defs.SCA_CH_I2C2, True)
        self._enable_chn(sca_defs.SCA_CH_I2C3, True)
        self._enable_chn(sca_defs.SCA_CH_I2C4, True)
        self._enable_chn(sca_defs.SCA_CH_I2C5, True)
        self._enable_chn(sca_defs.SCA_CH_I2C6, True)
        self._enable_chn(sca_defs.SCA_CH_I2C7, True)
        self._enable_chn(sca_defs.SCA_CH_I2C8, True)
        self._enable_chn(sca_defs.SCA_CH_I2C9, True)
        self._enable_chn(sca_defs.SCA_CH_I2CA, True)
        self._enable_chn(sca_defs.SCA_CH_I2CB, True)
        self._enable_chn(sca_defs.SCA_CH_I2CC, True)
        self._enable_chn(sca_defs.SCA_CH_I2CD, True)
        self._enable_chn(sca_defs.SCA_CH_I2CE, True)
        self._enable_chn(sca_defs.SCA_CH_I2CF, True)
        self._enable_chn(sca_defs.SCA_CH_JTAG, True)
        self._enable_chn(sca_defs.SCA_CH_ADC, True)
        self._enable_chn(sca_defs.SCA_CH_DAC, True)

import sys

import uhal

sys.path.append('./')

import sca_defs


class Sca(object):
    """
    SCA basic methods
    """
    SCA_ADDR = 0x00

    trans_id = 0x01

    debug = 0

    connectionFilePath = "etc/ipbus_lab202_gdpb_gbtx.xml"
    deviceId = "C0S00_gdpb202"
    # Creating the HwInterface
    connectionMgr = uhal.ConnectionManager("file://" + connectionFilePath)
    hw = connectionMgr.getDevice(deviceId)

    def __init__(self):
        pass

    def send_command(self, channel, command, data):
        node = self.hw.getNode("GBT-SCA.txAddr")
        node.write(self.SCA_ADDR)
        node = self.hw.getNode("GBT-SCA.txTransID")
        node.write(self.trans_id)

        self.trans_id += 1
        if self.trans_id == 0xff:  # 0x0 and 0xFF are reserved IDs
            self.trans_id = 1

        node = self.hw.getNode("GBT-SCA.txChn")
        node.write(channel)
        node = self.hw.getNode("GBT-SCA.txCmd")
        node.write(command)
        node = self.hw.getNode("GBT-SCA.txData")
        node.write(data)
        # start_transaction
        node = self.hw.getNode("GBT-SCA.sendCmd")
        node.write(1)
        node.write(0)
        self.hw.dispatch()

        if self.debug:
            print "    txTransID = %x\t" % self.get_reg_value("txTransID")
            print "    rxTransID = %x\n" % self.get_reg_value("rxTransID")
            print "    txChn = %x\t" % self.get_reg_value("txChn")
            print "    rxChn = %x\n" % self.get_reg_value("rxChn")
            print "    txCmd = %x\t" % self.get_reg_value("txCmd")
            print "    rxAddr = %x\n" % self.get_reg_value("rxAddr")
            print "    txData = %x\t" % self.get_reg_value("txData")
            print "    rxData = %x\n" % self.get_reg_value("rxData")
            print " \t"
            print "    rxCtrl = %x\n" % self.get_reg_value("rxCtrl")
            print " \t"
            print "    rxLen = %x\n" % self.get_reg_value("rxLen")
            print " \t"
            print "    rxErr = %x\n" % self.get_reg_value("rxErr")

        # while True:
        #    if self.checkErr(self.hw) == 0x00:
        #       break

    def send_reset(self):
        node = self.hw.getNode("GBT-SCA.rst")
        node.write(0)
        node.write(1)
        node.write(0)
        self.hw.dispatch()

    def send_connect(self):
        node = self.hw.getNode("GBT-SCA.connect")
        node.write(0)
        node.write(1)
        node.write(0)
        self.hw.dispatch()

    def get_reg_value(self, reg_name):
        node_name = "GBT-SCA." + reg_name
        node = self.hw.getNode(node_name)
        reg_val = node.read()
        self.hw.dispatch()
        return reg_val

    def check_error(self):
        node_name = "GBT-SCA.rx_flag"
        node = self.hw.getNode(node_name)
        rx_flag = node.read()

        node_name = "GBT-SCA.rxErr"
        node = self.hw.getNode(node_name)
        err_val = node.read()

        self.hw.dispatch()

        while rx_flag == 1:
            return err_val

    def read_sca_id(self):
        """Enable ADC channel, must do this before read chip ID"""
        self.send_command(sca_defs.SCA_CH_CTRL, sca_defs.SCA_CTRL_W_CRD, sca_defs.SCA_CTRL_CRD_ENADC)
        self.send_command(sca_defs.SCA_CH_ADC, sca_defs.SCA_CTRL_R_ID_V2, sca_defs.SCA_CTRL_DATA_R_ID)
        sca_id = self.get_reg_value("rxData")
        print "SCA ID = %x" % sca_id
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

    def get_chn_enabled(self, chn):
        if (chn >= 1) and (chn <= 31):
            read_cmd = self.get_node_control_cmd(chn, False)
            self.send_command(sca_defs.SCA_CH_CTRL, read_cmd, 0)
            mask = self.get_reg_value("rxData") >> 24
            bit = chn & 0x07
            return mask & (1 << bit)
        else:
            raise Exception("Channel out of range")

    def enable_chn(self, chn, enabled):
        read_cmd = self.get_node_control_cmd(chn, False)
        self.send_command(sca_defs.SCA_CH_CTRL, read_cmd, 0)
        mask = self.get_reg_value("rxData") >> 24
        bit = chn & 0x07
        if enabled:
            mask |= 1 << bit
        else:
            mask &= ~(1 << bit)
        write_cmd = self.get_node_control_cmd(chn, True)
        self.send_command(sca_defs.SCA_CH_CTRL, write_cmd, mask)

    def enable_all_channels(self):
        self.enable_chn(sca_defs.SCA_CH_SPI, True)
        self.enable_chn(sca_defs.SCA_CH_GPIO, True)
        self.enable_chn(sca_defs.SCA_CH_I2C0, True)
        self.enable_chn(sca_defs.SCA_CH_I2C1, True)
        self.enable_chn(sca_defs.SCA_CH_I2C2, True)
        self.enable_chn(sca_defs.SCA_CH_I2C3, True)
        self.enable_chn(sca_defs.SCA_CH_I2C4, True)
        self.enable_chn(sca_defs.SCA_CH_I2C5, True)
        self.enable_chn(sca_defs.SCA_CH_I2C6, True)
        self.enable_chn(sca_defs.SCA_CH_I2C7, True)
        self.enable_chn(sca_defs.SCA_CH_I2C8, True)
        self.enable_chn(sca_defs.SCA_CH_I2C9, True)
        self.enable_chn(sca_defs.SCA_CH_I2CA, True)
        self.enable_chn(sca_defs.SCA_CH_I2CB, True)
        self.enable_chn(sca_defs.SCA_CH_I2CC, True)
        self.enable_chn(sca_defs.SCA_CH_I2CD, True)
        self.enable_chn(sca_defs.SCA_CH_I2CE, True)
        self.enable_chn(sca_defs.SCA_CH_I2CF, True)
        self.enable_chn(sca_defs.SCA_CH_JTAG, True)
        self.enable_chn(sca_defs.SCA_CH_ADC, True)
        self.enable_chn(sca_defs.SCA_CH_DAC, True)

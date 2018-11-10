import sys

import uhal

sys.path.append('./')

import sca_defs


class Sca:
    ScaAddr = 0x00

    TransId = 0x01

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
        node.write(self.ScaAddr)
        node = self.hw.getNode("GBT-SCA.txTransID")
        node.write(self.TransId)

        self.TransId += 1
        if self.TransId == 0xff:  # 0x0 and 0xFF are reserved IDs
            self.TransId = 1

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
            print("    txTransID = %x\t") % self.getRegValue("txTransID")
            print("    rxTransID = %x\n") % self.getRegValue("rxTransID")
            print("    txChn = %x\t") % self.getRegValue("txChn")
            print("    rxChn = %x\n") % self.getRegValue("rxChn")
            print("    txCmd = %x\t") % self.getRegValue("txCmd")
            print("    rxAddr = %x\n") % self.getRegValue("rxAddr")
            print("    txData = %x\t") % self.getRegValue("txData")
            print("    rxData = %x\n") % self.getRegValue("rxData")
            print(" \t")
            print("    rxCtrl = %x\n") % self.getRegValue("rxCtrl")
            print(" \t")
            print("    rxLen = %x\n") % self.getRegValue("rxLen")
            print(" \t")
            print("    rxErr = %x\n") % self.getRegValue("rxErr")

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

    def getRegValue(self, regName):
        nodeName = "GBT-SCA." + regName
        node = self.hw.getNode(nodeName)
        regVal = node.read()
        self.hw.dispatch()
        return regVal

    def checkErr(self):
        nodeName = "GBT-SCA.rxFlag"
        node = self.hw.getNode(nodeName)
        rxFlag = node.read()

        nodeName = "GBT-SCA.rxErr"
        node = self.hw.getNode(nodeName)
        errVal = node.read()

        self.hw.dispatch()

        while rxFlag == 1:
            return errVal

    def readScaId(self):
        # Enable ADC channel, must do this before read chip ID
        self.send_command(sca_defs.SCA_CH_CTRL, sca_defs.SCA_CTRL_W_CRD, sca_defs.SCA_CTRL_CRD_ENADC)
        self.send_command(sca_defs.SCA_CH_ADC, sca_defs.SCA_CTRL_R_ID_V2, sca_defs.SCA_CTRL_DATA_R_ID)
        scaId = self.getRegValue("rxData")
        print("SCA ID = %x") % scaId
        return scaId

    def getNodeControlCmd(self, chn, forWrite):
        if (chn >= 1) and (chn <= 7):
            if forWrite:
                return sca_defs.SCA_CTRL_W_CRB
            else:
                return sca_defs.SCA_CTRL_R_CRB
        elif (chn >= 8) and (chn <= 15):
            if forWrite:
                return sca_defs.SCA_CTRL_W_CRC
            else:
                return sca_defs.SCA_CTRL_R_CRC
        elif (chn >= 16) and (chn <= 21):
            if forWrite:
                return sca_defs.SCA_CTRL_W_CRD
            else:
                return sca_defs.SCA_CTRL_R_CRD
        else:
            raise Exception("Channel out of range")

    def getChnEnabled(self, chn):
        if (chn >= 1) and (chn <= 31):
            readCmd = self.getNodeControlCmd(chn, False)
            self.send_command(sca_defs.SCA_CH_CTRL, readCmd, 0)
            mask = self.getRegValue("rxData") >> 24
            bit = chn & 0x07
            return mask & (1 << bit)
        else:
            raise Exception("Channel out of range")

    def enableChn(self, chn, enabled):
        readCmd = self.getNodeControlCmd(chn, False)
        self.send_command(sca_defs.SCA_CH_CTRL, readCmd, 0)
        mask = self.getRegValue("rxData") >> 24
        bit = chn & 0x07
        if enabled:
            mask |= 1 << bit
        else:
            mask &= ~(1 << bit)
        writeCmd = self.getNodeControlCmd(chn, True)
        self.send_command(sca_defs.SCA_CH_CTRL, writeCmd, mask)

    def enableAllChannels(self):
        self.enableChn(sca_defs.SCA_CH_SPI, True)
        self.enableChn(sca_defs.SCA_CH_GPIO, True)
        self.enableChn(sca_defs.SCA_CH_I2C0, True)
        self.enableChn(sca_defs.SCA_CH_I2C1, True)
        self.enableChn(sca_defs.SCA_CH_I2C2, True)
        self.enableChn(sca_defs.SCA_CH_I2C3, True)
        self.enableChn(sca_defs.SCA_CH_I2C4, True)
        self.enableChn(sca_defs.SCA_CH_I2C5, True)
        self.enableChn(sca_defs.SCA_CH_I2C6, True)
        self.enableChn(sca_defs.SCA_CH_I2C7, True)
        self.enableChn(sca_defs.SCA_CH_I2C8, True)
        self.enableChn(sca_defs.SCA_CH_I2C9, True)
        self.enableChn(sca_defs.SCA_CH_I2CA, True)
        self.enableChn(sca_defs.SCA_CH_I2CB, True)
        self.enableChn(sca_defs.SCA_CH_I2CC, True)
        self.enableChn(sca_defs.SCA_CH_I2CD, True)
        self.enableChn(sca_defs.SCA_CH_I2CE, True)
        self.enableChn(sca_defs.SCA_CH_I2CF, True)
        self.enableChn(sca_defs.SCA_CH_JTAG, True)
        self.enableChn(sca_defs.SCA_CH_ADC, True)
        self.enableChn(sca_defs.SCA_CH_DAC, True)

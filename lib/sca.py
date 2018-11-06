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

    # def __init__(self):

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
            print("    txTransID = "), hex(self.getRegValue("txTransID")),;
            print("    txChn = "), hex(self.getRegValue("txChn")),;
            print("    txCmd = "), hex(self.getRegValue("txCmd")),;
            print("    txData = "), hex(self.getRegValue("txData"))
            print("    rxAddr = "), hex(self.getRegValue("rxAddr")),;
            print("    rxCtrl = "), hex(self.getRegValue("rxCtrl")),;
            print("    rxTransID = "), hex(self.getRegValue("rxTransID")),;
            print("    rxChn = "), hex(self.getRegValue("rxChn")),;
            print("    rxData = "), hex(self.getRegValue("rxData")),;
            print("    rxLen = "), hex(self.getRegValue("rxLen")),;
            print("    rxErr = "), hex(self.getRegValue("rxErr"))
            print("")

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

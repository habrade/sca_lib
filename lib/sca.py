# !/usr/bin/python

import sys  # For sys.argv and sys.exit
import time

import uhal

from sca_defs import *


class Sca:

    def __init__(self):
        self.ScaAddr = 0x00
        self.TransId = 0x01

    def send_command(self, hw, channel, command, data):

        node = hw.getNode("GBT-SCA.txAddr")
        node.write(self.ScaAddr)
        node = hw.getNode("GBT-SCA.txTransID")
        node.write(self.TransId)

        self.TransId += 1
        if self.TransId == 0xff:  # 0x0 and 0xFF are reserved IDs
            self.TransId = 1

        node = hw.getNode("GBT-SCA.txChn")
        node.write(channel)
        node = hw.getNode("GBT-SCA.txCmd")
        node.write(command)
        node = hw.getNode("GBT-SCA.txData")
        node.write(data)
        # start_transaction
        node = hw.getNode("GBT-SCA.sendCmd")
        node.write(1)
        node.write(0)
        hw.dispatch()

        debug = 1
        if debug:
            print("    txTransID = "), hex(self.getRegValue(hw, "txTransID")),;
            print("    txChn = "), hex(self.getRegValue(hw, "txChn")),;
            print("    txCmd = "), hex(self.getRegValue(hw, "txCmd")),;
            print("    txData = "), hex(self.getRegValue(hw, "txData"))
            print("    rxAddr = "), hex(self.getRegValue(hw, "rxAddr")),;
            print("    rxCtrl = "), hex(self.getRegValue(hw, "rxCtrl")),;
            print("    rxTransID = "), hex(self.getRegValue(hw, "rxTransID")),;
            print("    rxChn = "), hex(self.getRegValue(hw, "rxChn")),;
            print("    rxData = "), hex(self.getRegValue(hw, "rxData")),;
            print("    rxLen = "), hex(self.getRegValue(hw, "rxLen")),;
            print("    rxErr = "), hex(self.getRegValue(hw, "rxErr"))
            print("")

        #while True:
        #    if self.checkErr(hw) == 0x00:
        #       break

    def send_reset(self, hw):
        node = hw.getNode("GBT-SCA.rst")
        node.write(0)
        node.write(1)
        node.write(0)
        hw.dispatch()

    def send_connect(self, hw):
        node = hw.getNode("GBT-SCA.connect")
        node.write(0)
        node.write(1)
        node.write(0)
        hw.dispatch()

    def getRegValue(self, hw, regName):
        nodeName = "GBT-SCA." + regName
        node = hw.getNode(nodeName)
        regVal = node.read()
        hw.dispatch()
        return regVal

    def checkErr(self, hw):
        nodeName = "GBT-SCA.rxFlag"
        node = hw.getNode(nodeName)
        rxFlag = node.read()

        nodeName = "GBT-SCA.rxErr"
        node = hw.getNode(nodeName)
        errVal = node.read()

        hw.dispatch()

        while rxFlag == 1:
            return errVal

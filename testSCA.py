#!/usr/bin/python

import random  # For randint
import sys  # For sys.argv and sys.exit
import time

import uhal

sys.path.append('./lib')
import sca
import sca_defs

if __name__ == '__main__':
    connectionFilePath = "etc/ipbus_lab202_gdpb_gbtx.xml"
    deviceId = "C0S00_gdpb202"

    # Creating the HwInterface
    connectionMgr = uhal.ConnectionManager("file://" + connectionFilePath)
    hw = connectionMgr.getDevice(deviceId)

    debug = 1

    sca_dev = sca.Sca()

    # Reset Chip
    sca_dev.send_reset(hw)
    # Connect SCA chip
    sca_dev.send_connect(hw)

    # Enable ADC channel, must do this before read chip ID
    sca_dev.send_command(hw, 0x00, 0x06, 0x10000000)
    # Read the Chip ID
    print("Read Chip ID")
    # SCA V1
    # sca_dev.send_command(hw, scaAddr, 0x02, 0x14, 0x91, 0x00000001)
    # SCA V2
    sca_dev.send_command(hw, 0x14, 0xD1, 0x00000001)
    print("Chip ID = "), hex(sca_dev.getRegValue(hw, "rxData"))

    # Enable GPIO
    print("Enable GPIO")
    sca_dev.send_command(hw, 0x00, 0x02, 0xff00000)

    # GPIO Direction Set, 1 -> output mode
    print("GPIO Direction Set, 1 -> output mode, 0 -> input mode")
    sca_dev.send_command(hw, 0x02, 0x20, 0xffffffff)

    # GPIO Direction READ
    print("GPIO Direction READ")
    sca_dev.send_command(hw, 0x02, 0x21, 0x00000000)
    print("Direction = "), hex(sca_dev.getRegValue(hw, "rxData"))

    # set GPIO value
    print("set GPIO value: 0xffffffff")
    sca_dev.send_command(hw, 0x02, 0x10, 0xffffffff)

    print("Get GPIO value")
    sca_dev.send_command(hw, 0x02, 0x11, 0x00000000)
    print("GPIO = "), hex(sca_dev.getRegValue(hw, "rxData"))
    if sca_dev.getRegValue(hw, "rxData") == 0xffffffff:
        print("Set to HIGH pass!")
    else:
        raise ValueError('oops!')

    print("set GPIO value: 0x00000000")
    sca_dev.send_command(hw, 0x02, 0x10, 0x00000000)
    if debug:
        print("Get GPIO value")
    sca_dev.send_command(hw, 0x02, 0x11, 0x00000000)
    print("GPIO = "), hex(sca_dev.getRegValue(hw, "rxData"))
    if sca_dev.getRegValue(hw, "rxData") == 0x00000000:
        print("Set to LOW pass!")
    else:
        raise ValueError('oops!')

    print(" ")
    print("test ADC")
    print(" ")

    while 1:
        sca_dev.send_command(hw, 0x14, 0x50, 0x00000008)
        sca_dev.send_command(hw, 0x14, 0x51, 0x00000000)
        # print ("Sel = "), hex(getRegValue(hw, "rxData"))
        sca_dev.send_command(hw, 0x14, 0x02, 0x00000001)
        print("ADC CH 8 = "), hex(sca_dev.getRegValue(hw, "rxData"))

        sca_dev.send_command(hw, 0x14, 0x50, 0x00000006)
        sca_dev.send_command(hw, 0x14, 0x51, 0x00000000)
        # print ("Sel = "), hex(sca_dev.getRegValue(hw, "rxData"))
        sca_dev.send_command(hw, 0x14, 0x02, 0x00000001)
        print("ADC CH 6 = "), hex(sca_dev.getRegValue(hw, "rxData"))

        sca_dev.send_command(hw, 0x14, 0x50, 0x0000001F)
        sca_dev.send_command(hw, 0x14, 0x51, 0x00000000)
        # print ("Sel = "), hex(sca_dev.getRegValue(hw, "rxData"))
        sca_dev.send_command(hw, 0x14, 0x02, 0x00000001)
        # sca_dev.send_command(hw,0x14, 0x41, 0x00000000)
        print("TEMP = "), hex(sca_dev.getRegValue(hw, "rxData"))
        time.sleep(1)

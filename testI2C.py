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
    # send_command(hw, 0x14, 0x91, 0x00000001)
    # SCA V2
    sca_dev.send_command(hw, 0x14, 0xD1, 0x00000001)
    print("Chip ID = "), hex(sca_dev.getRegValue(hw, "rxData"))

    # Enable I2C ch. 0
    sca_dev.send_command(hw, 0x00, 0x02, 0x08000000)

    # Control register:
    #   FREQ[1:0]   : "00" -> 100kHz, "01" -> 200kHz, "10" -> 400kHz, "11" -> 1MHz
    #   NBYTE[6:2]  : Number of bytes to be transmitted (used only for multi-byte transmission)
    #   SCLMODE[7]  : '0' -> Open-drain (Z/GND), '1' -> CMOS (VCC/GND)
    #
    #   Configuration:
    #       Multi-byte mode : ENABLED       -> ADDR + 2 bytes : < Register >< Value >
    #       Frequency       : 100kHz
    #       SCL mode        : Open-drain
    #
    #       Value           : 8'b00001000   -> 8'h08
    sca_dev.send_command(hw, 0x03, 0x30, 0x88000000)

    # send reset
    sca_dev.send_command(hw, 0x03, 0x40, 0xE0B60000)
    sca_dev.send_command(hw, 0x03, 0xDA, 0x77000000)
    sca_dev.send_command(hw, 0x03, 0x41, 0x00000000)
    time.sleep(1)

    # read ID
    sca_dev.send_command(hw, 0x03, 0x82, 0x77D00000)
    time.sleep(1)
    sca_dev.send_command(hw, 0x03, 0x86, 0x77000000)

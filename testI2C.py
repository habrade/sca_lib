#!/usr/bin/python

import sys  # For sys.argv and sys.exit

sys.path.append('./lib')
import scaI2c
import sca_defs

if __name__ == '__main__':
    sca_dev = scaI2c.ScaI2c()
    # Reset Chip
    sca_dev.send_reset()
    # Connect SCA chip
    sca_dev.send_connect()

    chipId = sca_dev.readScaId()
    print "SCA ID = %x" % chipId

    # Enable I2C ch. 0
    sca_dev.enableChn(sca_defs.SCA_CH_I2C0)

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
    sca_dev.send_command(sca_defs.SCA_CH_I2C0, sca_defs.SCA_I2C_W_CTRL, 0x88000000)

    # send reset
    sca_dev.send_command(sca_defs.SCA_CH_I2C0, 0x40, 0xE0B60000)
    sca_dev.send_command(sca_defs.SCA_CH_I2C0, 0xDA, 0x77000000)
    sca_dev.send_command(sca_defs.SCA_CH_I2C0, 0x41, 0x00000000)

    # read ID
    sca_dev.send_command(sca_defs.SCA_CH_I2C0, 0x82, 0x77D00000)
    sca_dev.send_command(sca_defs.SCA_CH_I2C0, 0x86, 0x77000000)

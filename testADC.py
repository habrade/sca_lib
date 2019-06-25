#!/usr/bin/env python
import sys
import time
import pvaccess
import logging

from lib import sca_adc

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

if __name__ == '__main__':

    sca_dev = sca_adc.ScaAdc(version=2)

    # Reset Chip
    sca_dev.send_reset()
    # Connect SCA chip
    sca_dev.send_connect()

    sca_id = sca_dev.read_sca_id()
    log.info("SCA ID = %x" % sca_id)

    PREFIX = "labtest:"

    # adc_value = []
    while True:
        sca_id_ch = pvaccess.Channel(PREFIX + "SCA:ID")
        sca_id_ch.put(int(sca_id))

        for i in range(32):
            sca_dev.w_sel(i)
            sca_dev.r_data()
            adc_value = sca_dev.start_conv()

            log.debug("ADC Ch %d = %x" % (i, adc_value))

            ch_name = PREFIX + "SCA:ADC:CH:" + str(i)
            ca_ch = pvaccess.Channel(ch_name)
            ca_ch.putUInt(int(adc_value))

        time.sleep(0.1)

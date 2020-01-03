import logging
import time

from bme280_defs import *
from sca_defs import *

logging.basicConfig(level=logging.INFO, format='%(asctime)s  %(name)s  %(levelname)s  %(message)s')
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

__author__ = "Sheng Dong"
__email__ = "s.dong@mails.ccnu.edu.cn"


class Bme280(object):
    def __init__(self, sca_i2c, t_mode=BME280_OSAMPLE_8, p_mode=BME280_OSAMPLE_8,
                 h_mode=BME280_OSAMPLE_8,
                 standby=BME280_STANDBY_250,
                 set_filter=BME280_FILTER_off):  # change here master out SCA_CH_I2C0 or SCA_CH_I2C1
        super(Bme280, self).__init__()

        self._sca_i2c = sca_i2c

        # Check that t_mode is valid.
        if t_mode not in [BME280_OSAMPLE_1, BME280_OSAMPLE_2, BME280_OSAMPLE_4,
                          BME280_OSAMPLE_8, BME280_OSAMPLE_16]:
            raise ValueError(
                'Unexpected t_mode value {0}.'.format(t_mode))
        self._t_mode = t_mode
        # Check that p_mode is valid.
        if p_mode not in [BME280_OSAMPLE_1, BME280_OSAMPLE_2, BME280_OSAMPLE_4,
                          BME280_OSAMPLE_8, BME280_OSAMPLE_16]:
            raise ValueError(
                'Unexpected p_mode value {0}.'.format(p_mode))
        self._p_mode = p_mode
        # Check that h_mode is valid.
        if h_mode not in [BME280_OSAMPLE_1, BME280_OSAMPLE_2, BME280_OSAMPLE_4,
                          BME280_OSAMPLE_8, BME280_OSAMPLE_16]:
            raise ValueError(
                'Unexpected h_mode value {0}.'.format(h_mode))
        self._h_mode = h_mode
        # Check that standby is valid.
        if standby not in [BME280_STANDBY_0p5, BME280_STANDBY_62p5,
                           BME280_STANDBY_125, BME280_STANDBY_250,
                           BME280_STANDBY_500, BME280_STANDBY_1000,
                           BME280_STANDBY_10, BME280_STANDBY_20]:
            raise ValueError(
                'Unexpected standby value {0}.'.format(standby))
        self._standby = standby
        # Check that filter is valid.
        if set_filter not in [BME280_FILTER_off, BME280_FILTER_2, BME280_FILTER_4,
                              BME280_FILTER_8, BME280_FILTER_16]:
            raise ValueError(
                'Unexpected filter value {0}.'.format(set_filter))
        self._filter = set_filter
        self.t_fine = 0.0
        # self._initial_sensor()

    def initial_sensor(self):
        self._sca_i2c.set_frq(SCA_I2C_SPEED_1000)
        self._sca_i2c.set_mode(SCA_I2C_MODE_OPEN_DRAIN)
        self.rst_dev()
        self._load_calibration()

        self._sca_i2c.write_reg(BME280_I2CADDR, BME280_REGISTER_CONTROL, 0x24)  # Sleep mode
        time.sleep(0.002)
        self._sca_i2c.write_reg(BME280_I2CADDR, BME280_REGISTER_CONFIG, ((self._standby << 5) | (self._filter << 2)))
        time.sleep(0.002)
        self._sca_i2c.write_reg(BME280_I2CADDR, BME280_REGISTER_CONTROL_HUM, self._h_mode)  # Set Humidity Oversample
        self._sca_i2c.write_reg(BME280_I2CADDR, BME280_REGISTER_CONTROL,
                                ((self._t_mode << 5) | (
                                        self._p_mode << 2) | 3))  # Set Temp/Pressure Oversample and enter Normal mode

    def _load_calibration(self):

        self.dig_T1 = self._sca_i2c.read_u16le(BME280_I2CADDR, BME280_REGISTER_DIG_T1)
        self.dig_T2 = self._sca_i2c.read_s16le(BME280_I2CADDR, BME280_REGISTER_DIG_T2)
        self.dig_T3 = self._sca_i2c.read_s16le(BME280_I2CADDR, BME280_REGISTER_DIG_T3)

        self.dig_P1 = self._sca_i2c.read_u16le(BME280_I2CADDR, BME280_REGISTER_DIG_P1)
        self.dig_P2 = self._sca_i2c.read_s16le(BME280_I2CADDR, BME280_REGISTER_DIG_P2)
        self.dig_P3 = self._sca_i2c.read_s16le(BME280_I2CADDR, BME280_REGISTER_DIG_P3)
        self.dig_P4 = self._sca_i2c.read_s16le(BME280_I2CADDR, BME280_REGISTER_DIG_P4)
        self.dig_P5 = self._sca_i2c.read_s16le(BME280_I2CADDR, BME280_REGISTER_DIG_P5)
        self.dig_P6 = self._sca_i2c.read_s16le(BME280_I2CADDR, BME280_REGISTER_DIG_P6)
        self.dig_P7 = self._sca_i2c.read_s16le(BME280_I2CADDR, BME280_REGISTER_DIG_P7)
        self.dig_P8 = self._sca_i2c.read_s16le(BME280_I2CADDR, BME280_REGISTER_DIG_P8)
        self.dig_P9 = self._sca_i2c.read_s16le(BME280_I2CADDR, BME280_REGISTER_DIG_P9)

        self.dig_H1 = self._sca_i2c.read_u8(BME280_I2CADDR, BME280_REGISTER_DIG_H1)
        self.dig_H2 = self._sca_i2c.read_s16le(BME280_I2CADDR, BME280_REGISTER_DIG_H2)
        self.dig_H3 = self._sca_i2c.read_u8(BME280_I2CADDR, BME280_REGISTER_DIG_H3)
        self.dig_H6 = self._sca_i2c.read_s8(BME280_I2CADDR, BME280_REGISTER_DIG_H7)

        try:
            h4 = self._sca_i2c.read_s8(BME280_I2CADDR, BME280_REGISTER_DIG_H4)
            h4 = (h4 << 4)
            self.dig_H4 = h4 | (self._sca_i2c.read_u8(BME280_I2CADDR, BME280_REGISTER_DIG_H5) & 0x0F)

            h5 = self._sca_i2c.read_s8(BME280_I2CADDR, BME280_REGISTER_DIG_H6)
            h5 = (h5 << 4)
            self.dig_H5 = h5 | (self._sca_i2c.read_u8(BME280_I2CADDR, BME280_REGISTER_DIG_H5) >> 4 & 0x0F)

            log.debug("dig_T1 = %d" % self.dig_T1)
            log.debug("dig_T2 = %d" % self.dig_T2)
            log.debug("dig_T3 = %d" % self.dig_T3)

            log.debug("dig_P1 = %d" % self.dig_P1)
            log.debug("dig_P2 = %d" % self.dig_P2)
            log.debug("dig_P3 = %d" % self.dig_P3)
            log.debug("dig_P4 = %d" % self.dig_P4)
            log.debug("dig_P5 = %d" % self.dig_P5)
            log.debug("dig_P6 = %d" % self.dig_P6)
            log.debug("dig_P7 = %d" % self.dig_P7)
            log.debug("dig_P8 = %d" % self.dig_P8)
            log.debug("dig_P9 = %d" % self.dig_P9)

            # log.debug("0xE4 = %#02x" % self._read_u8(BME280_REGISTER_DIG_H4))
            # log.debug("0xE5 = %#02x" % self._read_u8(BME280_REGISTER_DIG_H5))
            # log.debug("0xE6 = %#02x" % self._read_u8(BME280_REGISTER_DIG_H6))
            log.debug("dig_H1 = %d" % self.dig_H1)
            log.debug("dig_H2 = %d" % self.dig_H2)
            log.debug("dig_H3 = %d" % self.dig_H3)
            log.debug("dig_H4 = %d" % self.dig_H4)
            log.debug("dig_H5 = %d" % self.dig_H5)
            log.debug("dig_H6 = %d" % self.dig_H6)

        except TypeError:
            self.dig_H4 = 0
            self.dig_H5 = 0

    def rst_dev(self):
        return self._sca_i2c.write_reg(BME280_I2CADDR, BME280_REGISTER_SOFTRESET, 0xB6)

    # def set_sensor_mode(self, mode):
    #     mode_list = [BME280_MODE_NORMAL_SLEEP, BME280_MODE_SLEEP_NORMAL, BME280_MODE_SLEEP_FORCE]
    #     if mode in mode_list:
    #         self._ctrl_meas = (mode << 0) | (self._ctrl_meas & 0xfc)
    #         self._write_reg(BME280_REGISTER_CONTROL, self._ctrl_meas)
    #     else:
    #         raise Exception("Mode out of index")

    def read_id(self):
        try:
            return self._sca_i2c.read_u8(BME280_I2CADDR, BME280_REGISTER_CHIPID)
        except TypeError:
            pass

    def read_raw_temp(self):
        """Waits for reading to become available on device."""
        """Does a single burst read of all data values from device."""
        """Returns the raw (uncompensated) temperature from the sensor."""
        log.debug("First check whether BME280 Status OK!")
        try:
            while (self._sca_i2c.read_u8(BME280_I2CADDR,
                                         BME280_REGISTER_STATUS) & 0x08):  # Wait for conversion to complete (TODO : add timeout)
                time.sleep(0.002)
            self.BME280Data = self._sca_i2c.read_block(BME280_I2CADDR, BME280_REGISTER_DATA, 8)
        except TypeError:
            self.BME280Data = bytearray(8)

        for data in self.BME280Data:
            log.debug("BME280 Data: %#x" % data)

        raw = ((self.BME280Data[3] << 16) | (self.BME280Data[4] << 8) | self.BME280Data[5]) >> 4
        log.debug("raw temperature: %#x" % raw)
        return raw

    def read_raw_pressure(self):
        """Returns the raw (uncompensated) pressure level from the sensor."""
        """Assumes that the temperature has already been read """
        """i.e. that self.BME280Data[] has been populated."""
        raw = ((self.BME280Data[0] << 16) | (self.BME280Data[1] << 8) | self.BME280Data[2]) >> 4
        log.debug("raw pressure: %#x" % raw)
        return raw

    def read_raw_humidity(self):
        """Returns the raw (uncompensated) humidity value from the sensor."""
        """Assumes that the temperature has already been read """
        """i.e. that self.BME280Data[] has been populated."""
        raw = (self.BME280Data[6] << 8) | self.BME280Data[7]
        log.debug("raw humidity: %#x" % raw)
        return raw

    def read_temperature(self):
        """Gets the compensated temperature in degrees celsius."""
        # float in Python is double precision
        try:
            UT = float(self.read_raw_temp())

            var1 = (UT / 16384.0 - float(self.dig_T1) / 1024.0) * \
                   float(self.dig_T2)
            var2 = ((UT / 131072.0 - float(self.dig_T1) / 8192.0) * (
                    UT / 131072.0 - float(self.dig_T1) / 8192.0)) * float(self.dig_T3)
            self.t_fine = int(var1 + var2)
            temp = (var1 + var2) / 5120.0
            return temp
        except TypeError:
            return 0

    def read_pressure(self):
        """Gets the compensated pressure in Pascals."""
        adc = float(self.read_raw_pressure())
        var1 = float(self.t_fine) / 2.0 - 64000.0
        var2 = var1 * var1 * float(self.dig_P6) / 32768.0
        var2 = var2 + var1 * float(self.dig_P5) * 2.0
        var2 = var2 / 4.0 + float(self.dig_P4) * 65536.0
        var1 = (float(self.dig_P3) * var1 * var1 / 524288.0 +
                float(self.dig_P2) * var1) / 524288.0
        var1 = (1.0 + var1 / 32768.0) * float(self.dig_P1)
        if var1 == 0:
            return 0
        p = 1048576.0 - adc
        p = ((p - var2 / 4096.0) * 6250.0) / var1
        var1 = float(self.dig_P9) * p * p / 2147483648.0
        var2 = p * float(self.dig_P8) / 32768.0
        p = p + (var1 + var2 + float(self.dig_P7)) / 16.0
        return p

    def read_humidity(self):
        try:
            adc = float(self.read_raw_humidity())
            # print 'Raw humidity = {0:d}'.format (adc)
            h = float(self.t_fine) - 76800.0
            h = (adc - (float(self.dig_H4) * 64.0 + float(self.dig_H5) / 16384.0 * h)) * (
                    float(self.dig_H2) / 65536.0 * (
                    1.0 + float(self.dig_H6) / 67108864.0 * h * (1.0 + float(self.dig_H3) / 67108864.0 * h)))
            h = h * (1.0 - float(self.dig_H1) * h / 524288.0)
            if h > 100:
                h = 100
            elif h < 0:
                h = 0
            return h
        except TypeError:
            return 0

    def read_temperature_f(self):
        # Wrapper to get temp in F
        celsius = self.read_temperature()
        temp = celsius * 1.8 + 32
        return temp

    def read_pressure_inches(self):
        # Wrapper to get pressure in inches of Hg
        pascals = self.read_pressure()
        inches = pascals * 0.0002953
        return inches

    def read_dewpoint(self):
        # Return calculated dewpoint in C, only accurate at > 50% RH
        celsius = self.read_temperature()
        humidity = self.read_humidity()
        dewpoint = celsius - ((100 - humidity) / 5)
        return dewpoint

    def read_dewpoint_f(self):
        # Return calculated dewpoint in F, only accurate at > 50% RH
        dewpoint_c = self.read_dewpoint()
        dewpoint_f = dewpoint_c * 1.8 + 32
        return dewpoint_f

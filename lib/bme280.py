import logging
import sys
import time

import sca_i2c

sys.path.append('./')

import bme280_defs


class BME280(sca_i2c.ScaI2c):
    def __init__(self, t_mode=bme280_defs.BME280_OSAMPLE_1, p_mode=bme280_defs.BME280_OSAMPLE_1,
                 h_mode=bme280_defs.BME280_OSAMPLE_1,
                 standby=bme280_defs.BME280_STANDBY_250, filter=bme280_defs.BME280_FILTER_off,
                 **kwargs):
        sca_i2c.ScaI2c.__init__(chn=0)
        self._logger = logging.getLogger('__name__')
        # Check that t_mode is valid.
        if t_mode not in [bme280_defs.BME280_OSAMPLE_1, bme280_defs.BME280_OSAMPLE_2, bme280_defs.BME280_OSAMPLE_4,
                          bme280_defs.BME280_OSAMPLE_8, bme280_defs.BME280_OSAMPLE_16]:
            raise ValueError(
                'Unexpected t_mode value {0}.'.format(t_mode))
        self._t_mode = t_mode
        # Check that p_mode is valid.
        if p_mode not in [bme280_defs.BME280_OSAMPLE_1, bme280_defs.BME280_OSAMPLE_2, bme280_defs.BME280_OSAMPLE_4,
                          bme280_defs.BME280_OSAMPLE_8, bme280_defs.BME280_OSAMPLE_16]:
            raise ValueError(
                'Unexpected p_mode value {0}.'.format(p_mode))
        self._p_mode = p_mode
        # Check that h_mode is valid.
        if h_mode not in [bme280_defs.BME280_OSAMPLE_1, bme280_defs.BME280_OSAMPLE_2, bme280_defs.BME280_OSAMPLE_4,
                          bme280_defs.BME280_OSAMPLE_8, bme280_defs.BME280_OSAMPLE_16]:
            raise ValueError(
                'Unexpected h_mode value {0}.'.format(h_mode))
        self._h_mode = h_mode
        # Check that standby is valid.
        if standby not in [bme280_defs.BME280_STANDBY_0p5, bme280_defs.BME280_STANDBY_62p5,
                           bme280_defs.BME280_STANDBY_125, bme280_defs.BME280_STANDBY_250,
                           bme280_defs.BME280_STANDBY_500, bme280_defs.BME280_STANDBY_1000,
                           bme280_defs.BME280_STANDBY_10, bme280_defs.BME280_STANDBY_20]:
            raise ValueError(
                'Unexpected standby value {0}.'.format(standby))
        self._standby = standby
        # Check that filter is valid.
        if filter not in [bme280_defs.BME280_FILTER_off, bme280_defs.BME280_FILTER_2, bme280_defs.BME280_FILTER_4,
                          bme280_defs.BME280_FILTER_8, bme280_defs.BME280_FILTER_16]:
            raise ValueError(
                'Unexpected filter value {0}.'.format(filter))
        self._filter = filter
        # Create I2C device.
        # if i2c is None:
        #     import Adafruit_GPIO.I2C as I2C
        #     i2c = I2C
        # # Create device, catch permission errors
        # try:
        #     self._device = i2c.get_i2c_device(address, **kwargs)
        # except IOError:
        #     print("Unable to communicate with sensor, check permissions.")
        #     exit()
        # Load calibration values.
        self._load_calibration()
        self._device.write8(bme280_defs.BME280_REGISTER_CONTROL, 0x24)  # Sleep mode
        time.sleep(0.002)
        self._device.write8(bme280_defs.BME280_REGISTER_CONFIG, ((standby << 5) | (filter << 2)))
        time.sleep(0.002)
        self._device.write8(bme280_defs.BME280_REGISTER_CONTROL_HUM, h_mode)  # Set Humidity Oversample
        self._device.write8(bme280_defs.BME280_REGISTER_CONTROL, (
                (t_mode << 5) | (p_mode << 2) | 3))  # Set Temp/Pressure Oversample and enter Normal mode
        self.t_fine = 0.0

    def _load_calibration(self):

        self.dig_T1 = self._device.readU16LE(bme280_defs.BME280_REGISTER_DIG_T1)
        self.dig_T2 = self._device.readS16LE(bme280_defs.BME280_REGISTER_DIG_T2)
        self.dig_T3 = self._device.readS16LE(bme280_defs.BME280_REGISTER_DIG_T3)

        self.dig_P1 = self._device.readU16LE(bme280_defs.BME280_REGISTER_DIG_P1)
        self.dig_P2 = self._device.readS16LE(bme280_defs.BME280_REGISTER_DIG_P2)
        self.dig_P3 = self._device.readS16LE(bme280_defs.BME280_REGISTER_DIG_P3)
        self.dig_P4 = self._device.readS16LE(bme280_defs.BME280_REGISTER_DIG_P4)
        self.dig_P5 = self._device.readS16LE(bme280_defs.BME280_REGISTER_DIG_P5)
        self.dig_P6 = self._device.readS16LE(bme280_defs.BME280_REGISTER_DIG_P6)
        self.dig_P7 = self._device.readS16LE(bme280_defs.BME280_REGISTER_DIG_P7)
        self.dig_P8 = self._device.readS16LE(bme280_defs.BME280_REGISTER_DIG_P8)
        self.dig_P9 = self._device.readS16LE(bme280_defs.BME280_REGISTER_DIG_P9)

        self.dig_H1 = self._device.readU8(bme280_defs.BME280_REGISTER_DIG_H1)
        self.dig_H2 = self._device.readS16LE(bme280_defs.BME280_REGISTER_DIG_H2)
        self.dig_H3 = self._device.readU8(bme280_defs.BME280_REGISTER_DIG_H3)
        self.dig_H6 = self._device.readS8(bme280_defs.BME280_REGISTER_DIG_H7)

        h4 = self._device.readS8(bme280_defs.BME280_REGISTER_DIG_H4)
        h4 = (h4 << 4)
        self.dig_H4 = h4 | (self._device.readU8(bme280_defs.BME280_REGISTER_DIG_H5) & 0x0F)

        h5 = self._device.readS8(bme280_defs.BME280_REGISTER_DIG_H6)
        h5 = (h5 << 4)
        self.dig_H5 = h5 | (
                self._device.readU8(bme280_defs.BME280_REGISTER_DIG_H5) >> 4 & 0x0F)

        '''
        print '0xE4 = {0:2x}'.format (self._device.readU8 (bme280_defs.BME280_REGISTER_DIG_H4))
        print '0xE5 = {0:2x}'.format (self._device.readU8 (bme280_defs.BME280_REGISTER_DIG_H5))
        print '0xE6 = {0:2x}'.format (self._device.readU8 (bme280_defs.BME280_REGISTER_DIG_H6))
        print 'dig_H1 = {0:d}'.format (self.dig_H1)
        print 'dig_H2 = {0:d}'.format (self.dig_H2)
        print 'dig_H3 = {0:d}'.format (self.dig_H3)
        print 'dig_H4 = {0:d}'.format (self.dig_H4)
        print 'dig_H5 = {0:d}'.format (self.dig_H5)
        print 'dig_H6 = {0:d}'.format (self.dig_H6)
        '''

    def read_raw_temp(self):
        """Waits for reading to become available on device."""
        """Does a single burst read of all data values from device."""
        """Returns the raw (uncompensated) temperature from the sensor."""
        while (self._device.readU8(
                bme280_defs.BME280_REGISTER_STATUS) & 0x08):  # Wait for conversion to complete (TODO : add timeout)
            time.sleep(0.002)
        self.bme280_defs.BME280Data = self._device.readList(bme280_defs.BME280_REGISTER_DATA, 8)
        raw = ((self.bme280_defs.BME280Data[3] << 16) | (self.bme280_defs.BME280Data[4] << 8) |
               self.bme280_defs.BME280Data[5]) >> 4
        return raw

    def read_raw_pressure(self):
        """Returns the raw (uncompensated) pressure level from the sensor."""
        """Assumes that the temperature has already been read """
        """i.e. that bme280_defs.BME280Data[] has been populated."""
        raw = ((self.bme280_defs.BME280Data[0] << 16) | (self.bme280_defs.BME280Data[1] << 8) |
               self.bme280_defs.BME280Data[2]) >> 4
        return raw

    def read_raw_humidity(self):
        """Returns the raw (uncompensated) humidity value from the sensor."""
        """Assumes that the temperature has already been read """
        """i.e. that bme280_defs.BME280Data[] has been populated."""
        raw = (self.bme280_defs.BME280Data[6] << 8) | self.bme280_defs.BME280Data[7]
        return raw

    def read_temperature(self):
        """Gets the compensated temperature in degrees celsius."""
        # float in Python is double precision
        UT = float(self.read_raw_temp())
        var1 = (UT / 16384.0 - float(self.dig_T1) / 1024.0) * float(self.dig_T2)
        var2 = ((UT / 131072.0 - float(self.dig_T1) / 8192.0) * (
                UT / 131072.0 - float(self.dig_T1) / 8192.0)) * float(self.dig_T3)
        self.t_fine = int(var1 + var2)
        temp = (var1 + var2) / 5120.0
        return temp

    def read_pressure(self):
        """Gets the compensated pressure in Pascals."""
        adc = float(self.read_raw_pressure())
        var1 = float(self.t_fine) / 2.0 - 64000.0
        var2 = var1 * var1 * float(self.dig_P6) / 32768.0
        var2 = var2 + var1 * float(self.dig_P5) * 2.0
        var2 = var2 / 4.0 + float(self.dig_P4) * 65536.0
        var1 = (
                       float(self.dig_P3) * var1 * var1 / 524288.0 + float(self.dig_P2) * var1) / 524288.0
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
        adc = float(self.read_raw_humidity())
        # print 'Raw humidity = {0:d}'.format (adc)
        h = float(self.t_fine) - 76800.0
        h = (adc - (float(self.dig_H4) * 64.0 + float(self.dig_H5) / 16384.0 * h)) * (
                float(self.dig_H2) / 65536.0 * (1.0 + float(self.dig_H6) / 67108864.0 * h * (
                1.0 + float(self.dig_H3) / 67108864.0 * h)))
        h = h * (1.0 - float(self.dig_H1) * h / 524288.0)
        if h > 100:
            h = 100
        elif h < 0:
            h = 0
        return h

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


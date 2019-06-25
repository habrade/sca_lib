import logging
import sys
import time
import struct

import sca_i2c
import bme280_defs
from bme280_defs import *


class BME280(sca_i2c.ScaI2c):
    def __init__(self, t_mode=BME280_OSAMPLE_1, p_mode=BME280_OSAMPLE_1,
                 h_mode=BME280_OSAMPLE_1,
                 standby=BME280_STANDBY_250, set_filter=BME280_FILTER_off,
                 version=2, **kwargs):
        sca_i2c.ScaI2c.__init__(self, chn=0, version=version)
        self._log = logging.getLogger('__name__')
        self.BME280Data = []
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

        self._load_calibration()
        self._write8(BME280_REGISTER_CONTROL, 0x24)  # Sleep mode
        time.sleep(0.002)
        self._write8(BME280_REGISTER_CONFIG,
                     ((standby << 5) | (set_filter << 2)))
        time.sleep(0.002)
        self._write8(BME280_REGISTER_CONTROL_HUM,
                     h_mode)  # Set Humidity Oversample
        self._write8(BME280_REGISTER_CONTROL,
                     ((t_mode << 5) | (p_mode << 2) | 3))  # Set Temp/Pressure Oversample and enter Normal mode
        self.t_fine = 0.0

    def _load_calibration(self):

        self.dig_T1 = self._read_u16LE(BME280_REGISTER_DIG_T1)
        self.dig_T2 = self._read_s16LE(BME280_REGISTER_DIG_T2)
        self.dig_T3 = self._read_s16LE(BME280_REGISTER_DIG_T3)

        self.dig_P1 = self._read_u16LE(BME280_REGISTER_DIG_P1)
        self.dig_P2 = self._read_s16LE(BME280_REGISTER_DIG_P2)
        self.dig_P3 = self._read_s16LE(BME280_REGISTER_DIG_P3)
        self.dig_P4 = self._read_s16LE(BME280_REGISTER_DIG_P4)
        self.dig_P5 = self._read_s16LE(BME280_REGISTER_DIG_P5)
        self.dig_P6 = self._read_s16LE(BME280_REGISTER_DIG_P6)
        self.dig_P7 = self._read_s16LE(BME280_REGISTER_DIG_P7)
        self.dig_P8 = self._read_s16LE(BME280_REGISTER_DIG_P8)
        self.dig_P9 = self._read_s16LE(BME280_REGISTER_DIG_P9)

        self.dig_H1 = self._read_u8(BME280_REGISTER_DIG_H1)
        self.dig_H2 = self._read_s16LE(BME280_REGISTER_DIG_H2)
        self.dig_H3 = self._read_u8(BME280_REGISTER_DIG_H3)
        self.dig_H6 = self._read_s8(BME280_REGISTER_DIG_H7)

        h4 = self._read_s8(BME280_REGISTER_DIG_H4)
        h4 = (h4 << 4)
        self.dig_H4 = h4 | (self._read_u8(
            BME280_REGISTER_DIG_H5) & 0x0F)

        h5 = self._read_s8(BME280_REGISTER_DIG_H6)
        h5 = (h5 << 4)
        self.dig_H5 = h5 | (
            self._read_u8(BME280_REGISTER_DIG_H5) >> 4 & 0x0F)

        '''
        print '0xE4 = {0:2x}'.format (self._read_u8 (BME280_REGISTER_DIG_H4))
        print '0xE5 = {0:2x}'.format (self._read_u8 (BME280_REGISTER_DIG_H5))
        print '0xE6 = {0:2x}'.format (self._read_u8 (BME280_REGISTER_DIG_H6))
        print 'dig_H1 = {0:d}'.format (self.dig_H1)
        print 'dig_H2 = {0:d}'.format (self.dig_H2)
        print 'dig_H3 = {0:d}'.format (self.dig_H3)
        print 'dig_H4 = {0:d}'.format (self.dig_H4)
        print 'dig_H5 = {0:d}'.format (self.dig_H5)
        print 'dig_H6 = {0:d}'.format (self.dig_H6)
        '''

    def _write_raw8(self, value):
        """Write an 8-bit value on the bus (without register)."""
        self._log.debug("Write 0x%02 on the bus (without register)", value)
        return self.s_7b_w(BME280_I2CADDR, value)

    def _write8(self, register, value):
        """Write an 8-bit value to the specified register."""
        self._log.debug("Write 0x%02X to register 0x%02X", value, register)
        data = [register, value & 0xFF]
        return self._write_block(bytes(data))

    def _write16(self, register, value):
        """Write a 16-bit value to the specified register."""
        self._log.debug(
            "Write 0x%04X to register pair 0x%02X, 0x%02X", value, register, register + 1)
        value = value & 0xFFFF
        self._write_block((register << 24) | ((value & 0xff) << 16) | (
            register + 1) << 8 | (value >> 8 & 0xff))

    def _read_u8(self, register):
        """To be able to read registers, first the register must be sent in write mode"""
        self._write_raw8(register)
        return self.s_7b_r(BME280_I2CADDR)

    def _read_s8(self, register):
        """Read a signed byte from the specified register."""
        result = self._read_u8(register)
        if result > 127:
            result -= 256
        return result

    def _read_u16(self, register, little_endian=True):
        """Read an unsigned 16-bit value from the specified register, with the
        specified endianness (default little endian, or least significant byte
        first)."""
        resultBytes = self._read_block(register, 2)
        result = struct.unpack('>H', resultBytes)[0]
        self._log.debug(
            "Read 0x%04X from register pair 0x%02X, 0x%02X", result, register, register + 1)
        # Swap bytes if using big endian because read_word_data assumes little
        # endian on ARM (little endian) systems.
        if not little_endian:
            result = ((result << 8) & 0xFF00) + (result >> 8)
        return result

    def _read_s16(self, register, little_endian=True):
        """Read a signed 16-bit value from the specified register, with the specified endianness
        (default little endian, or least significant byte first)."""
        result = self._read_u16(register, little_endian)
        if result > 32767:
            result -= 65536
        return result

    def _read_u16LE(self, register):
        """Read an unsigned 16-bit value from the specified register, in little endian byte order."""
        return self._read_u16(register, little_endian=True)

    def _read_u16BE(self, register):
        """Read an unsigned 16-bit value from the specified register, in big
        endian byte order."""
        return self._read_u16(register, little_endian=False)

    def _read_s16LE(self, register):
        """Read a signed 16-bit value from the specified register, in little endian byte order."""
        return self._read_s16(register, little_endian=True)

    def _read_s16BE(self, register):
        """Read a signed 16-bit value from the specified register, in big
        endian byte order."""
        return self._read_s16(register, little_endian=False)

    def _write_block(self, value):
        nr_bytes = len(value)
        self.set_trans_byte_length(nr_bytes)
        self.set_data_reg(value)
        return self.m_7b_w(BME280_I2CADDR)

    def _read_block(self, register, nr_bytes):
        self._write_raw8(register)
        self.set_trans_byte_length(nr_bytes)
        if self.m_7b_r(BME280_I2CADDR):
            return self.get_data_reg(nr_bytes)
        else:
            self._log.error("Error during read")

    def rst_dev(self):
        self._write8(BME280_REGISTER_SOFTRESET, 0xB6)

    def read_id(self):
        return self._read_u8(BME280_REGISTER_CHIPID)

    def read_raw_temp(self):
        """Waits for reading to become available on device."""
        """Does a single burst read of all data values from device."""
        """Returns the raw (uncompensated) temperature from the sensor."""
        while (self._read_u8(
                BME280_REGISTER_STATUS) & 0x08):  # Wait for conversion to complete (TODO : add timeout)
            time.sleep(0.002)
        self.BME280Data = self._read_block(BME280_REGISTER_DATA, 8)
        raw = ((self.BME280Data[3] << 16) | (self.BME280Data[4] << 8) |
               self.BME280Data[5]) >> 4
        return raw

    def read_raw_pressure(self):
        """Returns the raw (uncompensated) pressure level from the sensor."""
        """Assumes that the temperature has already been read """
        """i.e. that self.BME280Data[] has been populated."""
        raw = ((self.BME280Data[0] << 16) | (self.BME280Data[1] << 8) |
               self.BME280Data[2]) >> 4
        return raw

    def read_raw_humidity(self):
        """Returns the raw (uncompensated) humidity value from the sensor."""
        """Assumes that the temperature has already been read """
        """i.e. that self.BME280Data[] has been populated."""
        raw = (self.BME280Data[6] << 8) | self.BME280Data[7]
        return raw

    def read_temperature(self):
        """Gets the compensated temperature in degrees celsius."""
        # float in Python is double precision
        UT = float(self.read_raw_temp())
        var1 = (UT / 16384.0 - float(self.dig_T1) / 1024.0) * \
            float(self.dig_T2)
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
        adc = float(self.read_raw_humidity())
        # print 'Raw humidity = {0:d}'.format (adc)
        h = float(self.t_fine) - 76800.0
        h = (adc - (float(self.dig_H4) * 64.0 + float(self.dig_H5) / 16384.0 * h)) * (float(self.dig_H2) / 65536.0 * (
            1.0 + float(self.dig_H6) / 67108864.0 * h * (1.0 + float(self.dig_H3) / 67108864.0 * h)))
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

# SPDX-FileCopyrightText: 2018 ktown for Adafruit Industries
#
# SPDX-License-Identifier: MIT

"""
`adafruit_htu21d`
====================================================

This is a breakout for the Adafruit HTU21D-F Temperature & Humidity
Sensor Breakout Board

* Author(s): ktown

Implementation Notes
--------------------

**Hardware:**

* `Adafruit HTU21D-F Temperature & Humidity Sensor Breakout Board
  <https://www.adafruit.com/product/1899>`_ (Product ID: 1899)

**Software and Dependencies:**

* Adafruit CircuitPython firmware for the supported boards:
  https://circuitpython.org/downloads

* Adafruit's Bus Device library:
  https://github.com/adafruit/Adafruit_CircuitPython_BusDevice

"""
try:
    import struct
except ImportError:
    import ustruct as struct

import time
from adafruit_bus_device.i2c_device import I2CDevice
from micropython import const

__version__ = "0.0.0-auto.0"
__repo__ = "https://github.com/adafruit/Adafruit_CircuitPython_HTU21D.git"

HUMIDITY = const(0xF5)
TEMPERATURE = const(0xF3)
_RESET = const(0xFE)
_WRITE_USER1 = const(0xE6)
_READ_USER1 = const(0xE7)
_USER1_VAL = const(0x3A)

_TEMP_RH_RES = (0, 1, 128, 129)


def _crc(data):
    crc = 0
    for byte in data:
        crc ^= byte
        for _ in range(8):
            if crc & 0x80:
                crc <<= 1
                crc ^= 0x131
            else:
                crc <<= 1
    return crc


class HTU21D:
    """
    A driver for the HTU21D-F temperature and humidity sensor.
    :param i2c_bus: The I2C bus the device is connected to
    :param int address: (optional) The I2C address of the device. Defaults to :const:`0x40`

    **Quickstart: Importing and using the HTU21D-F**

        Here is an example of using the :class:`HTU21D` class.
        First you will need to import the libraries to use the sensor

        .. code-block:: python

            import board
            from adafruit_htu21d import HTU21D

        Once this is done you can define your `board.I2C` object and define your sensor object

        .. code-block:: python

            i2c = board.I2C()  # uses board.SCL and board.SDA
            sensor = HTU21D(i2c)

        Now you have access to the :attr:`temperature` and :attr:`relative_humidity` attributes

        .. code-block:: python

            temperature = sensor.temperature
            relative_humidity = sensor.relative_humidity


    """

    def __init__(self, i2c_bus, address=0x40):
        self.i2c_device = I2CDevice(i2c_bus, address)
        self._command(_RESET)
        self._measurement = 0
        self._buffer = bytearray(3)
        time.sleep(0.01)

    def _command(self, command):
        with self.i2c_device as i2c:
            i2c.write(struct.pack("B", command))

    def _data(self):
        data = bytearray(3)
        while True:
            # While busy, the sensor doesn't respond to reads.
            try:
                with self.i2c_device as i2c:
                    i2c.readinto(data)
                    if data[0] != 0xFF:  # Check if read succeeded.
                        break
            except OSError:
                pass
        value, checksum = struct.unpack(">HB", data)
        if checksum != _crc(data[:2]):
            raise ValueError("CRC mismatch")
        return value

    @property
    def relative_humidity(self):
        """The measured relative humidity in percent."""
        self.measurement(HUMIDITY)
        self._measurement = 0
        time.sleep(0.016)
        return self._data() * 125.0 / 65536.0 - 6.0

    @property
    def temperature(self):
        """The measured temperature in degrees Celsius."""
        self.measurement(TEMPERATURE)
        self._measurement = 0
        time.sleep(0.050)
        return self._data() * 175.72 / 65536.0 - 46.85

    def measurement(self, what):
        """
        Starts a measurement.
        Starts a measurement of either ``HUMIDITY`` or ``TEMPERATURE``
        depending on the ``what`` argument. Returns immediately, and the
        result of the measurement can be retrieved with the
        :attr:`temperature` and :attr:`relative_humidity` properties. This way it
        will take much less time.
        This can be useful if you want to start the measurement, but don't
        want the call to block until the measurement is ready -- for instance,
        when you are doing other things at the same time.
        """
        if what not in (HUMIDITY, TEMPERATURE):
            raise ValueError()
        if not self._measurement:
            self._command(what)
        elif self._measurement != what:
            raise RuntimeError("other measurement in progress")
        self._measurement = what

    @property
    def temp_rh_resolution(self):
        """The temperature and relative humidity resolution

        Have one of the following values: [#f1]_

            =======  ==============  ==============
             value       RH res %        T res C
            =======  ==============  ==============
               0      0.04 (12bit)    0.01 (14bit)
               1      0.7  (8bit)     0.04 (12bit)
               2      0.17 (10bit)    0.02 (13bit)
               3      0.08 (11bit)    0.08 (11bit)
            =======  ==============  ==============


        .. [#f1] HTU21D(F) RH/T Sensor IC Datasheet. TE connectivity. 2017. p13

        """

        self._buffer[0] = _READ_USER1
        with self.i2c_device as i2c:
            i2c.write_then_readinto(self._buffer, self._buffer, out_end=1)

        return self._buffer[0]

    @temp_rh_resolution.setter
    def temp_rh_resolution(self, value):
        self._buffer[0] = _READ_USER1
        with self.i2c_device as i2c:
            i2c.write_then_readinto(self._buffer, self._buffer, out_end=1)

        register = (self._buffer[0] & 0xFE) | _TEMP_RH_RES[value]

        self._buffer[0] = 0xE6
        self._buffer[1] = register

        with self.i2c_device as i2c:
            i2c.write(self._buffer)

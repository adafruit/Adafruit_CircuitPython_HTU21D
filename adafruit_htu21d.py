# The MIT License (MIT)
#
# Copyright (c) 2018 ktown for Adafruit Industries
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

"""
`adafruit_htu21d`
====================================================

This is a breakout for the Adafruit HTU21D-F humidity sensor breakout.

* Author(s): ktown

Implementation Notes
--------------------

**Hardware:**

* Adafruit `HTU21D-F Temperature & Humidity Sensor Breakout Board
  <https://www.adafruit.com/product/1899>`_ (Product ID: 1899)

**Software and Dependencies:**

* Adafruit CircuitPython firmware for the supported boards:
  https://github.com/adafruit/circuitpython/releases

* Adafruit's Bus Device library:
  https://github.com/adafruit/Adafruit_CircuitPython_BusDevice
"""
try:
    import struct
except ImportError:
    import ustruct as struct

from adafruit_bus_device.i2c_device import I2CDevice
from micropython import const

__version__ = "0.0.0-auto.0"
__repo__ = "https://github.com/adafruit/Adafruit_CircuitPython_HTU21D.git"

HUMIDITY = const(0xf5)
TEMPERATURE = const(0xf3)
_RESET = const(0xfe)
_READ_USER1 = const(0xe7)
_USER1_VAL = const(0x3a)


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
    :param i2c_bus: The `busio.I2C` object to use. This is the only
    required parameter.
    :param int address: (optional) The I2C address of the device.
    """

    def __init__(self, i2c_bus, address=0x40):
        self.i2c_device = I2CDevice(i2c_bus, address)
        self._command(_RESET)
        self._measurement = 0

    def _command(self, command):
        with self.i2c_device as i2c:
            i2c.write(struct.pack('B', command))

    def _data(self):
        data = bytearray(3)
        while True:
            # While busy, the sensor doesn't respond to reads.
            try:
                with self.i2c_device as i2c:
                    i2c.readinto(data)
                    if data[0] != 0xff:  # Check if read succeeded.
                        break
            except OSError:
                pass
        value, checksum = struct.unpack('>HB', data)
        if checksum != _crc(data[:2]):
            raise ValueError("CRC mismatch")
        return value

    @property
    def relative_humidity(self):
        """The measured relative humidity in percent."""
        self.measurement(HUMIDITY)
        self._measurement = 0
        return self._data() * 125.0 / 65536.0 - 6.0

    @property
    def temperature(self):
        """The measured temperature in degrees Celcius."""
        self.measurement(TEMPERATURE)
        self._measurement = 0
        return self._data() * 175.72 / 65536.0 - 46.85

    def measurement(self, what):
        """
        Starts a measurement.
        Starts a measurement of either ``HUMIDITY`` or ``TEMPERATURE``
        depending on the ``what`` argument. Returns immediately, and the
        result of the measurement can be retrieved with the
        ``temperature`` and ``relative_humidity`` properties. This way it
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

# SPDX-FileCopyrightText: 2021 ladyada for Adafruit Industries
# SPDX-License-Identifier: MIT

import time

import board

from adafruit_htu21d import HTU21D

# Create sensor object, communicating over the board's default I2C bus
i2c = board.I2C()  # uses board.SCL and board.SDA
# i2c = board.STEMMA_I2C()  # For using the built-in STEMMA QT connector on a microcontroller
sensor = HTU21D(i2c)


while True:
    print(f"\nTemperature: {sensor.temperature:0.1f} C")
    print(f"Humidity: {sensor.relative_humidity:0.1f} %")
    time.sleep(2)

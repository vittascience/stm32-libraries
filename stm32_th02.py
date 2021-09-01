"""
MicroPython for Grove Temperature&Humidity (TH02) sensor (I2C)
https://github.com/vittascience/stm32-libraries
https://wiki.seeedstudio.com/Grove-TemptureAndHumidity_Sensor-High-Accuracy_AndMini-v1.0/

MIT License
Copyright (c) 2021 leomlr (Léo Meillier)

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

from time import sleep

class TH02:
  """
  Interface to the TH02 temp/humidity sensor.
  """
  CHECK_DELAY = 0.025

  CONVERSION_TEMP = 0x11
  # Convert without the built-in heater
  CONVERSION_HUMIDITY = 0x01

  REGISTER_STATUS = 0x00
  REGISTER_DATAH = 0x01
  REGISTER_DATAL = 0x02
  REGISTER_CONFIG = 0x03

  ADDRESS = 0x40

  def __init__(self, i2c):
    self.i2c = i2c

  def init_temp(self):
    """Send command to TH02 for convert temperature"""

  def init_humidity(self):
    """Send command to TH02 for convert humidity"""
    self.i2c.write_register(self.ADDRESS,
                self.REGISTER_CONFIG,
                self.CONVERSION_HUMIDITY)

  def is_ready(self):
    """Is sensor done with conversion"""
    status = self.i2c.read_register(self.ADDRESS,
                    self.REGISTER_STATUS)
    # Extract ready bit
    ready = not (status & 0x01)
    return bool(ready)

  def wait_until_ready(self):
    "Wait until conversion completes"
    sleep(self.CHECK_DELAY)
    for _ in range(8):
      if self.is_ready():
        return True
      sleep(self.CHECK_DELAY)
    return False

  def read_data(self):
    """Read the DATA registers"""
    data = self.i2c.read_register(self.ADDRESS, self.REGISTER_DATAH)
    data = data << 8
    data |= self.i2c.read_register(self.ADDRESS, self.REGISTER_DATAL)
    return data

  def calculate_temp(self, data):
    """Calculate temperature from register value"""
    temp = data >> 2
    temp /= 32.0
    temp -= 50.0
    return temp

  def calculate_humidity(self, data):
    """Calculate humidity from register value"""
    humidity = data >> 4
    humidity /= 16.0
    humidity -= 24.0
    return humidity

  def get_temperature(self):
    """Return temperature or -60 if there is an error"""
    self.i2c.write_register(self.ADDRESS,
                self.REGISTER_CONFIG,
                self.CONVERSION_TEMP)
    if self.wait_until_ready():
      data = self.read_data()
      return self.calculate_temp(data)

    # Error
    return -60

  def get_humidity(self):
    """Return relative humidity or -60 if there is an error"""
    self.i2c.write_register(self.ADDRESS,
                self.REGISTER_CONFIG,
                self.CONVERSION_HUMIDITY)

    if self.wait_until_ready():
      data = self.read_data()
      return self.calculate_humidity(data)

    # Error
    return -60

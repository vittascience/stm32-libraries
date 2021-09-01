"""
MicroPython for Grove Temperature&Humidity sensors (DHT11/DHT22)
https://github.com/vittascience/stm32-libraries

https://stm32python.gitlab.io/fr/docs/Micropython/grove/DHT
https://wiki.seeedstudio.com/Grove-TemperatureAndHumidity_Sensor/
https://wiki.seeedstudio.com/Grove-Temperature_and_Humidity_Sensor_Pro/

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

import dht

class DHTBase:
  def __init__(self, pin):
    self.pin = pin
    self.buf = bytearray(5)

  def measure(self):
    buf = self.buf
    dht.dht_readinto(self.pin, buf)
    if (buf[0] + buf[1] + buf[2] + buf[3]) & 0xFF != buf[4]:
      raise Exception("checksum error")

class DHT11(DHTBase):
  def humidity(self):
    return self.buf[0]
  def temperature(self):
    return self.buf[2]

class DHT22(DHTBase):
  def humidity(self):
    return (self.buf[0] << 8 | self.buf[1]) * 0.1
  def temperature(self):
    t = ((self.buf[2] & 0x7F) << 8 | self.buf[3]) * 0.1
    if self.buf[2] & 0x80:
      t = -t
    return t

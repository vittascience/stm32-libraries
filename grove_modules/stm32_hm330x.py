"""
MicroPython for Grove Laser PM2.5 Sensor (HM3301) (I2C)
https://github.com/vittascience/stm32-libraries
https://wiki.seeedstudio.com/Grove-Laser_PM2.5_Sensor-HM3301/

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

import utime

HM330_I2C_ADDR = 0x40
HM330_INIT = 0x80
HM330_MEM_ADDR = 0x88

class HM330X:

  def __init__(self, i2c, addr=HM330_I2C_ADDR):
    self._i2c = i2c
    self._addr = addr
    self._write([HM330_INIT])

  def read_data(self):
    return self._i2c.readfrom_mem(self._addr, HM330_MEM_ADDR, 29)

  def _write(self, buffer):
    self._i2c.writeto(self._addr, bytearray(buffer))

  def check_crc(self, data):
    sum=0
    for i in range(29-1):
      sum+=data[i]
    sum=sum&0xff
    return (sum==data[28])

  def parse_data(self, data):
    std_PM1=data[4]<<8|data[5]
    std_PM2_5=data[6]<<8|data[7]
    std_PM10=data[8]<<8|data[9]
    atm_PM1=data[10]<<8|data[11]          
    atm_PM2_5=data[12]<<8|data[13]
    atm_PM10=data[14]<<8|data[15]
    return [std_PM1,std_PM2_5,std_PM10,atm_PM1,atm_PM2_5,atm_PM10]

  def getData(self, select):
    datas=self.read_data()
    utime.sleep_ms(5)
    if(self.check_crc(datas)==True):
      data_parsed=self.parse_data(datas)
      return data_parsed[select]`;

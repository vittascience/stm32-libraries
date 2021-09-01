"""
MicroPython for Grove 16x2 LCD Series (I2C)
https://github.com/vittascience/stm32-libraries
https://wiki.seeedstudio.com/Grove-16x2_LCD_Series/

MIT License
Copyright (c) 2020 leomlr (Léo Meillier)

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

from utime import sleep_ms

LCD_I2C_ADDR = 0x3e
LCD_COMMAND = 0x80

# commands
LCD_CLEARDISPLAY = 0x01
LCD_RETURNHOME = 0x02
LCD_ENTRYMODESET = 0x04
LCD_DISPLAYCONTROL = 0x08
LCD_CURSORSHIFT = 0x10
LCD_FUNCTIONSET = 0x20
LCD_SETCGRAMADDR = 0x40
LCD_SETDDRAMADDR = 0x80

# flags for display entry mode
LCD_ENTRYRIGHT = 0x00
LCD_ENTRYLEFT = 0x02
LCD_ENTRYSHIFTINCREMENT = 0x01
LCD_ENTRYSHIFTDECREMENT = 0x00

# flags for display on/off control
LCD_DISPLAYON = 0x04
LCD_DISPLAYOFF = 0x00
LCD_CURSORON = 0x02
LCD_CURSOROFF = 0x00
LCD_BLINKON = 0x01
LCD_BLINKOFF = 0x00

# flags for display/cursor shift
LCD_DISPLAYMOVE = 0x08
LCD_CURSORMOVE = 0x00
LCD_MOVERIGHT = 0x04
LCD_MOVELEFT = 0x00

# flags for function set
LCD_8BITMODE = 0x10
LCD_4BITMODE = 0x00
LCD_2LINE = 0x08
LCD_1LINE = 0x00
LCD_5x10DOTS = 0x04
LCD_5x8DOTS = 0x00

class LCD1602:

  """ Initialize instance of LCD1602 """
  def __init__(self, i2c, addr=LCD_I2C_ADDR):
    self._i2c = i2c
    self._addr = addr
    self.fct = LCD_5x10DOTS|LCD_2LINE
    sleep_ms(50)
    self._command(LCD_FUNCTIONSET|self.fct)
    sleep_ms(4500)
    self._command(LCD_FUNCTIONSET|self.fct)
    sleep_ms(150)
    self._command(LCD_FUNCTIONSET|self.fct)
    self._command(LCD_FUNCTIONSET|self.fct)
    self.ctrl = LCD_DISPLAYON|LCD_CURSORON|LCD_BLINKOFF
    self._command(self.ctrl)
    self.clear()
    self.mod = LCD_ENTRYLEFT|LCD_ENTRYSHIFTDECREMENT
    self._command(LCD_ENTRYMODESET|self.mod)
    self.display(True)

  """ Write any text on screen """
  def writeTxt(self, text):
    for char in text:
      self.write_char(ord(char))

  """ Write any character on screen """
  def write_char(self, char):
    self._write([0x40, char])

  """ Place cursor on screen at (x, y) """
  def setCursor(self, x, y):
    x = (x|0x80) if y == 0 else (x|0xc0)
    self._write([0x80, x])

  """ Active display """
  def display(self, s):
    if s:
      self.ctrl |= LCD_DISPLAYON
      self._command(LCD_DISPLAYCONTROL|self.ctrl)
    else:
      self.ctrl &= ~LCD_DISPLAYON
      self._command(LCD_DISPLAYCONTROL|self.ctrl)

  """ Write any text on screen"""
  def cursor(self, s):
    if s:
      self.ctrl |= LCD_CURSORON
      self._command(LCD_DISPLAYCONTROL|self.ctrl)
    else:
      self.ctrl &= ~LCD_CURSORON
      self._command(LCD_DISPLAYCONTROL|self.ctrl)

  """ Return to home """
  def home(self):
    self._command(LCD_RETURNHOME)
    sleep_ms(2)

  """ Clear screen """
  def clear(self):
    self._command(LCD_CLEARDISPLAY)
    sleep_ms(2)

  """ Write i2c buffer """
  def _write(self, buffer):
    self._i2c.writeto(self._addr, bytearray(buffer))

  """ Send i2c command """
  def _command(self, cmd):
    self._write([LCD_COMMAND, cmd])

"""
MicroPython for Grove - RGB LED Matrix (MY92221)
https://github.com/vittascience/stm32-libraries
https://wiki.seeedstudio.com/Grove-RGB_LED_Matrix_w-Driver/ 

MIT License
Copyright (c) 2022 leomlr (Léo Meillier)

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

from micropython import const
import utime

I2C_CMD_CONTINUE_DATA = const(0x81)

GROVE_TWO_RGB_LED_MATRIX_DEF_I2C_ADDR = const(0x65) # L'adresse i2c de l'appareil par défaut
GROVE_TWO_RGB_LED_MATRIX_VID = const(0x2886) # ID de fournisseur de l'appareil
GROVE_TWO_RGB_LED_MATRIX_PID = const(0x8005) # ID produit de l'appareil

I2C_CMD_GET_DEV_ID = const(0x00) # Cette commande obtient les informations d'ID de périphérique
I2C_CMD_DISP_BAR = const(0x01) # Cette commande affiche la barre de LED
I2C_CMD_DISP_EMOJI = const(0x02) # Cette commande affiche les emoji
I2C_CMD_DISP_NUM = const(0x03) # Cette commande affiche le numéro
I2C_CMD_DISP_STR = const(0x04) # Cette commande affiche la chaîne
I2C_CMD_DISP_CUSTOM = const(0x05) # Cette commande affiche les images définies par l'utilisateur
I2C_CMD_DISP_OFF = const(0x06) # Cette commande nettoie l'affichage
I2C_CMD_DISP_ASCII = const(0x07) # ne pas utiliser
I2C_CMD_DISP_FLASH = const(0x08) # Cette commande affiche les images qui sont stockées en flash
I2C_CMD_DISP_COLOR_BAR = const(0x09) # Cette commande affiche une barre de led colorée
I2C_CMD_DISP_COLOR_WAVE = const(0x0a) # Cette commande affiche l'animation d'onde intégrée
I2C_CMD_DISP_COLOR_CLOCKWISE = const(0x0b) # Cette commande affiche l'animation intégrée dans le sens des aiguilles d'une montre
I2C_CMD_DISP_COLOR_ANIMATION = const(0x0c) # Cette commande affiche une autre animation intégrée
I2C_CMD_DISP_COLOR_BLOCK = const(0x0d) # Cette commande affiche une couleur définie par l'utilisateur
I2C_CMD_STORE_FLASH = const(0xa0) # Cette commande stocke les trames en flash
I2C_CMD_DELETE_FLASH = const(0xa1) # Cette commande supprime toutes les trames en flash

I2C_CMD_LED_ON = const(0xb0) # Cette commande allume le mode flash de l'indicateur LED
I2C_CMD_LED_OFF = const(0xb1) # Cette commande éteint le mode flash de l'indicateur LED
I2C_CMD_AUTO_SLEEP_ON = const(0xb2) # Cette commande active le mode veille automatique de l'appareil
I2C_CMD_AUTO_SLEEP_OFF = const(0xb3) # Cette commande désactive le mode veille automatique de l'appareil (mode par défaut)

I2C_CMD_DISP_ROTATE = const(0xb4) # Cette commande définit l'orientation de l'affichage
I2C_CMD_DISP_OFFSET = const(0xb5) # Cette commande définit le décalage d'affichage

I2C_CMD_SET_ADDR = const(0xc0) # Cette commande définit l'adresse i2c du périphérique
I2C_CMD_RST_ADDR = const(0xc1) # Cette commande réinitialise l'adresse i2c du périphérique
I2C_CMD_TEST_TX_RX_ON = const(0xe0) # Cette commande active le mode de test de la broche TX RX
I2C_CMD_TEST_TX_RX_OFF = const(0xe1) # Cette commande désactive le mode de test de la broche TX RX
I2C_CMD_TEST_GET_VER = const(0xe2) # Cette commande est utilisée pour obtenir la version du logiciel
I2C_CMD_GET_DEVICE_UID = const(0xf1) # Cette commande est utilisée pour obtenir l'identifiant de la puce

orientation_type_t = {
  'DISPLAY_ROTATE_0': 0,
  'DISPLAY_ROTATE_90': 1,
  'DISPLAY_ROTATE_180': 2,
  'DISPLAY_ROTATE_270': 3
}

COULEURS = {
  'rouge': 0x00,
  'orange': 0x12,
  'jaune': 0x18,
  'vert': 0x52,
  'cyan': 0x7f,
  'bleu': 0xaa,
  'violet': 0xc3,
  'rose': 0xdc,
  'blanc': 0xfe,
  'noir': 0xff
}

class GroveTwoRGBLedMatrix(object):
  def __init__(self, i2c = None, base = GROVE_TWO_RGB_LED_MATRIX_DEF_I2C_ADDR, screenNumber = 1):
    self.i2c = i2c
    self.offsetAddress = screenNumber - 1
    self.baseAddress = base
    self._addr = self.offsetAddress + self.baseAddress

  def getDeviceVID(self):
    self.i2c.writeto(self._addr, bytes([I2C_CMD_GET_DEV_ID]))
    data = self.i2c.readfrom(self._addr, 4)
    return data[0] + data[1] * 256

  def getDevicePID(self):
    self.i2c.writeto(self._addr, bytes([I2C_CMD_GET_DEV_ID]))
    data = self.i2c.readfrom(self._addr, 4)
    return data[2] + data[3] * 256

  def changeDeviceBaseAddress(self, newAddress):
    if not (newAddress >= 0x10 and newAddress <= 0x70):
      newAddress = GROVE_TWO_RGB_LED_MATRIX_DEF_I2C_ADDR
    data = [I2C_CMD_SET_ADDR, newAddress]
    self.baseAddress = newAddress
    self.i2c.writeto(self._addr, bytes(data))
    self._addr = self.baseAddress + self.offsetAddress
    utime.sleep_ms(200)

  def defaultDeviceAddress(self):
    self.i2c.writeto(self._addr, bytes([I2C_CMD_RST_ADDR]))
    self.baseAddress = GROVE_TWO_RGB_LED_MATRIX_DEF_I2C_ADDR
    self._addr = self.baseAddress + self.offsetAddress
    utime.sleep_ms(200)

  def turnOnLedFlash(self):
    self.i2c.writeto(self._addr, bytes([I2C_CMD_LED_ON]))

  def turnOffLedFlash(self):
    self.i2c.writeto(self._addr, bytes([I2C_CMD_LED_OFF]))

  def enableAutoSleep(self):
    self.i2c.writeto(self._addr, bytes([I2C_CMD_AUTO_SLEEP_ON]))

  def wakeDevice(self):
    utime.sleep_us(200)

  def disableAutoSleep(self):
    self.i2c.writeto(self._addr, bytes([I2C_CMD_AUTO_SLEEP_OFF]))

  def setDisplayOrientation(self, orientation):
    data = [I2C_CMD_DISP_ROTATE, orientation]
    self.i2c.writeto(self._addr, bytes(data))

  def setDisplayOffset(self, offset_x, offset_y):
    # convert to positive
    offset_x += 8
    offset_y += 8
    if offset_x < 0:
      offset_x = 0
    elif offset_x > 16:
      offset_x = 16
    if offset_y < 0:
      offset_y = 0
    elif offset_y > 16:
      offset_y = 16

    data = [I2C_CMD_DISP_OFFSET, offset_x, offset_y]
    self.i2c.writeto(self._addr, bytes(data))

  def displayBar(self, bar, duration_time, forever_flag, color):
    if bar > 32:
      bar = 32
    data = [I2C_CMD_DISP_BAR, bar, duration_time & 0xff, (duration_time >> 8) & 0xff, forever_flag, color]
    self.i2c.writeto(self._addr, bytes(data))

  def displayEmoji(self, emoji, duration_time, forever_flag):
    data = [I2C_CMD_DISP_EMOJI, emoji, duration_time & 0xff, (duration_time >> 8) & 0xff, forever_flag]
    self.i2c.writeto(self._addr, bytes(data))

  def displayNumber(self, number, duration_time, forever_flag, color):
    data = [I2C_CMD_DISP_NUM, number & 0xff, (number >> 8) & 0xff, duration_time & 0xff, (duration_time >> 8) & 0xff, forever_flag, color]
    self.i2c.writeto(self._addr, bytes(data))

  def displayString(self, str, duration_time, forever_flag, color):
    strlen = len(str)
    if strlen >= 28:
      strlen = 28
      
    data = [I2C_CMD_DISP_STR, forever_flag, duration_time & 0xff, (duration_time >> 8) & 0xff, strlen, color]
    for i in range(strlen):
      data.append(str[i])

    if strlen > 25:
      self.i2c.writeto(self._addr, bytes(data))
      utime.sleep_ms(1)
      self.i2c.writeto(self._addr, bytes([I2C_CMD_CONTINUE_DATA]))
      self.i2c.writeto(self._addr, bytes(data + 31))
    else:
      self.i2c.writeto(self._addr, bytes(data))

  def displayFrames(self, buffer, duration_time, forever_flag, frames_number):
    data = bytearray(72)
    # max 5 frames in storage
    if frames_number > 5:
      frames_number = 5
    elif frames_number == 0:
      return

    data[0] = I2C_CMD_DISP_CUSTOM
    data[1] = 0x0
    data[2] = 0x0
    data[3] = 0x0
    data[4] = frames_number
    for i in range(frames_number - 1, 0, -1):
      data[5] = i
      for j in range(64):
        data[8 + j] = buffer[j + i * 64]

      if i == 0:
        # display when everything is finished.
        data[1] = duration_time & 0xff
        data[2] = (duration_time >> 8) & 0xff
        data[3] = forever_flag

      self.i2c.writeto(self._addr, bytes(data))
      utime.sleep_ms(1)
      self.i2c.writeto(self._addr, bytes([I2C_CMD_CONTINUE_DATA]))
      self.i2c.writeto(self._addr, bytes(data + 24))
      utime.sleep_ms(1)
      self.i2c.writeto(self._addr, bytes([I2C_CMD_CONTINUE_DATA]))
      self.i2c.writeto(self._addr, bytes(data + 48))

  def displayFrames(self, buffer, duration_time, forever_flag, frames_number):
    data = bytearray(72)
    # max 5 frames in storage
    if frames_number > 5:
      frames_number = 5
    elif frames_number == 0:
      return

    data[0] = I2C_CMD_DISP_CUSTOM
    data[1] = 0x0
    data[2] = 0x0
    data[3] = 0x0
    data[4] = frames_number

    for i in range(frames_number - 1, 0, -1):
      data[5] = i
      # different from uint8_t buffer
      for j in range(8):
        for k in range(7, 0, -1):
          data[8 + j * 8 + (7 - k)] = buffer[j * 8 + k + i * 64]

      if i == 0:
        # display when everything is finished.
        data[1] = duration_time & 0xff
        data[2] = (duration_time >> 8) & 0xff
        data[3] = forever_flag
      self.i2c.writeto(self._addr, bytes(data))
      utime.sleep_ms(1)
      self.i2c.writeto(self._addr, bytes([I2C_CMD_CONTINUE_DATA]))
      self.i2c.writeto(self._addr, bytes(data + 24))
      utime.sleep_ms(1)
      self.i2c.writeto(self._addr, bytes([I2C_CMD_CONTINUE_DATA]))
      self.i2c.writeto(self._addr, bytes(data + 48))

  def stopDisplay(self):
    self.i2c.writeto(self._addr, bytes([I2C_CMD_DISP_OFF]))

  def storeFrames(self):
    self.i2c.writeto(self._addr, bytes([I2C_CMD_STORE_FLASH]))
    utime.sleep_ms(200)

  def deleteFrames(self):
    self.i2c.writeto(self._addr, bytes([I2C_CMD_DELETE_FLASH]))
    utime.sleep_ms(200)

  def displayFramesFromFlash(self, duration_time, forever_flag, _from, to):
    temp = 0
    # 1 <= _from <= to <= 5
    if _from < 1: _from = 1
    elif _from > 5: _from = 5

    if to < 1: to = 1
    elif to > 5: to = 5

    if _from > to:
      temp = _from
      _from = to
      to = temp

    data = [I2C_CMD_DISP_FLASH, duration_time & 0xff, (duration_time >> 8) & 0xff, forever_flag, _from - 1, to - 1]
    self.i2c.writeto(self._addr, bytes(data))
    utime.sleep_ms(200)

  def displayColorBlock(self, rgb, duration_time, forever_flag):
    data = [I2C_CMD_DISP_COLOR_BLOCK, (rgb >> 16) & 0xff, (rgb >> 8) & 0xff, rgb & 0xff, duration_time & 0xff, (duration_time >> 8) & 0xff, forever_flag]
    self.i2c.writeto(self._addr, bytes(data))

  def displayColorBar(self, bar, duration_time, forever_flag):
    if bar > 32:
      bar = 32
    data = [I2C_CMD_DISP_COLOR_BAR, bar, duration_time & 0xff, (duration_time >> 8) & 0xff, forever_flag]
    self.i2c.writeto(self._addr, bytes(data))

  def displayColorWave(self, color, duration_time, forever_flag):
    data = [I2C_CMD_DISP_COLOR_WAVE, color, duration_time & 0xff, (duration_time >> 8) & 0xff, forever_flag]
    self.i2c.writeto(self._addr, bytes(data))

  def displayClockwise(self, is_cw, is_big, duration_time, forever_flag):
    data = [I2C_CMD_DISP_COLOR_CLOCKWISE, is_cw, is_big, duration_time & 0xff, (duration_time >> 8) & 0xff, forever_flag]
    self.i2c.writeto(self._addr, bytes(data))

  def displayColorAnimation(self, index, duration_time, forever_flag):
    _from, to = None, None
    if index is 0:
      _from = 0
      to = 28
    elif index is 1:
      _from = 29
      to = 41
    elif index is 2: # rainbow cycle
      _from = 255
      to = 255
    elif index is 3: # fire
      _from = 254
      to = 254
    elif index is 4: # walking
      _from = 42
      to = 43
    elif index is 5: # broken heart
      _from = 44
      to = 52
    else: pass

    data = [I2C_CMD_DISP_COLOR_ANIMATION, _from, to, duration_time & 0xff, (duration_time >> 8) & 0xff, forever_flag]
    self.i2c.writeto(self._addr, bytes(data))

  def enableTestMode(self):
    self.i2c.writeto(self._addr, bytes([I2C_CMD_TEST_TX_RX_ON]))

  def disableTestMode(self):
    self.i2c.writeto(self._addr, bytes([I2C_CMD_TEST_TX_RX_OFF]))

  def getTestVersion(self):
    self.i2c.writeto(self._addr, bytes([I2C_CMD_TEST_GET_VER]))
    data = self.i2c.readfrom(self._addr, 3)
    return data[2] + data[1] * 256 + data[0] * 256 * 256

  def resetDevice(self): pass

  def getDeviceId(self):
    self.i2c.writeto(self._addr, bytes([I2C_CMD_GET_DEVICE_UID]))
    return self.i2c.readfrom(self._addr, 12)

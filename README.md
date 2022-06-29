# Stm32 Libraries
This folder contains custom libraries for STM32 boards in MicroPython used on the platform https://en.vittascience.com/stm32/

### Grove modules

* _stm32_bmp280.py_ driving Grove - Barometer sensor (BMP280) by I2C https://wiki.seeedstudio.com/Grove-Barometer_Sensor-BMP280/
* _stm32_chainableLED.py_ driving Grove - Chainable LED RGB (P9813) https://wiki.seeedstudio.com/Grove-Chainable_RGB_LED/
* _stm32_dht.py_ driving Grove - Temperature&Humidity sensors (DHT11/DHTT22) https://wiki.seeedstudio.com/Grove-TemperatureAndHumidity_Sensor/ & https://wiki.seeedstudio.com/Grove-Temperature_and_Humidity_Sensor_Pro/
* _stm32_gas.py_ driving Grove - Multichannel Gas Sensor v1.0 https://wiki.seeedstudio.com/Grove-Multichannel_Gas_Sensor/
* _stm32_hm330x.py_ driving the Grove - Laser PM (HM3301) sensor by I2C https://wiki.seeedstudio.com/Grove-Laser_PM2.5_Sensor-HM3301/
* _stm32_lcd_i2c.py_ driving Grove - LCD I2C Series https://wiki.seeedstudio.com/Grove-16x2_LCD_Series/
* _stm32_pcf85063tp.py_ driving Grove - High Precision RTC (PCF85063) https://wiki.seeedstudio.com/Grove_High_Precision_RTC/
* _stm32_rgb_led_matrix.py_ driving Grove - RGB LED Matrix (MY92221) https://wiki.seeedstudio.com/Grove-RGB_LED_Matrix_w-Driver/ 
* _stm32_th02.py_ driving Grove - Temperature&Humidity sensor v1.0 (TH02) by I2C https://wiki.seeedstudio.com/Grove-TemptureAndHumidity_Sensor-High-Accuracy_AndMini-v1.0/
* _stm32_vl53l0x.py_ driving Grove - Time Of Flight sensor (VL53L0X) by I2C https://wiki.seeedstudio.com/Grove-Time_of_Flight_Distance_Sensor-VL53L0X/

### Alphabot2-Ar

* _stm32_alphabot_v2.py_ driving Alphabot2-Ar robot https://www.waveshare.com/wiki/AlphaBot2-Ar
* _stm32_TRsensors.py_ driving the Alphabot2-Ar infrared sensors (QTRsensors) https://www.waveshare.com/wiki/AlphaBot2-Ar
* _stm32_pcf8574.py_ driving the component (PCF8574) allowing to connect 8 modules to a pin and communicate with them by I2C.

### IR remote control

* _stm32_ir_receiver.py_ driving IR receiver.
* _stm32_nec.py_ decode IR data receved for NEC remotes (8-bits & 16-bits) https://www.gotronic.fr/art-telecommande-ir-irc01-19568.htm

### Bluetooth Low Energy (BLE)

* _stm32_ble_sensor.py_ driving BLE functionalities e.g. Sending data to ST BLE Sensor App https://www.st.com/en/embedded-software/stblesensor.html
* _stm32_ble_uart.py_ driving BLE uart communication (with predifined standard UUIDs for RX and TX).
* _stm32_ble.py_ driving BLE uart communication. (Advanced library, customizable UUIDs for RX and TX).
* _stm32_bleAdvertising.py_ driving BLE basic functionalities e.g. (decoding, advertising, ...).

# Librairies Stm32
Ce dossier contient les librairies personnalisées pour la carte STM32 en MicroPython sur la plateforme https://fr.vittascience.com/stm32/

### Modules Grove

* _stm32_bmp280.py_ pilote le capteur (BMP280) en I2C https://wiki.seeedstudio.com/Grove-Barometer_Sensor-BMP280/
* _stm32_chainableLED.py_ pilote le module Grove Chainable LED RGB (P9813) https://wiki.seeedstudio.com/Grove-Chainable_RGB_LED/
* _stm32_dht.py_ pilote les capteurs Grove Temperature&Humidity (DHT11/DHTT22) https://wiki.seeedstudio.com/Grove-TemperatureAndHumidity_Sensor/ & https://wiki.seeedstudio.com/Grove-Temperature_and_Humidity_Sensor_Pro/
* _stm32_gas.py_ pilote le capteur de gas multicannal Grove v1.0 https://wiki.seeedstudio.com/Grove-Multichannel_Gas_Sensor/
* _stm32_hm330x.py_ pilote le capteur de particules Grove (HM3301) en I2C https://wiki.seeedstudio.com/Grove-Laser_PM2.5_Sensor-HM3301/
* _stm32_lcd_i2c.py_ pilote le module Grove LCD I2C Series https://wiki.seeedstudio.com/Grove-16x2_LCD_Series/
* _stm32_pcf85063tp.py_ pilote le module RTC Haute Precision Grove (PCF85063) https://wiki.seeedstudio.com/Grove_High_Precision_RTC/
* _stm32_rgb_led_matrix.py_ pilote le module Grove - RGB LED Matrix (MY92221) https://wiki.seeedstudio.com/Grove-RGB_LED_Matrix_w-Driver/
* _stm32_th02.py_ pilote le capteur de Température&Humidité Grove (TH02) v1.0 en I2C https://wiki.seeedstudio.com/Grove-TemptureAndHumidity_Sensor-High-Accuracy_AndMini-v1.0/
* _stm32_vl53l0x.py_ pilote le capteur Time Of Flight (VL53L0X) en I2C https://wiki.seeedstudio.com/Grove-Time_of_Flight_Distance_Sensor-VL53L0X/

### Alphabot2-Ar

* _stm32_alphabot_v2.py_ pilote le robot Alphabot2-Ar https://www.waveshare.com/wiki/AlphaBot2-Ar
* _stm32_TRsensors.py_ pilote les capteurs de ligne à infrarouge du robot Alphabot2-Ar (QTRsensors) https://www.waveshare.com/wiki/AlphaBot2-Ar
* _stm32_pcf8574.py_ pilote le composant (PCF8574) permettant de connecter 8 modules à une broche et communiquant en I2C.

### IR remote control

* _stm32_ir_receiver.py_ pilote un récepteur infrarouge.
* _stm32_nec.py_ décode les données infrarouges reçues https://www.gotronic.fr/art-telecommande-ir-irc01-19568.htm

### Bluetooth Low Energy (BLE)

* _stm32_ble_sensor.py_ pilote les fonctionnalités du BLE, par exemple: L'envoi de données à l'application mobile ST BLE Sensor  https://www.st.com/en/embedded-software/stblesensor.html
* _stm32_ble_uart.py_ pilote la communication UART du BLE (Les UUIDs RX/TX sont standards et prédéfinis).
* _stm32_ble.py_ pilote la communication UART (Librarie avancée avec UUID modifiables).
* _stm32_bleAdvertising.py_ pilote les fonctionnalités de base du BLE, par exemple: Décodage et annoces de connexions.

Le contenu de ce dossier est OpenSource.

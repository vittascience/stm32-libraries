##########################################################################################################
#
# The Lora class contains all the functions allowing to use the Lora module. 
# It allows to make a LoRa communication of class A with sending and receiving data.
#
##########################################################################################################


#---------------------------------------------------------------------------------------------------
#    Imports
#---------------------------------------------------------------------------------------------------
from driverAT import *
from time import sleep_ms
import re


class LoRa:
#---------------------------------------------------------------------------------------------------
#    Private variables
#---------------------------------------------------------------------------------------------------
    __LoRaDriverVersion = "1.0.1"
    __loRaIsJoined = False
    __loRaInLowPowerMode = False

    commandsAtList = {
        "LoRaAt"                 : AtCmd("AT", "+AT: OK"),
        "LoRaIdentify"           : AtCmd("AT+ID",        "+ID"),
        "LoRaKeys"               : AtCmd("AT+KEY",       "+KEY"),
        "LoRaJoin"               : AtCmd("AT+JOIN",      "+JOIN: Done",                        Timeout=20000),
        "LoRaMode"               : AtCmd("AT+MODE",      "+MODE",                              Timeout=3000),
        "LoRaSendString"         : AtCmd("AT+MSG",       ["+MSG: Done", "+MSG: PORT"],         Timeout=20000),
        "LoRaSendStringConfirm"  : AtCmd("AT+CMSG",      ["+CMSG: Done", "+CMSG: PORT"],       Timeout=20000),
        "LoRaSendData"           : AtCmd("AT+MSGHEX",    ["+MSGHEX: Done", "+MSGHEX: PORT"],   Timeout=20000),
        "LoRaSendDataConfirm"    : AtCmd("AT+CMSGHEX",   ["+CMSGHEX: Done", "+CMSGHEX: PORT"], Timeout=20000),
        "LoRaPort"               : AtCmd("AT+PORT",      "+PORT:"),
        "LoRaReset"              : AtCmd("AT+RESET",     "+RESET:"),
        "LoRaFactorySettings"    : AtCmd("AT+FDEFAULT",  "+FDEFAULT:"),
        "LoRaDfu"                : AtCmd("AT+DFU",       "+DFU:"),
        "LoRaClass"              : AtCmd("AT+CLASS",     "+CLASS:"),
        "LoRaDelay"              : AtCmd("AT+DELAY",     "+DELAY:"),
        "LoRaGetDelay"           : AtCmd("AT+DELAY",     "JRX2"),
        "LoRaGetRegion"          : AtCmd("AT+DR",        "+DR:"),
        "LoRaLW"                 : AtCmd("AT+LW",        "+LW:"),
        "LoRaGetDutyCycle"       : AtCmd("AT+LW",        "+LW: DC"),
        "LoRaGetBatteryLevel"    : AtCmd("AT+LW",        "+LW: BAT"),
        "LoRaGetTemp"            : AtCmd("AT+TEMP",      "+TEMP:"),
        "LoRaGetVersion"         : AtCmd("AT+LW",        "+LW: VER"),
        "LoRaRtc"                : AtCmd("AT+RTC",       "+RTC:"),
        "LoRaLowPower"           : AtCmd("AT+LOWPOWER" , "+LOWPOWER:"),
        "LoRaWakeUp"             : AtCmd("0" ,           "+LOWPOWER:", Timeout=2000),   
    }

    #-----------------------------------------------------------------------------------------------------
    # Constructor of Class LoRa.                                                                         #
    #                                                                                                    #
    # Args:                                                                                              #
    #    Bauderate (int): Bauderate for UART com between Micropython and LoRa-E5 module.                 #
    #    UartId (int): ID of the UART to which the Lora module is connected .                            #
    #    DataReceiveCallback (function pointer): Callback function for data reception on the lora network.#
    #    VerboseMode (Bool): Enables to display all the AT command received and sent.                    #
    #                                                                                                    #
    # Returns:                                                                                           #
    #    int: The return value. '0' for success, '-1' otherwise.                                         #
    #                                                                                                    #
    #-----------------------------------------------------------------------------------------------------
    def __init__(self, Baudrate = 9600, UartId = 0, DataReceiveCallback = None, VerboseMode = False):
        self.driverAT = DriverAtCmd(Baudrate, UartId, LoRa.commandsAtList, VerboseMode)
        self.dataReceiveCallback = DataReceiveCallback
        
        self.reset()
        nbTry = 0
        response = -1
        while(nbTry < 5 and response == -1):
            response = self.driverAT.sendCmd("LoRaAt")
            nbTry += 1


    #-----------------------------------------------------------------------------------------------------
    # Function to retrieve the version of the Lora driver                                                #
    #                                                                                                    #
    # Args:                                                                                              #
    #    None                                                                                            #
    #                                                                                                    #
    # Returns:                                                                                           #
    #    str: Retrun driver version.                                                                     #
    #                                                                                                    #
    #-----------------------------------------------------------------------------------------------------
    def getDriverVersion(self)->str:
        return self.__LoRaDriverVersion

    #-----------------------------------------------------------------------------------------------------
    # Function to setup the Lora network identifiers                                                     #
    #                                                                                                    #
    # Args:                                                                                              #
    #    DevAddr (str): Device address                                                                   #
    #    DevEui (str): Device EUI.                                                                       #
    #    AppEui (str): Application Eui.                                                                  #
    #    AppKey (str): Application key.                                                                  #
    #    AppSKey (str): Application session key (auto-generate in OTAA mode).                            #
    #    NWKSKEY (str): Network session key (auto-generate in OTAA mode).                                #
    #                                                                                                    #
    # Returns:                                                                                           #
    #    int: The return value. '0' for success, '-1' otherwise.                                         #
    #                                                                                                    #
    #-----------------------------------------------------------------------------------------------------
    def setIdentify(self, 
                    DevAddr = "00 00 00 00", 
                    DevEui  = None, 
                    AppEui  = "48 83 C7 DF 30 06 00 00", 
                    AppKey  = "71 A4 36 4B 48 45 03 5D D7 8A 4E D8 AC 7F 90 17", 
                    AppSKey = None, 
                    NWKSKEY = None):

        self.devEui  = ""
        self.appSKey = ""
        self.appEui  = ""
        self.appKey  = ""
        self.nwkskey = ""

        self.devAddr = self.__formatStringParameter(DevAddr)
        response = self.driverAT.sendCmd("LoRaIdentify", "DevAddr", self.devAddr)
        if self.__checkError(response) == -1:
            return -1
        
        if DevEui != None:
            self.devEui  = self.__formatStringParameter(DevEui)
            response = self.driverAT.sendCmd("LoRaIdentify", "DevEui", self.devEui)
            if self.__checkError(response) == -1:
                return -1
        
        self.appEui  = self.__formatStringParameter(AppEui)
        response = self.driverAT.sendCmd("LoRaIdentify", "AppEui", self.appEui)
        if self.__checkError(response) == -1:
            return -1
        
        self.appKey  = self.__formatStringParameter(AppKey)
        response = self.driverAT.sendCmd("LoRaKeys", "APPKEY", self.appKey)
        if self.__checkError(response) == -1:
            return -1
        
        if AppSKey != None:
            self.appSKey = self.__formatStringParameter(AppSKey)
            response = self.driverAT.sendCmd("LoRaKeys", "APPSKEY", self.appSKey)
            if self.__checkError(response) == -1:
                return -1
        
        if NWKSKEY != None:
            self.nwkskey = self.__formatStringParameter(NWKSKEY)
            response = self.driverAT.sendCmd("LoRaKeys", "NWKSKEY", self.nwkskey)
            if self.__checkError(response) == -1:
                return -1
            
        response = self.setMode("LWOTAA")
        if self.__checkError(response) == -1:
            return -1
        
        return 0

    #-----------------------------------------------------------------------------------------------------
    # Function to read the Lora network identifiers                                                      #
    #                                                                                                    #
    # Args:                                                                                              #
    #    None                                                                                            #
    #                                                                                                    #
    # Returns:                                                                                           #
    #    dict: If no error is detected, the dictionary is returned with the following values:            #
    #       - DevAddr (str): Device address                                                              #
    #       - DevEui (str): Device EUI.                                                                  #
    #       - AppEui (str): Application Eui.                                                             #
    #       - AppKey (str): Application key.                                                             #
    #       - AppSKey (str): Application session key (auto-generate in OTAA mode).                       #
    #       - NwkSKey (str): Network session key (auto-generate in OTAA mode).                           #
    #    int: Return value '-1' for error.                                                               #
    #-----------------------------------------------------------------------------------------------------
    def getIdentify(self):

        identify = dict()

        response = self.driverAT.sendCmd("LoRaIdentify", "DevAddr")
        if self.__checkError(response) == -1:
            return -1

        regex = "\+(.*?) (.*?)DevAddr, (.*)"
        m = re.search(regex, response.decode())
        identify['DevAddr'] = m.group(3).replace(":", " ")

        response = self.driverAT.sendCmd("LoRaIdentify", "DevEui")
        if self.__checkError(response) == -1:
            return -1

        regex = "\+(.*?) (.*?)DevEui, (.*)"
        m = re.search(regex, response.decode())
        identify['DevEui'] = m.group(3).replace(":", " ")

        response = self.driverAT.sendCmd("LoRaIdentify", "AppEui")
        if self.__checkError(response) == -1:
            return -1

        regex = "\+(.*?) (.*?)AppEui, (.*)"
        m = re.search(regex, response.decode())
        identify['AppEui'] = m.group(3).replace(":", " ")
        
        identify['AppKey'] = self.appKey
        identify['AppSKey'] = self.appSKey
        identify['NwkSKey'] = self.nwkskey

        return identify

    #-----------------------------------------------------------------------------------------------------
    # Function to join the LoRa network.                                                                 #
    #                                                                                                    #
    # Args:                                                                                              #
    #    None                                                                                            #
    #                                                                                                    #
    # Returns:                                                                                           #
    #    int: Retrun '0' for success join, '-1' for fail join.                                           #
    #                                                                                                    #
    #-----------------------------------------------------------------------------------------------------
    def join(self):
        response = self.driverAT.sendCmd("LoRaJoin")
        if response != None and response != -1:
            if response.decode().find("Join failed") != -1:
                return -1
            else:
                self.__loRaIsJoined = True
                return 0
        else:
            return -1

    #-----------------------------------------------------------------------------------------------------
    # Function to send raw data over the Lora network.                                                   #
    #                                                                                                    #
    # Args:                                                                                              #
    #    Data (str, bytearry, list): Data to send.                                                       #
    #    Port (int): Port to send data.                                                                  #
    #    NeedAck (Bool): True when looking for an acknowledge from the Lora network.                     #
    #                                                                                                    #
    # Returns:                                                                                           #
    #    int: The return value. '0' for success, '-1' otherwise.                                         #
    #                                                                                                    #
    #-----------------------------------------------------------------------------------------------------
    def sendData(self, Data, Port=1, NeedAck = False):
        self.setPort(Port)

        if self.__loRaIsJoined == True:
            if type(Data) is str:
                dataToSend = self.__formatStringParameter(Data)
            elif type(Data) is bytearray:
                hex_string = "".join("%02X" % x for x in Data)
                dataToSend = self.__formatStringParameter(hex_string)
            elif type(Data) is list:
                hex_string = "".join("%02X" % x for x in bytearray(Data))
                dataToSend = self.__formatStringParameter(hex_string)

            if NeedAck == False:
                response = self.driverAT.sendCmd("LoRaSendData", dataToSend)
            else:
                response = self.driverAT.sendCmd("LoRaSendDataConfirm", dataToSend)

            if response != None and response != -1:
                if response.decode().lower().find("error") != -1:
                    return -1
                else:
                    # Check if received data from LoRa network.
                    if response.decode().lower().find("port") != -1:
                        dataReceived = dict()
                        # Response = b'+MSG: Start'+MSG: FPENDING+MSG: PORT: 5; RX: "05050404030302020101"'
                        regex = "\+(.*?)PORT(.*?)(\d+);(.*?)\"(\d+)"
                        m = re.search(regex, response.decode())

                        portDataReceived = m.group(3)
                        dataReceived = self._unhexlify(m.group(5))
                        if(self.dataReceiveCallback != None):
                            self.dataReceiveCallback(Port = portDataReceived, DataReceived = dataReceived)
                    return 0
        else:
            return -1

    #-----------------------------------------------------------------------------------------------------
    # Function to send string data over the Lora network.                                                #
    #                                                                                                    #
    # Args:                                                                                              #
    #    Data (str): String to send.                                                                     #
    #    Port (int): Port to send data.                                                                  #
    #    NeedAck (Bool): True when looking for an acknowledge from the Lora network.                     #
    #                                                                                                    #
    # Returns:                                                                                           #
    #    int: The return value. '0' for success, '-1' otherwise.                                         #
    #                                                                                                    #
    #-----------------------------------------------------------------------------------------------------
    def sendString(self, Data, Port=1, NeedAck = False):
        self.setPort(Port)

        if self.__loRaIsJoined == True:
            if type(Data) is str:
                dataToSend = self.__formatStringParameter(Data)
            else:
                return -1

            if NeedAck == False:
                response = self.driverAT.sendCmd("LoRaSendString", dataToSend)
            else:
                response = self.driverAT.sendCmd("LoRaSendStringConfirm", dataToSend)
            
            if response != None and response != -1:
                if response.decode().lower().find("error") != -1:
                    return -1
                else:
                    # Check if received data from LoRa network.
                    if response.decode().lower().find("port") != -1:
                        dataReceived = dict()
                        # Response = b'+PMSG: Start'+PMSG: FPENDING+PMSG: PORT: 5; RX: "05050404030302020101"'
                        regex = "\+(.*?)PORT(.*?)(\d+);(.*?)\"(\d+)"
                        m = re.search(regex, response.decode())

                        portDataReceived = m.group(3)
                        dataReceived = self._unhexlify(m.group(5))
                        if(self.dataReceiveCallback != None):
                            self.dataReceiveCallback(Port = portDataReceived, DataReceived = dataReceived)
                    return 0
        else:
            return -1
 
    #-----------------------------------------------------------------------------------------------------
    # Function to setup port to send data over LoRa network.                                             #
    #                                                                                                    #
    # Args:                                                                                              #
    #    Port (int): Port to send data.                                                                  #
    #                                                                                                    #
    # Returns:                                                                                           #
    #    int: The return value. '0' for success, '-1' error.                                             #
    #                                                                                                    #
    #-----------------------------------------------------------------------------------------------------
    def setPort(self, Port=1):
        self.driverAT.sendCmd("LoRaPort", Port)

    #-----------------------------------------------------------------------------------------------------
    # Function to reset LoRa-E5 module.                                                                  #
    #                                                                                                    #
    # Args:                                                                                              #
    #    None                                                                                            #
    #                                                                                                    #
    # Returns:                                                                                           #
    #    int: The return value. '0' for success, '-1' error.                                             #
    #                                                                                                    #
    #-----------------------------------------------------------------------------------------------------
    def reset(self):
        response = self.driverAT.sendCmd("LoRaReset")
        if self.__checkError(response) == -1:
            return -1
        else:
            return 0

    #-----------------------------------------------------------------------------------------------------
    # Function to restore all parameters to the factory settings.                                        #
    #                                                                                                    #
    # Args:                                                                                              #
    #    None                                                                                            #
    #                                                                                                    #
    # Returns:                                                                                           #
    #    int: The return value. '0' for success, '-1' error.                                             #
    #                                                                                                    #
    #-----------------------------------------------------------------------------------------------------
    def factorySettings(self):
        response = self.driverAT.sendCmd("LoRaFactorySettings")
        if self.__checkError(response) == -1:
            return -1
        else:
            return 0

    #-----------------------------------------------------------------------------------------------------
    # Function to enable/disable DFU mode.                                                               #
    #                                                                                                    #
    # Args:                                                                                              #
    #    DfuState (Bool) : True = DFU is enable, False = DFU is disable                                  #
    #                                                                                                    #
    # Returns:                                                                                           #
    #    int: The return value. '0' for success, '-1' error.                                             #
    #                                                                                                    #
    #-----------------------------------------------------------------------------------------------------
    def setDfu(self, DfuState = False):
        if DfuState == True:
            response = self.driverAT.sendCmd("LoRaDfu", "ON")
        elif DfuState == False:
            response = self.driverAT.sendCmd("LoRaDfu", "OFF")
        else:
            return -1

        if self.__checkError(response) == -1:
            return -1
        else:
            return 0

    #-----------------------------------------------------------------------------------------------------
    # Function to get DFU mode state.                                                                    #
    #                                                                                                    #
    # Args:                                                                                              #
    #    None                                                                                            #
    #                                                                                                    #
    # Returns:                                                                                           #
    #    Bool: When no error detected return True if DFU is enable and False when DFU is disable.        #
    #    int: Return value '-1' for error.                                                               #
    #                                                                                                    #
    #-----------------------------------------------------------------------------------------------------
    def getDfu(self):
        response = self.driverAT.getCmd("LoRaDfu")
        if self.__checkError(response) == -1:
            return -1
        else:
            if response.decode().lower().find("on") != -1:
                return True
            else:
                return False

    #-----------------------------------------------------------------------------------------------------
    # Function to set working mode on LoRa network                                                       #
    #                                                                                                    #
    # Args:                                                                                              #
    #    Mode (str) : Working mode on LoRa network (LWABP, LWOTAA, TEST).                                #
    #                                                                                                    #
    # Returns:                                                                                           #
    #    int: Return value '0' for success, '-1' error.                                                  #
    #                                                                                                    #
    #-----------------------------------------------------------------------------------------------------
    def setMode(self, Mode):
        if Mode == "LWABP" or Mode == "LWOTAA" or Mode == "TEST":
            response = self.driverAT.sendCmd("LoRaMode", Mode)
            if self.__checkError(response) == -1:
                return -1
            else:
                return 0
        else:
            return -1

    #-----------------------------------------------------------------------------------------------------
    # Function to get working mode on LoRa network                                                       #
    #                                                                                                    #
    # Args:                                                                                              #
    #    Mode (str) : Working mode on LoRa network (LWABP, LWOTAA, TEST).                                #
    #                                                                                                    #
    # Returns:                                                                                           #
    #    str: When no error detected return the current working mode.                                    #
    #    int: Return value '-1' for error.                                                               #
    #                                                                                                    #
    #-----------------------------------------------------------------------------------------------------
    def getMode(self):
        response = self.driverAT.getCmd("LoRaMode")
        if self.__checkError(response) == -1:
            return -1
        else:
            if response.decode().lower().find("lwabp") != -1:
                return "LWABP"
            elif response.decode().lower().find("lwotaa") != -1:
                return "LWOTAA"
            elif response.decode().lower().find("test") != -1:
                return "TEST"
            else:
                return -1

    #-----------------------------------------------------------------------------------------------------
    # Function to set working class on LoRa network                                                      #
    #                                                                                                    #
    # Args:                                                                                              #
    #    Class (str) : Working mode on LoRa network (A, B, C).                                           #
    #                                                                                                    #
    # Returns:                                                                                           #
    #    int: Return value '0' for success, '-1' error.                                                  #
    #                                                                                                    #
    #-----------------------------------------------------------------------------------------------------
    def setClass(self, Class="A"):
        if Class == "A" or Class == "B" or Class == "C":
            response = self.driverAT.sendCmd("LoRaClass")
            if self.__checkError(response) == -1:
                return -1
            else:
                return 0
        else:
            return -1

    #-----------------------------------------------------------------------------------------------------
    # Function to get working class on LoRa network                                                      #
    #                                                                                                    #
    # Args:                                                                                              #
    #    Class (str) : Working mode on LoRa network (A, B, C).                                           #
    #                                                                                                    #
    # Returns:                                                                                           #
    #    str: When no error detected return the current working class.                                   #
    #    int: Return value '-1' for error.                                                               #
    #                                                                                                    #
    #-----------------------------------------------------------------------------------------------------
    def getClass(self):
        response = self.driverAT.getCmd("LoRaClass")
        if self.__checkError(response) != -1:
            m = response.decode()[response.decode().find("\+CLASS\:"):]
            if m.find("A") != -1:
                return "A"
            elif m.find("B") != -1:
                return "B"
            elif m.find("C") != -1:
                return "C"
            else:
                return -1
        else:
            return -1

    #-----------------------------------------------------------------------------------------------------
    # Function to configure all reception window delays                                                  #
    #                                                                                                    #
    # Args:                                                                                              #
    #    JRX1 (int) : Dalay for RX1 during join procedure (in ms).                                       #
    #    JRX2 (int) : Delay for RX2 during join procedure (in ms).                                       #
    #    RX1 (int) : Delay for RX1 during send procedure (in ms).                                        #
    #    RX2 (int) : Delay for RX2 during send procedure (in ms).                                        #
    #                                                                                                    #
    # Returns:                                                                                           #
    #    int: Return value '0' for success, '-1' error.                                                  #
    #                                                                                                    #
    #-----------------------------------------------------------------------------------------------------
    def setDelays(self, JRX1=5000, JRX2=6000, RX1=1000, RX2=2000):
        if type(JRX1)==int and type(JRX2)==int and type(RX1)==int and type(RX2)==int:
            response = self.driverAT.sendCmd("LoRaDelay", "JRX1", JRX1)
            if self.__checkError(response) == -1:
                return -1

            response = self.driverAT.sendCmd("LoRaDelay", "JRX2", JRX2)
            if self.__checkError(response) == -1:
                return -1

            response = self.driverAT.sendCmd("LoRaDelay", "RX1", RX1)
            if self.__checkError(response) == -1:
                return -1

            response = self.driverAT.sendCmd("LoRaDelay", "RX2", RX2)
            if self.__checkError(response) == -1:
                return -1

            return 0

        else:
            return -1

    #-----------------------------------------------------------------------------------------------------
    # Function to get all reception window delays                                                        #
    #                                                                                                    #
    # Args:                                                                                              #
    #    None.                                                                                           #
    #                                                                                                    #
    # Returns:                                                                                           #
    #    dict: If no error is detected, the dictionary is returned with the following values:            #
    #              - JRX1 (int) : Dalay for RX1 during join procedure (in ms).                           #
    #              - JRX2 (int) : Delay for RX2 during join procedure (in ms).                           #
    #              - RX1 (int) : Delay for RX1 during send procedure (in ms).                            #
    #              - RX2 (int) : Delay for RX2 during send procedure (in ms).                            #
    #    int: Return value '-1' for error.                                                               #
    #                                                                                                    #
    #-----------------------------------------------------------------------------------------------------
    def getDelays(self):
        response = self.driverAT.getCmd("LoRaGetDelay")
        if self.__checkError(response) != -1:
            delays = dict()
            # Response = b'+DELAY: RX1,1000+DELAY: RX2,2000+DELAY: JRX1,5000+DELAY: JRX2,6000'
            regex = "\+.*?:(.*?),(\d+)\+(.*?),(\d+)\+(.*?),(\d+)\+(.*?),(\d+)"
            m = re.search(regex, response.decode())
            delays["RX1"]  = int(m.group(2))
            delays["RX2"]  = int(m.group(4))
            delays["JRX1"] = int(m.group(6))
            delays["JRX2"] = int(m.group(8))

            return delays
        else:
            return -1

    #-----------------------------------------------------------------------------------------------------
    # Function to enable duty cycle control                                                              #
    #                                                                                                    #
    # Args:                                                                                              #
    #    Enable (Bool) : True duty cycle control is enable, False is disbale.                            #
    #    MaxDutyCycle (int) : Valeur beetwen 0 and 15 calculate with following equation:                 #
    #                                                                                                    #
    #                           DutyCycle (%) = 100 / (2 ^ MaxDutyCycle)                                 #   
    #                                                                                                    #
    # Returns:                                                                                           #
    #    int: Return value '0' for success, '-1' error.                                                  #
    #                                                                                                    #
    #-----------------------------------------------------------------------------------------------------
    def setDutyCycle(self, Enable=False, MaxDutyCycle=0):
        if Enable == True:
            response = self.driverAT.sendCmd("LoRaLW", "DC", "ON", MaxDutyCycle)
        elif Enable == False:
            response = self.driverAT.sendCmd("LoRaLW", "DC", "OFF")
        else:
            return -1

        if self.__checkError(response) == -1:
            return -1
        else:
            return 0

    #-----------------------------------------------------------------------------------------------------
    # Function to get duty cycle control status                                                          #
    #                                                                                                    #
    # Args:                                                                                              #               
    #    None                                                                                            #
    #                                                                                                    #
    # Returns:                                                                                           #
    #    dict: If no error is detected, the dictionary is returned with the following values:            #
    #              - Enable (Bool) : Dalay for RX1 during join procedure (in ms).                        #
    #              - Value (int) : Valeur beetwen 0 and 15 calculate with following equation:            #
    #                                                                                                    #
    #                              #DutyCycle (%) = 100 / (2 ^ MaxDutyCycle)                             #
    #                                                                                                    #
    #    int: Return value '-1' for error.                                                               #
    #                                                                                                    #
    #-----------------------------------------------------------------------------------------------------
    def getDutyCycle(self):
        response = self.driverAT.sendCmd("LoRaLW", "DC")
        if self.__checkError(response) != -1:

            dutyCycleState = dict()

            if response.decode().lower().find("on") != -1:
                regex = "\+(.*?)(\d+)"
                m = re.search(regex, response.decode())
                dutyCycleState["Value"] = int(m.group(2))
                dutyCycleState["Enable"] = True
            else:
                dutyCycleState["Value"] = 0
                dutyCycleState["Enable"] = False

            return dutyCycleState
        else:
            return -1

    #-----------------------------------------------------------------------------------------------------
    # Function to enable or disable public network.                                                      #
    #                                                                                                    #
    # Args:                                                                                              #
    #    PublicNetworkState (Bool) : True = public network is enable, False is disbale.                  #
    #                                                                                                    #
    # Returns:                                                                                           #
    #    int: Return value '0' for success, '-1' error.                                                  #
    #                                                                                                    #
    #-----------------------------------------------------------------------------------------------------
    def setPublicNetwork(self, PublicNetworkState=True):
        if PublicNetworkState == True:
            response = self.driverAT.sendCmd("LoRaLW", "NET", "ON")
        elif PublicNetworkState == False:
            response = self.driverAT.sendCmd("LoRaLW", "NET", "OFF")
        else:
            return -1

        if self.__checkError(response) == -1:
            return -1
        else:
            return 0

    #-----------------------------------------------------------------------------------------------------
    # Function to get public network status.                                                             #
    #                                                                                                    #
    # Args:                                                                                              #
    #    None                                                                                            #
    #                                                                                                    #
    # Returns:                                                                                           #
    #    Bool: True = public network is enable, False is disable.                                        #
    #    int: Return value '-1' for error.                                                               #
    #                                                                                                    #
    #-----------------------------------------------------------------------------------------------------
    def getPublicNetwork(self):
        response = self.driverAT.sendCmd("LoRaLW", "NET")
        if self.__checkError(response) == -1:
            return -1
        else:
            if response.decode().lower().find("on"):
                return True
            else:
                return False

    #-----------------------------------------------------------------------------------------------------
    # Function to going LoRa-E5 in sleep mode (low power).                                               #
    #                                                                                                    #
    # Args:                                                                                              #
    #    None                                                                                            #
    #                                                                                                    #
    # Returns:                                                                                           #
    #    int: Return value '0' for success, '-1' error.                                                  #
    #                                                                                                    #
    #-----------------------------------------------------------------------------------------------------
    def enterLowPowerMode(self):
        if self.__loRaInLowPowerMode == False:
            response = self.driverAT.sendCmd("LoRaLowPower")
            if self.__checkError(response) == -1:
                return -1
            else:
                self.__loRaInLowPowerMode = True
                return 0
        else:
            return 0

    #-----------------------------------------------------------------------------------------------------
    # Function to wake up LoRa-E5.                                                                       #
    #                                                                                                    #
    # Args:                                                                                              #
    #    None                                                                                            #
    #                                                                                                    #
    # Returns:                                                                                           #
    #    int: Return value '0' for success, '-1' error.                                                  #
    #                                                                                                    #
    #-----------------------------------------------------------------------------------------------------
    def wakeUp(self):
        if self.__loRaInLowPowerMode == True:
            response = self.driverAT.sendCmd("LoRaWakeUp")
            if self.__checkError(response) == -1:
                return -1
            else:
                if response.decode().lower().find("wakeup"):
                    self.__loRaInLowPowerMode = False
                    return 0
                else:
                    return -1
        else:
            return 0

    #-----------------------------------------------------------------------------------------------------
    # Function to get actual working region setting in LoRa-E5 module.                                   #
    #                                                                                                    #
    # Args:                                                                                              #
    #    None                                                                                            #
    #                                                                                                    #
    # Returns:                                                                                           #
    #    str: actual working region.                                                                     #
    #    int: Return value '-1' for error.                                                               #
    #                                                                                                    #
    #-----------------------------------------------------------------------------------------------------
    def getRegion(self):
        response = self.driverAT.sendCmd("LoRaGetRegion", "SCHEME")
        if self.__checkError(response) == -1:
            return -1
        else:
            regex = "\+(.*):(.*)"
            m = re.search(regex, response.decode())
            sleep_ms(1000)
            return m.group(2)

    #-----------------------------------------------------------------------------------------------------
    # Function to set date and hour in RTC of LoRa-E5 module.                                            #
    #                                                                                                    #
    # Args:                                                                                              #
    #    Year (int): Year.                                                                               #
    #    Month (int): Month.                                                                             #
    #    Day (int): Day.                                                                                 #
    #    Hour (int): Hour.                                                                               #
    #    Minute (int): Minute.                                                                           #
    #    Second (int): Second.                                                                           #
    #                                                                                                    #
    # Returns:                                                                                           #
    #    int: Return value '0' for success, '-1' error.                                                  #
    #                                                                                                    #
    #-----------------------------------------------------------------------------------------------------
    def setRtc(self, Year = 2000, Month = 1, Day = 1, Hour = 0, Minute = 0, Second = 0): 
        rtcValue = " \"%04d-%02d-%02d %02d:%02d:%02d\"" % (Year, Month, Day, Hour, Minute, Second)
        response = self.driverAT.sendCmd("LoRaRtc", rtcValue)
        if self.__checkError(response) == -1:
            return -1
        else:
            return 0

    #-----------------------------------------------------------------------------------------------------
    # Function to get date and hour in RTC of LoRa-E5 module.                                            #
    #                                                                                                    #
    # Args:                                                                                              #
    #    Year (int): Year.                                                                               #
    #    Month (int): Month.                                                                             #
    #    Day (int): Day.                                                                                 #
    #    Hour (int): Hour.                                                                               #
    #    Minute (int): Minute.                                                                           #
    #    Second (int): Second.                                                                           #
    #                                                                                                    #
    # Returns:                                                                                           #
    #    dict: If no error is detected, the dictionary is returned with the following values:            #
    #              - Year (int): Year.                                                                   #
    #              - Month (int): Month.                                                                 #
    #              - Day (int): Day.                                                                     #
    #              - Hour (int): Hour.                                                                   #
    #              - Minute (int): Minute.                                                               #
    #              - Second (int): Second.                                                               #
    #                                                                                                    #
    #    int: Return value '-1' for error.                                                               #
    #                                                                                                    #
    #-----------------------------------------------------------------------------------------------------
    def getRtc(self):
        response = self.driverAT.getCmd("LoRaRtc")
        if self.__checkError(response) == -1:
            return -1
        else:
            rtcValue = dict()
            regex = "\+(.*): (\d+)-(\d+)-(\d+) (\d+):(\d+):(\d+)"
            m = re.search(regex, response.decode())
            rtcValue["Year"]   = int(m.group(2))
            rtcValue["Month"]  = int(m.group(3))
            rtcValue["Day"]    = int(m.group(4))

            rtcValue["Hour"]   = int(m.group(5))
            rtcValue["Minute"] = int(m.group(6))
            rtcValue["Second"] = int(m.group(7))

            return rtcValue

    #-----------------------------------------------------------------------------------------------------
    # Function to set battery level in LoRa stack of LoRa-E5 module.                                     #
    #                                                                                                    #
    # Args:                                                                                              #
    #    BatteryLevel (int): Beetween 0 and 255 (for 0 to 100%).                                         #
    #                                                                                                    #
    # Returns:                                                                                           #
    #    int: Return value '0' for success, '-1' error.                                                  #
    #                                                                                                    #
    #-----------------------------------------------------------------------------------------------------
    def setBatteryLevel(self, BatteryLevel = 255):
        response = self.driverAT.sendCmd("LoRaLW", "BAT", BatteryLevel)
        if self.__checkError(response) == -1:
            return -1
        else:
            return 0

    #-----------------------------------------------------------------------------------------------------
    # Function to get battery level in LoRa stack of LoRa-E5 module.                                     #
    #                                                                                                    #
    # Args:                                                                                              #
    #    None                                                                                            #
    #                                                                                                    #
    # Returns:                                                                                           #
    #    int: actual battery level (beetween 0 and 255).                                                 #
    #    int: Return value '-1' for error.                                                               #
    #                                                                                                    #
    #-----------------------------------------------------------------------------------------------------
    def getBatteryLevel(self):
        response = self.driverAT.sendCmd("LoRaGetBatteryLevel", "BAT")
        if self.__checkError(response) == -1:
            return -1
        else:
            regex = "\+(.*?)(\d+)"
            m = re.search(regex, response.decode())
            return int(m.group(2))

    #-----------------------------------------------------------------------------------------------------
    # Function to get version of LoRa-E5 module.                                                         #
    #                                                                                                    #
    # Args:                                                                                              #
    #    None                                                                                            #
    #                                                                                                    #
    # Returns:                                                                                           #
    #    str: version of LoRa-E5 module.                                                                 #
    #    int: Return value '-1' for error.                                                               #
    #                                                                                                    #
    #-----------------------------------------------------------------------------------------------------
    def getVersion(self):
        response = self.driverAT.sendCmd("LoRaGetVersion", "VER")
        if self.__checkError(response) == -1:
            return -1
        else:
            regex = "(\d+)"
            m = re.search(regex, response.decode())
            version = "V" + m.group(1)
            return version

    #-----------------------------------------------------------------------------------------------------
    # Function to get temperature mesured by LoRa-E5 module.                                             #
    #                                                                                                    #
    # Args:                                                                                              #
    #    None                                                                                            #
    #                                                                                                    #
    # Returns:                                                                                           #
    #    int: temperature in °C.                                                                         #
    #    int: Return value '-1' for error.                                                               #
    #                                                                                                    #
    #-----------------------------------------------------------------------------------------------------
    def getTemperature(self):
        response = self.driverAT.getCmd("LoRaGetTemp")
        if self.__checkError(response) == -1:
            return -1
        else:
            regex = "\+(.*?):(.*?)(\d+)\.(\d+)"
            m = re.search(regex, response.decode())
            temperature = int(m.group(3)) + (int(m.group(4)) * 0.1)
            if m.group(2).find("-") != -1 :
                temperature = temperature * -1.0
            return temperature
            
    #-----------------------------------------------------------------------------------------------------
    # Private function to convert string hex "0A0B0C..." to bytearray.                                   #
    #                                                                                                    #
    # Args:                                                                                              #
    #    S (str): string to be converted.                                                                #
    #                                                                                                    #
    # Returns:                                                                                           #
    #    bytearray: String converted.                                                                    #
    #                                                                                                    #
    #-----------------------------------------------------------------------------------------------------
    def _unhexlify(self, S):
        return bytes(int(S[i:i+2], 16) for i in range(0, len(S), 2))

    #-----------------------------------------------------------------------------------------------------
    # Private function to check parameter need \" char                                                   #
    #                                                                                                    #
    # Args:                                                                                              #
    #    Parameter (str): string to be check.                                                            #
    #                                                                                                    #
    # Returns:                                                                                           #
    #    str: Parameter with \" caracter                                                                 #
    #                                                                                                    #
    #-----------------------------------------------------------------------------------------------------
    def __formatStringParameter(self, Parameter):
        if Parameter.find("\"") != -1:
            return Parameter
        else:
            return ("\"" + Parameter + "\"")

    #-----------------------------------------------------------------------------------------------------
    # Private function to check and detect error in response module.                                     #
    #                                                                                                    #
    # Args:                                                                                              #
    #    Response (str): Response message of LoRa-E5 module.                                             #
    #                                                                                                    #
    # Returns:                                                                                           #
    #    int: Return value '-1' when error detected, '0' for no error.                                   #
    #                                                                                                    #
    #-----------------------------------------------------------------------------------------------------
    def __checkError(self, Response):
        if Response != None:
            if type(Response) == bytes:
                if Response.decode().lower().find("error") != -1:
                    return -1
                else:
                    return 0
            elif type(Response) == int:
                if Response == -1:
                    return -1
                else:
                    return 0
        else:
            return -1

#End class LoRa
#End file

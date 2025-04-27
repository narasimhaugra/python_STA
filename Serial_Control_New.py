# @ author - Varun Pandey
# Ver # 1, dated - Dec 22, 2021
# this code has been moved from NormalFiring.py - to properly organize the code structure

import time

import nidaqmx
import serial
import serial.tools.list_ports

from Compare import Compare, xCompare
from EventsStrings import locateStringsToCompareFromEvent
# following imports added by Manoj Vadali on May 6th 2024
from ReadingQue import ReadingQue
from RelayControlBytes import *


class serialControl:
    
    def __init__(self,
                 r=None, SULU_EEPROM_command_byte=None, MULU_EEPROM_command_byte=None,
                 CARTRIDGE_EEPROM_command_byte=None, NCDComPort=None, PowerPackComPort=None,
                 BlackBoxComPort=None, USB6351ComPort=None, ArduinoUNOComPort=None,
                 FtdiUartComPort=None, OUTPUT_PATH=None, videoPath=None, EEA_RELOAD_EEPROM_command_byte=None):
        # self.serial_port = 0
        self.serial_port = serial.Serial()
        self.r = r if r is not None else None                       # Used in NormalFiring
        self.SULU_EEPROM_command_byte = SULU_EEPROM_command_byte if SULU_EEPROM_command_byte is not None else None
        self.MULU_EEPROM_command_byte = MULU_EEPROM_command_byte if MULU_EEPROM_command_byte is not None else None
        self.CARTRIDGE_EEPROM_command_byte = CARTRIDGE_EEPROM_command_byte if CARTRIDGE_EEPROM_command_byte is not None else None
        self.EEA_RELOAD_EEPROM_command_byte = EEA_RELOAD_EEPROM_command_byte if EEA_RELOAD_EEPROM_command_byte is not None else None

        self.NCDComPort = NCDComPort if NCDComPort is not None else None
        self.PowerPackComPort = PowerPackComPort if PowerPackComPort is not None else None
        self.BlackBoxComPort = BlackBoxComPort if BlackBoxComPort is not None else None
        self.USB6351ComPort = USB6351ComPort if USB6351ComPort is not None else None
        self.ArduinoUNOComPort = ArduinoUNOComPort if ArduinoUNOComPort is not None else None
        self.FtdiUartComPort = FtdiUartComPort if FtdiUartComPort is not None else None
        self.OUTPUT_PATH = OUTPUT_PATH if OUTPUT_PATH is not None else None
        self.videoPath = videoPath if videoPath is not None else None
        self.Test_Results = []
        self.Normal_Firing_Test_Results = []
        self.Adapter_1W_OC_In_Fire_Mode_Results = []

    def wait(self, number_of_seconds):
        time.sleep(number_of_seconds)

    def batt_config(self, case):
        switch = {"Insufficient": 9,
                  "Low": 25,
                  "Full": 99,
                  "RSOC": 120,
                  }
        return switch.get(case)

    def OpenSerialConnection(self):
        #print(self.NCDComPort, self.PowerPackComPort, self.BlackBoxComPort, self.USB6351ComPort, self.ArduinoUNOComPort)
        # self.serial_port = serial.Serial()
        self.serial_port.baudrate = 115200
        # self.serial_port.port = 'COM6'
        self.serial_port.port = self.NCDComPort
        self.serial_port.parity = "N"
        self.serial_port.stopbits = 1
        self.serial_port.xonxoff = 0
        self.serial_port.timeout = 3
        self.serial_port.open()
        # print(self.serial_port)

    def disconnectSerialConnection(self):
        self.serial_port.close()

    def send_decimal_bytes(self, decimal_bytes):
        #self.serial_port.flushInput()
        #self.serial_port.flushOutput()

        decimal_bytes = bytearray(decimal_bytes)
        self.serial_port.write(decimal_bytes)

    def receive_decimal_bytes(self):
        decimal_bytes = bytearray()
        decimal_bytes.extend(self.serial_port.read())
        print(decimal_bytes)
        print("RECEIVE SUCCESS")

    def Switch_ONN_Relay(self, Bank_number, Relay_number):
        self.send_decimal_bytes(TURN_ONN_INDIVIDUAL_RELAYS_IN_EACH_BANK[Bank_number - 1][Relay_number - 1])
        self.wait(.05) # malla

    def Switch_OFF_Relay(self, Bank_number, Relay_number):
        self.send_decimal_bytes(
            TURN_OFF_INDIVIDUAL_RELAYS_IN_EACH_BANK[Bank_number - 1][Relay_number - 1])
        self.wait(.05)  # vadali updated from 1 to .01 need to minimize the delay between the relay turn on #malla

    def Switch_ONN_ALL_Relays_In_Each_Bank(self, Bank_number):
        self.send_decimal_bytes(TURN_ONN_ALL_RELAYS_IN_EACH_BANK[Bank_number - 1])
        self.wait(.1)
    def Switch_OFF_ALL_Relays_In_Each_Bank(self, Bank_number):
        self.send_decimal_bytes(TURN_OFF_ALL_RELAYS_IN_EACH_BANK[Bank_number - 1])
        self.wait(.1)
    def Switch_OFF_ALL_Relays_In_All_Banks(self, Bank_number):
        self.send_decimal_bytes(TURN_OFF_ALL_RELAYS_IN_ALL_BANKS[Bank_number])
        self.wait(.1)

    def ConnectingSULUReload(self):
        self.Switch_ONN_Relay(5, 8)  # B5:R8 - ON
        self.wait(.2)
        self.Switch_ONN_Relay(3, 2)  # B3:R2 - ON
        self.wait(.2)
        #self.Switch_ONN_Relay(3, 3)  # B3:R3 - ON
        self.wait(.2)
        self.Switch_ONN_Relay(3, 1)  # B3:R1 - ON
        self.wait(.2)

    def ConnectingEEAReload(self):
        self.Switch_ONN_Relay(5, 8)  # B5:R8 - ON
        self.wait(.2)
        self.Switch_ONN_Relay(3, 2)  # B3:R2 - ON
        self.wait(.2)
        self.Switch_ONN_Relay(3, 3)  # B3:R3 - ON
        self.wait(.2)


    def ConnectingLegacyReload(self):
        self.Switch_ONN_Relay(5, 8)  # B5:R8 - ON
        self.wait(.2)
        self.Switch_ONN_Relay(3, 1)  # B3:R1 - ON

    def DisconnectingLegacyReload(self):
        self.Switch_ONN_Relay(5, 8)  # B5:R8 - ON
        self.wait(.2)
        self.Switch_ONN_Relay(3, 1)  # B3:R1 - ON

    def ConnectingMULUReload(self):
        self.Switch_ONN_Relay(5, 8)  # B5:R8 - ON
        self.wait(.2)
        self.Switch_ONN_Relay(3, 2)  # B3:R2 - ON
        self.wait(.2)
        self.Switch_ONN_Relay(3, 1)  # B3:R1 - ON
        self.wait(.2)

    def RemovingMULUReload(self):

        self.Switch_OFF_Relay(3, 2)  # B3:R2 - ON
        self.wait(.2)
        self.Switch_OFF_Relay(3, 1)  # B3:R1 - ON
        self.wait(.2)
        self.Switch_OFF_Relay(5, 8)  # B5:R8 - ON
        self.wait(.2)

    def DisconnectingEEAReload(self):
        self.Switch_OFF_Relay(5, 8)  # B5:R8 - ON # Need to check connection and modify this line Manoj Vadali
        self.wait(.2)
        self.Switch_OFF_Relay(3, 2)  # B3:R2 - ON
        self.wait(.2)
        self.Switch_OFF_Relay(3, 3)  # B3:R3 - ON
        self.wait(.2)

    def ConnectingCartridge(self, CARTRIDGE_EEPROM_command_byte,  BlackBoxComPort):
        # connecting to ACC#
        self.Switch_OFF_Relay(3, 3)  # B3:R3 - ON
        self.wait(.2)
        self.Switch_ONN_Relay(5, 4)  # B5:R4 - ON
        self.wait(.2)
        self.Switch_OFF_Relay(3, 4)  # B5:R4 - ON
        self.wait(.2)
        self.Switch_ONN_Relay(5, 3)  # B5:R6 - ON
        ##CARTRIDGE_EEPROM_command_byte=CARTRIDGE_EEPROM_command_byte
       # BlackBoxComPort=BlackBoxComPort
        print(CARTRIDGE_EEPROM_command_byte)
        self.wait(10)
        ser = serial.Serial(BlackBoxComPort, 9600)
        ############# READ ###################
        command = bytes(CARTRIDGE_EEPROM_command_byte)
        ser.flush()
        ser.flushInput()
        ser.flushOutput()
        ser.write(command)
        self.wait(5)
        # print(command)
        # ser.write(command)
        # self.wait(7)
        #ser.write(command)
        # self.wait(7)
        s = ser.read(2)
        s = list(s)
        packet_size = s[1]
        read_data = ser.read(packet_size - 2)
        read_data = list(read_data)
        print("==== Cartridge Reset READ DATA ====")
        print(read_data[1:-1])
        for retry in range(5):
            if len(read_data[1:-1]) == 5:
                ser.close()
                self.wait(5)
                ser = serial.Serial(self.BlackBoxComPort, 9600)
                self.wait(5)

                ser.write(command)
                self.wait(3)
                # ser.write(command)
                # serialControlObj.wait(5)
                # print(command)
                s = ser.read(2)
                s = list(s)
                packet_size = s[1]
                read_data = ser.read(packet_size - 2)
                read_data = list(read_data)
                print("==== Cartridge Reset READ DATA ====")
                print(read_data[1:-1])

        ser.close()
        self.Switch_OFF_Relay(5, 3)  # B5:R1 - OFF
        self.wait(.2)
        self.Switch_OFF_Relay(5, 4)  # B5:R1 - OFF
        self.wait(5)
        self.Switch_ONN_Relay(3, 3)  # B3:R4 - ON
        self.wait(0.2)
        self.Switch_ONN_Relay(3, 4)  # B3:R4 - ON

        # self.Switch_OFF_Relay(5, 3)  # B5:R1 - OFF
        # self.Switch_OFF_Relay(5, 7)  # B5:R6 - OFF
        self.wait(0.5)

    def ClampCycleTest(self):
        self.Switch_ONN_Relay(2, 5)  # B2:R5 - ON
        self.wait(6)
        self.Switch_OFF_Relay(2, 5)  # B2:R5 - OFF
        self.Switch_ONN_Relay(2, 4)  # B2:R4 - ON
        self.wait(6)
        self.Switch_OFF_Relay(2, 4)  # B2:R4 - OFF

    def Clamping(self):
        self.Switch_ONN_Relay(2, 5)  # B2:R5 - ON
        self.wait(6)
        self.Switch_OFF_Relay(2, 5)  # B2:R5 - OFF

    def GreenKeyAck(self):
        self.Switch_ONN_Relay(3, 5)  # B3:R5 - ON
        self.wait(1)
        self.Switch_OFF_Relay(3, 5)  # B3:R5 - OFF

    def Firing(self):
        self.Switch_ONN_Relay(2, 5)  # B2:R5 - ON
        self.wait(7)
        self.Switch_OFF_Relay(2, 5)  # B2:R5 - OFF

    def Retracting(self):
        self.Switch_ONN_Relay(2, 4)  # B2:R4 - ON
        self.wait(1)
        self.Switch_OFF_Relay(2, 4)  # B2:R4 - OFF

    def Unclamping(self):
        self.Switch_ONN_Relay(2, 4)  # B2:R4 - ON
        self.wait(6)
        self.Switch_OFF_Relay(2, 4)  # B2:R4 - OFF

    def Articulation(self):
        self.Switch_ONN_Relay(2, 3)  # B2:R3 - ON
        self.Switch_OFF_Relay(2, 3)  # B2:R3 - OFF
        self.Switch_ONN_Relay(2, 6)  # B2:R6 - ON
        self.Switch_OFF_Relay(2, 6)  # B2:R6 - OFF

    def Rotation(self):

        self.Switch_ONN_Relay(2, 7)  # B2:R7 - ON
        self.wait(1)
        self.Switch_OFF_Relay(2, 7)  # B2:R7 - OFF

        self.Switch_ONN_Relay(2, 8)  # B2:R8 - ON
        self.wait(1)
        self.Switch_OFF_Relay(2, 8)  # B2:R8 - OFF
        # self.Switch_ONN_Relay(2, 7)  # B2:R7 - ON
        # self.Switch_OFF_Relay(2, 7)  # B2:R7 - OFF

    def right_clockwise_rotation(self):
        self.wait(5)
        self.Switch_ONN_Relay(2, 7)  # B2:R7 - ON
        self.wait(1)
        self.Switch_OFF_Relay(2, 7)  # B2:R7 - OFF

    def left_clockwise_rotation(self):
        self.wait(5)
        self.Switch_ONN_Relay(2, 7)  # B2:R7 - ON
        self.wait(1)
        self.Switch_OFF_Relay(2, 7)  # B2:R7 - OFF

    def right_counterclockwise_rotation(self):
        self.wait(5)
        self.Switch_ONN_Relay(2, 7)  # B2:R7 - ON
        self.wait(1)
        self.Switch_OFF_Relay(2, 7)  # B2:R7 - OFF

    def left_counterclockwise_rotation(self):
        self.wait(5)
        self.Switch_ONN_Relay(2, 7)  # B2:R7 - ON
        self.wait(1)
        self.Switch_OFF_Relay(2, 7)  # B2:R7 - OFF

    def Adapter_Rotation_Tests(self, SuccessFlag, my_Serthread, videoPath):
        # Right CW Rotation

        my_Serthread.clearQue()
        self.right_clockwise_rotation()
        Timestamps, Strings_from_PowerPack = ReadingQue(my_Serthread.readQue)
        serialControl.convertListtoLogFile(Strings_from_PowerPack, str(videoPath + '\\TotalLog.txt'), fileOpenMode='a')

        Strings_to_Compare = locateStringsToCompareFromEvent('Adapter CW Rotated')
        if SuccessFlag:
            result = Compare('Adapter CW Rotated', Strings_to_Compare, Strings_from_PowerPack)
            self.Test_Results.append('Adapter CW Rotated:' + result)
        else:
            result = xCompare('Adapter CW Rotated', Strings_to_Compare, Strings_from_PowerPack)
            self.Test_Results.append('xAdapter CW Rotated:' + result)
        print(self.Test_Results)

        # Right CCW Rotation

        my_Serthread.clearQue()
        self.wait(5)
        self.Switch_ONN_Relay(2, 8)  # B2:R8 - ON
        self.wait(5)
        self.Switch_OFF_Relay(2, 8)  # B2:R8 - OFF
        Timestamps, Strings_from_PowerPack = ReadingQue(my_Serthread.readQue)
        serialControl.convertListtoLogFile(Strings_from_PowerPack, str(videoPath + '\\TotalLog.txt'), fileOpenMode='a')

        Strings_to_Compare = locateStringsToCompareFromEvent('Adapter CCW Rotated')
        if SuccessFlag:
            result = Compare('Adapter CCW Rotated', Strings_to_Compare, Strings_from_PowerPack)
            self.Test_Results.append('Adapter CCW Rotated:' + result)
        else:
            result = xCompare('Adapter CCW Rotated', Strings_to_Compare, Strings_from_PowerPack)
            self.Test_Results.append('xAdapter CCW Rotated:' + result)
        print(self.Test_Results)

        # Left CW Rotation
        my_Serthread.clearQue()
        self.wait(5)
        self.Switch_ONN_Relay(2, 1)  # B2:R1 - ON
        self.wait(5)
        self.Switch_OFF_Relay(2, 1)  # B2:R1 - OFF
        Timestamps, Strings_from_PowerPack = ReadingQue(my_Serthread.readQue)
        serialControl.convertListtoLogFile(Strings_from_PowerPack, str(videoPath + '\\TotalLog.txt'), fileOpenMode='a')

        Strings_to_Compare = locateStringsToCompareFromEvent('Adapter CW Rotated')
        if SuccessFlag:
            result = Compare('Adapter CW Rotated', Strings_to_Compare, Strings_from_PowerPack)
            self.Test_Results.append('Adapter CW Rotated:' + result)
        else:
            result = xCompare('Adapter CW Rotated', Strings_to_Compare, Strings_from_PowerPack)
            self.Test_Results.append('xAdapter CW Rotated:' + result)
        print(self.Test_Results)

        # Left  CCW Rotation
        my_Serthread.clearQue()
        self.wait(5)
        self.Switch_ONN_Relay(2, 2)  # B2:R2 - ON
        self.wait(5)
        self.Switch_OFF_Relay(2, 2)  # B2:R2 - OFF
        Timestamps, Strings_from_PowerPack = ReadingQue(my_Serthread.readQue)
        serialControl.convertListtoLogFile(Strings_from_PowerPack, str(videoPath + '\\TotalLog.txt'), fileOpenMode='a')

        Strings_to_Compare = locateStringsToCompareFromEvent('Adapter CCW Rotated')
        if SuccessFlag:
            result = Compare('Adapter CCW Rotated', Strings_to_Compare, Strings_from_PowerPack)
            self.Test_Results.append('Adapter CCW Rotated:' + result)
        else:
            result = xCompare('Adapter CCW Rotated', Strings_to_Compare, Strings_from_PowerPack)
            self.Test_Results.append('xAdapter CCW Rotated:' + result)
        print(self.Test_Results)


    def Reload_Articulation_Tests(self, SuccessFlag, my_Serthread, videoPath):
        my_Serthread.clearQue()
        self.wait(5)
        self.Switch_ONN_Relay(2, 6)  # B2:R6 - ON
        self.wait(5)
        self.Switch_OFF_Relay(2, 6)  # B2:R6 - OFF

        Timestamps, Strings_from_PowerPack = ReadingQue(my_Serthread.readQue)
        serialControl.convertListtoLogFile(Strings_from_PowerPack, str(videoPath + '\\TotalLog.txt'),
                                           fileOpenMode='a')
        Strings_to_Compare = locateStringsToCompareFromEvent('Right Articulation')
        if SuccessFlag:
            result = Compare('Right Articulation', Strings_to_Compare, Strings_from_PowerPack)
            self.Normal_Firing_Test_Results.append('Right Articulation:' + result)
        else:
            result = xCompare('Right Articulation', Strings_to_Compare, Strings_from_PowerPack)
            self.Normal_Firing_Test_Results.append('xRight Articulation:' + result)
        print(self.Normal_Firing_Test_Results)

        # Centering Articulation Test
        my_Serthread.clearQue()
        self.wait(5)
        self.Switch_ONN_Relay(2, 4)  # B2:R4 - ON
        self.wait(7)
        self.Switch_OFF_Relay(2, 4)  # B2:R4 - OFF
        Timestamps, Strings_from_PowerPack = ReadingQue(my_Serthread.readQue)
        serialControl.convertListtoLogFile(Strings_from_PowerPack, str(videoPath + '\\TotalLog.txt'),
                                           fileOpenMode='a')
        Strings_to_Compare = locateStringsToCompareFromEvent('Centering Articulation')
        if SuccessFlag:
            result = Compare('Centering Articulation', Strings_to_Compare, Strings_from_PowerPack)
            self.Normal_Firing_Test_Results.append('Centering Articulation:' + result)
        else:
            result = xCompare('Centering Articulation', Strings_to_Compare, Strings_from_PowerPack)
            self.Normal_Firing_Test_Results.append('xCentering Articulation:' + result)
        print(self.Normal_Firing_Test_Results)

        # Left Articulation Test
        my_Serthread.clearQue()
        self.wait(5)
        self.Switch_ONN_Relay(2, 3)  # B2:R3 - ON
        self.wait(7)
        self.Switch_OFF_Relay(2, 3)  # B2:R3 - OFF

        Timestamps, Strings_from_PowerPack = ReadingQue(my_Serthread.readQue)
        serialControl.convertListtoLogFile(Strings_from_PowerPack, str(videoPath + '\\TotalLog.txt'),
                                           fileOpenMode='a')
        Strings_to_Compare = locateStringsToCompareFromEvent('Left Articulation')
        if SuccessFlag:
            result = Compare('Left Articulation', Strings_to_Compare, Strings_from_PowerPack)
            self.Normal_Firing_Test_Results.append('Left Articulation:' + result)
        else:
            result = xCompare('Left Articulation', Strings_to_Compare, Strings_from_PowerPack)
            self.Normal_Firing_Test_Results.append('xLeft Articulation:' + result)
        print(self.Normal_Firing_Test_Results)

        # Centering Articulation Test
        my_Serthread.clearQue()
        self.wait(5)
        self.Switch_ONN_Relay(2, 4)  # B2:R4 - ON
        self.wait(7)
        self.Switch_OFF_Relay(2, 4)  # B2:R4 - OFF
        Timestamps, Strings_from_PowerPack = ReadingQue(my_Serthread.readQue)
        serialControl.convertListtoLogFile(Strings_from_PowerPack, str(videoPath + '\\TotalLog.txt'),
                                           fileOpenMode='a')
        Strings_to_Compare = locateStringsToCompareFromEvent('Centering Articulation')
        if SuccessFlag:
            result = Compare('Centering Articulation', Strings_to_Compare, Strings_from_PowerPack)
            self.Normal_Firing_Test_Results.append('Centering Articulation:' + result)
        else:
            result = xCompare('Centering Articulation', Strings_to_Compare, Strings_from_PowerPack)
            self.Normal_Firing_Test_Results.append('xCentering Articulation:' + result)
        print(self.Normal_Firing_Test_Results)


    def Reload_Clamp_Cycle_Test(self, SuccessFlag, my_Serthread, videoPath):
        with nidaqmx.Task() as task:
            task.ao_channels.add_ao_voltage_chan('Dev1/ao0')
            print('1 Channel 1 Sample Write:')
            print(task.write(0.7))
        my_Serthread.clearQue()
        self.wait(5)
        self.Switch_ONN_Relay(2, 5)  # B2:R5 - ON
        self.wait(10)
        self.Switch_OFF_Relay(2, 5)  # B2:R5 - OFF
        Timestamps, Strings_from_PowerPack = ReadingQue(my_Serthread.readQue)
        serialControl.convertListtoLogFile(Strings_from_PowerPack, str(videoPath + '\\TotalLog.txt'), fileOpenMode='a')
        Strings_to_Compare = locateStringsToCompareFromEvent('Clamp Cycle Test Clamping')

        if SuccessFlag:
            result = Compare('Clamp Cycle Test Clamping', Strings_to_Compare, Strings_from_PowerPack)
            self.Test_Results.append('Clamp Cycle Test Clamping:' + result)
            print("Step: Clamp Cycle Test Clamping Performed")

        else:
            result = xCompare('Clamp Cycle Test Clamping', Strings_to_Compare, Strings_from_PowerPack)
            self.Test_Results.append('xClamp Cycle Test Clamping:' + result)

        print(self.Test_Results)

        my_Serthread.clearQue()
        self.wait(5)
        with nidaqmx.Task() as task:
            task.ao_channels.add_ao_voltage_chan('Dev1/ao0')
            print('1 Channel 1 Sample Write:')
            print(task.write(0))

        self.Switch_ONN_Relay(2, 4)  # B2:R4 - ON
        self.wait(10)
        self.Switch_OFF_Relay(2, 4)  # B2:R4 - OFF

        Timestamps, Strings_from_PowerPack = ReadingQue(my_Serthread.readQue)
        serialControl.convertListtoLogFile(Strings_from_PowerPack, str(videoPath + '\\TotalLog.txt'), fileOpenMode='a')

        Strings_to_Compare = locateStringsToCompareFromEvent('Clamp Cycle Test Un-Clamping')
        if SuccessFlag:
            result = Compare('Clamp Cycle Test Un-Clamping', Strings_to_Compare, Strings_from_PowerPack)
            self.Test_Results.append('Clamp Cycle Test Un-Clamping:' + result)
        else:
            result = xCompare('Clamp Cycle Test Un-Clamping', Strings_to_Compare, Strings_from_PowerPack)
            self.Test_Results.append('xClamp Cycle Test Un-Clamping:' + result)

        print("Step: Clamp Cycle Test Un-Clamping Performed")
        print(self.Test_Results)


    def RemovingSULUReload(self):
        self.Switch_OFF_Relay(3, 1)  # B3:R1 - OFF
        self.Switch_OFF_Relay(3, 2)  # B3:R2 - OFF
        self.Switch_OFF_Relay(3, 3)  # B3:R3 - ON
        self.Switch_OFF_Relay(5, 8)  # B5:R8 - OFF


    def removeAdapter(self):
        self.Switch_OFF_Relay(1, 2)  # B1:R2 - OFF
        self.Switch_OFF_Relay(1, 3)  # B1:R3 - OFF
        self.Switch_OFF_Relay(1, 4)  # B1:R4 - OFF
        self.Switch_OFF_Relay(1, 1)  # B1:R1 - OFF
        self.Switch_OFF_Relay(1, 7)  # B1:R7 - OFF
        self.Switch_OFF_Relay(1, 6)  # B1:R7 - OFF



    def ConnectAdapter(self):
        self.Switch_ONN_Relay(1, 8)  # B1:R7 - OFF
        self.wait(5)
        self.Switch_ONN_Relay(1, 1)  # B1:R1 - OFF
        self.Switch_ONN_Relay(1, 2)  # B1:R2 - OFF
        self.Switch_ONN_Relay(1, 3)  # B1:R3 - OFF
        self.Switch_ONN_Relay(1, 4)  # B1:R4 - OFF
        self.Switch_ONN_Relay(1, 7)  # B1:R7 - OFF
        self.Switch_ONN_Relay(1, 6)  # B1:R7 - OFF



    def removeClamshell(self):
        self.Switch_OFF_Relay(1, 5)  # B1:R5 - OFF

    def connectClamshell(self):
        self.Switch_ONN_Relay(1, 5)  # B1:R5 - ON

    def PlacingPowerPackOnCharger(self):
        self.Switch_ONN_Relay(3, 8)
        self.Switch_ONN_Relay(3, 7)
        # self.Switch_ONN_Relay(4, 8)
        # self.Switch_ONN_Relay(5, 7)
        #self.wait(500)  # change this value after code verification to 1.5 hours =5400 seconds
        # self.Switch_OFF_Relay(4, 8)
        # self.Switch_OFF_Relay(5, 7)

    def removingPowerPackFromCharger(self):
        self.Switch_OFF_Relay(3, 7)
        self.Switch_OFF_Relay(3, 8)

    def ForceDecode(self, case):
        switch = {"Low": 1,
                  "Medium": 3.5,
                  "High": 5,
                  "Excessieve": 4,
                  "Load Profile": 5,
                  "65": 3.25,
                  "70": 3.5,
                  "30": 1.5
                  }
        a = switch.get(case)
        return a

    def EEAForceDecode(self, case):
        switch = {"Low": 2,
                  "Medium": 3.5,
                  "High": 5,
                  "Excessieve": 4,
                  "Load Profile": 5,
                  "65": 3.25,
                  "70": 3.5,
                  "30": 1.5
                  }
        a = switch.get(case)
        return a

    def RetractionForceDecode(self, case):
        switch = {"Low": 0.2,
                  "Medium": 1,
                  "High": 2,
                  "Excessieve": 4,
                  "Load Profile": 5,
                  "65": 3.25,
                  "70": 3.5,
                  "30": 1.5
                  }
        b = switch.get(case)
        return b
    def convertListtoLogFile(LogStringsList, LogFileName, fileOpenMode):
        with open(LogFileName, fileOpenMode) as logFile:
            [logFile.write(singleData + "\n") for singleData in LogStringsList]

# LogFile Name and LogStringsList are mandatory arguments
# fileOpenMode is a default argument which is 'w' by default, can be overridden by passing 'a' for opening the log file in append mode
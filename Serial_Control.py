# @ author - Varun Pandey
# Ver # 1, dated - Dec 22, 2021
# this code has been moved from NormalFiring.py - to properly organize the code structure

import time

import serial
import serial.tools.list_ports

import OLEDRecordingThread
from CRC16 import fetch_command, calc
from RelayControlBytes import *


class serialControl:
    
    def __init__(self,
                 r=None, SULU_EEPROM_command_byte=None, MULU_EEPROM_command_byte=None,
                 CARTRIDGE_EEPROM_command_byte=None, NCDComPort=None, PowerPackComPort=None,
                 BlackBoxComPort=None, USB6351ComPort=None, ArduinoUNOComPort=None,
                 FtdiUartComPort=None, OUTPUT_PATH=None, videoPath=None,
                 EEA_RELOAD_EEPROM_command_byte=None):
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
        self.videoPath = videoPath
        self.Test_Results = []
        self.Smoke_test_Results=[]
        self.Normal_Firing_Test_Results = []
        self.Recovery_items_Test_Results = []
        self.Firing_Recovery_items_Test_Results = []
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
        self.send_decimal_bytes(
            TURN_ONN_INDIVIDUAL_RELAYS_IN_EACH_BANK[Bank_number - 1][Relay_number - 1])
        self.wait(.1) # malla

    def Switch_OFF_Relay(self, Bank_number, Relay_number):
        self.send_decimal_bytes(
            TURN_OFF_INDIVIDUAL_RELAYS_IN_EACH_BANK[Bank_number - 1][Relay_number - 1])
        self.wait(.1)  # vadali updated from 1 to .01 need to minimize the delay between the relay turn on #malla

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

    def EEANoStaplesDetectedStateExit(self):
        logs_to_compare = 'No Staples Detected State Exit'
        self.Switch_ONN_Relay(2, 4)
        self.wait(1)  # Holding for 1 Second to Enter No Staples Exit Screen And High Speed Firing Recovery Screen Shows
        self.Switch_OFF_Relay(2, 4)
        self.wait(.2)
        self.Switch_ONN_Relay(2, 4)
        self.wait(3)  # Holding for 3 Seconds to Enter No Staples Exit Screen Shows Without Yellow Rectangle Segment
        self.Switch_OFF_Relay(2, 4)
        self.wait(.2)
        self.Switch_ONN_Relay(2, 4)
        self.wait(20)  # Holding for 20 Seconds to Trocar Extends to FULL Open Position - MAX_LIMIT
        self.Switch_OFF_Relay(2, 4)
        self.wait(.2)
        self.Switch_ONN_Relay(2, 5)
        self.wait(20)  # Holding for 20 Seconds to achieve CLAMP GAP.
        self.Switch_OFF_Relay(2, 5)
        self.wait(.2)
        self.Switch_ONN_Relay(2, 1)
        self.Switch_ONN_Relay(2, 2)
        self.Switch_ONN_Relay(2, 7)
        self.Switch_ONN_Relay(2, 8)
        self.wait(2)  # Holding for 2 Seconds to EEA Reload Removal Screen Shows along with SSE State.
        self.Switch_OFF_Relay(2, 8)
        self.Switch_OFF_Relay(2, 7)
        self.Switch_OFF_Relay(2, 2)
        self.Switch_OFF_Relay(2, 1)
        self.compare_logs(logs_to_compare=logs_to_compare, SuccessFlag=True, is_firing_test=True)


    def EEASurgicalSiteExtractionStateExit(self, logs_to_compare=None, occurrence=None):
        if 12_1 == occurrence:
            logs_to_compare = 'Rotation Operation During SP IP'
        elif 12_2 == occurrence:
            logs_to_compare = 'SSE Exit'
        elif 40 == occurrence:
            logs_to_compare = 'EEA SSE Countdown Exit'

        self.Switch_ONN_Relay(2, 1)
        self.Switch_ONN_Relay(2, 2)
        self.Switch_ONN_Relay(2, 7)
        self.Switch_ONN_Relay(2, 8)
        self.wait(3)  # Holding for 3 Seconds to Exit SSE State.
        self.Switch_OFF_Relay(2, 8)
        self.Switch_OFF_Relay(2, 7)
        self.Switch_OFF_Relay(2, 2)
        self.Switch_OFF_Relay(2, 1)
        self.compare_logs(logs_to_compare=logs_to_compare, SuccessFlag=True, is_firing_test=True)

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
        OLEDRecordingThread.exitFlag = True

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

    def write_eeprom_data(self, data_bytes, fixtureValidationReq=False):
        if fixtureValidationReq:
            pass
        else:
            print(f'command_bytes : {data_bytes}')
        Enable_OW = b'\xAA\x04\x07\x24'
        write_1_wire_command_byte = [0xAA, 0x4C, 0x0A]
        read_1_wire_command_byte = [0xAA, 0x0C, 0x0B]
        # In case of 'NACK' we are retrying to get 'ACK' for at max of 5 times
        try:
            with serial.Serial(port=self.BlackBoxComPort, baudrate=500000, timeout=3) as ser:
                ser.write(Enable_OW)

                for retry in range(5):
                    # ############ READ ###################
                    time.sleep(2)
                    packet_size = 0
                    while packet_size != 12:
                        # ser.write(Enable_OW)
                        # ser.flush()
                        s = ser.read(2)
                        s = list(s)
                        packet_size = s[1]
                        if packet_size != 12:
                            ser.read(packet_size - 2)
                        if fixtureValidationReq:
                            pass
                        else:
                            print("One-Wire is not detected!")
                        self.wait(0.1)

                    read_data = ser.read(packet_size - 2)
                    one_wire_address = list(read_data)[1:-1]
                    if fixtureValidationReq:
                        pass
                    else:
                        print(f"one_wire_address: {one_wire_address}")

                    prefix_command = write_1_wire_command_byte + one_wire_address
                    command_bytes = fetch_command(prefix_list=prefix_command, data_byte=data_bytes,
                                                  fixtureValidationReq=fixtureValidationReq)

                    ser.write(command_bytes)
                    self.wait(1)

                    read_command = read_1_wire_command_byte + one_wire_address
                    crc_value = calc(read_command)
                    crc_value = int(crc_value, 16)
                    read_command.append(crc_value)

                    if fixtureValidationReq:
                        pass
                    else:
                        print(read_command)
                    read_command = bytes(read_command)

                    ser.flush()
                    ser.flushInput()
                    ser.flushOutput()
                    ser.write(read_command)

                    cmd = 0
                    while cmd != 0x0B:
                        s = ser.read(3)
                        cmd = s[2]
                        length = s[1]
                        read_data = ser.read(length - 3)

                    # print(list(read_data[:64]))
                    command_list = list(command_bytes)[11:75]
                    # print("Command List ", command_list)
                    if list(read_data[:64]) == command_list:
                        if fixtureValidationReq:
                            pass
                        else:
                            print(f"one wire is written successfully with the data! \n{data_bytes}")
                        break
        except serial.SerialException as e:
            print(f"Failed to open port: {e}")

    def read_eeprom_data(self) -> list:
        # print(simple_colors.yellow(f'command_bytes : {data_bytes}'))
        Enable_OW = b'\xAA\x04\x07\x24'
        # write_1_wire_command_byte = [0xAA, 0x4C, 0x0A]
        read_1_wire_command_byte = [0xAA, 0x0C, 0x0B]
        # In case of 'NACK' we are retrying to get 'ACK' for at max of 5 times
        try:
            with serial.Serial(self.BlackBoxComPort, 500000) as ser:
                ser.write(Enable_OW)

                for retry in range(5):
                    # ############ READ ###################
                    time.sleep(1)
                    packet_size = 0
                    while packet_size != 12:
                        # ser.flush()
                        # ser.flushInput()
                        # ser.flushOutput()
                        s = ser.read(2)
                        s = list(s)
                        packet_size = s[1]
                        read_data = ser.read(packet_size - 2)
                        print(f'read_data: {list(read_data)}')
                        print("One-Wire is not detected!")
                        self.wait(0.5)

                    # read_data = ser.read(packet_size - 2)
                    one_wire_address = list(read_data)[1:-1]
                    print(f"one_wire_address: {one_wire_address}")

                    # prefix_command = write_1_wire_command_byte + one_wire_address

                    # command_bytes = fetch_command(prefix_list=prefix_command, data_byte=data_bytes)

                    # ser.write(command_bytes)
                    # self.wait(1)

                    read_command = read_1_wire_command_byte + one_wire_address
                    crc_value = calc(read_command)
                    crc_value = int(crc_value, 16)
                    read_command.append(crc_value)
                    print(read_command)
                    read_command = bytes(read_command)

                    # ser.flush()
                    # ser.flushInput()
                    # ser.flushOutput()
                    ser.write(read_command)

                    cmd = 0
                    while cmd != 0x0B:
                        s = ser.read(3)
                        cmd = s[2]
                        length = s[1]
                        read_data = ser.read(length - 3)

                    print(list(read_data[:64]))
                    # command_list = list(command_bytes)[11:75]
                    # if list(read_data[:64]) == command_list:
                    #     print(simple_colors.green(f"one wire is written successfully with the data! \n{data_bytes}"))
                    #     break
        except serial.SerialException as e:
            print(f"Failed to open port: {e}")

        # serialControl.close_serial_port(ser)
        return list(read_data[:64])


    def configure_clamshell_serial_control(self, byte_data, fixture_validation=False):
        self.Switch_OFF_Relay(1, 5)
        self.wait(1)

        self.Switch_ONN_Relay(5, 5)  # B5:R5 - ON
        self.Switch_ONN_Relay(5, 1)  # B5:R1 - ON

        self.wait(1)
        self.write_eeprom_data(data_bytes=byte_data, fixtureValidationReq=fixture_validation)

        self.Switch_OFF_Relay(5, 1)  # B5:R1 - OFF
        self.Switch_OFF_Relay(5, 5)  # B5:R1 - OFF
        self.wait(1)

    ## If it is a 21mm or 25mm reload, press the up-toggle button to remove the TAID
    ## If it is a 28mm, 31mm or 33mm reload, wait for the ship cap to be automatically ejected
    def configure_eea_reload_serial_control(self, reload_length, reload_color, ship_cap_status, reload_state=None,
                             fix_validation_req=False):
        EEA_RELOAD_EEPROM = [2, 3, 0x1C, 0x31, 0x32, 0x33, 0x34, 0x35, 0x36, 0x37, 0x38, 0x39, 0x31, 0x32, 0x33,
                             0x34,
                             0x35, 0x36, 4, 4, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                             0,
                             0, 0, 0x1D, 0x80, 0x78, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1]
        reload_diameter = enumerate([21, 25, 28, 31, 33], 1)
        reload_colors = enumerate(['Purple', 'Black'], 3)
        ship_cap_presence = enumerate(['No', 'Yes'], 4)

        for number, length in reload_diameter:
            if length == reload_length:
                EEA_RELOAD_EEPROM[
                    1] = number  # number will be 1 for 21mm, 2 for 25mm, 3 for 28mm, 4 for 31mm, and 5 for 33mm reload lengths
                break

        for count, possible_color in reload_colors:
            if possible_color == reload_color:
                EEA_RELOAD_EEPROM[19] = count  # count will be 3 for Purple, 4 for Black reload colors
                break

        for presence, possible_check in ship_cap_presence:
            if possible_check == ship_cap_status:
                EEA_RELOAD_EEPROM[
                    18] = presence  # presence will be 4 for No, 5 for Yes Ship Cap/TAID Presence checks
                break

        self.Switch_ONN_Relay(5, 2)  # B5:R2 - ON
        self.Switch_ONN_Relay(5, 6)  # B5:R6 - ON

        self.write_eeprom_data(data_bytes=EEA_RELOAD_EEPROM, fixtureValidationReq=fix_validation_req)

        self.Switch_OFF_Relay(5, 2)  # B5:R1 - OFF
        self.Switch_OFF_Relay(5, 6)  # B5:R2 - OFF

# LogFile Name and LogStringsList are mandatory arguments
# fileOpenMode is a default argument which is 'w' by default, can be overridden by passing 'a' for opening the log file in append mode
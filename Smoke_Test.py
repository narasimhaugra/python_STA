import sys

import nidaqmx
# import serial.tools.list_ports_windows
import serial
import serial.tools.list_ports

import MCPThread
import OLEDRecordingThread
from CRC16 import CRC16
from CRC16 import calc
from Compare import Compare
from Prepare_Output_Json_File import *
from ReadBatteryRSOC import read_battery_RSOC
from ReadStatusVariables import ReadStatusVariables
from Read_Handle_Fire_Count import GetHandleUseCount
from ReadingQue import ReadingQue
from RelayControlBytes import *
from Serial_Relay_Control import serialControl
from SmokeTestEventsStrings import locateStringsToCompareFromSmokeEvent


def find_first_occurrences(string):
    result = {}
    for i, char in enumerate(string):
        if char not in result:
            result[char] = i
    return result


def eea_open_button(serialControlObj, videoPath, log_string):
    serialControlObj.my_Serthread.clearQue()
    serialControlObj.wait(5)
    serialControlObj.Switch_ONN_Relay(2, 4)  # B2:R5 - ON
    serialControlObj.wait(20)
    serialControlObj.Switch_OFF_Relay(2, 4)  # B2:R5 - OFF

    if log_string != 'NONE':
        Timestamps, Strings_from_PowerPack = ReadingQue(serialControlObj.my_Serthread.readQue)
        serialControl.convertListtoLogFile(Strings_from_PowerPack, str(videoPath + '\\TotalLog.txt'), fileOpenMode='a')
        Strings_to_Compare = locateStringsToCompareFromSmokeEvent(log_string)
        result = Compare(log_string, Strings_to_Compare, Strings_from_PowerPack)
        serialControlObj.Smoke_test_Results.append(log_string + result)


def eea_close_button_with_obstruction(serRangeSensor, serialControlObj, videoPath, log_string):
    serRangeSensor.close()
    serRangeSensor = serial.Serial(serialControlObj.ArduinoUNOComPort, 115200)
    serialControlObj.my_Serthread.clearQue()
    serialControlObj.wait(5)
    # cf = serialControlObj.EEAForceDecode(clampingForce)
    serialControlObj.Switch_ONN_Relay(2, 5)  # B2:R5 - ON
    read_data1 = 200
    serRangeSensor.flushOutput()
    serRangeSensor.flush()
    serRangeSensor.flushInput()
    while not 100 < read_data1 <= 105:
        try:
            ser_bytes1 = serRangeSensor.readline()
            read_data1 = float(ser_bytes1.decode('ascii'))
            # serialControlObj.wait(.1)
            print(read_data1)
        except:
            pass

    with nidaqmx.Task() as task:
        task.ao_channels.add_ao_voltage_chan('Dev1/ao0')
        print('1 Channel 1 Sample Write:')
        print(task.write(4))
    serialControlObj.wait(25)

    Timestamps, Strings_from_PowerPack = ReadingQue(serialControlObj.my_Serthread.readQue)
    serialControl.convertListtoLogFile(Strings_from_PowerPack, str(videoPath + '\\TotalLog.txt'), fileOpenMode='a')
    Strings_to_Compare = locateStringsToCompareFromSmokeEvent(log_string)
    result = Compare(log_string, Strings_to_Compare, Strings_from_PowerPack)
    serialControlObj.Normal_Firing_Test_Results.append(log_string + result)
    serialControlObj.Switch_OFF_Relay(2, 5)

    with nidaqmx.Task() as task:
        task.ao_channels.add_ao_voltage_chan('Dev1/ao0')
        print('1 Channel 1 Sample Write:')
        print(task.write(0))
    serialControlObj.wait(10)


def eea_close_button_single_layer(serRangeSensor, serialControlObj, videoPath, log_string):
    serRangeSensor.close()
    serRangeSensor = serial.Serial(serialControlObj.ArduinoUNOComPort, 115200)
    serialControlObj.my_Serthread.clearQue()
    serialControlObj.wait(5)
    # cf = serialControlObj.EEAForceDecode(clampingForce)
    serialControlObj.Switch_ONN_Relay(2, 5)  # B2:R5 - ON
    read_data1 = 200
    serRangeSensor.flushOutput()
    serRangeSensor.flush()
    serRangeSensor.flushInput()
    while not 65 < read_data1 <= 85:
        try:
            ser_bytes1 = serRangeSensor.readline()
            read_data1 = float(ser_bytes1.decode('ascii'))
            # serialControlObj.wait(.1)
            print("----------------------" + read_data1)
        except:
            pass

    with nidaqmx.Task() as task:
        task.ao_channels.add_ao_voltage_chan('Dev1/ao0')
        print('1 Channel 1 Sample Write:')
        print(task.write(1.2))  # need to update the value
    serialControlObj.wait(25)
    serRangeSensor.close()

    Timestamps, Strings_from_PowerPack = ReadingQue(serialControlObj.my_Serthread.readQue)
    serialControl.convertListtoLogFile(Strings_from_PowerPack, str(videoPath + '\\TotalLog.txt'), fileOpenMode='a')
    Strings_to_Compare = locateStringsToCompareFromSmokeEvent(log_string)
    result = Compare(log_string, Strings_to_Compare, Strings_from_PowerPack)
    serialControlObj.Normal_Firing_Test_Results.append(log_string + result)
    serialControlObj.Switch_OFF_Relay(2, 5)
    serialControlObj.wait(.5)


def eea_close_button_New(serRangeSensor, serialControlObj, videoPath, log_string):
    serRangeSensor.close()
    serRangeSensor = serial.Serial(serialControlObj.ArduinoUNOComPort, 115200)
    serialControlObj.my_Serthread.clearQue()

    serialControlObj.wait(5)
    # cf = serialControlObj.EEAForceDecode(clampingForce)
    serialControlObj.Switch_ONN_Relay(2, 5)  # B2:R5 - ON
    read_data1 = 200
    serRangeSensor.flushOutput()
    serRangeSensor.flush()
    serRangeSensor.flushInput()
    while not 65 < read_data1 <= 95:
        try:
            ser_bytes1 = serRangeSensor.readline()
            read_data1 = float(ser_bytes1.decode('ascii'))
            # serialControlObj.wait(.1)
            print(read_data1)
        except:
            print("Fail----------------------------------------------")
            pass

    with nidaqmx.Task() as task:
        task.ao_channels.add_ao_voltage_chan('Dev1/ao0')
        print('1 Channel 1 Sample Write:')
        print(task.write(2))  # need to update the value

    serialControlObj.wait(25)
    serRangeSensor.close()
    Timestamps, Strings_from_PowerPack = ReadingQue(serialControlObj.my_Serthread.readQue)
    serialControl.convertListtoLogFile(Strings_from_PowerPack, str(videoPath + '\\TotalLog.txt'), fileOpenMode='a')
    Strings_to_Compare = locateStringsToCompareFromSmokeEvent(log_string)
    result = Compare(log_string, Strings_to_Compare, Strings_from_PowerPack)
    serialControlObj.Normal_Firing_Test_Results.append(log_string + result)
    serialControlObj.Switch_OFF_Relay(2, 5)
    print("-----------------------------------------------", Strings_from_PowerPack)
    print("------------------------------------------------", Strings_to_Compare)
    print(serialControlObj.Normal_Firing_Test_Results)


def eea_close_button(serRangeSensor, serialControlObj, videoPath, log_string):
    serRangeSensor.close()
    serRangeSensor = serial.Serial(serialControlObj.ArduinoUNOComPort, 115200)
    serialControlObj.my_Serthread.clearQue()

    serialControlObj.wait(5)
    # cf = serialControlObj.EEAForceDecode(clampingForce)
    serialControlObj.Switch_ONN_Relay(2, 5)  # B2:R5 - ON
    read_data1 = 200
    serRangeSensor.flushOutput()
    serRangeSensor.flush()
    serRangeSensor.flushInput()
    while not 65 < read_data1 <= 80:
        try:
            ser_bytes1 = serRangeSensor.readline()
            read_data1 = float(ser_bytes1.decode('ascii'))
            # serialControlObj.wait(.1)
            print(read_data1)
        except:
            print("Fail----------------------------------------------")
            pass

    with nidaqmx.Task() as task:
        task.ao_channels.add_ao_voltage_chan('Dev1/ao0')
        print('1 Channel 1 Sample Write:')
        print(task.write(2))  # need to update the value

    serialControlObj.wait(25)
    serRangeSensor.close()
    Timestamps, Strings_from_PowerPack = ReadingQue(serialControlObj.my_Serthread.readQue)
    serialControl.convertListtoLogFile(Strings_from_PowerPack, str(videoPath + '\\TotalLog.txt'), fileOpenMode='a')
    Strings_to_Compare = locateStringsToCompareFromSmokeEvent(log_string)
    result = Compare(log_string, Strings_to_Compare, Strings_from_PowerPack)
    serialControlObj.Normal_Firing_Test_Results.append(log_string + result)
    serialControlObj.Switch_OFF_Relay(2, 5)
    print("-----------------------------------------------", Strings_from_PowerPack)
    print("------------------------------------------------", Strings_to_Compare)
    print(serialControlObj.Normal_Firing_Test_Results)


def SmokeTest(r, SULU_EEPROM_command_byte, MULU_EEPROM_command_byte, CARTRIDGE_EEPROM_command_byte, NCDComPort,
              PowerPackComPort, BlackBoxComPort, USB6351ComPort, ArduinoUNOComPort, OUTPUT_PATH, videoPath, p,
              EEA_RELOAD_EEPROM_command_byte):
    # print('normal firing', r, SULU_EEPROM_command_byte, MULU_EEPROM_command_byte, CARTRIDGE_EEPROM_command_byte, i)
    # Test_Results = []
    NCDComPort = NCDComPort
    print(NCDComPort, 'NCD COM Port')
    print("-----------------EEA Smoke Test-------------------")
    serialControlObj = serialControl(r, SULU_EEPROM_command_byte, MULU_EEPROM_command_byte,
                                     CARTRIDGE_EEPROM_command_byte, NCDComPort, PowerPackComPort, BlackBoxComPort,
                                     USB6351ComPort, ArduinoUNOComPort, OUTPUT_PATH, videoPath,
                                     EEA_RELOAD_EEPROM_command_byte)
    serialControlObj.OpenSerialConnection()
    # Normal_Firing(serialControlObj) #, PowerPackComPort)
    Smoke_Firing(serialControlObj, EEA_RELOAD_EEPROM_command_byte, NCDComPort,
                 PowerPackComPort, BlackBoxComPort, USB6351ComPort, ArduinoUNOComPort, OUTPUT_PATH, videoPath, p)
    serialControlObj.disconnectSerialConnection()


def Smoke_Firing(serialControlObj, EEA_RELOAD_EEPROM_command_byte, NCDComPort,
                 PowerPackComPort, BlackBoxComPort, USB6351ComPort, ArduinoUNOComPort, OUTPUT_PATH, videoPath, p):
    # r = getrow('C:\Python\Test_Configurator.xlsx', 0)
    PowerPackComPort = PowerPackComPort
    EEA_RELOAD_EEPROM_command_byte = EEA_RELOAD_EEPROM_command_byte
    ArduinoUNOComPort = ArduinoUNOComPort
    NCDComPort = NCDComPort
    print(NCDComPort)
    iterPass = 0
    firePass = 0
    TestBatteryLevelMax = serialControlObj.r['Battery RSOC Max Level']
    TestBatteryLevelMin = serialControlObj.r['Battery RSOC Min Level']
    clampingForce = serialControlObj.r['Clamping Force']
    firingForce = serialControlObj.r['Firing Force']
    # articulationStateinFiring = serialControlObj.r['Articulation State for clamping & firing']
    numberOfFiringsinProcedure = serialControlObj.r['Num of Firings in Procedure']
    retractionForce = serialControlObj.r['Retraction Force']
    print(TestBatteryLevelMax, TestBatteryLevelMin, clampingForce, firingForce, numberOfFiringsinProcedure)
    with nidaqmx.Task() as task:
        task.ao_channels.add_ao_voltage_chan('Dev1/ao0')
        print('1 Channel 1 Sample Write: ')
        print(task.write(0.0))

    serialControlObj.send_decimal_bytes(TURN_OFF_ALL_RELAYS_IN_ALL_BANKS[0])
    # serialControlObj.wait(0.5)
    # serialControlObj.Switch_ONN_Relay(3, 8)
    #
    # serialControlObj.wait(0.5)
    # serialControlObj.Switch_ONN_Relay(3, 7)
    #
    # serialControlObj.wait(60)
    #
    # serialControlObj.send_decimal_bytes(TURN_OFF_ALL_RELAYS_IN_ALL_BANKS[0])
    # print("Step: Remove Signia Power Handle from Charger")
    # serialControlObj.wait(40)

    # ###################################  RESETTING CLAMSHELL   #############################################################################
    #
    byte_data = [2, 3, 4, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    crc_value = CRC16(0x00, byte_data)
    crc_value = hex(crc_value)
    print('Original CRC: ', crc_value)
    # crc_second_byte = crc_value[2:4]
    # crc_first_byte = crc_value[4:]
    l = len(crc_value)
    crc_second_byte = crc_value[2:(l - 2)]
    crc_first_byte = crc_value[(l - 2):]
    # print(crc_first_byte)
    # print(crc_second_byte)
    byte_data.append(int(crc_first_byte, 16))
    byte_data.append(int(crc_second_byte, 16))
    # print(byte_data)
    # print(len(byte_data))
    ######################################
    byte_lst = [170, 69, 2, 1] + byte_data
    # print(byte_lst)
    crc_value = calc(bytes(byte_lst))
    crc_value = int(crc_value, 16)
    byte_lst.append(crc_value)
    command_byte = (byte_lst)
    # print(command_byte)
    # serialControlObj.Switch_ONN_Relay(5, 8)  # B5:R1 - ON
    serialControlObj.Switch_ONN_Relay(5, 1)  # B5:R1 - ON
    serialControlObj.Switch_ONN_Relay(5, 5)  # B5:R1 - ON
    ser = serial.Serial(serialControlObj.BlackBoxComPort, 9600)
    serialControlObj.wait(5)
    ############# READ ###################
    command = bytes(command_byte)
    print('Clamshell ResetByte array', command)
    ser.write(command)
    serialControlObj.wait(3)
    # serialControlObj.wait(5)
    print(command)
    s = ser.read(2)
    s = list(s)
    packet_size = s[1]
    read_data = ser.read(packet_size - 2)
    read_data = list(read_data)
    print("==== Clamshell Reset READ DATA ====")
    print(read_data[1:-1])
    ser.close()
    serialControlObj.Switch_OFF_Relay(5, 1)  # B5:R1 - OFF
    serialControlObj.Switch_OFF_Relay(5, 5)  # B5:R1 - OFF
    serialControlObj.wait(1)

    if False:  # (read_battery_RSOC(25,PowerPackComPort) > TestBatteryLevelMax):  # and (read_battery_RSOC(25, PowerPackComPort) > TestBatteryLevelMin):
        serialControlObj.Switch_ONN_Relay(1, 8)
        serialControlObj.wait(10)
        print("EEA Adapter Engaged to Power Pack Mechanically")

        # TEST STEP: Attach the EGIA Adapter
        serialControlObj.Switch_ONN_ALL_Relays_In_Each_Bank(1)  # B1 - ALL ON
        print("Step: EEA Adapter Connected")
        serialControlObj.wait(20)
        serialControlObj.ConnectingEEAReload()
        print("Step: EEA Reload Connected")
        serialControlObj.wait(5)

        with nidaqmx.Task() as task:
            task.ao_channels.add_ao_voltage_chan('Dev1/ao0')
            print('Setting the particle brake for quick discharging the Power Pack')
            print(task.write(2.0))

        while (read_battery_RSOC(25,
                                 PowerPackComPort)) > TestBatteryLevelMax:  # and (read_battery_RSOC(25, PowerPackComPort) > TestBatteryLevelMin):
            serialControlObj.Switch_ONN_Relay(2,
                                              5)  # B2:R5 - ON -- some operations battery discharge Check if loaded condition of trocar can be explored for quick discharge
            serialControlObj.wait(7)
            serialControlObj.Switch_OFF_Relay(2, 5)  # B2:R5 - ON
            serialControlObj.Switch_ONN_Relay(2, 4)  # B2:R5 - ON
            serialControlObj.wait(7)
            serialControlObj.Switch_OFF_Relay(2, 4)  # B2:R5 - ON

        serialControlObj.DisconnectingEEAReload()
        serialControlObj.Switch_OFF_ALL_Relays_In_Each_Bank(1)  # Disconnected the clamshell
        serialControlObj.wait(10)
    if False:  # (read_battery_RSOC(25, PowerPackComPort) < TestBatteryLevelMin):  # and (read_battery_RSOC(25, PowerPackComPort) <= TestBatteryLevelMax):
        # print('entered elif loop')
        serialControlObj.Switch_ONN_Relay(3, 7)  # battery charge
        serialControlObj.wait(0.5)
        serialControlObj.Switch_ONN_Relay(3, 8)
        # need to optimize this delay so that handle does not go to sleep or does not result communciation
        serialControlObj.wait(5)
        while (read_battery_RSOC(50,
                                 PowerPackComPort) < TestBatteryLevelMin):  # and (read_battery_RSOC(25, PowerPackComPort) <= TestBatteryLevelMax):
            pass

    # serialControlObj.wait(20)
    # print("----------Placing Power Pack on Charger for startup Test--------------")
    # serialControlObj.Switch_ONN_Relay(3, 7)
    # serialControlObj.wait(.2)
    # serialControlObj.Switch_ONN_Relay(3, 8)
    # serialControlObj.wait(60)
    # print("----------Removing Power Pack from Charger for startup Test--------------")
    # serialControlObj.Switch_OFF_Relay(3, 7)
    # serialControlObj.wait(.2)
    # serialControlObj.Switch_OFF_Relay(3, 8)
    serialControlObj.startup_log()
    # while True:
    #     # seriallistData = serial.tools.list_ports.comports()
    #     # print(seriallistData)
    #     singiaPowerFound = False
    #     if any("SigniaPowerHandle" in s for s in serial.tools.list_ports.comports()):
    #         singiaPowerFound = True
    #     else:
    #         print('Signia Com Port Closed')
    #         singiaPowerFound = False
    #         break
    #
    # # serialControlObj.wait(4)
    # strPort = 'None'
    # # serialControlObj.wait(2)
    # while not 'SigniaPowerHandle' in strPort:
    #     ports = serial.tools.list_ports.comports()
    #     # strPort = 'None'
    #     numConnection = len(ports)
    #     for z in range(0, numConnection):
    #         port = ports[z]
    #         strPort = str(port)
    #         if 'SigniaPowerHandle' in strPort:
    #             print(ports[z], 'Available')
    #             break
    # serialControlObj.wait(7)
    #
    # PPnotReady = True
    # while PPnotReady:
    #     try:
    #
    #         serPP = serial.Serial(serialControlObj.PowerPackComPort, 115200, bytesize=8, parity='N', stopbits=1,
    #                               timeout=0.05, xonxoff=0)
    #         serialControlObj.my_Serthread = MCPThread.readingPowerPack(serPP, 1000)
    #         serialControlObj.my_Serthread.clearQue()
    #         MCPThread.readingPowerPack.exitFlag = False
    #         serialControlObj.my_Serthread.start()
    #         PPnotReady = False
    #         # print(sys.argv[0], end=" ")
    #     except:
    #         pass
    #
    # serialControlObj.Test_Results.append(
    #     str(serialControlObj.r['Scenario Num']) + '#' + str(p + 1) + "@" + serialControlObj.r[
    #         'Test Scenario'])  # + str(i+1))
    #
    # serialControlObj.wait(60)
    # searchFlag = True
    """
    Timestamps, Strings_from_PowerPack, data_path = ReadingQue(1000, serialControlObj.my_Serthread.readQue, searchFlag)
    serialControl.convertListtoLogFile(Strings_from_PowerPack, (videoPath + '\\StartUpLog.txt'), fileOpenMode='w')
    serialControl.convertListtoLogFile(Strings_from_PowerPack, 'TotalLog.txt', fileOpenMode='a')
    Strings_to_Compare = locateStringsToCompareFromSmokeEvent('Remove Signia Power Handle from Charger')
    result = Compare('Remove Signia Power Handle from Charger', Strings_to_Compare, Strings_from_PowerPack)
    data_path = "None" if not data_path else data_path
    serialControlObj.Test_Results.append('Eventlog:' + data_path)
    serialControlObj.Test_Results.append('Remove Signia Power Handle from Charger:' + result)

    

    serialControlObj.Switch_ONN_Relay(5, 1)  # B5:R1 - ON
    serialControlObj.Switch_ONN_Relay(5, 5)  # B5:R1 - ON
    ser = serial.Serial(serialControlObj.BlackBoxComPort, 9600)
    serialControlObj.wait(5)
    ############# READ ###################
    # command = bytes(command_byte) # Commented by Manoj Vadali
    print('Clamshell ResetByte array', command)
    ser.write(command)
    serialControlObj.wait(1)
    # serialControlObj.wait(5)
    # print(command)
    s = ser.read(2)
    s = list(s) 
    packet_size = s[1]
    read_data = ser.read(packet_size - 2)
    read_data = list(read_data)
    print("==== Clamshell Reset READ DATA ====")
    print(read_data[1:-1])
    ser.close()
    serialControlObj.Switch_OFF_Relay(5, 1)  # B5:R1 - OFF
    serialControlObj.Switch_OFF_Relay(5, 5)  # B5:R1 - OFF
    serialControlObj.wait(1)
    serialControlObj.my_Serthread.clearQue()
    serialControlObj.wait(5)

    serialControlObj.connectClamshell()
    print("Step: Clamshell Connected")
    serialControlObj.wait(5)
    Timestamps, Strings_from_PowerPack = ReadingQue(200, serialControlObj.my_Serthread.readQue)
    # serialControl.convertListtoLogFile(Strings_from_PowerPack, 'TotalLog.txt', fileOpenMode='a')
    serialControl.convertListtoLogFile(Strings_from_PowerPack, str(videoPath + '\\TotalLog.txt'), fileOpenMode='a')
    Strings_to_Compare = locateStringsToCompareFromSmokeEvent('Clamshell Connected')
    result = Compare('Clamshell Connected', Strings_to_Compare, Strings_from_PowerPack)



    serialControlObj.Test_Results.append('Connected Clamshell:' + result)
    print(Timestamps)
    print(serialControlObj.Test_Results)

    ## Engaging the Adapter - Controlling the stepper motor
    serialControlObj.Switch_ONN_Relay(1, 8)
    serialControlObj.wait(7)
    print("EEA Adapter Engaged to Power Pack Mechanically")

    serialControlObj.my_Serthread.clearQue()
    serialControlObj.wait(5)
    # TEST STEP: Attach the EEA Adapter
    serialControlObj.Switch_ONN_ALL_Relays_In_Each_Bank(1)  # B1 - ALL ON
    print("Step: EEA Adapter Connected")
    serialControlObj.wait(40)
    Timestamps, Strings_from_PowerPack = ReadingQue(1000, serialControlObj.my_Serthread.readQue)
    serialControl.convertListtoLogFile(Strings_from_PowerPack, str(videoPath + '\\TotalLog.txt'), fileOpenMode='a')
    Strings_to_Compare = locateStringsToCompareFromSmokeEvent('EEA Adapter Connected')
    result = Compare('EEA Adapter Connected', Strings_to_Compare, Strings_from_PowerPack)
    serialControlObj.Test_Results.append('EEA Adapter Connected:' + result)
    print(serialControlObj.Test_Results)

    Strings_to_Compare = locateStringsToCompareFromSmokeEvent('Trocar Home Position')
    result = Compare('Trocar Home Position', Strings_to_Compare, Strings_from_PowerPack)
    serialControlObj.Test_Results.append('Trocar Home Position:' + result)
    print(serialControlObj.Test_Results)



    # serialControlObj.wait(5)
    serialControlObj.my_Serthread.clearQue()
    serialControlObj.wait(5)

    ###  Performing Tip Protector Detection ###
    serRangeSensor = serial.Serial(serialControlObj.ArduinoUNOComPort, 115200)
    serRangeSensor.flushOutput()
    serRangeSensor.flush()
    serRangeSensor.flushInput()

    MCPThread.readingPowerPack.exitFlag = True
    serPP.close()
    serialControlObj.wait(2)
    print(serialControlObj.Test_Results)
    HandleFireCount1, HandleProcedureCount = GetHandleUseCount(PowerPackComPort)
    print('Before Firing Handle Fire Count:' + str(HandleFireCount1),
          'Handle Procedure Count:' + str(HandleProcedureCount))
    serialControlObj.wait(2)
    StatusVariables1 = ReadStatusVariables(PowerPackComPort)
    StatusVariables1 = StatusVariables1[13:61]
    StatusVariables1 = StatusVariables1[4:8] + StatusVariables1[12:16] + StatusVariables1[20:24] + StatusVariables1[
                                                                                                   28:32] + StatusVariables1[
                                                                                                            36:40] + StatusVariables1[
                                                                                                                     44:48]
    print('Before Firing Status Variables: ', StatusVariables1)
    serPP = serial.Serial(serialControlObj.PowerPackComPort, 115200, bytesize=8, parity='N', stopbits=1,timeout=0.05, xonxoff=0)
    MCPThread.readingPowerPack.exitFlag = False
    serialControlObj.my_Serthread = MCPThread.readingPowerPack(serPP, 1000)
    serialControlObj.my_Serthread.clearQue()
    serialControlObj.my_Serthread.start()

    serialControlObj.Normal_Firing_Test_Results = []
    serialControlObj.Normal_Firing_Test_Results.append('Firing =' + str(1))
    OLEDRecordingThread.exitFlag = False

    if serialControlObj.r['Reload Type'] == "EEA":
        videoThread = OLEDRecordingThread.myThread(
            (str(serialControlObj.r['Scenario Num']) + '#' + str(1) + serialControlObj.r['Test Scenario'] + '_' +
             serialControlObj.r['Reload Type'] + '_' + str(1)),
            serialControlObj.videoPath)
        videoThread.start()
        serialControlObj.Switch_ONN_Relay(5, 2)  # B5:R2 - ON
        serialControlObj.Switch_ONN_Relay(5, 6)  # B5:R6 - ON
        serialControlObj.wait(5)
        ser = serial.Serial(serialControlObj.BlackBoxComPort, 9600)
        ############# READ ###################
        # command = bytes(serialControlObj.SULU_EEPROM_command_byte)
        command = bytes(EEA_RELOAD_EEPROM_command_byte)

        print('EEA RELOAD command', command)
        ser.write(command)
        serialControlObj.wait(5)
        # print(command)
        s = ser.read(2)
        s = list(s)
        packet_size = s[1]
        read_data = ser.read(packet_size - 2)
        read_data = list(read_data)
        print("==== EEA Reload Reset READ DATA ====")
        print(read_data[1:-1])
        ser.close()
        serialControlObj.Switch_OFF_Relay(5, 2)  # B5:R1 - OFF
        serialControlObj.Switch_OFF_Relay(5, 6)  # B5:R2 - OFF
        serialControlObj.wait(5)

        # TEST STEP: Connecting EEA Reload  147 and 148

        serialControlObj.my_Serthread.clearQue()
        serialControlObj.wait(5)
        serialControlObj.ConnectingEEAReload()
        serialControlObj.wait(5)
        Timestamps, Strings_from_PowerPack = ReadingQue(1000, serialControlObj.my_Serthread.readQue)
        serialControl.convertListtoLogFile(Strings_from_PowerPack, str(videoPath + '\\TotalLog.txt'), fileOpenMode='a')

        if serialControlObj.r['Ship cap Present'] == "Yes":
            Strings_to_Compare = locateStringsToCompareFromSmokeEvent('EEA RELOAD Connected with Ship cap',
                                                                 Length=serialControlObj.r.get('Reload Diameter(mm)'),
                                                                 Color=serialControlObj.r.get('Reload Color'))
            result = Compare('EEA RELOAD Connected', Strings_to_Compare, Strings_from_PowerPack)
            serialControlObj.Normal_Firing_Test_Results.append('EEA RELOAD Connected:' + result)

        elif serialControlObj.r['Ship cap Present'] == "No":
            Strings_to_Compare = locateStringsToCompareFromSmokeEvent('EEA RELOAD Connected without Ship cap',
                                                                 Length=serialControlObj.r.get('Reload Diameter(mm)'),
                                                                 Color=serialControlObj.r.get('Reload Color'))
            result = Compare('EEA RELOAD Connected', Strings_to_Compare, Strings_from_PowerPack)
            serialControlObj.Normal_Firing_Test_Results.append('EEA RELOAD Connected:' + result)

        print("Step: EEA Reload Connected")
        print(serialControlObj.Normal_Firing_Test_Results)
        serialControlObj.wait(3)

        # TEST STEP: Extension of Trocar Open button   150 to 151
        eea_open_button(serialControlObj, serialControlObj.my_Serthread, videoPath,"EEA Trocar Position Screen")


        #Insert one layer of foam, an obstruction 152 to 156
        eea_close_button_with_obstruction(serRangeSensor, serialControlObj, serialControlObj.my_Serthread, videoPath,
                         "Error Screens - Obstruction On Trocar Close")

        # EEA_FULL_OPEN_POSITION  157
        eea_open_button(serialControlObj, serialControlObj.my_Serthread, videoPath, "Error Screens - Obstruction On Trocar Open")

        # Remove  Anvil, obstruction, and foam.  158

        #159

        serRangeSensor.close()
        serRangeSensor = serial.Serial(serialControlObj.ArduinoUNOComPort, 115200)
        serialControlObj.my_Serthread.clearQue()
        serialControlObj.wait(5)
        # cf = serialControlObj.EEAForceDecode(clampingForce)
        serialControlObj.Switch_ONN_Relay(2, 5)
        # B2:R5 - ON
        serialControlObj.wait(3)
        serialControlObj.Switch_OFF_Relay(2, 5)

        serialControlObj.Switch_ONN_Relay(2, 4)
        # B2:R5 - ON
        serialControlObj.wait(5)
        serialControlObj.Switch_OFF_Relay(2, 4)

        Timestamps, Strings_from_PowerPack = ReadingQue(1000, serialControlObj.my_Serthread.readQue)
        serialControl.convertListtoLogFile(Strings_from_PowerPack, str(videoPath + '\\TotalLog.txt'), fileOpenMode='a')
        Strings_to_Compare = locateStringsToCompareFromSmokeEvent('EEA Trocar Position Screen')
        result = Compare('EEA Trocar Position Screen', Strings_to_Compare, Strings_from_PowerPack)
        serialControlObj.Normal_Firing_Test_Results.append('EEA Trocar Position Screen:' + result)


        # #160
        eea_close_button_single_layer(serRangeSensor, serialControlObj, serialControlObj.my_Serthread, videoPath,"Low Speed Clamping zone")


        #161 Rotation compensation 164 CAUTION_TONE plays 800ms after anvil is detected   165  LOW_TISSUE_COMPRESSION screens alternate every 500ms


        #167
        eea_open_button(serialControlObj, serialControlObj.my_Serthread, videoPath, "NONE")
        #foam for a total of 6 layers



        #168 to 175
        eea_close_button(serRangeSensor, serialControlObj, serialControlObj.my_Serthread, videoPath,
                         "EEA Clamping on Tissue")

        # Timestamps, Strings_from_PowerPack = ReadingQue(1000, serialControlObj.my_Serthread.readQue)
        # serialControl.convertListtoLogFile(Strings_from_PowerPack, str(videoPath + '\\TotalLog.txt'), fileOpenMode='a')
        # Strings_to_Compare = locateStringsToCompareFromSmokeEvent('EEA Clamping on Tissue')
        # result = Compare('EEA Clamping on Tissue', Strings_to_Compare, Strings_from_PowerPack)
        # serialControlObj.Normal_Firing_Test_Results.append( 'EEA Clamping on Tissue:' + result)


        print(serialControlObj.Normal_Firing_Test_Results)

        # TEST STEP: Acknowledge Safety Key (Green LED) for firing

        #176
        serialControlObj.my_Serthread.clearQue()
        serialControlObj.wait(5)

        serialControlObj.GreenKeyAck()
        serialControlObj.wait(2)
        Timestamps, Strings_from_PowerPack = ReadingQue(500, serialControlObj.my_Serthread.readQue)
        serialControl.convertListtoLogFile(Strings_from_PowerPack, str(videoPath + '\\TotalLog.txt'), fileOpenMode='a')
        Strings_to_Compare = locateStringsToCompareFromSmokeEvent('EEA Green Key Ack')
        result = Compare('EEA Green Key Ack', Strings_to_Compare, Strings_from_PowerPack)
        serialControlObj.Normal_Firing_Test_Results.append('EEA Green Key Ack:' + result)
        print("Step: Acknowledged Safety Key (Green LED) for firing")
        print(serialControlObj.Normal_Firing_Test_Results)
        # rlist = {'Test Step': ['Safety Key: Acknowledged'], 'Test Result': [result]}
        # df = df.append(pd.DataFrame(rlist))

        # TEST STEP: Firing
        # ff = serialControlObj.EEAForceDecode(firingForce)
        with nidaqmx.Task() as task:
            task.ao_channels.add_ao_voltage_chan('Dev1/ao0')
            print('1 Channel 1 Sample Write: ')
            print(task.write(3.25))  # Updated the 2.75 to 3.25 by Manoj Vadali 8th nov 2023

        serialControlObj.my_Serthread.clearQue()
        serialControlObj.wait(5)
        serialControlObj.Switch_ONN_Relay(4, 1)
        serialControlObj.Switch_ONN_Relay(4, 2)  # To turn on Linear actuator
        serialControlObj.wait(2.5)  # 27th nov (2 seconds changed to 3 on Nov 6th 20223)
        serialControlObj.Switch_ONN_Relay(2, 5)  # B2:R5 - ON
        serialControlObj.wait(0.5)
        serialControlObj.Switch_OFF_Relay(2, 5)  # B2:R5 - OFF  # Need to test Manoj Vadali
        # serialControlObj.wait(1)
        serialControlObj.wait(6)  # 27th nov updated from 6 to 4
        serialControlObj.Switch_OFF_Relay(4, 1)
        serialControlObj.Switch_OFF_Relay(4, 2)  # To turn on Linear actuator
        serialControlObj.wait(3)  # Manoj changed on 27th from 0.5 to 2
        # with nidaqmx.Task() as task:
        #     task.ao_channels.add_ao_voltage_chan('Dev1/ao0')
        #     print('1 Channel 1 Sample Write: ')
        #     print(task.write(0))  # Updated the ff to zero by Manoj Vadali
        # serialControlObj.wait(2)
        serialControlObj.Switch_ONN_Relay(4, 3)
        serialControlObj.Switch_ONN_Relay(4, 4)  # To turn on Linear actuator at full power
        #serialControlObj.wait(5)  # need to optimize based on firing duration (changed from 7 to 5 8th nov by Manoj vadali
        serialControlObj.wait(2)
        with nidaqmx.Task() as task:
            task.ao_channels.add_ao_voltage_chan('Dev1/ao0')
            print('1 Channel 1 Sample Write: ')
            print(task.write(0))  # Updated the ff to zero by Manoj Vadali
        serialControlObj.wait(10)

        serialControlObj.Switch_OFF_Relay(4, 3)
        serialControlObj.Switch_OFF_Relay(4, 4)  # To turn off Linear actuator from full power
        serialControlObj.wait(.5)  # need to optimize based on firing duration
        serialControlObj.Switch_ONN_Relay(4, 5)
        serialControlObj.Switch_ONN_Relay(4, 6)  # To turn on Linear actuator at full power
        serialControlObj.wait(30)  # need to optimize based on firing duration

        Timestamps, Strings_from_PowerPack = ReadingQue(1000, serialControlObj.my_Serthread.readQue)
        serialControl.convertListtoLogFile(Strings_from_PowerPack, str(videoPath + '\\TotalLog.txt'), fileOpenMode='a')
        Strings_to_Compare = locateStringsToCompareFromSmokeEvent('EEA Firing')
        result = Compare('EEA Firing', Strings_to_Compare, Strings_from_PowerPack)
        serialControlObj.Normal_Firing_Test_Results.append('EEA Firing:' + result)
        print("Step:EEA Firing")
        print(serialControlObj.Normal_Firing_Test_Results)

        eea_tilt_prompt_one_Time = 0
        eea_tilt_prompt_two_Time = 0
        res = find_first_occurrences(Strings_from_PowerPack)
        print(res)
        for i, item in enumerate(res):
            if item == "GUI_NewState: EEA_TILT_PROMPT_1":
                print(f"Index {i}: {item}")
                eea_tilt_prompt_one_Time = int(Timestamps[i])
            if item == "GUI_NewState: EEA_TILT_PROMPT_2":
                print(f"Index {i}: {item}")
                eea_tilt_prompt_two_Time = int(Timestamps[i])

        eea_tilt_prompt_screen_time  = float((eea_tilt_prompt_two_Time-eea_tilt_prompt_one_Time)/1000)
        print(eea_tilt_prompt_screen_time)

        serialControlObj.my_Serthread.clearQue()
        serialControlObj.wait(5)
        # TEST STEP: Unlocking the Anvil (Tilt Operation)
        # rf = serialControlObj.RetractionForceDecode(retractionForce)
        # serialControlObj.wait(1)
        # rf = 0.2*int(rf)
        # with nidaqmx.Task() as task:
        #     task.ao_channels.add_ao_voltage_chan('Dev1/ao0')
        #     print('1 Channel 1 Sample Write: ')
        #     print(task.write(0))

        # Tilt Operation of Anvil
        serialControlObj.my_Serthread.clearQue()
        serialControlObj.wait(5)
        #194
        serialControlObj.Switch_ONN_Relay(2, 4)  # B2:R5 - ON
        serialControlObj.wait(0.5)
        serialControlObj.Switch_OFF_Relay(2, 4)  # B2:R5 - OFF  # Need to test Manoj Vadali

        serialControlObj.wait(10)

        Timestamps, Strings_from_PowerPack = ReadingQue(1000, serialControlObj.my_Serthread.readQue)
        serialControl.convertListtoLogFile(Strings_from_PowerPack, str(videoPath + '\\TotalLog.txt'), fileOpenMode='a')
        Strings_to_Compare = locateStringsToCompareFromSmokeEvent('Tilt Operation of Anvil')
        result = Compare('Tilt Operation of Anvil', Strings_to_Compare, Strings_from_PowerPack)
        serialControlObj.Normal_Firing_Test_Results.append('Tilt Operation of Anvil:' + result)
        print("Step:Tilt Operation of Anvil")
        print(serialControlObj.Normal_Firing_Test_Results)

        # Surgical Site Extraction (SSE)
        serialControlObj.my_Serthread.clearQue()
        serialControlObj.wait(5)

        serialControlObj.Switch_ONN_Relay(2, 4)  # B2:R5 - ON
        serialControlObj.wait(6)
        serialControlObj.Switch_OFF_Relay(2, 4)  # B2:R5 - OFF  # Need to test Manoj Vadali

        serialControlObj.wait(20)
        Timestamps, Strings_from_PowerPack = ReadingQue(1000, serialControlObj.my_Serthread.readQue)
        serialControl.convertListtoLogFile(Strings_from_PowerPack, str(videoPath + '\\TotalLog.txt'), fileOpenMode='a')
        Strings_to_Compare = locateStringsToCompareFromSmokeEvent('SSE')
        result = Compare('SSE', Strings_to_Compare, Strings_from_PowerPack)
        serialControlObj.Normal_Firing_Test_Results.append('SSE:' + result)
        print("Step:SSE")
        print(serialControlObj.Normal_Firing_Test_Results)



        #201
        #press ant key Close, Open, Articulate, and Rotate buttons
        serialControlObj.my_Serthread.clearQue()
        serialControlObj.wait(5)

        serialControlObj.Switch_ONN_Relay(2, 4)  # B2:R5 - ON
        serialControlObj.wait(6)
        serialControlObj.Switch_OFF_Relay(2, 4)  # B2:R5 - OFF

        serialControlObj.wait(5)
        Timestamps, Strings_from_PowerPack = ReadingQue(200, serialControlObj.my_Serthread.readQue)
        serialControl.convertListtoLogFile(Strings_from_PowerPack, str(videoPath + '\\TotalLog.txt'), fileOpenMode='a')
        Strings_to_Compare = locateStringsToCompareFromSmokeEvent('EEA Locked')
        result = Compare('EEA Locked', Strings_to_Compare, Strings_from_PowerPack)
        serialControlObj.Normal_Firing_Test_Results.append('EEA Locked:' + result)

        print(serialControlObj.Normal_Firing_Test_Results)

        #Saftey_Key 202
        serialControlObj.my_Serthread.clearQue()
        serialControlObj.wait(5)

        serialControlObj.Switch_ONN_Relay(3, 5)  # B2:R5 - ON
        serialControlObj.wait(6)
        serialControlObj.Switch_OFF_Relay(3, 5)  # B2:R5 - OFF

        serialControlObj.wait(5)
        Timestamps, Strings_from_PowerPack = ReadingQue(200, serialControlObj.my_Serthread.readQue)
        serialControl.convertListtoLogFile(Strings_from_PowerPack, str(videoPath + '\\TotalLog.txt'), fileOpenMode='a')
        Strings_to_Compare = locateStringsToCompareFromSmokeEvent('EEA Caution Tone')
        result = Compare('EEA Caution Tone', Strings_to_Compare, Strings_from_PowerPack)
        serialControlObj.Normal_Firing_Test_Results.append('EEA Caution Tone:' + result)

        print(serialControlObj.Normal_Firing_Test_Results)

        #204
        serialControlObj.my_Serthread.clearQue()
        serialControlObj.wait(5)

        serialControlObj.DisconnectingEEAReload()
        Timestamps, Strings_from_PowerPack = ReadingQue(1000, serialControlObj.my_Serthread.readQue)
        serialControl.convertListtoLogFile(Strings_from_PowerPack, str(videoPath + '\\TotalLog.txt'), fileOpenMode='a')
        Strings_to_Compare = locateStringsToCompareFromSmokeEvent('Remove Reload')
        result = Compare('Remove Reload', Strings_to_Compare, Strings_from_PowerPack)
        serialControlObj.Normal_Firing_Test_Results.append('Remove Reload:' + result)
        print("Step:EEA Remove Reload")
        print(serialControlObj.Normal_Firing_Test_Results)

        serialControlObj.my_Serthread.clearQue()
        serialControlObj.wait(5)

        for item in serialControlObj.Normal_Firing_Test_Results:
            # print(item)
            temp = 'PASS'
            try:
                if (((str.split(item, ':', 1))[1]) == 'PASS'):
                    # serialControlObj.Test_Results.append(serialControlObj.Normal_Firing_Test_Results[0] + ':FAIL')
                    pass
                elif (((str.split(item, ':', 1))[1]) == 'FAIL'):
                    temp = 'FAIL'
                    # print(str('Firing =' + str(i + 1) + ':  Failed'))
                    break
            except:
                pass
        if temp == 'PASS':
            firePass = firePass + 1
        print('% of Successful Firings: ', int(100 * (firePass) / (1)))
        # serialControlObj.Test_Results.append(temp)

        MCPThread.readingPowerPack.exitFlag = True
        serPP.close()
        print(serialControlObj.Test_Results)
        HandleFireCount2, HandleProcedureCount = GetHandleUseCount(PowerPackComPort)
        print('After Firing Handle Fire Count:' + str(HandleFireCount2),
              'Handle Procedure Count:' + str(HandleProcedureCount))
        serialControlObj.wait(2)
        StatusVariables2 = ReadStatusVariables(PowerPackComPort)
        StatusVariables2 = StatusVariables2[13:61]
        StatusVariables2 = StatusVariables2[4:8] + StatusVariables2[12:16] + StatusVariables2[20:24] + StatusVariables2[
                                                                                                       28:32] + StatusVariables2[
                                                                                                                36:40] + StatusVariables2[
                                                                                                                         44:48]

        print('StatusVariable After Firing', StatusVariables2)
        serPP = serial.Serial(serialControlObj.PowerPackComPort, 115200, bytesize=8, parity='N', stopbits=1,
                              timeout=0.05, xonxoff=0)
        MCPThread.readingPowerPack.exitFlag = False
        serialControlObj.my_Serthread = MCPThread.readingPowerPack(serPP, 1000)
        serialControlObj.my_Serthread.clearQue()
        serialControlObj.my_Serthread.start()

        if (HandleFireCount2 - HandleFireCount1) == 1 and (StatusVariables1 == StatusVariables2):
            temp = 'PASS'
        serialControlObj.Test_Results.append('Firing =' + str(1) + ':' + temp)

        indentation = "     "
        # Indent the items in the new array
        serialControlObj.Normal_Firing_Test_Results = [indentation + item for item in
                                                       serialControlObj.Normal_Firing_Test_Results]
        serialControlObj.Test_Results = serialControlObj.Test_Results + serialControlObj.Normal_Firing_Test_Results

        serialControlObj.my_Serthread.clearQue()
        serialControlObj.wait(5)
        serialControlObj.removeAdapter()
        serialControlObj.wait(10)
        Timestamps, Strings_from_PowerPack = ReadingQue(1500, serialControlObj.my_Serthread.readQue)
        serialControl.convertListtoLogFile(Strings_from_PowerPack, str(videoPath + '\\TotalLog.txt'), fileOpenMode='a')
        Strings_to_Compare = locateStringsToCompareFromSmokeEvent('Remove EEA Adapter')
        result = Compare('Remove EEA Adapter', Strings_to_Compare, Strings_from_PowerPack)
        serialControlObj.Test_Results.append('Remove EEA Adapter:' + result)
        print("Step: Removed EEA Adapter")
        print(serialControlObj.Test_Results)
        serialControlObj.wait(2)

        # print("Disengaged adapter Stepper motor controlled")
        serialControlObj.Switch_OFF_Relay(1, 8)
        print('Adapter Clutch Disengaged')

        # TEST STEP: Remove Clamshell
        serialControlObj.my_Serthread.clearQue()
        serialControlObj.wait(5)
        serialControlObj.send_decimal_bytes(TURN_OFF_ALL_RELAYS_IN_ALL_BANKS[0])
        serialControlObj.wait(5)
        Timestamps, Strings_from_PowerPack = ReadingQue(100, serialControlObj.my_Serthread.readQue)
        serialControl.convertListtoLogFile(Strings_from_PowerPack, str(videoPath + '\\TotalLog.txt'), fileOpenMode='a')
        Strings_to_Compare = locateStringsToCompareFromSmokeEvent('Remove Clamshell')
        result = Compare('Remove Clamshell', Strings_to_Compare, Strings_from_PowerPack)
        serialControlObj.Test_Results.append('Remove Clamshell:' + result)
        print("Step: Removed Clamshell")
        print(serialControlObj.Test_Results)
        serialControlObj.wait(2) 
        """

    # TEST STEP: Remove Adapter
    # Case 8: EEA Recovery

    with nidaqmx.Task() as task:
        task.ao_channels.add_ao_voltage_chan('Dev1/ao0')
        print('1 Channel 1 Sample Write: ')
        print(task.write(0.0))

    serialControlObj.send_decimal_bytes(TURN_OFF_ALL_RELAYS_IN_ALL_BANKS[0])
    # serialControlObj.wait(0.5)
    # serialControlObj.Switch_ONN_Relay(3, 8)
    #
    # serialControlObj.wait(0.5)
    # serialControlObj.Switch_ONN_Relay(3, 7)
    #
    # serialControlObj.wait(60)
    #
    # serialControlObj.send_decimal_bytes(TURN_OFF_ALL_RELAYS_IN_ALL_BANKS[0])
    # print("Step: Remove Signia Power Handle from Charger")
    # serialControlObj.wait(40)

    # ###################################  RESETTING CLAMSHELL   #############################################################################
    #
    serialControlObj.connectClamshellTest()
    # byte_data = [2, 3, 4, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    #              0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    # crc_value = CRC16(0x00, byte_data)
    # crc_value = hex(crc_value)
    # print('Original CRC: ', crc_value)
    # # crc_second_byte = crc_value[2:4]
    # # crc_first_byte = crc_value[4:]
    # l = len(crc_value)
    # crc_second_byte = crc_value[2:(l - 2)]
    # crc_first_byte = crc_value[(l - 2):]
    # # print(crc_first_byte)
    # # print(crc_second_byte)
    # byte_data.append(int(crc_first_byte, 16))
    # byte_data.append(int(crc_second_byte, 16))
    # # print(byte_data)
    # # print(len(byte_data))
    # ######################################
    # byte_lst = [170, 69, 2, 1] + byte_data
    # # print(byte_lst)
    # crc_value = calc(bytes(byte_lst))
    # crc_value = int(crc_value, 16)
    # byte_lst.append(crc_value)
    # command_byte = (byte_lst)
    # # print(command_byte)
    # # serialControlObj.Switch_ONN_Relay(5, 8)  # B5:R1 - ON
    # serialControlObj.Switch_ONN_Relay(5, 1)  # B5:R1 - ON
    # serialControlObj.Switch_ONN_Relay(5, 5)  # B5:R1 - ON
    # ser = serial.Serial(serialControlObj.BlackBoxComPort, 9600)
    # serialControlObj.wait(5)
    # ############# READ ###################
    # command = bytes(command_byte)
    # print('Clamshell ResetByte array', command)
    # ser.write(command)
    # serialControlObj.wait(3)
    # # serialControlObj.wait(5)
    # print(command)
    # s = ser.read(2)
    # s = list(s)
    # packet_size = s[1]
    # read_data = ser.read(packet_size - 2)
    # read_data = list(read_data)
    # print("==== Clamshell Reset READ DATA ====")
    # print(read_data[1:-1])
    # ser.close()
    # serialControlObj.Switch_OFF_Relay(5, 1)  # B5:R1 - OFF
    # serialControlObj.Switch_OFF_Relay(5, 5)  # B5:R1 - OFF
    # serialControlObj.wait(1)

    if False:
        # (read_battery_RSOC(25,PowerPackComPort) > TestBatteryLevelMax):  # and (read_battery_RSOC(25, PowerPackComPort) > TestBatteryLevelMin):
        serialControlObj.Switch_ONN_Relay(1, 8)
        serialControlObj.wait(10)
        print("EEA Adapter Engaged to Power Pack Mechanically")

        # TEST STEP: Attach the EGIA Adapter
        serialControlObj.Switch_ONN_ALL_Relays_In_Each_Bank(1)  # B1 - ALL ON
        print("Step: EEA Adapter Connected")
        serialControlObj.wait(20)
        serialControlObj.ConnectingEEAReload()
        print("Step: EEA Reload Connected")
        serialControlObj.wait(5)

        with nidaqmx.Task() as task:
            task.ao_channels.add_ao_voltage_chan('Dev1/ao0')
            print('Setting the particle brake for quick discharging the Power Pack')
            print(task.write(2.0))

        while (read_battery_RSOC(25,
                                 PowerPackComPort)) > TestBatteryLevelMax:  # and (read_battery_RSOC(25, PowerPackComPort) > TestBatteryLevelMin):
            serialControlObj.Switch_ONN_Relay(2,
                                              5)  # B2:R5 - ON -- some operations battery discharge Check if loaded condition of trocar can be explored for quick discharge
            serialControlObj.wait(7)
            serialControlObj.Switch_OFF_Relay(2, 5)  # B2:R5 - ON
            serialControlObj.Switch_ONN_Relay(2, 4)  # B2:R5 - ON
            serialControlObj.wait(7)
            serialControlObj.Switch_OFF_Relay(2, 4)  # B2:R5 - ON

        serialControlObj.DisconnectingEEAReload()
        serialControlObj.Switch_OFF_ALL_Relays_In_Each_Bank(1)  # Disconnected the clamshell
        serialControlObj.wait(10)
    if False:  # (read_battery_RSOC(25, PowerPackComPort) < TestBatteryLevelMin):  # and (read_battery_RSOC(25, PowerPackComPort) <= TestBatteryLevelMax):
        # print('entered elif loop')
        serialControlObj.Switch_ONN_Relay(3, 7)  # battery charge
        serialControlObj.wait(0.5)
        serialControlObj.Switch_ONN_Relay(3, 8)
        # need to optimize this delay so that handle does not go to sleep or does not result communciation
        serialControlObj.wait(5)
        while (read_battery_RSOC(50,
                                 PowerPackComPort) < TestBatteryLevelMin):  # and (read_battery_RSOC(25, PowerPackComPort) <= TestBatteryLevelMax):
            pass

    # serialControlObj.wait(20)
    # print("----------Placing Power Pack on Charger for startup Test--------------")
    # serialControlObj.Switch_ONN_Relay(3, 7)
    # serialControlObj.wait(.2)
    # serialControlObj.Switch_ONN_Relay(3, 8)
    # serialControlObj.wait(60)
    # print("----------Removing Power Pack from Charger for startup Test--------------")
    # serialControlObj.Switch_OFF_Relay(3, 7)
    # serialControlObj.wait(.2)
    # serialControlObj.Switch_OFF_Relay(3, 8)

    # serialControlObj.wait(60)
    # searchFlag = True
    #
    # Timestamps, Strings_from_PowerPack, data_path = ReadingQue(1000, serialControlObj.my_Serthread.readQue, searchFlag)
    # serialControl.convertListtoLogFile(Strings_from_PowerPack, (videoPath + '\\StartUpLog.txt'), fileOpenMode='w')
    # serialControl.convertListtoLogFile(Strings_from_PowerPack, 'TotalLog.txt', fileOpenMode='a')
    # Strings_to_Compare = locateStringsToCompareFromSmokeEvent('Remove Signia Power Handle from Charger')
    # result = Compare('Remove Signia Power Handle from Charger', Strings_to_Compare, Strings_from_PowerPack)
    # data_path = "None" if not data_path else data_path
    # serialControlObj.Smoke_test_Results.append('Eventlog:' + data_path)
    # serialControlObj.Smoke_test_Results.append('Remove Signia Power Handle from Charger:' + result)

    # appending data_path, post checking the value of data_path with None

    # serialControlObj.Switch_ONN_Relay(5, 1)  # B5:R1 - ON
    # serialControlObj.Switch_ONN_Relay(5, 5)  # B5:R1 - ON
    # ser = serial.Serial(serialControlObj.BlackBoxComPort, 9600)
    # serialControlObj.wait(5)
    # ############# READ ###################
    # # command = bytes(command_byte) # Commented by Manoj Vadali
    # print('Clamshell ResetByte array', command)
    # ser.write(command)
    # serialControlObj.wait(1)
    # # serialControlObj.wait(5)
    # # print(command)
    # s = ser.read(2)
    # s = list(s)
    # packet_size = s[1]
    # read_data = ser.read(packet_size - 2)
    # read_data = list(read_data)
    # print("==== Clamshell Reset READ DATA ====")
    # print(read_data[1:-1])
    # ser.close()
    # serialControlObj.Switch_OFF_Relay(5, 1)  # B5:R1 - OFF
    # serialControlObj.Switch_OFF_Relay(5, 5)  # B5:R1 - OFF
    # serialControlObj.wait(1)
    # serialControlObj.my_Serthread.clearQue()
    # serialControlObj.wait(5)
    #
    # serialControlObj.connectClamshell()
    # print("Step: Clamshell Connected")
    # serialControlObj.wait(5)
    # Timestamps, Strings_from_PowerPack = ReadingQue(200, serialControlObj.my_Serthread.readQue)
    # # serialControl.convertListtoLogFile(Strings_from_PowerPack, 'TotalLog.txt', fileOpenMode='a')
    # serialControl.convertListtoLogFile(Strings_from_PowerPack, str(videoPath + '\\TotalLog.txt'), fileOpenMode='a')
    # Strings_to_Compare = locateStringsToCompareFromSmokeEvent('Clamshell Connected')
    # result = Compare('Clamshell Connected', Strings_to_Compare, Strings_from_PowerPack)
    #
    # serialControlObj.Smoke_test_Results.append('Connected Clamshell:' + result)
    # print(Timestamps)
    # print(serialControlObj.Smoke_test_Results)

    serialControlObj.connect_adapter_test()

    # serialControlObj.Switch_ONN_Relay(1, 8)
    # serialControlObj.wait(7)
    # print("EEA Adapter Engaged to Power Pack Mechanically")
    #
    # serialControlObj.my_Serthread.clearQue()
    # serialControlObj.wait(5)
    # # TEST STEP: Attach the EEA Adapter
    # serialControlObj.Switch_ONN_ALL_Relays_In_Each_Bank(1)  # B1 - ALL ON
    # print("Step: EEA Adapter Connected")
    serialControlObj.wait(40)

    serialControlObj.Switch_ONN_Relay(2, 1)
    serialControlObj.Switch_ONN_Relay(2, 2)
    serialControlObj.Switch_ONN_Relay(2, 7)
    serialControlObj.Switch_ONN_Relay(2, 8)
    serialControlObj.wait(9)
    serialControlObj.Switch_OFF_Relay(2, 1)
    serialControlObj.Switch_OFF_Relay(2, 2)
    serialControlObj.Switch_OFF_Relay(2, 7)
    serialControlObj.Switch_OFF_Relay(2, 8)
    serialControlObj.wait(30)

    serialControlObj.connect_
    remove_adapter_and_reattach(serialControlObj, serialControlObj.my_Serthread, videoPath, 'EEA Adapter Connected with EEA Reload',
                                EEA_RELOAD_EEPROM_command_byte)
    serPP.close()
    HandleFireCount1, HandleProcedureCount = GetHandleUseCount(PowerPackComPort)
    print('Before Firing Handle Fire Count:' + str(HandleFireCount1),
          'Handle Procedure Count:' + str(HandleProcedureCount))
    serialControlObj.wait(2)
    StatusVariables1 = ReadStatusVariables(PowerPackComPort)
    StatusVariables1 = StatusVariables1[13:61]
    StatusVariables1 = StatusVariables1[4:8] + StatusVariables1[12:16] + StatusVariables1[20:24] + StatusVariables1[
                                                                                                   28:32] + StatusVariables1[
                                                                                                            36:40] + StatusVariables1[
                                                                                                                     44:48]
    print('Before Firing Status Variables: ', StatusVariables1)
    serPP = serial.Serial(serialControlObj.PowerPackComPort, 115200, bytesize=8, parity='N', stopbits=1,
                          timeout=0.05, xonxoff=0)
    MCPThread.readingPowerPack.exitFlag = False
    serialControlObj.my_Serthread = MCPThread.readingPowerPack(serPP, 1000)
    serialControlObj.my_Serthread.clearQue()
    serialControlObj.my_Serthread.start()

    # serRangeSensor = serial.Serial(serialControlObj.ArduinoUNOComPort, 115200)

    serialControlObj.wait(5)
    serialControlObj.Switch_ONN_Relay(2, 4)  # B2:R5 - ON
    serialControlObj.wait(5)
    serialControlObj.Switch_OFF_Relay(2, 4)  # B2:R5 - OFF

    serialControlObj.my_Serthread.clearQue()

    # 206
    remove_adapter_and_reattach(serialControlObj, serialControlObj.my_Serthread, videoPath,
                                'Remove EEA Adapter Connected and Reattach', EEA_RELOAD_EEPROM_command_byte)

    # 207

    serialControlObj.my_Serthread.clearQue()
    serialControlObj.wait(5)

    serialControlObj.Switch_ONN_Relay(2, 4)
    serialControlObj.wait(15)
    serialControlObj.Switch_OFF_Relay(2, 4)

    # with nidaqmx.Task() as task:
    #     task.ao_channels.add_ao_voltage_chan('Dev1/ao0')
    #     print('1 Channel 1 Sample Write: ')
    #     print(task.write(2))

    serialControlObj.Switch_ONN_Relay(2, 5)
    serialControlObj.wait(1)
    serialControlObj.Switch_OFF_Relay(2, 5)
    serialControlObj.wait(5)

    Timestamps, Strings_from_PowerPack = ReadingQue(1000, serialControlObj.my_Serthread.readQue)
    serialControl.convertListtoLogFile(Strings_from_PowerPack, str(videoPath + '\\TotalLog.txt'), fileOpenMode='a')
    Strings_to_Compare = locateStringsToCompareFromSmokeEvent('Trocar Retracts Slightly in High Speed Clamping')

    result = Compare('Trocar Retracts Slightly in High Speed Clamping', Strings_to_Compare, Strings_from_PowerPack)
    serialControlObj.Normal_Firing_Test_Results.append('Trocar Retracts Slightly in High Speed Clamping:' + result)
    print(serialControlObj.Normal_Firing_Test_Results)

    with nidaqmx.Task() as task:
        task.ao_channels.add_ao_voltage_chan('Dev1/ao0')
        print('1 Channel 1 Sample Write: ')
        print(task.write(0))
    # 208
    remove_adapter_and_reattach(serialControlObj, serialControlObj.my_Serthread, videoPath,
                                'Verify EEA Trocar Position Screen Shows After Calibrating',
                                EEA_RELOAD_EEPROM_command_byte)
    serialControlObj.wait(2)
    # 209
    # eea_close_button_New(serRangeSensor, serialControlObj, serialControlObj.my_Serthread, videoPath, "EEA Clamping on Tissue")
    # serRangeSensor.close()
    serRangeSensor = serial.Serial(serialControlObj.ArduinoUNOComPort, 115200)
    serialControlObj.my_Serthread.clearQue()
    serialControlObj.wait(5)
    # cf = serialControlObj.EEAForceDecode(clampingForce)
    serialControlObj.Switch_ONN_Relay(2, 5)  # B2:R5 - ON
    read_data1 = 100
    serRangeSensor.flushOutput()
    serRangeSensor.flush()
    serRangeSensor.flushInput()
    # while not 65 < read_data1 <= 80:
    #     try:
    #         ser_bytes1 = serRangeSensor.readline()
    #         read_data1 = float(ser_bytes1.decode('ascii'))
    #         # serialControlObj.wait(.1)
    #         print(read_data1)
    #     except:
    #         print("Fail==============================================")
    #         pass
    serialControlObj.wait(1)
    with nidaqmx.Task() as task:
        task.ao_channels.add_ao_voltage_chan('Dev1/ao0')
        print('1 Channel 1 Sample Write:')
        print(task.write(2))

    serialControlObj.wait(25)
    Timestamps, Strings_from_PowerPack = ReadingQue(serialControlObj.my_Serthread.readQue)
    serialControl.convertListtoLogFile(Strings_from_PowerPack, str(videoPath + '\\TotalLog.txt'), fileOpenMode='a')
    Strings_to_Compare = locateStringsToCompareFromSmokeEvent('EEA Clamping on Tissue')
    result = Compare('EEA Clamping on Tissue', Strings_to_Compare, Strings_from_PowerPack)
    serialControlObj.Smoke_test_Results.append(
        'EEA Clamping on Tissue:' + result)  # Updated from Test Results to normal Firing Test Results on Nov 9th by manoj Vadali

    print("Step: EEA Clamping on Tissue")
    print(serialControlObj.Smoke_test_Results)
    serialControlObj.Switch_OFF_Relay(2, 5)
    serialControlObj.wait(5)
    # 210
    remove_adapter_and_reattach(serialControlObj, serialControlObj.my_Serthread, videoPath,
                                'Verify EEA CTC Clamping in Progress screen shows at 100% after Calibrating',
                                EEA_RELOAD_EEPROM_command_byte)

    # 211
    serialControlObj.my_Serthread.clearQue()
    serialControlObj.wait(5)

    serialControlObj.GreenKeyAck()
    serialControlObj.wait(2)
    Timestamps, Strings_from_PowerPack = ReadingQue(serialControlObj.my_Serthread.readQue)
    serialControl.convertListtoLogFile(Strings_from_PowerPack, str(videoPath + '\\TotalLog.txt'), fileOpenMode='a')
    Strings_to_Compare = locateStringsToCompareFromSmokeEvent('EEA Green Key Ack')
    result = Compare('EEA Green Key Ack', Strings_to_Compare, Strings_from_PowerPack)
    serialControlObj.Smoke_test_Results.append('EEA Green Key Ack:' + result)
    print("Step: Acknowledged Safety Key (Green LED) for firing")
    print(serialControlObj.Smoke_test_Results)

    with nidaqmx.Task() as task:
        task.ao_channels.add_ao_voltage_chan('Dev1/ao0')
        print('1 Channel 1 Sample Write: ')
        print(task.write(3.25))  # Updated the 2.75 to 3.25 by Manoj Vadali 8th nov 2023

    serialControlObj.Switch_ONN_Relay(2, 5)  # B2:R5 - ON
    serialControlObj.wait(0.5)
    serialControlObj.Switch_OFF_Relay(2, 5)  # B2:R5 - OFF  # Need to test Manoj Vadali

    remove_adapter_and_reattach(serialControlObj, serialControlObj.my_Serthread, videoPath,
                                'Remove the Adapter During Stapling', EEA_RELOAD_EEPROM_command_byte)

    # 214,215 and 216 pending
    # 217 and 218
    serialControlObj.my_Serthread.clearQue()
    serialControlObj.wait(5)
    serialControlObj.GreenKeyAck()
    serialControlObj.wait(2)

    serialControlObj.Switch_ONN_Relay(4, 1)
    serialControlObj.Switch_ONN_Relay(4, 2)  # To turn on Linear actuator
    serialControlObj.wait(4)  # 27th nov (2 seconds changed to 3 on Nov 6th 20223)
    serialControlObj.Switch_ONN_Relay(2, 5)  # B2:R5 - ON
    serialControlObj.wait(0.5)
    serialControlObj.Switch_OFF_Relay(2, 5)  # B2:R5 - OFF  # Need to test Manoj Vadali
    # serialControlObj.wait(1)
    serialControlObj.wait(3)  # 27th nov updated from 6 to 4
    serialControlObj.Switch_OFF_Relay(4, 1)
    serialControlObj.Switch_OFF_Relay(4, 2)  # To turn on Linear actuator
    serialControlObj.wait(3)  # Manoj changed on 27th from 0.5 to 2
    with nidaqmx.Task() as task:
        task.ao_channels.add_ao_voltage_chan('Dev1/ao0')
        print('1 Channel 1 Sample Write: ')
        print(task.write(0))  # Updated the ff to zero by Manoj Vadali

    remove_adapter_and_reattach(serialControlObj, serialControlObj.my_Serthread, videoPath,
                                'Verify Stapling Completes then Remove Adapter During Cutting',
                                EEA_RELOAD_EEPROM_command_byte)

    # 219 and 220 pending

    # 221,222 and 223
    serialControlObj.my_Serthread.clearQue()
    serialControlObj.wait(5)

    serialControlObj.GreenKeyAck()
    serialControlObj.wait(2)

    serialControlObj.wait(2.5)  # 27th nov (2 seconds changed to 3 on Nov 6th 20223)
    serialControlObj.Switch_ONN_Relay(2, 5)  # B2:R5 - ON
    serialControlObj.wait(0.5)
    serialControlObj.Switch_OFF_Relay(2, 5)  # B2:R5 - OFF  # Need to test Manoj Vadali
    # serialControlObj.wait(1)

    serialControlObj.Switch_ONN_Relay(4, 3)
    serialControlObj.Switch_ONN_Relay(4, 4)  # To turn on Linear actuator at full power
    serialControlObj.wait(5)  # need to optimize based on firing duration (changed from 7 to 5 8th nov by Manoj vadali
    serialControlObj.Switch_OFF_Relay(4, 3)
    serialControlObj.Switch_OFF_Relay(4, 4)  # To turn off Linear actuator from full power
    serialControlObj.wait(.5)  # need to optimize based on firing duration

    serialControlObj.Switch_ONN_Relay(4, 5)
    serialControlObj.Switch_ONN_Relay(4, 6)
    serialControlObj.wait(30)

    remove_adapter_and_reattach(serialControlObj, serialControlObj.my_Serthread, videoPath,
                                'Verify Cutting Completes then Remove Adapter', EEA_RELOAD_EEPROM_command_byte)

    #

    # 224

    serialControlObj.my_Serthread.clearQue()
    serialControlObj.wait(5)

    serialControlObj.Switch_ONN_Relay(2, 4)
    serialControlObj.wait(.5)
    serialControlObj.Switch_OFF_Relay(2, 4)

    remove_adapter_and_reattach(serialControlObj, serialControlObj.my_Serthread, videoPath,
                                'Reattach Adapter and Verify EEA Tilt Prompt Screens', EEA_RELOAD_EEPROM_command_byte)

    # UNKNOWN_ADAPTER
    # working fine --------------------------------------------------
    # 225
    serialControlObj.my_Serthread.clearQue()
    serialControlObj.wait(5)

    serialControlObj.Switch_ONN_Relay(2, 4)
    serialControlObj.wait(5)
    serialControlObj.Switch_OFF_ALL_Relays_In_Each_Bank(1)
    serialControlObj.connectClamshell()
    serialControlObj.wait(5)
    serialControlObj.Switch_ONN_ALL_Relays_In_Each_Bank(1)
    serialControlObj.wait(40)

    serialControlObj.Switch_OFF_Relay(2, 4)

    serialControlObj.wait(25)
    Timestamps, Strings_from_PowerPack = ReadingQue(serialControlObj.my_Serthread.readQue)
    serialControl.convertListtoLogFile(Strings_from_PowerPack, str(videoPath + '\\TotalLog.txt'), fileOpenMode='a')
    Strings_to_Compare = locateStringsToCompareFromSmokeEvent('Reattach Adapter when TILT_POSITION is Reached')
    result = Compare('Reattach Adapter when TILT_POSITION is Reached', Strings_to_Compare, Strings_from_PowerPack)
    serialControlObj.Smoke_test_Results.append('Reattach Adapter when TILT_POSITION is Reached:' + result)
    print(serialControlObj.Smoke_test_Results.append)

    # 226
    serialControlObj.my_Serthread.clearQue()
    serialControlObj.wait(5)

    serialControlObj.Switch_ONN_Relay(2, 4)
    serialControlObj.wait(5)
    serialControlObj.Switch_OFF_Relay(2, 4)
    serialControlObj.wait(5)
    remove_adapter_and_reattach(serialControlObj, serialControlObj.my_Serthread, videoPath,
                                'Reattach Adapter and Verify EEA TILT_OPEN Prompt Screen',
                                EEA_RELOAD_EEPROM_command_byte)
    # 227 and 228
    serialControlObj.my_Serthread.clearQue()
    serialControlObj.wait(5)

    serialControlObj.Switch_ONN_Relay(2, 4)
    serialControlObj.wait(1)
    serialControlObj.Switch_OFF_Relay(2, 4)

    remove_adapter_and_reattach(serialControlObj, serialControlObj.my_Serthread, videoPath,
                                'Reattach Adapter and Verify EEA TILT_OPEN Complete Screen',
                                EEA_RELOAD_EEPROM_command_byte)

    serialControlObj.my_Serthread.clearQue()
    serialControlObj.DisconnectingEEAReload()
    serialControlObj.wait(2)

    serialControlObj.Switch_ONN_Relay(2, 1)
    serialControlObj.Switch_ONN_Relay(2, 2)
    serialControlObj.Switch_ONN_Relay(2, 7)
    serialControlObj.Switch_ONN_Relay(2, 8)
    serialControlObj.wait(9)
    serialControlObj.Switch_OFF_Relay(2, 1)
    serialControlObj.Switch_OFF_Relay(2, 2)
    serialControlObj.Switch_OFF_Relay(2, 7)
    serialControlObj.Switch_OFF_Relay(2, 8)
    serialControlObj.wait(30)

    remove_adapter_and_reattach(serialControlObj, serialControlObj.my_Serthread, videoPath, 'EEA Adapter Connected with EEA Reload',
                                EEA_RELOAD_EEPROM_command_byte)

    serialControlObj.my_Serthread.clearQue()
    serialControlObj.wait(5)
    serialControlObj.Switch_ONN_Relay(2, 4)  # B2:R5 - ON
    serialControlObj.wait(20)
    serialControlObj.Switch_OFF_Relay(2, 4)  # B2:R5 - OFF

    #    serRangeSensor.close()
    serRangeSensor = serial.Serial(serialControlObj.ArduinoUNOComPort, 115200)
    serialControlObj.my_Serthread.clearQue()
    serialControlObj.wait(5)
    # cf = serialControlObj.EEAForceDecode(clampingForce)
    serialControlObj.Switch_ONN_Relay(2, 5)  # B2:R5 - ON
    read_data1 = 200
    serRangeSensor.flushOutput()
    serRangeSensor.flush()
    serRangeSensor.flushInput()
    while not 65 < read_data1 <= 80:
        try:
            ser_bytes1 = serRangeSensor.readline()
            read_data1 = float(ser_bytes1.decode('ascii'))
            # serialControlObj.wait(.1)
            print(read_data1)
        except:
            pass

    with nidaqmx.Task() as task:
        task.ao_channels.add_ao_voltage_chan('Dev1/ao0')
        print('1 Channel 1 Sample Write:')
        print(task.write(2))
    serialControlObj.wait(25)

    print("Step: EEA Clamping on Tissue")
    print(serialControlObj.Normal_Firing_Test_Results)

    # TEST STEP: Acknowledge Safety Key (Green LED) for firing
    serialControlObj.my_Serthread.clearQue()
    serialControlObj.wait(5)
    serialControlObj.Switch_OFF_Relay(2, 5)  # B2:R5 - ON
    serialControlObj.GreenKeyAck()
    serialControlObj.wait(2)

    print("Step: Acknowledged Safety Key (Green LED) for firing")

    # rlist = {'Test Step': ['Safety Key: Acknowledged'], 'Test Result': [result]}
    # df = df.append(pd.DataFrame(rlist))

    # TEST STEP: Firing
    # ff = serialControlObj.EEAForceDecode(firingForce)
    with nidaqmx.Task() as task:
        task.ao_channels.add_ao_voltage_chan('Dev1/ao0')
        print('1 Channel 1 Sample Write: ')
        print(task.write(3.25))  # Updated the 2.75 to 3.25 by Manoj Vadali 8th nov 2023

    serialControlObj.wait(5)

    serialControlObj.Switch_ONN_Relay(2, 5)  # B2:R5 - ON
    serialControlObj.wait(0.5)
    serialControlObj.Switch_OFF_Relay(2, 5)  # B2:R5 - OFF  # Need to test Manoj Vadali

    with nidaqmx.Task() as task:
        task.ao_channels.add_ao_voltage_chan('Dev1/ao0')
        print('1 Channel 1 Sample Write: ')
        print(task.write(0))  # Updated the ff to zero by Manoj Vadali

    remove_adapter_and_reattach(serialControlObj, serialControlObj.my_Serthread, videoPath, 'Remove Adapter',
                                EEA_RELOAD_EEPROM_command_byte)

    serialControlObj.my_Serthread.clearQue()
    serialControlObj.wait(5)

    serialControlObj.Switch_ONN_Relay(2, 4)
    serialControlObj.wait(5)
    serialControlObj.Switch_OFF_Relay(2, 4)

    Timestamps, Strings_from_PowerPack = ReadingQue(serialControlObj.my_Serthread.readQue)
    serialControl.convertListtoLogFile(Strings_from_PowerPack, str(videoPath + '\\TotalLog.txt'), fileOpenMode='a')
    Strings_to_Compare = locateStringsToCompareFromSmokeEvent('EEA SURGICAL_SITE_EXTRACTION')
    result = Compare('EEA SURGICAL_SITE_EXTRACTION', Strings_to_Compare, Strings_from_PowerPack)
    serialControlObj.Smoke_test_Results.append('EEA SURGICAL_SITE_EXTRACTION:' + result)
    print("Step:EEA SURGICAL_SITE_EXTRACTION ")
    print(serialControlObj.Smoke_test_Results)

    eea_open_button(serialControlObj, serialControlObj.serialControlObj.my_Serthread, videoPath, "SSE Fully Opening State")

    serialControlObj.Switch_ONN_Relay(2, 5)
    serialControlObj.wait(5)
    serialControlObj.Switch_OFF_Relay(2, 5)

    Timestamps, Strings_from_PowerPack = ReadingQue(serialControlObj.my_Serthread.readQue)
    serialControl.convertListtoLogFile(Strings_from_PowerPack, str(videoPath + '\\TotalLog.txt'), fileOpenMode='a')
    Strings_to_Compare = locateStringsToCompareFromSmokeEvent('SSE Fully Closing State')
    result = Compare('SSE Fully Closing State', Strings_to_Compare, Strings_from_PowerPack)
    serialControlObj.Smoke_test_Results.append('SSE Fully Closing State:' + result)

    print(serialControlObj.Smoke_test_Results)

    # 235
    serialControlObj.my_Serthread.clearQue()
    serialControlObj.DisconnectingEEAReload()
    serialControlObj.wait(2)

    Timestamps, Strings_from_PowerPack = ReadingQue(serialControlObj.my_Serthread.readQue)
    serialControl.convertListtoLogFile(Strings_from_PowerPack, str(videoPath + '\\TotalLog.txt'), fileOpenMode='a')
    Strings_to_Compare = locateStringsToCompareFromSmokeEvent('EEA Surgical Site Exit Prompt Screens')
    result = Compare('EEA Surgical Site Exit Prompt Screens', Strings_to_Compare, Strings_from_PowerPack)
    serialControlObj.Smoke_test_Results.append('EEA Surgical Site Exit Prompt Screens:' + result)
    print("Step:EEA Surgical Site Exit Prompt Screens")
    print(serialControlObj.Smoke_test_Results)

    serialControlObj.my_Serthread.clearQue()
    serialControlObj.wait(2)
    serialControlObj.Switch_ONN_Relay(2, 1)
    serialControlObj.Switch_ONN_Relay(2, 2)
    serialControlObj.Switch_ONN_Relay(2, 7)
    serialControlObj.Switch_ONN_Relay(2, 8)
    serialControlObj.wait(9)
    serialControlObj.Switch_OFF_Relay(2, 1)
    serialControlObj.Switch_OFF_Relay(2, 2)
    serialControlObj.Switch_OFF_Relay(2, 7)
    serialControlObj.Switch_OFF_Relay(2, 8)
    serialControlObj.wait(30)

    Timestamps, Strings_from_PowerPack = ReadingQue(serialControlObj.my_Serthread.readQue)
    serialControl.convertListtoLogFile(Strings_from_PowerPack, str(videoPath + '\\TotalLog.txt'), fileOpenMode='a')
    Strings_to_Compare = locateStringsToCompareFromSmokeEvent('EEA Surgical Site Countdown Screens')
    result = Compare('EEA Surgical Site Countdown Screens', Strings_to_Compare, Strings_from_PowerPack)
    serialControlObj.Smoke_test_Results.append('EEA Surgical Site Countdown Screens:' + result)
    print("Step:EEA Surgical Site Countdown Screens")
    print(serialControlObj.Smoke_test_Results)

    MCPThread.readingPowerPack.exitFlag = True
    serPP.close()
    print(serialControlObj.Test_Results)
    HandleFireCount2, HandleProcedureCount = GetHandleUseCount(PowerPackComPort)
    print('After Firing Handle Fire Count:' + str(HandleFireCount2),
          'Handle Procedure Count:' + str(HandleProcedureCount))
    serialControlObj.wait(2)
    StatusVariables2 = ReadStatusVariables(PowerPackComPort)
    StatusVariables2 = StatusVariables2[13:61]
    StatusVariables2 = StatusVariables2[4:8] + StatusVariables2[12:16] + StatusVariables2[20:24] + StatusVariables2[
                                                                                                   28:32] + StatusVariables2[
                                                                                                            36:40] + StatusVariables2[
                                                                                                                     44:48]

    print('StatusVariable After Firing', StatusVariables2)
    serPP = serial.Serial(serialControlObj.PowerPackComPort, 115200, bytesize=8, parity='N', stopbits=1,
                          timeout=0.05, xonxoff=0)
    MCPThread.readingPowerPack.exitFlag = False
    serialControlObj.my_Serthread = MCPThread.readingPowerPack(serPP, 1000)
    serialControlObj.my_Serthread.clearQue()
    serialControlObj.my_Serthread.start()

    if (HandleFireCount2 - HandleFireCount1) == 1 and (StatusVariables1 == StatusVariables2):
        temp = 'PASS'
    serialControlObj.Test_Results.append('Firing =' + str(1) + ':' + temp)

    indentation = "     "
    # Indent the items in the new array
    serialControlObj.Normal_Firing_Test_Results = [indentation + item for item in
                                                   serialControlObj.Normal_Firing_Test_Results]
    serialControlObj.Smoke_test_Results = serialControlObj.Smoke_test_Results + serialControlObj.Normal_Firing_Test_Results

    serialControlObj.my_Serthread.clearQue()
    serialControlObj.wait(5)
    serialControlObj.removeAdapter()
    serialControlObj.wait(10)
    Timestamps, Strings_from_PowerPack = ReadingQue(serialControlObj.my_Serthread.readQue)
    serialControl.convertListtoLogFile(Strings_from_PowerPack, str(videoPath + '\\TotalLog.txt'), fileOpenMode='a')
    Strings_to_Compare = locateStringsToCompareFromSmokeEvent('Remove EEA Adapter')
    result = Compare('Remove EEA Adapter', Strings_to_Compare, Strings_from_PowerPack)
    serialControlObj.Smoke_test_Results.append('Remove EEA Adapter:' + result)
    print("Step: Removed EEA Adapter")
    print(serialControlObj.Smoke_test_Results)
    serialControlObj.wait(2)

    # print("Disengaged adapter Stepper motor controlled")
    serialControlObj.Switch_OFF_Relay(1, 8)
    print('Adapter Clutch Disengaged')

    # TEST STEP: Remove Clamshell
    serialControlObj.my_Serthread.clearQue()
    serialControlObj.wait(5)
    serialControlObj.send_decimal_bytes(TURN_OFF_ALL_RELAYS_IN_ALL_BANKS[0])
    serialControlObj.wait(5)
    Timestamps, Strings_from_PowerPack = ReadingQue( serialControlObj.my_Serthread.readQue)
    serialControl.convertListtoLogFile(Strings_from_PowerPack, str(videoPath + '\\TotalLog.txt'), fileOpenMode='a')
    Strings_to_Compare = locateStringsToCompareFromSmokeEvent('Remove Clamshell')
    result = Compare('Remove Clamshell', Strings_to_Compare, Strings_from_PowerPack)
    serialControlObj.Smoke_test_Results.append('Remove Clamshell:' + result)
    print("Step: Removed Clamshell")
    print(serialControlObj.Smoke_test_Results)
    serialControlObj.wait(2)

    for item in serialControlObj.Test_Results:
        # print(item)
        temp2 = 'PASS'
        try:
            if (((str.split(item, ':', 1))[1]) == 'PASS'):
                # serialControlObj.Test_Results.append(serialControlObj.Normal_Firing_Test_Results[0] + ':FAIL')
                pass
            elif (((str.split(item, ':', 1))[1]) == 'FAIL'):
                temp2 = 'FAIL'
                print(str((serialControlObj.Test_Results[0] + ':  Failed')))
                break
        except:
            pass
    if temp2 == 'PASS':
        iterPass = int(iterPass) + 1
        print(serialControlObj.r['Test Scenario'] + '% of Successful Executions: ' + str(
            100 * ((iterPass) / (serialControlObj.r['Num Times to Execute']))))

    # Iteration_Results.append()
    # results_path = serialControlObj.OUTPUT_PATH + '\\Results.xlsx'
    # df.to_excel(results_path)
    serialControlObj.my_Serthread.clearQue()
    serialControlObj.wait(5)
    MCPThread.readingPowerPack.exitFlag = True
    serPP.close()
    OLEDRecordingThread.exitFlag = True
    with open(str((videoPath + '\\sample_result.txt')), 'a') as datalog:
        datalog.write('\n'.join(serialControlObj.Test_Results) + '\n')
    CS = [sys.argv[index + 1] for index, ele in enumerate(sys.argv) if ele == "-c" or ele == "--changeset"]
    TT = [sys.argv[index + 1] for index, ele in enumerate(sys.argv) if ele == "-t" or ele == "--test"]
    INTG = '--integration' in sys.argv
    RP = [sys.argv[index + 1] for index, ele in enumerate(sys.argv) if ele == "-r" or ele == "--root"]
    calculatePassFail(str((videoPath + '\\sample_result.txt')), str(RP[0] + '\\Test_Configurator.json'),
                      str((videoPath + '\\StartUpLog.txt')), str(TT[0]), str(CS[0]), str(INTG))
    serialControlObj.PlacingPowerPackOnCharger()
    print('Power Pack Placed on Charger')
    print('------------------- End of Test Scenario --------------')
    serialControlObj.wait(30)
    # serialControlObj.disconnectSerialConnection()


def remove_adapter_and_reattach(serialControlObj, videoPath, log_string, EEA_RELOAD_EEPROM_command_byte):
    # serialControlObj.removeAdapter()
    serialControlObj.Switch_OFF_ALL_Relays_In_Each_Bank(1)
    serialControlObj.connectClamshell()

    serialControlObj.wait(5)

    # serialControlObj.ConnectAdapter()
    serialControlObj.Switch_ONN_ALL_Relays_In_Each_Bank(1)

    serialControlObj.wait(40)

    # serialControlObj.wait(5)

    ###  Performing Tip Protector Detection ###

    # serRangeSensor = serial.Serial(serialControlObj.ArduinoUNOComPort, 115200)
    # serRangeSensor.flushOutput()
    # serRangeSensor.flush()
    # serRangeSensor.flushInput()

    # MCPThread.readingPowerPack.exitFlag = True

    serialControlObj.wait(2)
    print(serialControlObj.Test_Results)
    if 'EEA Adapter Connected with EEA Reload' == log_string:
        if serialControlObj.r['Reload Type'] == "EEA":
            videoThread = OLEDRecordingThread.myThread(
                (str(serialControlObj.r['Scenario Num']) + '#' + str(1) + serialControlObj.r['Test Scenario'] + '_' +
                 serialControlObj.r['Reload Type'] + '_' + str(1)),
                serialControlObj.videoPath)
            videoThread.start()
            serialControlObj.Switch_ONN_Relay(5, 2)  # B5:R2 - ON
            serialControlObj.Switch_ONN_Relay(5, 6)  # B5:R6 - ON
            serialControlObj.wait(5)
            ser = serial.Serial(serialControlObj.BlackBoxComPort, 9600)
            serialControlObj.wait(1)
            ############# READ ###################
            # command = bytes(serialControlObj.SULU_EEPROM_command_byte)
            command = bytes(EEA_RELOAD_EEPROM_command_byte)

            print('EEA RELOAD command', command)
            ser.write(command)
            serialControlObj.wait(5)
            # print(command)
            s = ser.read(2)
            s = list(s)
            packet_size = s[1]
            read_data = ser.read(packet_size - 2)
            read_data = list(read_data)
            print("==== EEA Reload Reset READ DATA ====")
            print(read_data[1:-1])
            ser.close()
            serialControlObj.Switch_OFF_Relay(5, 2)  # B5:R1 - OFF
            serialControlObj.Switch_OFF_Relay(5, 6)  # B5:R2 - OFF
            serialControlObj.wait(5)

            # TEST STEP: Connecting EEA Reload  147 and 148

            serialControlObj.wait(5)
            serialControlObj.ConnectingEEAReload()
            serialControlObj.wait(5)

            print("Step: EEA Reload Connected")

    Timestamps, Strings_from_PowerPack = ReadingQue( serialControlObj.my_Serthread.readQue)
    serialControl.convertListtoLogFile(Strings_from_PowerPack, str(videoPath + '\\TotalLog.txt'),
                                       fileOpenMode='a')
    Strings_to_Compare = locateStringsToCompareFromSmokeEvent(log_string)

    result = Compare(log_string, Strings_to_Compare, Strings_from_PowerPack)
    serialControlObj.Smoke_test_Results.append(log_string + result)
    if (result == 'FAIL'):
        print("split_Strings_from_PowerPack-----------------------", Strings_from_PowerPack)
        print("Strings_to_Compare-----------------------", Strings_to_Compare)
    print(serialControlObj.Smoke_test_Results)

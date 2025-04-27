#'''Rapid Switching Between Legacy & Smart Reloads  Wiritten by Manoj vadali 23-Feb-2022'''#

import sys

import nidaqmx
import pandas as pd
import serial
import serial.tools.list_ports

import MCPThread
import OLEDRecordingThread
from CRC16 import CRC16
from CRC16 import calc
from Compare import Compare
from EventsStrings import locateStringsToCompareFromEvent
from Prepare_Output_Json_File import *
from ReadBatteryRSOC import read_battery_RSOC
from ReadStatusVariables import ReadStatusVariables
from ReadingQue import ReadingQue
from RelayControlBytes import *
from Serial_Control import serialControl


def RapidSwitchingBetweenLegacyandSmartReloads(r, SULU_EEPROM_command_byte, MULU_EEPROM_command_byte, CARTRIDGE_EEPROM_command_byte, NCDComPort,
                 PowerPackComPort, BlackBoxComPort, USB6351ComPort, ArduinoUNOComPort, OUTPUT_PATH, videoPath,p):
    #print('Rapid Reload Insertion & Removal', r, SULU_EEPROM_command_byte, MULU_EEPROM_command_byte, CARTRIDGE_EEPROM_command_byte)
    serialControlObj = serialControl(r, SULU_EEPROM_command_byte, MULU_EEPROM_command_byte, CARTRIDGE_EEPROM_command_byte, NCDComPort, PowerPackComPort, BlackBoxComPort, USB6351ComPort, ArduinoUNOComPort, OUTPUT_PATH, videoPath)
    serialControlObj.OpenSerialConnection()
    Rapid_Switching_Between_Legacy_and_Smart_Reloads(serialControlObj, SULU_EEPROM_command_byte, MULU_EEPROM_command_byte, CARTRIDGE_EEPROM_command_byte, NCDComPort,
                 PowerPackComPort, BlackBoxComPort, USB6351ComPort, ArduinoUNOComPort, OUTPUT_PATH, videoPath,p)
    serialControlObj.disconnectSerialConnection()



# Purpose-To perform Normal Firing Scenarios
def Rapid_Switching_Between_Legacy_and_Smart_Reloads(serialControlObj, SULU_EEPROM_command_byte, MULU_EEPROM_command_byte, CARTRIDGE_EEPROM_command_byte, NCDComPort,
                 PowerPackComPort, BlackBoxComPort, USB6351ComPort, ArduinoUNOComPort, OUTPUT_PATH, videoPath,p):
        # r = getrow('C:\Python\Test_Configurator.xlsx', 0)
    TestBatteryLevelMax = serialControlObj.r['Battery RSOC Max Level']
    TestBatteryLevelMin = serialControlObj.r['Battery RSOC Min Level']
#    TimeDelayReloadInsertion = serialControlObj.r['Time Delay between Reload Insertion Cycle (Sec)": 3']
    iterPass = 0
    firePass = 0
    with nidaqmx.Task() as task:
        task.ao_channels.add_ao_voltage_chan('Dev1/ao0')
        print('1 Channel 1 Sample Write: ')
        print(task.write(0.25))

    serialControlObj.send_decimal_bytes(TURN_OFF_ALL_RELAYS_IN_ALL_BANKS[0])
    serialControlObj.wait(0.5)
    serialControlObj.Switch_ONN_Relay(3, 8)

    serialControlObj.wait(0.5)
    serialControlObj.Switch_ONN_Relay(3, 7)

    serialControlObj.wait(60)

    serialControlObj.send_decimal_bytes(TURN_OFF_ALL_RELAYS_IN_ALL_BANKS[0])
    print("Step: Remove Signia Power Handle from Charger")
    serialControlObj.wait(30)

    # while True:
    #     # seriallistData = serial.tools.list_ports.comports()
    #     # print(seriallistData)
    #     singiaPowerFound = False
    #     for singlePort in serial.tools.list_ports.comports():
    #         # print(str(singlePort))
    #         if 'SigniaPowerHandle' in str(singlePort):
    #             singiaPowerFound = True
    #             continue
    #     if singiaPowerFound:
    #         continue
    #     else:
    #         print('break from here')
    #         singiaPowerFound = False
    #         break
    #    serialControlObj.wait(15)

    # MCPThread.readingPowerPack.exitFlag = True

    if (read_battery_RSOC(25, PowerPackComPort) > TestBatteryLevelMax):  # and (
        # read_battery_RSOC(25, PowerPackComPort) > TestBatteryLevelMin):
        serialControlObj.Switch_ONN_Relay(1, 8)
        serialControlObj.wait(10)
        print("Adapter Engaged to Power Pack Mechanically")

        # TEST STEP: Attach the EGIA Adapter
        serialControlObj.Switch_ONN_ALL_Relays_In_Each_Bank(1)  # B1 - ALL ON
        print("Step: Adapter Connected")
        serialControlObj.wait(20)
        serialControlObj.ConnectingLegacyReload()
        print("Step: Legacy Reload Connected")
        serialControlObj.wait(5)
        while (read_battery_RSOC(25,
                                 PowerPackComPort) > TestBatteryLevelMax):  # and (read_battery_RSOC(25, PowerPackComPort) > TestBatteryLevelMin):
            serialControlObj.Switch_ONN_Relay(2, 5)  # B2:R5 - ON -- some operations battery discharge
            serialControlObj.wait(7)
            serialControlObj.Switch_OFF_Relay(2, 5)  # B2:R5 - ON
            serialControlObj.Switch_ONN_Relay(2, 4)  # B2:R5 - ON
            serialControlObj.wait(7)
            serialControlObj.Switch_OFF_Relay(2, 4)  # B2:R5 - ON

        serialControlObj.Switch_OFF_Relay(3, 1)  # B3:R1 - OFF
        serialControlObj.Switch_OFF_ALL_Relays_In_Each_Bank(1)
        serialControlObj.wait(10)
    if (read_battery_RSOC(25,
                          PowerPackComPort) < TestBatteryLevelMin):  # and (read_battery_RSOC(25, PowerPackComPort) <= TestBatteryLevelMax):
        # print('entered elif loop')
        serialControlObj.Switch_ONN_Relay(3, 7)  # battery charge
        serialControlObj.wait(0.5)
        serialControlObj.Switch_ONN_Relay(3, 8)
        # need to optimize this delay so that handle does not go to sleep or does not result communciation
        # failure while placing on charger
        serialControlObj.wait(10)
        while (read_battery_RSOC(50,
                                 PowerPackComPort) < TestBatteryLevelMin):  # and (read_battery_RSOC(25, PowerPackComPort) <= TestBatteryLevelMax):
            pass
            # serialControlObj.wait(.01)
            # read_battery_RSOC(10, PowerPackComPort)

    # if read_battery_RSOC(10, PowerPackComPort) == TestBatteryLevel:
    #      pass
    serialControlObj.wait(20)
    print("----------Placing Power Pack on Charger for startup Test--------------")
    serialControlObj.Switch_ONN_Relay(3, 7)
    serialControlObj.wait(0.2)
    serialControlObj.Switch_ONN_Relay(3, 8)
    serialControlObj.wait(60)
    print("----------Removing Power Pack from Charger for startup Test--------------")
    serialControlObj.Switch_OFF_Relay(3, 7)
    serialControlObj.wait(.2)
    serialControlObj.Switch_OFF_Relay(3, 8)

    while True:
        # seriallistData = serial.tools.list_ports.comports()
        # print(seriallistData)
        singiaPowerFound = False
        if any("SigniaPowerHandle" in s for s in serial.tools.list_ports.comports()):
            singiaPowerFound = True
        else:
            print('break from here')
            singiaPowerFound = False
            break

    strPort = 'None'
    # serialControlObj.wait(2)
    while (not 'SigniaPowerHandle' in strPort):
        ports = serial.tools.list_ports.comports()
        # strPort = 'None'
        numConnection = len(ports)
        for i in range(0, numConnection):
            port = ports[i]
            strPort = str(port)
            if 'SigniaPowerHandle' in strPort:
                print(ports[i])
                break
    # serialControlObj.wait(30)
    serialControlObj.wait(6)

    PPnotReady = True
    while PPnotReady:
        try:

            serPP = serial.Serial(serialControlObj.PowerPackComPort, 115200, bytesize=8, parity='N', stopbits=1,
                                  timeout=0.05, xonxoff=0)
            my_Serthread = MCPThread.readingPowerPack(serPP, 1000)
            my_Serthread.clearQue()
            MCPThread.readingPowerPack.exitFlag = False
            my_Serthread.start()
            PPnotReady = False
            # print(sys.argv[0], end=" ")
        except:
            pass
    # my_Serthread.clearQue()

    serialControlObj.Test_Results.append(
        str(serialControlObj.r['Scenario Num']) + '#' + str(p + 1) + "@" + serialControlObj.r[
            'Test Scenario'])  # + str(i+1))

    serialControlObj.wait(60)
    searchFlag = True

    Timestamps, Strings_from_PowerPack, data_path = ReadingQue(my_Serthread.readQue, searchFlag)
    serialControl.convertListtoLogFile(Strings_from_PowerPack, (videoPath + '\\StartUpLog.txt'), fileOpenMode='w')
    serialControl.convertListtoLogFile(Strings_from_PowerPack, 'TotalLog.txt', fileOpenMode='a')
    data_path = "None" if not data_path else data_path
    serialControlObj.Test_Results.append('Eventlog:' + data_path)

    ################################################################################################################

    byte_data = [2, 3, 4, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    crc_value = CRC16(0x00, byte_data)
    crc_value = hex(crc_value)
    # print('Original CRC: ', crc_value)
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
    print(command_byte)
    serialControlObj.Switch_ONN_Relay(5, 1)  # B5:R1 - ON
    serialControlObj.Switch_ONN_Relay(5, 5)  # B5:R1 - ON
    ser = serial.Serial(serialControlObj.BlackBoxComPort, 9600)
    serialControlObj.wait(5)
    ############# READ ###################
    command = bytes(command_byte)
    ser.write(command)
    serialControlObj.wait(3)
    serialControlObj.wait(5)
    print(command)
    s = ser.read(2)
    s = list(s)
    packet_size = s[1]
    read_data = ser.read(packet_size - 2)
    read_data = list(read_data)
    print("==== READ DATA ====")
    print(read_data[1:-1])
    ser.close()
    serialControlObj.Switch_OFF_Relay(5, 1)  # B5:R1 - OFF
    serialControlObj.Switch_OFF_Relay(5, 5)  # B5:R1 - OFF
    serialControlObj.wait(1)
    my_Serthread.clearQue()
    serialControlObj.wait(5)

    serialControlObj.connectClamshell()
    print("Step: Clamshell Connected")
    serialControlObj.wait(5)
    Timestamps, Strings_from_PowerPack = ReadingQue(my_Serthread.readQue)
    #serialControl.convertListtoLogFile(Strings_from_PowerPack, (videoPath + '\\StartUpLog.txt'), fileOpenMode='w')
    serialControl.convertListtoLogFile(Strings_from_PowerPack, 'TotalLog.txt', fileOpenMode='a')
    Strings_to_Compare = locateStringsToCompareFromEvent('Clamshell Connected')
    result = Compare('Clamshell Connected', Strings_to_Compare, Strings_from_PowerPack)

    rlist = {'Test Step': ['Clamshell Connected'], 'Test Result': [result]}
    df = pd.DataFrame(rlist)

    serialControlObj.Test_Results.append('Connected Clamshell:' + result)
    print(serialControlObj.Test_Results)

    ## Engaging the Adapter - Controlling the stepper motor
    serialControlObj.Switch_ONN_Relay(1, 8)
    serialControlObj.wait(7)
    print("Adapter Engaged to Power Pack Mechanically")

    my_Serthread.clearQue()
    serialControlObj.wait(5)
    # TEST STEP: Attach the EGIA Adapter
    serialControlObj.Switch_ONN_ALL_Relays_In_Each_Bank(1)  # B1 - ALL ON
    print("Step: Adapter Connected")
    serialControlObj.wait(10)
    Timestamps, Strings_from_PowerPack = ReadingQue(my_Serthread.readQue)
    #serialControl.convertListtoLogFile(Strings_from_PowerPack, (videoPath + '\\StartUpLog.txt'), fileOpenMode='w')
    serialControl.convertListtoLogFile(Strings_from_PowerPack, 'TotalLog.txt', fileOpenMode='a')
    '''Strings_to_Compare = ['  1Wire Device Adapter authenticated and identified',
                          ' GUI_NewState: ADAPTER_DETECTED',
                          ' GUI_NewState: EGIA_ADAPTER_CALIBRATING',
                          ' SM_NewSystemEventAlert: ADAPTER_FULLY_CALIBRATED',
                          ' Piezo: All Good',
                          ' GUI_NewState: EGIA_REQUEST_RELOAD']'''
    Strings_to_Compare = locateStringsToCompareFromEvent('Adapter Connected')
    result = Compare('Adapter Connected', Strings_to_Compare, Strings_from_PowerPack)
    serialControlObj.Test_Results.append('Adapter Connected:'+ result)
    print(serialControlObj.Test_Results)

    rlist = {'Test Step': ['Adapter Connected'], 'Test Result': [result]}
    df = df.append(pd.DataFrame(rlist))



    OLEDRecordingThread.exitFlag = False
    #videoThread = OLEDRecordingThread.myThread((serialControlObj.r['Test Scenario'] + '_' +
     #                                               serialControlObj.r['Reload Type'] + '_' + str(i)),
      #                                             serialControlObj.videoPath)
    videoThread = OLEDRecordingThread.myThread(
            (str(serialControlObj.r['Scenario Num']) + '#' + str(p + 1) + serialControlObj.r['Test Scenario'] + '_' +
             serialControlObj.r['Reload Type']), serialControlObj.videoPath)

    videoThread.start()


    # Commented below code for Reload switching between legacy and smart  reloads by  vadali
    # if serialControlObj.r['Reload Type'] == "Tri-Staple":
    #
    #     MCPThread.readingPowerPack.exitFlag = True
    #     serPP.close()
    #     # print(serialControlObj.Test_Results)
    #     # HandleFireCount1, HandleProcedureCount = GetHandleUseCount(PowerPackComPort)
    #     serialControlObj.wait(2)
    #     StatusVariables1 = ReadStatusVariables(PowerPackComPort)
    #     StatusVariables1 = StatusVariables1[13:61]
    #     # print(StatusVariables1)
    #     serPP = serial.Serial(serialControlObj.PowerPackComPort, 115200, bytesize=8, parity='N', stopbits=1,
    #                           timeout=0.05, xonxoff=0)
    #     MCPThread.readingPowerPack.exitFlag = False
    #     my_Serthread = MCPThread.readingPowerPack(serPP, 1000)
    #     my_Serthread.clearQue()
    #
    #     serialControlObj.ConnectingLegacyReload()
    #     serialControlObj.wait(5)
    #     Timestamps, Strings_from_PowerPack = ReadingQue(my_Serthread.readQue)
    #     serialControl.convertListtoLogFile(Strings_from_PowerPack, str(videoPath + '\\TotalLog.txt'), fileOpenMode='a')
    #     Strings_to_Compare = locateStringsToCompareFromEvent('Tri-Staple Connected')
    #     result = Compare('Tri-Staple Connected', Strings_to_Compare, Strings_from_PowerPack)
    #     serialControlObj.Test_Results.append('Tri-Staple Connected:' + result)
    #     print("Step: Tri-Staple Reload Connected")
    #     print(serialControlObj.Test_Results)
    #     serialControlObj.wait(3)
    #
    #     #print(serialControlObj.videoPath)
    #     for q in range(p):
    #         serialControlObj.wait(serialControlObj.r['Time Delay After Reload Insertion (Sec)'])
    #         serialControlObj.DisconnectingLegacyReload()
    #         serialControlObj.wait(serialControlObj.r['Time Delay After Reload Removal (Sec)'])
    #         serialControlObj.ConnectingLegacyReload()
    #
    #         print("Rapid Reload Removal & Insertion Cycle: " + str((1 + q)))
    #     # "Time Delay between Reload Insertion Cycle (Sec)"
    #     MCPThread.readingPowerPack.exitFlag = True
    #     serPP.close()
    #     StatusVariables2= ReadStatusVariables(PowerPackComPort)
    #     StatusVariables2 = StatusVariables2[13:61]
    #     temp_res = 'FAIL'
    #     if StatusVariables2 == StatusVariables1: temp_res= 'PASS'
    #     serialControlObj.DisconnectingLegacyReload()
    #     serialControlObj.Test_Results.append('Test Result =1:' + temp_res)
    #     serPP = serial.Serial(serialControlObj.PowerPackComPort, 115200, bytesize=8, parity='N', stopbits=1,
    #                           timeout=0.05, xonxoff=0)
    #     MCPThread.readingPowerPack.exitFlag = False
    #     my_Serthread = MCPThread.readingPowerPack(serPP, 1000)
    #     my_Serthread.clearQue()
    #     my_Serthread.start()
    if serialControlObj.r['Reload Type'] == "SULU":
        serialControlObj.Switch_ONN_Relay(5, 2)  # B5:R2 - ON
        serialControlObj.Switch_ONN_Relay(5, 6)  # B5:R6 - ON
        serialControlObj.wait(5)
        ser = serial.Serial(serialControlObj.BlackBoxComPort, 9600)
        ############# READ ###################
        command = bytes(serialControlObj.SULU_EEPROM_command_byte)
        print('SULU command', command)
        ser.write(command)
        serialControlObj.wait(5)
        # print(command)
        # s = ser.read(2)
        # s = list(s)
        # packet_size = s[1]
        # read_data = ser.read(packet_size - 2)
        # read_data = list(read_data)
        # #print("==== READ DATA ====")
        # #print(read_data[1:-1])
        ser.close()
        serialControlObj.Switch_OFF_Relay(5, 2)  # B5:R1 - OFF
        serialControlObj.Switch_OFF_Relay(5, 6)  # B5:R2 - OFF
        serialControlObj.wait(5)

        # TEST STEP: Connecting SULU Reload

        my_Serthread.clearQue()
        serialControlObj.wait(5)
        serialControlObj.ConnectingSULUReload()
        serialControlObj.wait(5)
        Timestamps, Strings_from_PowerPack = ReadingQue(my_Serthread.readQue)
        #serialControl.convertListtoLogFile(Strings_from_PowerPack, (videoPath + '\\StartUpLog.txt'), fileOpenMode='w')
        serialControl.convertListtoLogFile(Strings_from_PowerPack, 'TotalLog.txt', fileOpenMode='a')
        '''Strings_to_Compare = [' 1Wire Device Reload attached on 1WireBus Reload',
                              ' P_SIG_RELOAD_SWITCH_EVENT: switch closed',
                              ' ReloadConnected: Type=SULU, Length=45, Color=Purple',
                              ' Smart reload', ' SM_NewSystemEventAlert: RELOAD_INSTALLED',
                              ' EGIA Reload Values, ReloadID(1) Color(3) OneWireID(3074)',
                              ' GUI_NewState: EGIA_WAIT_FOR_CLAMP_CYCLE_CLOSE']'''
        Strings_to_Compare = locateStringsToCompareFromEvent('SULU Connected',
                                                             Length=serialControlObj.r.get('Reload Length(mm)'),
                                                             Color=serialControlObj.r.get('Reload Color'))
        result = Compare('SULU Connected', Strings_to_Compare, Strings_from_PowerPack)
        serialControlObj.Test_Results.append('SULU Connected:'+ result)
        print("Step: SULU Reload Connected")
        print(serialControlObj.Test_Results)
        serialControlObj.wait(3)

        MCPThread.readingPowerPack.exitFlag = True
        serPP.close()
        # print(serialControlObj.Test_Results)
        # HandleFireCount1, HandleProcedureCount = GetHandleUseCount(PowerPackComPort)
        serialControlObj.wait(2)
        StatusVariables1 = ReadStatusVariables(PowerPackComPort)
        StatusVariables1 = StatusVariables1[13:61]
        # print(StatusVariables1)
        serPP = serial.Serial(serialControlObj.PowerPackComPort, 115200, bytesize=8, parity='N', stopbits=1,
                              timeout=0.05, xonxoff=0)
        MCPThread.readingPowerPack.exitFlag = False
        my_Serthread = MCPThread.readingPowerPack(serPP, 1000)
        my_Serthread.clearQue()
        for q in range(p):
            serialControlObj.wait(serialControlObj.r['Time Delay After Reload Insertion (Sec)'])
            serialControlObj.RemovingSULUReload()
            serialControlObj.wait(serialControlObj.r['Time Delay After Reload Removal (Sec)'])
            serialControlObj.ConnectingLegacyReload()
            serialControlObj.wait(serialControlObj.r['Time Delay After Reload Insertion (Sec)'])
            serialControlObj.DisconnectingLegacyReload()
            serialControlObj.wait(serialControlObj.r['Time Delay After Reload Removal (Sec)'])
            serialControlObj.ConnectingSULUReload()

            print("Rapid Reload Removal & Insertion Cycle: " + str((1 + q)))
        # "Time Delay between Reload Insertion Cycle (Sec)"
        MCPThread.readingPowerPack.exitFlag = True
        serPP.close()
        StatusVariables2= ReadStatusVariables(PowerPackComPort)
        StatusVariables2 = StatusVariables2[13:61]
        temp_res = 'FAIL'
        if StatusVariables2 == StatusVariables1: temp_res= 'PASS'
        serialControlObj.DisconnectingLegacyReload()
        serialControlObj.Test_Results.append('Test Result =1:' + temp_res)

        serPP = serial.Serial(serialControlObj.PowerPackComPort, 115200, bytesize=8, parity='N', stopbits=1,
                              timeout=0.05, xonxoff=0)
        MCPThread.readingPowerPack.exitFlag = False
        my_Serthread = MCPThread.readingPowerPack(serPP, 1000)
        my_Serthread.clearQue()
        my_Serthread.start()

        if serialControlObj.r['Reload Type'] == "MULU":

            # videoThread = OLEDRecordingThread.myThread(
            #     (serialControlObj.r['Test Scenario'] + '_' + serialControlObj.r['Reload Type'] + '_' + str(i)), serialControlObj.videoPath)
            # videoThread.start()
            serialControlObj.Switch_ONN_Relay(5, 2)  # B5:R2 - ON
            serialControlObj.Switch_ONN_Relay(5, 6)  # B5:R6 - ON
            serialControlObj.Switch_OFF_Relay(5, 8)  # B5:R8 - OFF
            ser = serial.Serial(serialControlObj.BlackBoxComPort, 9600)
            ############# READ ###################
            command = bytes(serialControlObj.MULU_EEPROM_command_byte)
            ser.write(command)
            serialControlObj.wait(5)
            ser.write(command)
            serialControlObj.wait(5)
            ser.write(command)
            serialControlObj.wait(5)
            # print(command)
            # s = ser.read(2)
            # s = list(s)
            # packet_size = s[1]
            # read_data = ser.read(packet_size - 2)
            # read_data = list(read_data)
            # print("==== READ DATA ====")
            # print(read_data[1:-1])
            ser.close()
            serialControlObj.Switch_OFF_Relay(5, 2)  # B5:R2 - OFF
            serialControlObj.Switch_OFF_Relay(5, 6)  # B5:R6 - OFF
            serialControlObj.wait(5)

            my_Serthread.clearQue()
            serialControlObj.wait(5)
            serialControlObj.ConnectingMULUReload()
            serialControlObj.wait(5)
            Timestamps, Strings_from_PowerPack = ReadingQue(my_Serthread.readQue)
            # serialControl.convertListtoLogFile(Strings_from_PowerPack, (videoPath + '\\StartUpLog.txt'),
            #                                    fileOpenMode='w')
            serialControl.convertListtoLogFile(Strings_from_PowerPack, 'TotalLog.txt', fileOpenMode='a')
            '''Strings_to_Compare = [' 1Wire Device Reload attached on 1WireBus Reload',
                                  ' P_SIG_RELOAD_SWITCH_EVENT: switch closed',
                                  ' ReloadConnected: Type=MULU, Length=45, Color=Purple',
                                  ' Smart reload', ' SM_NewSystemEventAlert: RELOAD_INSTALLED',
                                  ' EGIA Reload Values, ReloadID(1) Color(3) OneWireID(3074)',
                                  ' GUI_NewState: EGIA_WAIT_FOR_CLAMP_CYCLE_CLOSE']'''
            Strings_to_Compare = locateStringsToCompareFromEvent('MULU Connected',
                                                                 Length=serialControlObj.r.get('Reload Length(mm)'))
            result = Compare('MULU Connected', Strings_to_Compare, Strings_from_PowerPack)
            serialControlObj.Test_Results.append('MULU Connected:'+ result)
            print("Step: MULU Reload Connected")
            print(serialControlObj.Test_Results)
            rlist = {'Test Step': ['MULU Reload Connected'], 'Test Result': [result]}
            df = df.append(pd.DataFrame(rlist))

            serialControlObj.wait(3)

            my_Serthread.clearQue()
            serialControlObj.wait(5)
            serialControlObj.ConnectingCartridge()
            serialControlObj.wait(5)
            Timestamps, Strings_from_PowerPack = ReadingQue(my_Serthread.readQue)
            # serialControl.convertListtoLogFile(Strings_from_PowerPack, (videoPath + '\\StartUpLog.txt'),
            #                                    fileOpenMode='w')
            serialControl.convertListtoLogFile(Strings_from_PowerPack, 'TotalLog.txt', fileOpenMode='a')
            '''Strings_to_Compare = [' 1Wire Device Reload attached on 1WireBus Reload',
                                  ' P_SIG_RELOAD_SWITCH_EVENT: switch closed',
                                  ' ReloadConnected: Type=MULU, Length=45, Color=Purple',
                                  ' Smart reload', ' SM_NewSystemEventAlert: RELOAD_INSTALLED',
                                  ' EGIA Reload Values, ReloadID(1) Color(3) OneWireID(3074)',
                                  ' GUI_NewState: EGIA_WAIT_FOR_CLAMP_CYCLE_CLOSE']'''
            Strings_to_Compare = locateStringsToCompareFromEvent('Cartridge Connected',
                                                                 Length=serialControlObj.r.get('Reload Length(mm)'),
                                                                 Color=serialControlObj.r.get('Cartridge Color'))
            result = Compare('Cartridge Connected', Strings_to_Compare, Strings_from_PowerPack)
            serialControlObj.Test_Results.append('Cartridge Connected:'+ result)
            print("Step: Cartridge Connected")
            print(serialControlObj.Test_Results)
            rlist = {'Test Step': ['Cartridge Connected'], 'Test Result': [result]}
            df = df.append(pd.DataFrame(rlist))

            MCPThread.readingPowerPack.exitFlag = True
            serPP.close()
            # print(serialControlObj.Test_Results)
            # HandleFireCount1, HandleProcedureCount = GetHandleUseCount(PowerPackComPort)
            serialControlObj.wait(2)
            StatusVariables1 = ReadStatusVariables(PowerPackComPort)
            StatusVariables1 = StatusVariables1[13:61]
            # print(StatusVariables1)
            serPP = serial.Serial(serialControlObj.PowerPackComPort, 115200, bytesize=8, parity='N', stopbits=1,
                                  timeout=0.05, xonxoff=0)
            MCPThread.readingPowerPack.exitFlag = False
            my_Serthread = MCPThread.readingPowerPack(serPP, 1000)
            my_Serthread.clearQue()
            for q in range(p):
                serialControlObj.wait(serialControlObj.r['Time Delay After Reload Insertion (Sec)'])
                serialControlObj.RemovingMULUReload()
                serialControlObj.wait(serialControlObj.r['Time Delay After Reload Removal (Sec)'])
                serialControlObj.ConnectingLegacyReload()
                serialControlObj.wait(serialControlObj.r['Time Delay After Reload Insertion (Sec)'])
                serialControlObj.DisconnectingLegacyReload()
                serialControlObj.wait(serialControlObj.r['Time Delay After Reload Removal (Sec)'])
                serialControlObj.ConnectingMULUReload()


                print("Rapid Reload Removal & Insertion Cycle: " + str((1+q)))
            # "Time Delay between Reload Insertion Cycle (Sec)"
            MCPThread.readingPowerPack.exitFlag = True
            serPP.close()
            StatusVariables2 = ReadStatusVariables(PowerPackComPort)
            StatusVariables2 = StatusVariables2[13:61]
            temp_res = 'FAIL'
            if StatusVariables2 == StatusVariables1: temp_res = 'PASS'
            serialControlObj.DisconnectingLegacyReload()
            serialControlObj.Test_Results.append('Test Result =1:' + temp_res)

            serPP = serial.Serial(serialControlObj.PowerPackComPort, 115200, bytesize=8, parity='N', stopbits=1,
                                  timeout=0.05, xonxoff=0)
            MCPThread.readingPowerPack.exitFlag = False
            my_Serthread = MCPThread.readingPowerPack(serPP, 1000)
            my_Serthread.clearQue()
            my_Serthread.start()

            #OLEDRecordingThread.exitFlag = True

        if serialControlObj.r['Reload Type'] == "SULU":
            my_Serthread.clearQue()
            serialControlObj.wait(5)
            serialControlObj.RemovingSULUReload()
            serialControlObj.wait(5)
            Timestamps, Strings_from_PowerPack = ReadingQue(my_Serthread.readQue)
            # serialControl.convertListtoLogFile(Strings_from_PowerPack, (videoPath + '\\StartUpLog.txt'),
            #                                    fileOpenMode='w')
            serialControl.convertListtoLogFile(Strings_from_PowerPack, 'TotalLog.txt', fileOpenMode='a')
            # Strings_to_Compare = [' GUI_NewState: EGIA_REQUEST_RELOAD']
            Strings_to_Compare = locateStringsToCompareFromEvent('Remove Reload')
            result = Compare('Remove Reload', Strings_to_Compare, Strings_from_PowerPack)
            serialControlObj.Test_Results.append('Remove Reload:'+ result)
            print("Step: Removed Reload")
            print(serialControlObj.Test_Results)
            serialControlObj.wait(2)
        if serialControlObj.r['Reload Type'] == "MULU":
            my_Serthread.clearQue()
            serialControlObj.wait(5)
            serialControlObj.Switch_OFF_Relay(3, 4)  # B3:R4 - OFF
            serialControlObj.Switch_OFF_Relay(3, 3)
            serialControlObj.RemovingMULUReload()
            serialControlObj.wait(5)
            Timestamps, Strings_from_PowerPack = ReadingQue(my_Serthread.readQue)
            # serialControl.convertListtoLogFile(Strings_from_PowerPack, (videoPath + '\\StartUpLog.txt'),
            #                                    fileOpenMode='w')
            serialControl.convertListtoLogFile(Strings_from_PowerPack, 'TotalLog.txt', fileOpenMode='a')
            # Strings_to_Compare = [' GUI_NewState: EGIA_REQUEST_RELOAD']
            Strings_to_Compare = locateStringsToCompareFromEvent('Remove Reload')
            result = Compare('Remove Reload', Strings_to_Compare, Strings_from_PowerPack)
            serialControlObj.Test_Results.append('Remove Reload:'+ result)

            print(serialControlObj.Test_Results)

            serialControlObj.wait(10)

    # TEST STEP: Remove Adapter
    my_Serthread.clearQue()
    serialControlObj.wait(5)
    serialControlObj.removeAdapter()
    serialControlObj.wait(10)
    Timestamps, Strings_from_PowerPack = ReadingQue(my_Serthread.readQue)
    #serialControl.convertListtoLogFile(Strings_from_PowerPack, (videoPath + '\\StartUpLog.txt'), fileOpenMode='w')
    serialControl.convertListtoLogFile(Strings_from_PowerPack, 'TotalLog.txt', fileOpenMode='a')
    Strings_to_Compare = locateStringsToCompareFromEvent('Remove Adapter')
    result = Compare('Remove Adapter', Strings_to_Compare, Strings_from_PowerPack)
    serialControlObj.Test_Results.append('Remove Adapter:'+ result)
    print("Step: Removed Adapter")
    print(serialControlObj.Test_Results)
    serialControlObj.wait(2)

    # print("Disengaged adapter Stepper motor controlled")
    serialControlObj.Switch_OFF_Relay(1, 8)
    print('Adapter Clutch Disengaged')

    # TEST STEP: Remove Clamshell
    my_Serthread.clearQue()
    serialControlObj.wait(5)
    serialControlObj.send_decimal_bytes(TURN_OFF_ALL_RELAYS_IN_ALL_BANKS[0])
    serialControlObj.wait(5)
    Timestamps, Strings_from_PowerPack = ReadingQue(my_Serthread.readQue)
    #serialControl.convertListtoLogFile(Strings_from_PowerPack, (videoPath + '\\StartUpLog.txt'), fileOpenMode='w')
    serialControl.convertListtoLogFile(Strings_from_PowerPack, 'TotalLog.txt', fileOpenMode='a')
    Strings_to_Compare = locateStringsToCompareFromEvent('Remove Clamshell')
    result = Compare('Remove Clamshell', Strings_to_Compare, Strings_from_PowerPack)
    serialControlObj.Test_Results.append('Remove Clamshell:' + result)
    print("Step: Removed Clamshell")
    print(serialControlObj.Test_Results)
    serialControlObj.wait(5)
    results_path = serialControlObj.OUTPUT_PATH + '\\Results.xlsx'
    df.to_excel(results_path)
    my_Serthread.clearQue()
    serialControlObj.wait(5)
    MCPThread.readingPowerPack.exitFlag = True
    serPP.close()
    OLEDRecordingThread.exitFlag = True
    with open(str((videoPath + '\\sample_result.txt')), 'a') as datalog:
            datalog.write('\n'.join(serialControlObj.Test_Results) + '\n')
    CS = [sys.argv[index+1] for index, ele in enumerate(sys.argv) if ele == "-c" or ele == "--changeset"]
    TT = [sys.argv[index+1] for index, ele in enumerate(sys.argv) if ele == "-t" or ele == "--test"]
    INTG = '--integration' in sys.argv
    RP = [sys.argv[index + 1] for index, ele in enumerate(sys.argv) if ele == "-r" or ele == "--root"]
    calculatePassFail(str((videoPath + '\\sample_result.txt')), str(RP[0] + '\\Test_Configurator.json'), str((videoPath +'\\StartUpLog.txt')), str(TT[0]), str(CS[0]), str(INTG))
    serialControlObj.PlacingPowerPackOnCharger()
    print('Power Pack Placed on Charger')
    print('------------------- End of Test Scenario --------------')
    serialControlObj.wait(30)

""" Name: EEA Tilt and Firing Retraction Recovery and Lockup; Function: T105_TiltAndTiltOpen_TiltAndFiringRetractionRecoveryAndLockup
Checks Performed During Stapling Recovery and Cutting Recovery Providing correct options
During firing recovery calibration fails or not,
Created by Ugra Narasimha, Date: 15-November-2024"""

from Serial_Control import serialControl
import os, sys

import MCPThread
import serial.tools.list_ports
# import serial.tools.list_ports_windows
import serial
from Compare import Compare
import nidaqmx
# import pandas as pd
from ReadBatteryRSOC import read_battery_RSOC
from CRC16 import CRC16
from CRC16 import calc
from ReadingQue import ReadQue
import OLEDRecordingThread
from RelayControlBytes import *
from EventsStrings import locateStringsToCompareFromEvent
from Read_Handle_Fire_Count import GetHandleUseCount
from ReadStatusVariables import ReadStatusVariables
from AdapterReadWrite import *
from Prepare_Output_Json_File import *


def T105_TiltAndTiltOpen_TiltAndFiringRetractionRecoveryAndLockup(r, SULU_EEPROM_command_byte, MULU_EEPROM_command_byte,
                                      CARTRIDGE_EEPROM_command_byte, NCDComPort, PowerPackComPort, BlackBoxComPort, USB6351ComPort, ArduinoUNOComPort,
                                      FtdiUartComPort, OUTPUT_PATH, videoPath, p,
                                      EEA_RELOAD_EEPROM_command_byte):
    # print('Recovery Items verification ', r, SULU_EEPROM_command_byte, MULU_EEPROM_command_byte, CARTRIDGE_EEPROM_command_byte, i)
    NCDComPort = NCDComPort
    print(NCDComPort, 'NCD COM Port')
    print("-----------------EEA Tilt And Firing Retraction Recovery And Lockup Case 1 -------------------")
    serialControlObj = serialControl(r, SULU_EEPROM_command_byte, MULU_EEPROM_command_byte,
                                     CARTRIDGE_EEPROM_command_byte, NCDComPort, PowerPackComPort, BlackBoxComPort,
                                     USB6351ComPort, ArduinoUNOComPort, FtdiUartComPort, OUTPUT_PATH, videoPath,
                                     EEA_RELOAD_EEPROM_command_byte)
    serialControlObj.OpenSerialConnection()
    T105_Tilt_TiltOpen_TiltAndFiringRetractionRecovery_And_Lockup(serialControlObj, EEA_RELOAD_EEPROM_command_byte, NCDComPort,
                                          PowerPackComPort, BlackBoxComPort, USB6351ComPort, ArduinoUNOComPort,
                                          FtdiUartComPort, OUTPUT_PATH, videoPath, p)
    serialControlObj.disconnectSerialConnection()


# Purpose-To perform recovery Items Failure Scenarios
def T105_Tilt_TiltOpen_TiltAndFiringRetractionRecovery_And_Lockup(serialControlObj, EEA_RELOAD_EEPROM_command_byte, NCDComPort,
                                          PowerPackComPort, BlackBoxComPort, USB6351ComPort, ArduinoUNOComPort,
                                          FtdiUartComPort, OUTPUT_PATH, videoPath, p):
    PowerPackComPort = PowerPackComPort
    EEA_RELOAD_EEPROM_command_byte = EEA_RELOAD_EEPROM_command_byte
    ArduinoUNOComPort = ArduinoUNOComPort
    NCDComPort = NCDComPort
    FtdiUartComPort = FtdiUartComPort
    print(NCDComPort)
    iterPass = 0
    firePass = 0
    TestBatteryLevelMax = serialControlObj.r['Battery RSOC Max Level']
    TestBatteryLevelMin = serialControlObj.r['Battery RSOC Min Level']
    clampingForce = serialControlObj.r['Clamping Force']
    firingForce = serialControlObj.r['Firing Force']
    numberOfFiringsinProcedure = serialControlObj.r['Num of Firings in Procedure']

    print(TestBatteryLevelMax, TestBatteryLevelMin, clampingForce, firingForce, numberOfFiringsinProcedure)

    with nidaqmx.Task() as task:
        task.ao_channels.add_ao_voltage_chan('Dev1/ao0')
        print('1 Channel 1 Sample Write: ')
        print(task.write(0.0))

    # Pre-conditioning:
    ## Remove handle form charger
    serialControlObj.send_decimal_bytes(TURN_OFF_ALL_RELAYS_IN_ALL_BANKS[0])
    serialControlObj.wait(0.5)
    serialControlObj.Switch_ONN_Relay(3, 8)

    serialControlObj.wait(0.5)
    serialControlObj.Switch_ONN_Relay(3, 7)

    serialControlObj.wait(60)

    serialControlObj.send_decimal_bytes(TURN_OFF_ALL_RELAYS_IN_ALL_BANKS[0])
    print("Step: Remove Signia Power Handle from Charger")
    serialControlObj.wait(40)

    ## By Reset Clamshell - Clamshell Connecting
    ###################################  RESETTING CLAMSHELL   #############################################################################

    byte_data = [2, 3, 4, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    crc_value = CRC16(0x00, byte_data)
    crc_value = hex(crc_value)
    print('Original CRC: ', crc_value)
    l = len(crc_value)
    crc_second_byte = crc_value[2:(l - 2)]
    crc_first_byte = crc_value[(l - 2):]
    byte_data.append(int(crc_first_byte, 16))
    byte_data.append(int(crc_second_byte, 16))
    ###################################### CLAMSHELL PACKET FRAMING #########################################################################
    byte_lst = [170, 69, 2, 1] + byte_data
    crc_value = calc(bytes(byte_lst))
    crc_value = int(crc_value, 16)
    byte_lst.append(crc_value)
    command_byte = byte_lst
    serialControlObj.Switch_ONN_Relay(5, 1)  # B5:R1 - ON
    serialControlObj.Switch_ONN_Relay(5, 5)  # B5:R1 - ON
    ser = serial.Serial(serialControlObj.BlackBoxComPort, 9600)
    serialControlObj.wait(5)
    ############# READ ###################
    command = bytes(command_byte)
    print('Clamshell ResetByte array', command)
    ser.write(command)
    serialControlObj.wait(3)
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

    ## Checking Battery RSOC Desired Values
    if read_battery_RSOC(25, PowerPackComPort) > TestBatteryLevelMax:  # and (read_battery_RSOC(25, PowerPackComPort) > TestBatteryLevelMin):
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

        while (read_battery_RSOC(25,PowerPackComPort)) > TestBatteryLevelMax:  # and (read_battery_RSOC(25, PowerPackComPort) > TestBatteryLevelMin):
            serialControlObj.Switch_ONN_Relay(2,5)  # B2:R5 - ON -- some operations' battery discharge Check if loaded condition of trocar can be explored for quick discharge
            serialControlObj.wait(7)
            serialControlObj.Switch_OFF_Relay(2, 5)  # B2:R5 - ON
            serialControlObj.Switch_ONN_Relay(2, 4)  # B2:R5 - ON
            serialControlObj.wait(7)
            serialControlObj.Switch_OFF_Relay(2, 4)  # B2:R5 - ON

        serialControlObj.DisconnectingEEAReload()
        serialControlObj.Switch_OFF_ALL_Relays_In_Each_Bank(1)  # Disconnected the clamshell
        serialControlObj.wait(10)
    if read_battery_RSOC(25,
                         PowerPackComPort) < TestBatteryLevelMin:  # and (read_battery_RSOC(25, PowerPackComPort) <= TestBatteryLevelMax):
        # print('entered elif loop')
        serialControlObj.Switch_ONN_Relay(3, 7)  # battery charge
        serialControlObj.wait(0.5)
        serialControlObj.Switch_ONN_Relay(3, 8)
        # need to optimize this delay so that handle does not go to sleep or does not result communication
        serialControlObj.wait(5)
        while (read_battery_RSOC(50,
                                 PowerPackComPort) < TestBatteryLevelMin):  # and (read_battery_RSOC(25, PowerPackComPort) <= TestBatteryLevelMax):
            pass

    serialControlObj.wait(20)
    '''
    ###################################################################################################################
    ## CASE 1: Tilt, Tilt Open 
    ###################################################################################################################
    '''
    ## STEP 1: Removing Handle From The Charger
    print("----------Placing Power Pack on Charger for startup Test--------------")
    serialControlObj.Switch_ONN_Relay(3, 7)
    serialControlObj.wait(.2)
    serialControlObj.Switch_ONN_Relay(3, 8)
    serialControlObj.wait(60)
    print("----------Removing Power Pack from Charger for startup Test--------------")
    serialControlObj.Switch_OFF_Relay(3, 7)
    serialControlObj.wait(.2)
    serialControlObj.Switch_OFF_Relay(3, 8)

    ## Once removing from the charger, searching for the comports
    while True:
        signiaPowerFound = False
        if any("SigniaPowerHandle" in s for s in serial.tools.list_ports.comports()):
            signiaPowerFound = True
        else:
            print('Signia Com Port Closed')
            signiaPowerFound = False
            break

    strPort = 'None'
    # Signia Comport Available
    while not 'SigniaPowerHandle' in strPort:
        ports = serial.tools.list_ports.comports()
        # strPort = 'None'
        numConnection = len(ports)
        for i in range(0, numConnection):
            port = ports[i]
            strPort = str(port)
            if 'SigniaPowerHandle' in strPort:
                print(ports[i], 'Available')
                break

    serialControlObj.wait(5)

    # Once Signia Comport Available, Opening the Port
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
        except:
            pass

    serialControlObj.Test_Results.append(
        str(serialControlObj.r['Scenario Num']) + '#' + str(p + 1) + "@" + serialControlObj.r['Test Scenario'])

    serialControlObj.wait(60)
    searchFlag = True

    Timestamps, Strings_from_PowerPack, data_path = ReadQue(1000, my_Serthread.readQue, searchFlag)
    serialControl.convertListtoLogFile(Strings_from_PowerPack, (videoPath + '\StartUpLog.txt'), fileOpenMode='w')
    serialControl.convertListtoLogFile(Strings_from_PowerPack, 'TotalLog.txt', fileOpenMode='a')
    Strings_to_Compare = locateStringsToCompareFromEvent('Remove Signia Power Handle from Charger')
    # print(Strings_from_PowerPack)

    result = Compare('Remove Signia Power Handle from Charger', Strings_to_Compare, Strings_from_PowerPack)
    data_path = "None" if not data_path else data_path
    serialControlObj.Test_Results.append('Eventlog:' + data_path)
    serialControlObj.Test_Results.append('Remove Signia Power Handle from Charger:' + result)

    ## STEP 2: Clamshell Connected
    # Turning ON Clamshell One Wire
    serialControlObj.connectClamshell()
    print("Step: Clamshell Connected")

    serialControlObj.wait(5)

    Timestamps, Strings_from_PowerPack = ReadQue(200, my_Serthread.readQue)
    serialControl.convertListtoLogFile(Strings_from_PowerPack, str(videoPath + '\\TotalLog.txt'), fileOpenMode='a')
    Strings_to_Compare = locateStringsToCompareFromEvent('Clamshell Connected')
    result = Compare('Clamshell Connected', Strings_to_Compare, Strings_from_PowerPack)

    # Capturing Clamshell connected data into the Test Results
    serialControlObj.Test_Results.append('Connected Clamshell:' + result)
    print(serialControlObj.Test_Results)

    # ## STEP 3: Record Power Pack and Adapter usage Counts
    # # For capturing Adapter Usage Counts - Adapter needs to be connected Mechanically
    # # Engaging the Adapter - Controlling the stepper motor
    # serialControlObj.Switch_ONN_Relay(1, 8)
    # serialControlObj.wait(7)
    # print("EEA Adapter Engaged to Power Pack Mechanically")
    #
    # MCPThread.readingPowerPack.exitFlag = True
    # serPP.close()
    # serialControlObj.wait(2)
    #
    # # Reading Power Pack Usage Counts
    # HandleFireCount, HandleProcedureCount = GetHandleUseCount(PowerPackComPort)
    #
    # # Reading Adapter EEPROM Usage Counts
    # AdapterEeProcedureCount, AdapterEeFireCount = GetAdapterEepromUsageCounts(FtdiUartComPort)
    #
    # # For capturing Onewire Usage counts from the Adapter via BB, below relays should be ON.
    # serialControlObj.Switch_ONN_Relay(5, 8) # B5:R8 - ON
    # serialControlObj.Switch_ONN_Relay(6, 1) # B6:R1 - ON
    #
    # # Reading Adapter One-Wire usage Counts
    # AdapterOwProcedureCount, AdapterOwFireCount = GetAdapterOnewireUsageCounts(BlackBoxComPort)
    #
    # serialControlObj.Switch_OFF_Relay(6, 1)  # B6:R1 - OFF
    # serialControlObj.Switch_OFF_Relay(5, 8)  # B5:R8 - OFF
    #
    # print('Before Firing Handle Fire Count:' + str(HandleFireCount),
    #       'Handle Procedure Count:' + str(HandleProcedureCount))
    # print('Before Firing Adapter Eeprom Fire Count:' + str(AdapterEeFireCount),
    #       'Adapter Eeprom Procedure Count:' + str(AdapterEeProcedureCount))
    # print('Before Firing Adapter Onewire Fire Count:' + str(AdapterOwFireCount),
    #       'Adapter Onewire Procedure Count:' + str(AdapterOwProcedureCount))
    #
    # # Re-Opening the PowerPackComPort
    # serPP = serial.Serial(serialControlObj.PowerPackComPort, 115200, bytesize=8, parity='N', stopbits=1,
    #                       timeout=0.05, xonxoff=0)
    # MCPThread.readingPowerPack.exitFlag = False
    # my_Serthread = MCPThread.readingPowerPack(serPP, 1000)
    # my_Serthread.clearQue()
    # my_Serthread.start()

    ## STEP 4: Adapter Connected With INIT State.
    my_Serthread.clearQue()
    serialControlObj.wait(5)
    serialControlObj.Switch_ONN_ALL_Relays_In_Each_Bank(1)  # B1 - ALL ON
    print("Step: EEA Adapter Connected")

    serialControlObj.wait(40)

    Timestamps, Strings_from_PowerPack = ReadQue(1000, my_Serthread.readQue)
    serialControl.convertListtoLogFile(Strings_from_PowerPack, str(videoPath + '\\TotalLog.txt'), fileOpenMode='a')
    Strings_to_Compare = locateStringsToCompareFromEvent('EEA Adapter Connected')
    result = Compare('EEA Adapter Connected', Strings_to_Compare, Strings_from_PowerPack)
    serialControlObj.Test_Results.append('EEA Adapter Connected:' + result)
    print(serialControlObj.Test_Results)

    my_Serthread.clearQue()
    serialControlObj.wait(5)

    # For Integrated Trocar this step would be -   Range Sensor to Force Compensate
    # For Non-Integrated Trocar this step would be - TPD ( Tip Protect Detection )
    serRangeSensor = serial.Serial(serialControlObj.ArduinoUNOComPort, 115200)
    serRangeSensor.flushOutput()
    serRangeSensor.flush()
    serRangeSensor.flushInput()

    # Record system Status variables Before Firing
    serialControlObj.wait(2)
    StatusVariables1 = ReadStatusVariables(PowerPackComPort)
    StatusVariables1 = StatusVariables1[13:61]
    StatusVariables1 = StatusVariables1[4:8] + StatusVariables1[12:16] + StatusVariables1[20:24] + StatusVariables1[
                                                                                                   28:32] + StatusVariables1[
                                                                                                            36:40] + StatusVariables1[
                                                                                                                     44:48]
    print('Before Firing Status Variables: ', StatusVariables1)

    # Creating Test Results Array to capture the Multiple Events During Firing ( Reload Connected, Green Key ACK, Trocar, Anvil, Firing Status )
    serialControlObj.Tilt_Tilt_Recovery_items_Test_Results = []
    serialControlObj.Tilt_Tilt_Recovery_items_Test_Results.append('Firing =' + str(1))
    OLEDRecordingThread.exitFlag = False

    ## STEP 5: Connecting EEA Reload Along with Ship Cap Presence Check
    if serialControlObj.r['Reload Type'] == "EEA":
        videoThread = OLEDRecordingThread.myThread(
            (str(serialControlObj.r['Scenario Num']) + '#' + str(p + 1) + serialControlObj.r['Test Scenario'] + '_' +
             serialControlObj.r['Reload Type'] + '_' + str(1)),
            serialControlObj.videoPath)
        videoThread.start()
        serialControlObj.Switch_ONN_Relay(5, 2)  # B5:R2 - ON
        serialControlObj.Switch_ONN_Relay(5, 6)  # B5:R6 - ON
        serialControlObj.wait(5)
        ser = serial.Serial(serialControlObj.BlackBoxComPort, 9600)
        ############# READ ###################
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

        # Turning ON EEA Reload One Wire
        my_Serthread.clearQue()
        serialControlObj.wait(5)
        serialControlObj.ConnectingEEAReload()
        serialControlObj.wait(10)
        Timestamps, Strings_from_PowerPack = ReadQue(1000, my_Serthread.readQue)
        serialControl.convertListtoLogFile(Strings_from_PowerPack, str(videoPath + '\\TotalLog.txt'), fileOpenMode='a')

        # Ship Cap Presence check
        if serialControlObj.r['Ship cap Present'] == "Yes":
            Strings_to_Compare = locateStringsToCompareFromEvent('EEA RELOAD Connected with Ship cap',
                                                                 Length=serialControlObj.r.get('Reload Diameter(mm)'),
                                                                 Color=serialControlObj.r.get('Reload Color'))
            result = Compare('EEA RELOAD Connected', Strings_to_Compare, Strings_from_PowerPack)
            serialControlObj.Tilt_Recovery_items_Test_Results.append('EEA RELOAD Connected:' + result)
        elif serialControlObj.r['Ship cap Present'] == "No":
            Strings_to_Compare = locateStringsToCompareFromEvent('EEA RELOAD Connected without Ship cap',
                                                                 Length=serialControlObj.r.get('Reload Diameter(mm)'),
                                                                 Color=serialControlObj.r.get('Reload Color'))
            result = Compare('EEA RELOAD Connected', Strings_to_Compare, Strings_from_PowerPack)
            serialControlObj.Tilt_Recovery_items_Test_Results.append('EEA RELOAD Connected:' + result)

        print("Step: EEA Reload Connected")
        print(serialControlObj.Tilt_Recovery_items_Test_Results)
        serialControlObj.wait(3)

        ## STEP 6: Extention of Trocar
        my_Serthread.clearQue()
        serialControlObj.wait(5)
        serialControlObj.Switch_ONN_Relay(2, 4)  # B2:R5 - ON
        serialControlObj.wait(10)
        serialControlObj.Switch_OFF_Relay(2, 4)  # B2:R5 - OFF

        Timestamps, Strings_from_PowerPack = ReadQue(1000, my_Serthread.readQue)
        serialControl.convertListtoLogFile(Strings_from_PowerPack, str(videoPath + '\\TotalLog.txt'), fileOpenMode='a')
        Strings_to_Compare = locateStringsToCompareFromEvent('EEA Trocar Extention with Reload')
        result = Compare('EEA Trocar Extention with Reload', Strings_to_Compare, Strings_from_PowerPack)
        serialControlObj.Test_Results.append('EEA Trocar Extention with Reload:' + result)

        ## STEP 7: Clamping on Tissue - Retraction of Trocar Until Clamp GAP is reached
        my_Serthread.clearQue()
        serialControlObj.wait(5)
        cf = serialControlObj.EEAForceDecode(clampingForce)
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

        serialControlObj.wait(25)  # waiting time for clamping on tissue Manoj Vadali need to update based on tissue thichkness pls check?

        Timestamps, Strings_from_PowerPack = ReadQue(1000, my_Serthread.readQue)
        serialControl.convertListtoLogFile(Strings_from_PowerPack, str(videoPath + '\\TotalLog.txt'), fileOpenMode='a')
        Strings_to_Compare = locateStringsToCompareFromEvent('EEA Clamping on Tissue')
        result = Compare('EEA Clamping on Tissue', Strings_to_Compare, Strings_from_PowerPack)
        serialControlObj.Test_Results.append('EEA Clamping on Tissue:' + result)
        print("Step: EEA Clamping on Tissue")
        print(serialControlObj.Tilt_Recovery_items_Test_Results)

        my_Serthread.clearQue()
        serialControlObj.wait(5)
        serialControlObj.Switch_OFF_Relay(2, 5)  # B2:R5 - OFF

        ## STEP 8: Safety Key Acknowledgement
        serialControlObj.GreenKeyAck()
        serialControlObj.wait(2)
        Timestamps, Strings_from_PowerPack = ReadQue(200, my_Serthread.readQue)
        serialControl.convertListtoLogFile(Strings_from_PowerPack, str(videoPath + '\\TotalLog.txt'), fileOpenMode='a')
        Strings_to_Compare = locateStringsToCompareFromEvent('EEA Green Key Ack')
        result = Compare('EEA Green Key Ack', Strings_to_Compare, Strings_from_PowerPack)
        serialControlObj.Tilt_Recovery_items_Test_Results.append('EEA Green Key Ack:' + result)
        print("Step: Acknowledged Safety Key (Green LED) for firing")
        print(serialControlObj.Tilt_Recovery_items_Test_Results)

        ## STEP 9: Firing
        # ff = serialControlObj.EEAForceDecode(firingForce)
        with nidaqmx.Task() as task:
            task.ao_channels.add_ao_voltage_chan('Dev1/ao0')
            print('1 Channel 1 Sample Write: ')
            print(task.write(3.25))

        my_Serthread.clearQue()
        serialControlObj.wait(5)
        serialControlObj.Switch_ONN_Relay(4, 1)
        serialControlObj.Switch_ONN_Relay(4, 2)  # To turn on Linear actuator
        serialControlObj.wait(3)
        serialControlObj.Switch_ONN_Relay(2, 5)  # B2:R5 - ON
        serialControlObj.wait(0.5)
        serialControlObj.Switch_OFF_Relay(2, 5)  # B2:R5 - OFF
        serialControlObj.wait(4)

        # Remove Adapter when 1st EEA Stapling In Progress
        serialControlObj.Switch_OFF_Relay(1, 8)  # B1:R8 - Turning Off - Adapter Clutch Disengaged
        serialControlObj.removeAdapter()
        serialControlObj.wait(2)

        serialControlObj.Switch_OFF_Relay(4, 1)
        serialControlObj.Switch_OFF_Relay(4, 2)  # To turn on Linear actuator
        serialControlObj.wait(3)
        with nidaqmx.Task() as task:
            task.ao_channels.add_ao_voltage_chan('Dev1/ao0')
            print('1 Channel 1 Sample Write: ')
            print(task.write(0))

        serialControlObj.Switch_ONN_Relay(4, 3)
        serialControlObj.Switch_ONN_Relay(4, 4)  # To turn on Linear actuator at full power
        serialControlObj.wait(5)
        serialControlObj.Switch_OFF_Relay(4, 3)
        serialControlObj.Switch_OFF_Relay(4, 4)  # To turn off Linear actuator from full power
        serialControlObj.wait(.5)
        serialControlObj.Switch_ONN_Relay(4, 5)
        serialControlObj.Switch_ONN_Relay(4, 6)  # To turn on Linear actuator at full power
        serialControlObj.wait(30)

        Timestamps, Strings_from_PowerPack = ReadQue(1000, my_Serthread.readQue)
        serialControl.convertListtoLogFile(Strings_from_PowerPack, str(videoPath + '\\TotalLog.txt'),
                                           fileOpenMode='a')

        Strings_to_Compare = locateStringsToCompareFromEvent('EEA Firing')
        result = Compare('EEA Firing', Strings_to_Compare, Strings_from_PowerPack)
        serialControlObj.Tilt_Recovery_items_Test_Results.append('EEA Firing:' + result)
        print("Step: Firing Completed")
        print(serialControlObj.Tilt_Recovery_items_Test_Results)
        serialControlObj.wait(7)

    ## STEP 10: Remove Adapter 
    # From Adapter EEPROM
    RecoveryIDEeprom  = GetAdapterEEPROMRecoveryIdData(FtdiUartComPort)
    RecoveryStateString = AdapterRecoveryStates(RecoveryIDEeprom)
    print("Recovery ID After Removing Adapter During 1st EEA Stapling In Progress : ", RecoveryStateString)
    serialControlObj.Test_Results.append(RecoveryStateString + ":" + RecoveryIDEeprom)
    print(serialControlObj.Test_Results)

    # From Adapter Onewire
    # Engaging the Adapter
    serialControlObj.Switch_ONN_Relay(1, 8)
    serialControlObj.wait(7)
    print("EEA Adapter Engaged to Power Pack Mechanically")

    RecoveryIdHighByte, RecoveryIdLowByte =  GetAdapterOnewireRecoveryIdData(BlackBoxComPort)

    RecoveryIdOnewire = int((RecoveryIdLowByte, 16)) * 256 + int(RecoveryIdHighByte, 16)

    # Recovery State Verifying in the Adapter onewire and Capturing into the Test Results
    serialControlObj.Test_Results.append("5th to Last Byte : " + RecoveryIdHighByte)
    serialControlObj.Test_Results.append("4th to Last Byte : " + RecoveryIdLowByte)
    print(serialControlObj.Test_Results)

    if RecoveryIDEeprom == RecoveryIdOnewire:
        pass


    ## STEP 11: Re-Attaching the Adapter to the Power Pack
    my_Serthread.clearQue()
    serialControlObj.wait(5)
    serialControlObj.ConnectAdapter()
    print("Step: EEA Adapter Re-Connected")

    serialControlObj.wait(40)

    Timestamps, Strings_from_PowerPack = ReadQue(1000, my_Serthread.readQue)
    serialControl.convertListtoLogFile(Strings_from_PowerPack, str(videoPath + '\\TotalLog.txt'), fileOpenMode='a')
    Strings_to_Compare = locateStringsToCompareFromEvent('EEA Adapter Re-Connected After Stapling In Progress')
    result = Compare('EEA Adapter Re-Connected After Stapling In Progress', Strings_to_Compare, Strings_from_PowerPack)
    serialControlObj.Test_Results.append('EEA Adapter Re-Connected After Stapling In Progress:' + result)
    print(serialControlObj.Test_Results)

    ## STEP 11: Performing Rotation, Articulation and Close Operation
    my_Serthread.clearQue()

    # Right CW Rotation
    serialControlObj.Switch_ONN_Relay(2, 7)  # B2:R7 - ON
    serialControlObj.wait(5)
    serialControlObj.Switch_OFF_Relay(2, 7)  # B2:R7 - OFF

    # Left Articulation
    my_Serthread.clearQue()
    serialControlObj.wait(5)
    serialControlObj.Switch_ONN_Relay(2, 3)  # B2:R3 - ON
    serialControlObj.wait(7)
    serialControlObj.Switch_OFF_Relay(2, 3)  # B2:R3 - OFF

    # Close Key Operation
    my_Serthread.clearQue()
    serialControlObj.wait(5)
    serialControlObj.Switch_ONN_Relay(2, 5)  # B2:R5 - ON
    serialControlObj.wait(10)
    serialControlObj.Switch_OFF_Relay(2, 5)  # B2:R5 - OFF

    Timestamps, Strings_from_PowerPack = ReadQue(1000, my_Serthread.readQue)
    serialControl.convertListtoLogFile(Strings_from_PowerPack, str(videoPath + '\\TotalLog.txt'),
                                       fileOpenMode='a')
    Strings_to_Compare = locateStringsToCompareFromEvent('Rotation & Articulation & Close Operation During SP IP')
    result = Compare('Rotation & Articulation & Close Operation During SP IP', Strings_to_Compare, Strings_from_PowerPack)
    serialControlObj.Test_Results.append('Rotation & Articulation & Close Operation During SP IP:' + result)
    print(serialControlObj.Test_Results)

    ## STEP 12: Holding Rotation Buttons
    serialControlObj.Switch_ONN_Relay(2, 1)  # B2:R7 - ON
    serialControlObj.Switch_ONN_Relay(2, 2)  # B2:R8 - ON
    serialControlObj.Switch_ONN_Relay(2, 7)  # B2:R1 - ON
    serialControlObj.Switch_ONN_Relay(2, 8)  # B2:R2 - ON

    serialControlObj.wait(4)

    serialControlObj.Switch_OFF_Relay(2, 8)  # B2:R7 - OFF
    serialControlObj.Switch_OFF_Relay(2, 7)  # B2:R8 - OFF
    serialControlObj.Switch_OFF_Relay(2, 2)  # B2:R1 - OFF
    serialControlObj.Switch_OFF_Relay(2, 1)  # B2:R2 - OFF

    Timestamps, Strings_from_PowerPack = ReadQue(1000, my_Serthread.readQue)
    serialControl.convertListtoLogFile(Strings_from_PowerPack, str(videoPath + '\\TotalLog.txt'), fileOpenMode='a')
    Strings_to_Compare = locateStringsToCompareFromEvent('Rotation Operation During SP IP')
    result = Compare('Rotation Operation During SP IP', Strings_to_Compare, Strings_from_PowerPack)
    serialControlObj.Test_Results.append('Rotation Operation During SP IP:' + result)
    print("Step: Rotation Operation During SP IP")
    print(serialControlObj.Test_Results)

    ## STEP 13: Staples Detected Exit State - Fully open position
    my_Serthread.clearQue()
    serialControlObj.wait(5)

    # Handling here, No staples detected State Exit, Full Open position, SSE.
    serialControlObj.EEANoStaplesDetectedStateExit()

    Timestamps, Strings_from_PowerPack = ReadQue(1000, my_Serthread.readQue)
    serialControl.convertListtoLogFile(Strings_from_PowerPack, str(videoPath + '\\TotalLog.txt'), fileOpenMode='a')
    Strings_to_Compare = locateStringsToCompareFromEvent('No Staples Detected State Exit')
    result = Compare('No Staples Detected State Exit', Strings_to_Compare, Strings_from_PowerPack)
    serialControlObj.Normal_Firing_Test_Results.append('No Staples Detected State Exit:' + result)
    print("No Staples Detected State Exit")
    print(serialControlObj.Normal_Firing_Test_Results)

    ## STEP 14: Remove Reload
    my_Serthread.clearQue()
    serialControlObj.wait(5)
    serialControlObj.DisconnectingEEAReload()

    Timestamps, Strings_from_PowerPack = ReadQue(1000, my_Serthread.readQue)
    serialControl.convertListtoLogFile(Strings_from_PowerPack, str(videoPath + '\\TotalLog.txt'), fileOpenMode='a')
    Strings_to_Compare = locateStringsToCompareFromEvent('EEA Remove Reload Enter SSE')
    result = Compare('EEA Remove Reload Enter SSE', Strings_to_Compare, Strings_from_PowerPack)
    serialControlObj.Normal_Firing_Test_Results.append('EEA Remove Reload Enter SSE:' + result)
    print("EEA Remove Reload Enter SSE")
    print(serialControlObj.Normal_Firing_Test_Results)

    ## STEP 15: Surgical Site Extraction (SSE)
    my_Serthread.clearQue()
    serialControlObj.wait(5)

    # Surgical Site Extraction Exit
    serialControlObj.EEASurgicalSiteExtractionStateExit()

    Timestamps, Strings_from_PowerPack = ReadQue(1000, my_Serthread.readQue)
    serialControl.convertListtoLogFile(Strings_from_PowerPack, str(videoPath + '\\TotalLog.txt'), fileOpenMode='a')
    Strings_to_Compare = locateStringsToCompareFromEvent('SSE Exit')
    result = Compare('SSE Exit', Strings_to_Compare, Strings_from_PowerPack)
    serialControlObj.Tilt_Recovery_items_Test_Results.append('SSE Exit:' + result)
    print("Step:SSE Exit")
    print(serialControlObj.Tilt_Recovery_items_Test_Results)

    ## STEP 16: Remove Adapter
    my_Serthread.clearQue()
    serialControlObj.wait(5)
    serialControlObj.DisconnectingEEAReload()

    Timestamps, Strings_from_PowerPack = ReadQue(1000, my_Serthread.readQue)
    serialControl.convertListtoLogFile(Strings_from_PowerPack, str(videoPath + '\\TotalLog.txt'), fileOpenMode='a')
    Strings_to_Compare = locateStringsToCompareFromEvent('Remove EEA Adapter')
    result = Compare('Remove EEA Adapter', Strings_to_Compare, Strings_from_PowerPack)
    serialControlObj.Normal_Firing_Test_Results.append('Remove EEA Adapter:' + result)
    print("Remove EEA Adapter")
    print(serialControlObj.Normal_Firing_Test_Results)

    ## STEP 16: Record Adapter usage Counts - Adapter Firing and Procedure Count Incremented by 1
    # For capturing Adapter Usage Counts - Adapter needs to be connected Mechanically
    # Engaging the Adapter - Controlling the stepper motor
    serialControlObj.Switch_ONN_Relay(1, 8)
    serialControlObj.wait(7)
    print("EEA Adapter Engaged to Power Pack Mechanically")

    MCPThread.readingPowerPack.exitFlag = True
    serPP.close()
    serialControlObj.wait(2)

    # Reading Adapter EEPROM Usage Counts
    AdapterEeProcedureCount, AdapterEeFireCount = GetAdapterEepromUsageCounts(FtdiUartComPort)

    # For capturing Onewire Usage counts from the Adapter via BB, below relays should be ON.
    serialControlObj.Switch_ONN_Relay(5, 8)  # B5:R8 - ON
    serialControlObj.Switch_ONN_Relay(6, 1)  # B6:R1 - ON

    # Reading Adapter One-Wire usage Counts
    AdapterOwProcedureCount, AdapterOwFireCount = GetAdapterOnewireUsageCounts(BlackBoxComPort)

    serialControlObj.Switch_OFF_Relay(6, 1)  # B6:R1 - OFF
    serialControlObj.Switch_OFF_Relay(5, 8)  # B5:R8 - OFF

    print('Adapter Eeprom Fire Count:' + str(AdapterEeFireCount),
          'Adapter Eeprom Procedure Count:' + str(AdapterEeProcedureCount))
    print('Adapter Onewire Fire Count:' + str(AdapterOwFireCount),
          'Adapter Onewire Procedure Count:' + str(AdapterOwProcedureCount))

    serPP = serial.Serial(serialControlObj.PowerPackComPort, 115200, bytesize=8, parity='N', stopbits=1,
                          timeout=0.05, xonxoff=0)
    MCPThread.readingPowerPack.exitFlag = False
    my_Serthread = MCPThread.readingPowerPack(serPP, 1000)
    my_Serthread.clearQue()
    my_Serthread.start()

    ## STEP 14: Re-Connecting the adapter with INIT State
    my_Serthread.clearQue()
    serialControlObj.wait(5)
    serialControlObj.Switch_ONN_ALL_Relays_In_Each_Bank(1)  # B1 - ALL ON
    print("Step: EEA Adapter Connected")

    serialControlObj.wait(40)

    Timestamps, Strings_from_PowerPack = ReadQue(1000, my_Serthread.readQue)
    serialControl.convertListtoLogFile(Strings_from_PowerPack, str(videoPath + '\\TotalLog.txt'), fileOpenMode='a')
    Strings_to_Compare = locateStringsToCompareFromEvent('EEA Adapter Connected')
    result = Compare('EEA Adapter Connected', Strings_to_Compare, Strings_from_PowerPack)
    serialControlObj.Test_Results.append('EEA Adapter Connected:' + result)
    print(serialControlObj.Test_Results)

    ## STEP 15: Attaching EEA reload along with ship cap presence check
    if serialControlObj.r['Reload Type'] == "EEA":
        videoThread = OLEDRecordingThread.myThread(
            (str(serialControlObj.r['Scenario Num']) + '#' + str(p + 1) + serialControlObj.r['Test Scenario'] + '_' +
             serialControlObj.r['Reload Type'] + '_' + str(1)),
            serialControlObj.videoPath)
        videoThread.start()
        serialControlObj.Switch_ONN_Relay(5, 2)  # B5:R2 - ON
        serialControlObj.Switch_ONN_Relay(5, 6)  # B5:R6 - ON
        serialControlObj.wait(5)
        ser = serial.Serial(serialControlObj.BlackBoxComPort, 9600)
        ############# READ ###################
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

        # Turning ON EEA Reload One Wire
        my_Serthread.clearQue()
        serialControlObj.wait(5)
        serialControlObj.ConnectingEEAReload()
        serialControlObj.wait(5)
        Timestamps, Strings_from_PowerPack = ReadQue(1000, my_Serthread.readQue)
        serialControl.convertListtoLogFile(Strings_from_PowerPack, str(videoPath + '\\TotalLog.txt'), fileOpenMode='a')

        if serialControlObj.r['Ship cap Present'] == "Yes":
            Strings_to_Compare = locateStringsToCompareFromEvent('EEA RELOAD Connected with Ship cap',
                                                                 Length=serialControlObj.r.get('Reload Diameter(mm)'),
                                                                 Color=serialControlObj.r.get('Reload Color'))
            result = Compare('EEA RELOAD Connected', Strings_to_Compare, Strings_from_PowerPack)
            serialControlObj.Tilt_Recovery_items_Test_Results.append('EEA RELOAD Connected:' + result)
        elif serialControlObj.r['Ship cap Present'] == "No":
            Strings_to_Compare = locateStringsToCompareFromEvent('EEA RELOAD Connected without Ship cap',
                                                                 Length=serialControlObj.r.get('Reload Diameter(mm)'),
                                                                 Color=serialControlObj.r.get('Reload Color'))
            result = Compare('EEA RELOAD Connected', Strings_to_Compare, Strings_from_PowerPack)
            serialControlObj.Tilt_Recovery_items_Test_Results.append('EEA RELOAD Connected:' + result)

        print("Step: EEA Reload Connected")
        print(serialControlObj.Tilt_Recovery_items_Test_Results)
        serialControlObj.wait(3)

        ## STEP 16: Extension of Trocar
        my_Serthread.clearQue()
        serialControlObj.wait(5)
        serialControlObj.Switch_ONN_Relay(2, 4)  # B2:R5 - ON
        serialControlObj.wait(10)
        serialControlObj.Switch_OFF_Relay(2, 4)  # B2:R5 - OFF

        Timestamps, Strings_from_PowerPack = ReadQue(1000, my_Serthread.readQue)
        serialControl.convertListtoLogFile(Strings_from_PowerPack, str(videoPath + '\\TotalLog.txt'), fileOpenMode='a')
        Strings_to_Compare = locateStringsToCompareFromEvent('EEA Trocar Extention with Reload')
        result = Compare('EEA Trocar Extention with Reload', Strings_to_Compare, Strings_from_PowerPack)
        serialControlObj.Test_Results.append('EEA Trocar Extention with Reload:' + result)

        ## STEP 17: Clamping on Tissue - Retraction of Trocar Until Clamp GAP is reached
        my_Serthread.clearQue()
        serialControlObj.wait(5)
        cf = serialControlObj.EEAForceDecode(clampingForce)
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

        Timestamps, Strings_from_PowerPack = ReadQue(1000, my_Serthread.readQue)
        serialControl.convertListtoLogFile(Strings_from_PowerPack, str(videoPath + '\\TotalLog.txt'), fileOpenMode='a')
        Strings_to_Compare = locateStringsToCompareFromEvent('EEA Clamping on Tissue')
        result = Compare('EEA Clamping on Tissue', Strings_to_Compare, Strings_from_PowerPack)
        serialControlObj.Test_Results.append('EEA Clamping on Tissue:' + result)
        print("Step: EEA Clamping on Tissue")
        print(serialControlObj.Tilt_Recovery_items_Test_Results)

        my_Serthread.clearQue()
        serialControlObj.wait(5)
        serialControlObj.Switch_OFF_Relay(2, 5)  # B2:R5 - OFF

        # STEP 18: Safety Key Acknowledgement
        serialControlObj.GreenKeyAck()
        serialControlObj.wait(2)
        Timestamps, Strings_from_PowerPack = ReadQue(200, my_Serthread.readQue)
        serialControl.convertListtoLogFile(Strings_from_PowerPack, str(videoPath + '\\TotalLog.txt'), fileOpenMode='a')
        Strings_to_Compare = locateStringsToCompareFromEvent('EEA Green Key Ack')
        result = Compare('EEA Green Key Ack', Strings_to_Compare, Strings_from_PowerPack)
        serialControlObj.Tilt_Recovery_items_Test_Results.append('EEA Green Key Ack:' + result)
        print("Step: Acknowledged Safety Key (Green LED) for firing")
        print(serialControlObj.Tilt_Recovery_items_Test_Results)

        ## STEP 19: Firing
        # ff = serialControlObj.EEAForceDecode(firingForce)
        with nidaqmx.Task() as task:
            task.ao_channels.add_ao_voltage_chan('Dev1/ao0')
            print('1 Channel 1 Sample Write: ')
            print(task.write(3.25))

        my_Serthread.clearQue()
        serialControlObj.wait(5)
        serialControlObj.Switch_ONN_Relay(4, 1)
        serialControlObj.Switch_ONN_Relay(4, 2)  # To turn on Linear actuator
        serialControlObj.wait(3)
        serialControlObj.Switch_ONN_Relay(2, 5)  # B2:R5 - ON
        serialControlObj.wait(0.5)
        serialControlObj.Switch_OFF_Relay(2, 5)  # B2:R5 - OFF

        serialControlObj.wait(4)
        serialControlObj.Switch_OFF_Relay(4, 1)
        serialControlObj.Switch_OFF_Relay(4, 2)  # To turn on Linear actuator
        serialControlObj.wait(1)
        with nidaqmx.Task() as task:
            task.ao_channels.add_ao_voltage_chan('Dev1/ao0')
            print('1 Channel 1 Sample Write: ')
            print(task.write(0))

        # Remove Adapter when 2nd EEA Stapling In Progress
        serialControlObj.Switch_OFF_Relay(1, 8)  # B1:R8 - Turning Off - Adapter Clutch Disengaged
        serialControlObj.removeAdapter()
        serialControlObj.wait(5)

        Timestamps, Strings_from_PowerPack = ReadQue(1000, my_Serthread.readQue)
        serialControl.convertListtoLogFile(Strings_from_PowerPack, str(videoPath + '\\TotalLog.txt'),
                                           fileOpenMode='a')

        Strings_to_Compare = locateStringsToCompareFromEvent('Remove Adapter When 2nd EEA Stapling In Progress')
        result = Compare('Remove Adapter When 2nd EEA Stapling In Progress', Strings_to_Compare, Strings_from_PowerPack)
        serialControlObj.Tilt_Recovery_items_Test_Results.append('Recovery Adapter When 2nd EEA Stapling In Progress:' + result)
        print("Step: Remove Adapter When 2nd EEA Stapling In Progress")
        print(serialControlObj.Tilt_Recovery_items_Test_Results)
        serialControlObj.wait(7)

        ## STEP 20: Verifying Recovery ID data
        # From Adapter EEPROM
        RecoveryIDEeprom = GetAdapterEEPROMRecoveryIdData(FtdiUartComPort)
        RecoveryStateString = AdapterRecoveryStates(RecoveryIDEeprom)
        print("Recovery ID After Removing Adapter During 2nd EEA Stapling In Progress : ", RecoveryStateString)
        serialControlObj.Test_Results.append(RecoveryStateString + ":" + RecoveryIDEeprom)
        print(serialControlObj.Test_Results)

        # Engaging the Adapter
        serialControlObj.Switch_ONN_Relay(1, 8)
        serialControlObj.wait(7)
        print("EEA Adapter Engaged to Power Pack Mechanically")

        RecoveryIdHighByte, RecoveryIdLowByte = GetAdapterOnewireRecoveryIdData(BlackBoxComPort)

        RecoveryIdOnewire = int((RecoveryIdLowByte, 16)) * 256 + int(RecoveryIdHighByte, 16)

        # Recovery State Verifying in the Adapter onewire and Capturing into the Test Results
        serialControlObj.Test_Results.append("5th to Last Byte : " + RecoveryIdHighByte)
        serialControlObj.Test_Results.append("4th to Last Byte : " + RecoveryIdLowByte)
        print(serialControlObj.Test_Results)

        if RecoveryIDEeprom == RecoveryIdOnewire:
            pass

        ## STEP 11: Re-Attaching the Adapter to the Power Pack
        my_Serthread.clearQue()
        serialControlObj.wait(5)
        serialControlObj.ConnectAdapter()
        print("Step: EEA Adapter Re-Connected")

        serialControlObj.wait(40)

        Timestamps, Strings_from_PowerPack = ReadQue(1000, my_Serthread.readQue)
        serialControl.convertListtoLogFile(Strings_from_PowerPack, str(videoPath + '\\TotalLog.txt'), fileOpenMode='a')
        Strings_to_Compare = locateStringsToCompareFromEvent('EEA Adapter Re-Connected After Stapling In Progress')
        result = Compare('EEA Adapter Re-Connected After Stapling In Progress', Strings_to_Compare,
                         Strings_from_PowerPack)
        serialControlObj.Test_Results.append('EEA Adapter Re-Connected After Stapling In Progress:' + result)
        print(serialControlObj.Test_Results)

        ## STEP 11: Performing Rotation, Articulation and Close Operation
        my_Serthread.clearQue()

        # Right CW Rotation
        serialControlObj.Switch_ONN_Relay(2, 7)  # B2:R7 - ON
        serialControlObj.wait(5)
        serialControlObj.Switch_OFF_Relay(2, 7)  # B2:R7 - OFF

        # Left Articulation
        my_Serthread.clearQue()
        serialControlObj.wait(5)
        serialControlObj.Switch_ONN_Relay(2, 3)  # B2:R3 - ON
        serialControlObj.wait(7)
        serialControlObj.Switch_OFF_Relay(2, 3)  # B2:R3 - OFF

        # Close Key Operation
        my_Serthread.clearQue()
        serialControlObj.wait(5)
        serialControlObj.Switch_ONN_Relay(2, 5)  # B2:R5 - ON
        serialControlObj.wait(10)
        serialControlObj.Switch_OFF_Relay(2, 5)  # B2:R5 - OFF

        Timestamps, Strings_from_PowerPack = ReadQue(1000, my_Serthread.readQue)
        serialControl.convertListtoLogFile(Strings_from_PowerPack, str(videoPath + '\\TotalLog.txt'),
                                           fileOpenMode='a')
        Strings_to_Compare = locateStringsToCompareFromEvent('Rotation & Articulation & Close Operation During SP IP')
        result = Compare('Rotation & Articulation & Close Operation During SP IP', Strings_to_Compare,
                         Strings_from_PowerPack)
        serialControlObj.Test_Results.append('Rotation & Articulation & Close Operation During SP IP:' + result)
        print(serialControlObj.Test_Results)

        ## STEP 12: Holding Rotation Buttons
        serialControlObj.Switch_ONN_Relay(2, 1)  # B2:R7 - ON
        serialControlObj.Switch_ONN_Relay(2, 2)  # B2:R8 - ON
        serialControlObj.Switch_ONN_Relay(2, 7)  # B2:R1 - ON
        serialControlObj.Switch_ONN_Relay(2, 8)  # B2:R2 - ON

        serialControlObj.wait(4)

        serialControlObj.Switch_OFF_Relay(2, 8)  # B2:R7 - OFF
        serialControlObj.Switch_OFF_Relay(2, 7)  # B2:R8 - OFF
        serialControlObj.Switch_OFF_Relay(2, 2)  # B2:R1 - OFF
        serialControlObj.Switch_OFF_Relay(2, 1)  # B2:R2 - OFF

        Timestamps, Strings_from_PowerPack = ReadQue(1000, my_Serthread.readQue)
        serialControl.convertListtoLogFile(Strings_from_PowerPack, str(videoPath + '\\TotalLog.txt'), fileOpenMode='a')
        Strings_to_Compare = locateStringsToCompareFromEvent('Rotation Operation During SP IP')
        result = Compare('Rotation Operation During SP IP', Strings_to_Compare, Strings_from_PowerPack)
        serialControlObj.Test_Results.append('Rotation Operation During SP IP:' + result)
        print("Step: Rotation Operation During SP IP")
        print(serialControlObj.Test_Results)

        ## STEP 13: Staples Detected Exit State - Fully open position
        my_Serthread.clearQue()
        serialControlObj.wait(5)

        # Handling here, No staples detected State Exit, Full Open position, SSE.
        serialControlObj.EEANoStaplesDetectedStateExit()

        Timestamps, Strings_from_PowerPack = ReadQue(1000, my_Serthread.readQue)
        serialControl.convertListtoLogFile(Strings_from_PowerPack, str(videoPath + '\\TotalLog.txt'), fileOpenMode='a')
        Strings_to_Compare = locateStringsToCompareFromEvent('No Staples Detected State Exit')
        result = Compare('No Staples Detected State Exit', Strings_to_Compare, Strings_from_PowerPack)
        serialControlObj.Test_Results.append('No Staples Detected State Exit:' + result)
        print("No Staples Detected State Exit")
        print(serialControlObj.Test_Results)

        ## STEP 14: Remove Reload
        my_Serthread.clearQue()
        serialControlObj.wait(5)
        serialControlObj.DisconnectingEEAReload()

        Timestamps, Strings_from_PowerPack = ReadQue(1000, my_Serthread.readQue)
        serialControl.convertListtoLogFile(Strings_from_PowerPack, str(videoPath + '\\TotalLog.txt'), fileOpenMode='a')
        Strings_to_Compare = locateStringsToCompareFromEvent('EEA Remove Reload Enter SSE')
        result = Compare('EEA Remove Reload Enter SSE', Strings_to_Compare, Strings_from_PowerPack)
        serialControlObj.Tilt_Recovery_items_Test_Results.append('EEA Remove Reload Enter SSE:' + result)
        print("EEA Remove Reload Enter SSE")
        print(serialControlObj.Tilt_Recovery_items_Test_Results)

        ## STEP 15: Surgical Site Extraction (SSE)
        my_Serthread.clearQue()
        serialControlObj.wait(5)

        # Surgical Site Extraction Exit
        serialControlObj.EEASurgicalSiteExtractionStateExit()

        Timestamps, Strings_from_PowerPack = ReadQue(1000, my_Serthread.readQue)
        serialControl.convertListtoLogFile(Strings_from_PowerPack, str(videoPath + '\\TotalLog.txt'), fileOpenMode='a')
        Strings_to_Compare = locateStringsToCompareFromEvent('SSE Exit')
        result = Compare('SSE Exit', Strings_to_Compare, Strings_from_PowerPack)
        serialControlObj.Test_Results.append('SSE Exit:' + result)
        print("Step:SSE Exit")
        print(serialControlObj.Test_Results)

        ## STEP 16: Remove Adapter
        my_Serthread.clearQue()
        serialControlObj.wait(5)
        serialControlObj.removeAdapter()
        serialControlObj.Switch_OFF_Relay(1, 8) # Dis Engaging the Adapter Clutch

        Timestamps, Strings_from_PowerPack = ReadQue(1000, my_Serthread.readQue)
        serialControl.convertListtoLogFile(Strings_from_PowerPack, str(videoPath + '\\TotalLog.txt'), fileOpenMode='a')
        Strings_to_Compare = locateStringsToCompareFromEvent('Remove EEA Adapter')
        result = Compare('Remove EEA Adapter', Strings_to_Compare, Strings_from_PowerPack)
        serialControlObj.Test_Results.append('Remove EEA Adapter:' + result)
        print("Remove EEA Adapter")
        print(serialControlObj.Test_Results)

        ## STEP 17: Record Adapter usage Counts - Adapter Firing and Procedure Count Incremented by 1
        # For capturing Adapter Usage Counts - Adapter needs to be connected Mechanically
        # Engaging the Adapter - Controlling the stepper motor
        serialControlObj.Switch_ONN_Relay(1, 8)
        serialControlObj.wait(7)
        print("EEA Adapter Engaged to Power Pack Mechanically")

        MCPThread.readingPowerPack.exitFlag = True
        serPP.close()
        serialControlObj.wait(2)

        # Reading Adapter EEPROM Usage Counts
        AdapterEeProcedureCount, AdapterEeFireCount = GetAdapterEepromUsageCounts(FtdiUartComPort)

        # For capturing Onewire Usage counts from the Adapter via BB, below relays should be ON.
        serialControlObj.Switch_ONN_Relay(5, 8)  # B5:R8 - ON
        serialControlObj.Switch_ONN_Relay(6, 1)  # B6:R1 - ON

        # Reading Adapter One-Wire usage Counts
        AdapterOwProcedureCount, AdapterOwFireCount = GetAdapterOnewireUsageCounts(BlackBoxComPort)

        serialControlObj.Switch_OFF_Relay(6, 1)  # B6:R1 - OFF
        serialControlObj.Switch_OFF_Relay(5, 8)  # B5:R8 - OFF

        print('Adapter Eeprom Fire Count:' + str(AdapterEeFireCount),
              'Adapter Eeprom Procedure Count:' + str(AdapterEeProcedureCount))
        print('Adapter Onewire Fire Count:' + str(AdapterOwFireCount),
              'Adapter Onewire Procedure Count:' + str(AdapterOwProcedureCount))

        ## STEP 28: DisEngage the Adapter Clutch
        serialControlObj.Switch_OFF_Relay(1, 8)
        print('Adapter Clutch Disengaged')

        ## STEP 25: Remove Clamshell
        my_Serthread.clearQue()
        serialControlObj.Switch_OFF_Relay(1, 5)
        serialControlObj.wait(5)
        Timestamps, Strings_from_PowerPack = ReadQue(100, my_Serthread.readQue)
        serialControl.convertListtoLogFile(Strings_from_PowerPack, str(videoPath + '\\TotalLog.txt'), fileOpenMode='a')
        Strings_to_Compare = locateStringsToCompareFromEvent('Remove Clamshell')
        result = Compare('Remove Clamshell', Strings_to_Compare, Strings_from_PowerPack)
        serialControlObj.Test_Results.append('Remove Clamshell:' + result)
        print("Step: Removed Clamshell")
        print(serialControlObj.Test_Results)
        serialControlObj.wait(2)

        for item in serialControlObj.Test_Results:
            # print(item)
            temp2 = 'PASS'
            try:
                if (((str.split(item, ':', 1))[1]) == 'PASS'):
                    # serialControlObj.Test_Results.append(serialControlObj.Tilt_Recovery_items_Test_Results[0] + ':FAIL')
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

        my_Serthread.clearQue()
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

        ## STEP 26: Placing Power pack on the Charger
        serialControlObj.PlacingPowerPackOnCharger()
        print('Power Pack Placed on Charger')
        print('------------------- End of Test Scenario --------------')
        serialControlObj.wait(30)
        print('------------------- EEA Firing Recovery Requirements Case 1 End --------------')

##################################################################################################################################################

def T106_FireRetract_TiltAndFiringRetractionRecoveryAndLockup(r, SULU_EEPROM_command_byte, MULU_EEPROM_command_byte,
                                      CARTRIDGE_EEPROM_command_byte, NCDComPort, PowerPackComPort, BlackBoxComPort, USB6351ComPort, ArduinoUNOComPort,
                                      FtdiUartComPort, OUTPUT_PATH, videoPath, p,
                                      EEA_RELOAD_EEPROM_command_byte):

    # print('Recovery Items verification ', r, SULU_EEPROM_command_byte, MULU_EEPROM_command_byte, CARTRIDGE_EEPROM_command_byte, i)
    NCDComPort = NCDComPort
    print(NCDComPort, 'NCD COM Port')
    print("-----------------EEA Tilt And Firing Retraction Recovery And Lockup Case 2 -------------------")
    serialControlObj = serialControl(r, SULU_EEPROM_command_byte, MULU_EEPROM_command_byte,
                                     CARTRIDGE_EEPROM_command_byte, NCDComPort, PowerPackComPort, BlackBoxComPort,
                                     USB6351ComPort, ArduinoUNOComPort, FtdiUartComPort, OUTPUT_PATH, videoPath,
                                     EEA_RELOAD_EEPROM_command_byte)
    serialControlObj.OpenSerialConnection()
    T106_Fire_Retract_TiltAndFiringRetractionRecoveryAndLockup(serialControlObj, EEA_RELOAD_EEPROM_command_byte, NCDComPort,
                                                     PowerPackComPort, BlackBoxComPort, USB6351ComPort, ArduinoUNOComPort,
                                                     FtdiUartComPort, OUTPUT_PATH, videoPath, p)
    serialControlObj.disconnectSerialConnection()


def T106_Fire_Retract_TiltAndFiringRetractionRecoveryAndLockup(serialControlObj, EEA_RELOAD_EEPROM_command_byte, NCDComPort,
                                          PowerPackComPort, BlackBoxComPort, USB6351ComPort, ArduinoUNOComPort,
                                          FtdiUartComPort, OUTPUT_PATH, videoPath, p):


    PowerPackComPort = PowerPackComPort
    EEA_RELOAD_EEPROM_command_byte = EEA_RELOAD_EEPROM_command_byte
    ArduinoUNOComPort = ArduinoUNOComPort
    NCDComPort = NCDComPort
    FtdiUartComPort = FtdiUartComPort
    print(NCDComPort)
    iterPass = 0
    firePass = 0
    TestBatteryLevelMax = serialControlObj.r['Battery RSOC Max Level']
    TestBatteryLevelMin = serialControlObj.r['Battery RSOC Min Level']
    clampingForce = serialControlObj.r['Clamping Force']
    firingForce = serialControlObj.r['Firing Force']
    numberOfFiringsinProcedure = serialControlObj.r['Num of Firings in Procedure']

    print(TestBatteryLevelMax, TestBatteryLevelMin, clampingForce, firingForce, numberOfFiringsinProcedure)

    with nidaqmx.Task() as task:
        task.ao_channels.add_ao_voltage_chan('Dev1/ao0')
        print('1 Channel 1 Sample Write: ')
        print(task.write(0.0))

    # Pre-conditioning:
    ## Remove handle form charger
    serialControlObj.send_decimal_bytes(TURN_OFF_ALL_RELAYS_IN_ALL_BANKS[0])
    serialControlObj.wait(0.5)
    serialControlObj.Switch_ONN_Relay(3, 8)

    serialControlObj.wait(0.5)
    serialControlObj.Switch_ONN_Relay(3, 7)

    serialControlObj.wait(60)

    serialControlObj.send_decimal_bytes(TURN_OFF_ALL_RELAYS_IN_ALL_BANKS[0])
    print("Step: Remove Signia Power Handle from Charger")
    serialControlObj.wait(40)

    ## By Reset Clamshell - Clamshell Connecting
    ###################################  RESETTING CLAMSHELL   #############################################################################

    byte_data = [2, 3, 4, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    crc_value = CRC16(0x00, byte_data)
    crc_value = hex(crc_value)
    print('Original CRC: ', crc_value)
    l = len(crc_value)
    crc_second_byte = crc_value[2:(l - 2)]
    crc_first_byte = crc_value[(l - 2):]
    byte_data.append(int(crc_first_byte, 16))
    byte_data.append(int(crc_second_byte, 16))
    ###################################### CLAMSHELL PACKET FRAMING #########################################################################
    byte_lst = [170, 69, 2, 1] + byte_data
    crc_value = calc(bytes(byte_lst))
    crc_value = int(crc_value, 16)
    byte_lst.append(crc_value)
    command_byte = byte_lst
    serialControlObj.Switch_ONN_Relay(5, 1)  # B5:R1 - ON
    serialControlObj.Switch_ONN_Relay(5, 5)  # B5:R1 - ON
    ser = serial.Serial(serialControlObj.BlackBoxComPort, 9600)
    serialControlObj.wait(5)
    ############# READ ###################
    command = bytes(command_byte)
    print('Clamshell ResetByte array', command)
    ser.write(command)
    serialControlObj.wait(3)
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

    ## Checking Battery RSOC Desired Values
    if read_battery_RSOC(25, PowerPackComPort) > TestBatteryLevelMax:  # and (read_battery_RSOC(25, PowerPackComPort) > TestBatteryLevelMin):
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

        while (read_battery_RSOC(25,PowerPackComPort)) > TestBatteryLevelMax:  # and (read_battery_RSOC(25, PowerPackComPort) > TestBatteryLevelMin):
            serialControlObj.Switch_ONN_Relay(2,5)  # B2:R5 - ON -- some operations' battery discharge Check if loaded condition of trocar can be explored for quick discharge
            serialControlObj.wait(7)
            serialControlObj.Switch_OFF_Relay(2, 5)  # B2:R5 - ON
            serialControlObj.Switch_ONN_Relay(2, 4)  # B2:R5 - ON
            serialControlObj.wait(7)
            serialControlObj.Switch_OFF_Relay(2, 4)  # B2:R5 - ON

        serialControlObj.DisconnectingEEAReload()
        serialControlObj.Switch_OFF_ALL_Relays_In_Each_Bank(1)  # Disconnected the clamshell
        serialControlObj.wait(10)
    if read_battery_RSOC(25,
                         PowerPackComPort) < TestBatteryLevelMin:  # and (read_battery_RSOC(25, PowerPackComPort) <= TestBatteryLevelMax):
        # print('entered elif loop')
        serialControlObj.Switch_ONN_Relay(3, 7)  # battery charge
        serialControlObj.wait(0.5)
        serialControlObj.Switch_ONN_Relay(3, 8)
        # need to optimize this delay so that handle does not go to sleep or does not result communication
        serialControlObj.wait(5)
        while (read_battery_RSOC(50,
                                 PowerPackComPort) < TestBatteryLevelMin):  # and (read_battery_RSOC(25, PowerPackComPort) <= TestBatteryLevelMax):
            pass

    serialControlObj.wait(20)
    '''
    ###################################################################################################################
    ## CASE 2: Cutting Recovery
    ###################################################################################################################
    '''
    ## STEP 1: Removing Handle From The Charger
    print("----------Placing Power Pack on Charger for startup Test--------------")
    serialControlObj.Switch_ONN_Relay(3, 7)
    serialControlObj.wait(.2)
    serialControlObj.Switch_ONN_Relay(3, 8)
    serialControlObj.wait(60)
    print("----------Removing Power Pack from Charger for startup Test--------------")
    serialControlObj.Switch_OFF_Relay(3, 7)
    serialControlObj.wait(.2)
    serialControlObj.Switch_OFF_Relay(3, 8)

    ## Once removing from the charger, searching for the comports
    while True:
        signiaPowerFound = False
        if any("SigniaPowerHandle" in s for s in serial.tools.list_ports.comports()):
            signiaPowerFound = True
        else:
            print('Signia Com Port Closed')
            signiaPowerFound = False
            break

    strPort = 'None'
    # Signia Comport Available
    while not 'SigniaPowerHandle' in strPort:
        ports = serial.tools.list_ports.comports()
        # strPort = 'None'
        numConnection = len(ports)
        for i in range(0, numConnection):
            port = ports[i]
            strPort = str(port)
            if 'SigniaPowerHandle' in strPort:
                print(ports[i], 'Available')
                break

    serialControlObj.wait(5)

    # Once Signia Comport Available, Opening the Port
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
        except:
            pass

    serialControlObj.Test_Results.append(
        str(serialControlObj.r['Scenario Num']) + '#' + str(p + 1) + "@" + serialControlObj.r['Test Scenario'])

    serialControlObj.wait(60)
    searchFlag = True

    Timestamps, Strings_from_PowerPack, data_path = ReadQue(1000, my_Serthread.readQue, searchFlag)
    serialControl.convertListtoLogFile(Strings_from_PowerPack, (videoPath + '\StartUpLog.txt'), fileOpenMode='w')
    serialControl.convertListtoLogFile(Strings_from_PowerPack, 'TotalLog.txt', fileOpenMode='a')
    Strings_to_Compare = locateStringsToCompareFromEvent('Remove Signia Power Handle from Charger')

    result = Compare('Remove Signia Power Handle from Charger', Strings_to_Compare, Strings_from_PowerPack)
    data_path = "None" if not data_path else data_path
    serialControlObj.Test_Results.append('Eventlog:' + data_path)
    serialControlObj.Test_Results.append('Remove Signia Power Handle from Charger:' + result)

    ## STEP 2: Clamshell Connected
    # Turning ON Clamshell One Wire
    serialControlObj.connectClamshell()
    print("Step: Clamshell Connected")

    serialControlObj.wait(5)

    Timestamps, Strings_from_PowerPack = ReadQue(200, my_Serthread.readQue)
    serialControl.convertListtoLogFile(Strings_from_PowerPack, str(videoPath + '\\TotalLog.txt'), fileOpenMode='a')
    Strings_to_Compare = locateStringsToCompareFromEvent('Clamshell Connected')
    result = Compare('Clamshell Connected', Strings_to_Compare, Strings_from_PowerPack)

    # Capturing Clamshell connected data into the Test Results
    serialControlObj.Test_Results.append('Connected Clamshell:' + result)
    print(serialControlObj.Test_Results)

    ## STEP 3: Record Power Pack and Adapter usage Counts
    # For capturing Adapter Usage Counts - Adapter needs to be connected Mechanically
    # Engaging the Adapter - Controlling the stepper motor
    serialControlObj.Switch_ONN_Relay(1, 8)
    serialControlObj.wait(7)
    print("EEA Adapter Engaged to Power Pack Mechanically")

    MCPThread.readingPowerPack.exitFlag = True
    serPP.close()
    serialControlObj.wait(2)

    # Reading Power Pack Usage Counts
    HandleFireCount, HandleProcedureCount = GetHandleUseCount(PowerPackComPort)

    # Reading Adapter EEPROM Usage Counts
    AdapterEeProcedureCount, AdapterEeFireCount = GetAdapterEepromUsageCounts(FtdiUartComPort)

    # For capturing Onewire Usage counts from the Adapter via BB, below relays should be ON.
    serialControlObj.Switch_ONN_Relay(5, 8) # B5:R8 - ON
    serialControlObj.Switch_ONN_Relay(6, 1) # B6:R1 - ON

    # Reading Adapter One-Wire usage Counts
    AdapterOwProcedureCount, AdapterOwFireCount = GetAdapterOnewireUsageCounts(BlackBoxComPort)

    serialControlObj.Switch_OFF_Relay(6, 1)  # B6:R1 - OFF
    serialControlObj.Switch_OFF_Relay(5, 8)  # B5:R8 - OFF

    print('Before Firing Handle Fire Count:' + str(HandleFireCount),
          'Handle Procedure Count:' + str(HandleProcedureCount))
    print('Before Firing Adapter Eeprom Fire Count:' + str(AdapterEeFireCount),
          'Adapter Eeprom Procedure Count:' + str(AdapterEeProcedureCount))
    print('Before Firing Adapter Onewire Fire Count:' + str(AdapterOwFireCount),
          'Adapter Onewire Procedure Count:' + str(AdapterOwProcedureCount))

    # Re-Opening the PowerPackComPort
    serPP = serial.Serial(serialControlObj.PowerPackComPort, 115200, bytesize=8, parity='N', stopbits=1,
                          timeout=0.05, xonxoff=0)
    MCPThread.readingPowerPack.exitFlag = False
    my_Serthread = MCPThread.readingPowerPack(serPP, 1000)
    my_Serthread.clearQue()
    my_Serthread.start()

    ## STEP 4: Adapter Connected With INIT State.
    my_Serthread.clearQue()
    serialControlObj.wait(5)
    serialControlObj.Switch_ONN_ALL_Relays_In_Each_Bank(1)  # B1 - ALL ON
    print("Step: EEA Adapter Connected")

    serialControlObj.wait(40)

    Timestamps, Strings_from_PowerPack = ReadQue(1000, my_Serthread.readQue)
    serialControl.convertListtoLogFile(Strings_from_PowerPack, str(videoPath + '\\TotalLog.txt'), fileOpenMode='a')
    Strings_to_Compare = locateStringsToCompareFromEvent('EEA Adapter Connected')
    result = Compare('EEA Adapter Connected', Strings_to_Compare, Strings_from_PowerPack)
    serialControlObj.Test_Results.append('EEA Adapter Connected:' + result)
    print(serialControlObj.Test_Results)

    my_Serthread.clearQue()
    serialControlObj.wait(5)

    # For Integrated Trocar this step would be -   Range Sensor to Force Compensate
    # For Non-Integrated Trocar this step would be - TPD ( Tip Protect Detection )
    serRangeSensor = serial.Serial(serialControlObj.ArduinoUNOComPort, 115200)
    serRangeSensor.flushOutput()
    serRangeSensor.flush()
    serRangeSensor.flushInput()

    # Record system Status variables Before Firing
    serialControlObj.wait(2)
    StatusVariables1 = ReadStatusVariables(PowerPackComPort)
    StatusVariables1 = StatusVariables1[13:61]
    StatusVariables1 = StatusVariables1[4:8] + StatusVariables1[12:16] + StatusVariables1[20:24] + StatusVariables1[
                                                                                                   28:32] + StatusVariables1[
                                                                                                            36:40] + StatusVariables1[
                                                                                                                     44:48]
    print('Before Firing Status Variables: ', StatusVariables1)

    # Creating Test Results Array to capture the Multiple Events During Firing ( Reload Connected, Green Key ACK, Trocar, Anvil, Firing Status )
    serialControlObj.Tilt_Recovery_items_Test_Results = []
    serialControlObj.Tilt_Recovery_items_Test_Results.append('Firing =' + str(1))
    OLEDRecordingThread.exitFlag = False

    ## STEP 5: Connecting EEA Reload Along with Ship Cap Presence Check
    if serialControlObj.r['Reload Type'] == "EEA":
        videoThread = OLEDRecordingThread.myThread(
            (str(serialControlObj.r['Scenario Num']) + '#' + str(p + 1) + serialControlObj.r['Test Scenario'] + '_' +
             serialControlObj.r['Reload Type'] + '_' + str(1)),
            serialControlObj.videoPath)
        videoThread.start()
        serialControlObj.Switch_ONN_Relay(5, 2)  # B5:R2 - ON
        serialControlObj.Switch_ONN_Relay(5, 6)  # B5:R6 - ON
        serialControlObj.wait(5)
        ser = serial.Serial(serialControlObj.BlackBoxComPort, 9600)
        ############# READ ###################
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

        # Turning ON EEA Reload One Wire
        my_Serthread.clearQue()
        serialControlObj.wait(5)
        serialControlObj.ConnectingEEAReload()
        serialControlObj.wait(10)
        Timestamps, Strings_from_PowerPack = ReadQue(1000, my_Serthread.readQue)
        serialControl.convertListtoLogFile(Strings_from_PowerPack, str(videoPath + '\\TotalLog.txt'), fileOpenMode='a')

        # Ship Cap Presence check
        if serialControlObj.r['Ship cap Present'] == "Yes":
            Strings_to_Compare = locateStringsToCompareFromEvent('EEA RELOAD Connected with Ship cap',
                                                                 Length=serialControlObj.r.get('Reload Diameter(mm)'),
                                                                 Color=serialControlObj.r.get('Reload Color'))
            result = Compare('EEA RELOAD Connected', Strings_to_Compare, Strings_from_PowerPack)
            serialControlObj.Tilt_Recovery_items_Test_Results.append('EEA RELOAD Connected:' + result)
        elif serialControlObj.r['Ship cap Present'] == "No":
            Strings_to_Compare = locateStringsToCompareFromEvent('EEA RELOAD Connected without Ship cap',
                                                                 Length=serialControlObj.r.get('Reload Diameter(mm)'),
                                                                 Color=serialControlObj.r.get('Reload Color'))
            result = Compare('EEA RELOAD Connected', Strings_to_Compare, Strings_from_PowerPack)
            serialControlObj.Tilt_Recovery_items_Test_Results.append('EEA RELOAD Connected:' + result)

        print("Step: EEA Reload Connected")
        print(serialControlObj.Tilt_Recovery_items_Test_Results)
        serialControlObj.wait(3)

        ## STEP 6: Extention of Trocar
        my_Serthread.clearQue()
        serialControlObj.wait(5)
        serialControlObj.Switch_ONN_Relay(2, 4)  # B2:R5 - ON
        serialControlObj.wait(10)
        serialControlObj.Switch_OFF_Relay(2, 4)  # B2:R5 - OFF

        Timestamps, Strings_from_PowerPack = ReadQue(1000, my_Serthread.readQue)
        serialControl.convertListtoLogFile(Strings_from_PowerPack, str(videoPath + '\\TotalLog.txt'), fileOpenMode='a')
        Strings_to_Compare = locateStringsToCompareFromEvent('EEA Trocar Extention with Reload')
        result = Compare('EEA Trocar Extention with Reload', Strings_to_Compare, Strings_from_PowerPack)
        serialControlObj.Test_Results.append('EEA Trocar Extention with Reload:' + result)

        ## STEP 7: Clamping on Tissue - Retraction of Trocar Until Clamp GAP is reached
        my_Serthread.clearQue()
        serialControlObj.wait(5)
        cf = serialControlObj.EEAForceDecode(clampingForce)
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

        serialControlObj.wait(25)  # waiting time for clamping on tissue Manoj Vadali need to update based on tissue thichkness pls check?

        Timestamps, Strings_from_PowerPack = ReadQue(1000, my_Serthread.readQue)
        serialControl.convertListtoLogFile(Strings_from_PowerPack, str(videoPath + '\\TotalLog.txt'), fileOpenMode='a')
        Strings_to_Compare = locateStringsToCompareFromEvent('EEA Clamping on Tissue')
        result = Compare('EEA Clamping on Tissue', Strings_to_Compare, Strings_from_PowerPack)
        serialControlObj.Test_Results.append('EEA Clamping on Tissue:' + result)
        print("Step: EEA Clamping on Tissue")
        print(serialControlObj.Tilt_Recovery_items_Test_Results)

        my_Serthread.clearQue()
        serialControlObj.wait(5)
        serialControlObj.Switch_OFF_Relay(2, 5)  # B2:R5 - OFF

        ## STEP 8: Safety Key Acknowledgement
        serialControlObj.GreenKeyAck()
        serialControlObj.wait(2)
        Timestamps, Strings_from_PowerPack = ReadQue(200, my_Serthread.readQue)
        serialControl.convertListtoLogFile(Strings_from_PowerPack, str(videoPath + '\\TotalLog.txt'), fileOpenMode='a')
        Strings_to_Compare = locateStringsToCompareFromEvent('EEA Green Key Ack')
        result = Compare('EEA Green Key Ack', Strings_to_Compare, Strings_from_PowerPack)
        serialControlObj.Tilt_Recovery_items_Test_Results.append('EEA Green Key Ack:' + result)
        print("Step: Acknowledged Safety Key (Green LED) for firing")
        print(serialControlObj.Tilt_Recovery_items_Test_Results)

        ## STEP 9: Firing
        # ff = serialControlObj.EEAForceDecode(firingForce)
        with nidaqmx.Task() as task:
            task.ao_channels.add_ao_voltage_chan('Dev1/ao0')
            print('1 Channel 1 Sample Write: ')
            print(task.write(3.25))

        my_Serthread.clearQue()
        serialControlObj.wait(5)
        serialControlObj.Switch_ONN_Relay(4, 1)
        serialControlObj.Switch_ONN_Relay(4, 2)  # To turn on Linear actuator
        serialControlObj.wait(3)
        serialControlObj.Switch_ONN_Relay(2, 5)  # B2:R5 - ON
        serialControlObj.wait(0.5)
        serialControlObj.Switch_OFF_Relay(2, 5)  # B2:R5 - OFF
        serialControlObj.wait(4)

        serialControlObj.Switch_OFF_Relay(4, 1)
        serialControlObj.Switch_OFF_Relay(4, 2)  # To turn on Linear actuator
        serialControlObj.wait(1)
        with nidaqmx.Task() as task:
            task.ao_channels.add_ao_voltage_chan('Dev1/ao0')
            print('1 Channel 1 Sample Write: ')
            print(task.write(0))

        serialControlObj.Switch_ONN_Relay(4, 3)
        serialControlObj.Switch_ONN_Relay(4, 4)  # To turn on Linear actuator at full power

        # Remove Adapter when Cutting Starts
        serialControlObj.Switch_OFF_Relay(1, 8)  # B1:R8 - Turning Off - Adapter Clutch Disengaged
        serialControlObj.removeAdapter()
        serialControlObj.wait(5)

        serialControlObj.Switch_OFF_Relay(4, 3)
        serialControlObj.Switch_OFF_Relay(4, 4)  # To turn on Linear actuator at full power
        serialControlObj.wait(.5)  # need to optimize based on firing duration
        serialControlObj.Switch_ONN_Relay(4, 5)
        serialControlObj.Switch_ONN_Relay(4, 6)  # To turn on Linear actuator at full power
        serialControlObj.wait(30)  # need to optimize based on firing duration

        Timestamps, Strings_from_PowerPack = ReadQue(1000, my_Serthread.readQue)
        serialControl.convertListtoLogFile(Strings_from_PowerPack, str(videoPath + '\\TotalLog.txt'),
                                           fileOpenMode='a')

        Strings_to_Compare = locateStringsToCompareFromEvent('Remove Adapter When Cutting Starts')
        result = Compare('Remove Adapter When Cutting Starts', Strings_to_Compare, Strings_from_PowerPack)
        serialControlObj.Tilt_Recovery_items_Test_Results.append('Remove Adapter When Cutting Starts:' + result)
        print("Step:Remove Adapter When Cutting Starts")
        print(serialControlObj.Tilt_Recovery_items_Test_Results)
        serialControlObj.wait(7)

    ## STEP 10: Re-Attaching the Adapter to the Power Pack
    my_Serthread.clearQue()
    serialControlObj.wait(5)
    serialControlObj.ConnectAdapter()
    print("Step: EEA Adapter Re-Connected")

    serialControlObj.wait(40)

    Timestamps, Strings_from_PowerPack = ReadQue(1000, my_Serthread.readQue)
    serialControl.convertListtoLogFile(Strings_from_PowerPack, str(videoPath + '\\TotalLog.txt'), fileOpenMode='a')
    Strings_to_Compare = locateStringsToCompareFromEvent('EEA Adapter Re-Connected After Stapling In Progress')
    result = Compare('EEA Adapter Re-Connected After Stapling In Progress', Strings_to_Compare, Strings_from_PowerPack)
    serialControlObj.Test_Results.append('EEA Adapter Re-Connected After Stapling In Progress:' + result)
    print(serialControlObj.Test_Results)

    ## STEP 11: Performing Rotation, Articulation and Close Operation
    my_Serthread.clearQue()

    # Right CW Rotation
    serialControlObj.Switch_ONN_Relay(2, 7)  # B2:R7 - ON
    serialControlObj.wait(5)
    serialControlObj.Switch_OFF_Relay(2, 7)  # B2:R7 - OFF

    # Left Articulation
    my_Serthread.clearQue()
    serialControlObj.wait(5)
    serialControlObj.Switch_ONN_Relay(2, 3)  # B2:R3 - ON
    serialControlObj.wait(7)
    serialControlObj.Switch_OFF_Relay(2, 3)  # B2:R3 - OFF

    # Close Key Operation
    my_Serthread.clearQue()
    serialControlObj.wait(5)
    serialControlObj.Switch_ONN_Relay(2, 5)  # B2:R5 - ON
    serialControlObj.wait(10)
    serialControlObj.Switch_OFF_Relay(2, 5)  # B2:R5 - OFF

    Timestamps, Strings_from_PowerPack = ReadQue(1000, my_Serthread.readQue)
    serialControl.convertListtoLogFile(Strings_from_PowerPack, str(videoPath + '\\TotalLog.txt'),
                                       fileOpenMode='a')
    Strings_to_Compare = locateStringsToCompareFromEvent('Rotation & Articulation & Close Operation During SP IP')
    result = Compare('Rotation & Articulation & Close Operation During SP IP', Strings_to_Compare, Strings_from_PowerPack)
    serialControlObj.Test_Results.append('Rotation & Articulation & Close Operation During SP IP:' + result)
    print(serialControlObj.Test_Results)

    ## STEP 12: Holding Rotation Buttons
    serialControlObj.Switch_ONN_Relay(2, 1)  # B2:R7 - ON
    serialControlObj.Switch_ONN_Relay(2, 2)  # B2:R8 - ON
    serialControlObj.Switch_ONN_Relay(2, 7)  # B2:R1 - ON
    serialControlObj.Switch_ONN_Relay(2, 8)  # B2:R2 - ON

    serialControlObj.wait(4)

    serialControlObj.Switch_OFF_Relay(2, 8)  # B2:R7 - OFF
    serialControlObj.Switch_OFF_Relay(2, 7)  # B2:R8 - OFF
    serialControlObj.Switch_OFF_Relay(2, 2)  # B2:R1 - OFF
    serialControlObj.Switch_OFF_Relay(2, 1)  # B2:R2 - OFF

    Timestamps, Strings_from_PowerPack = ReadQue(1000, my_Serthread.readQue)
    serialControl.convertListtoLogFile(Strings_from_PowerPack, str(videoPath + '\\TotalLog.txt'), fileOpenMode='a')
    Strings_to_Compare = locateStringsToCompareFromEvent('Rotation Operation During SP IP')
    result = Compare('Rotation Operation During SP IP', Strings_to_Compare, Strings_from_PowerPack)
    serialControlObj.Test_Results.append('Rotation Operation During SP IP:' + result)
    print("Step: Rotation Operation During SP IP")
    print(serialControlObj.Test_Results)

    ## STEP 13: Staples Detected Exit State - Fully open position
    my_Serthread.clearQue()
    serialControlObj.wait(5)

    # Handling here, No staples detected State Exit, Full Open position, SSE.
    serialControlObj.EEANoStaplesDetectedStateExit()

    Timestamps, Strings_from_PowerPack = ReadQue(1000, my_Serthread.readQue)
    serialControl.convertListtoLogFile(Strings_from_PowerPack, str(videoPath + '\\TotalLog.txt'), fileOpenMode='a')
    Strings_to_Compare = locateStringsToCompareFromEvent('No Staples Detected State Exit')
    result = Compare('No Staples Detected State Exit', Strings_to_Compare, Strings_from_PowerPack)
    serialControlObj.Normal_Firing_Test_Results.append('No Staples Detected State Exit:' + result)
    print("No Staples Detected State Exit")
    print(serialControlObj.Normal_Firing_Test_Results)

    ## STEP 14: Remove Reload
    my_Serthread.clearQue()
    serialControlObj.wait(5)
    serialControlObj.DisconnectingEEAReload()

    Timestamps, Strings_from_PowerPack = ReadQue(1000, my_Serthread.readQue)
    serialControl.convertListtoLogFile(Strings_from_PowerPack, str(videoPath + '\\TotalLog.txt'), fileOpenMode='a')
    Strings_to_Compare = locateStringsToCompareFromEvent('EEA Remove Reload Enter SSE')
    result = Compare('EEA Remove Reload Enter SSE', Strings_to_Compare, Strings_from_PowerPack)
    serialControlObj.Normal_Firing_Test_Results.append('EEA Remove Reload Enter SSE:' + result)
    print("EEA Remove Reload Enter SSE")
    print(serialControlObj.Normal_Firing_Test_Results)

    ## STEP 15: Surgical Site Extraction (SSE)
    my_Serthread.clearQue()
    serialControlObj.wait(5)

    # Surgical Site Extraction Exit
    serialControlObj.EEASurgicalSiteExtractionStateExit()

    Timestamps, Strings_from_PowerPack = ReadQue(1000, my_Serthread.readQue)
    serialControl.convertListtoLogFile(Strings_from_PowerPack, str(videoPath + '\\TotalLog.txt'), fileOpenMode='a')
    Strings_to_Compare = locateStringsToCompareFromEvent('SSE Exit')
    result = Compare('SSE Exit', Strings_to_Compare, Strings_from_PowerPack)
    serialControlObj.Tilt_Recovery_items_Test_Results.append('SSE Exit:' + result)
    print("Step:SSE Exit")
    print(serialControlObj.Tilt_Recovery_items_Test_Results)

    ## STEP 16: Remove Adapter
    my_Serthread.clearQue()
    serialControlObj.wait(5)
    serialControlObj.DisconnectingEEAReload()

    Timestamps, Strings_from_PowerPack = ReadQue(1000, my_Serthread.readQue)
    serialControl.convertListtoLogFile(Strings_from_PowerPack, str(videoPath + '\\TotalLog.txt'), fileOpenMode='a')
    Strings_to_Compare = locateStringsToCompareFromEvent('Remove EEA Adapter')
    result = Compare('Remove EEA Adapter', Strings_to_Compare, Strings_from_PowerPack)
    serialControlObj.Normal_Firing_Test_Results.append('Remove EEA Adapter:' + result)
    print("Remove EEA Adapter")
    print(serialControlObj.Normal_Firing_Test_Results)

    ## STEP 16: Record Adapter usage Counts - Adapter Firing and Procedure Count Incremented by 1
    # For capturing Adapter Usage Counts - Adapter needs to be connected Mechanically
    # Engaging the Adapter - Controlling the stepper motor
    serialControlObj.Switch_ONN_Relay(1, 8)
    serialControlObj.wait(7)
    print("EEA Adapter Engaged to Power Pack Mechanically")

    MCPThread.readingPowerPack.exitFlag = True
    serPP.close()
    serialControlObj.wait(2)

    # Reading Adapter EEPROM Usage Counts
    AdapterEeProcedureCount, AdapterEeFireCount = GetAdapterEepromUsageCounts(FtdiUartComPort)

    # For capturing Onewire Usage counts from the Adapter via BB, below relays should be ON.
    serialControlObj.Switch_ONN_Relay(5, 8)  # B5:R8 - ON
    serialControlObj.Switch_ONN_Relay(6, 1)  # B6:R1 - ON

    # Reading Adapter One-Wire usage Counts
    AdapterOwProcedureCount, AdapterOwFireCount = GetAdapterOnewireUsageCounts(BlackBoxComPort)

    serialControlObj.Switch_OFF_Relay(6, 1)  # B6:R1 - OFF
    serialControlObj.Switch_OFF_Relay(5, 8)  # B5:R8 - OFF

    print('Adapter Eeprom Fire Count:' + str(AdapterEeFireCount),
          'Adapter Eeprom Procedure Count:' + str(AdapterEeProcedureCount))
    print('Adapter Onewire Fire Count:' + str(AdapterOwFireCount),
          'Adapter Onewire Procedure Count:' + str(AdapterOwProcedureCount))

    serPP = serial.Serial(serialControlObj.PowerPackComPort, 115200, bytesize=8, parity='N', stopbits=1,
                          timeout=0.05, xonxoff=0)
    MCPThread.readingPowerPack.exitFlag = False
    my_Serthread = MCPThread.readingPowerPack(serPP, 1000)
    my_Serthread.clearQue()
    my_Serthread.start()

    ## STEP 14: Re-Connecting the adapter with INIT State
    my_Serthread.clearQue()
    serialControlObj.wait(5)
    serialControlObj.Switch_ONN_ALL_Relays_In_Each_Bank(1)  # B1 - ALL ON
    print("Step: EEA Adapter Connected")

    serialControlObj.wait(40)

    Timestamps, Strings_from_PowerPack = ReadQue(1000, my_Serthread.readQue)
    serialControl.convertListtoLogFile(Strings_from_PowerPack, str(videoPath + '\\TotalLog.txt'), fileOpenMode='a')
    Strings_to_Compare = locateStringsToCompareFromEvent('EEA Adapter Connected')
    result = Compare('EEA Adapter Connected', Strings_to_Compare, Strings_from_PowerPack)
    serialControlObj.Test_Results.append('EEA Adapter Connected:' + result)
    print(serialControlObj.Test_Results)

    ## STEP 15: Attaching EEA reload along with ship cap presence check
    if serialControlObj.r['Reload Type'] == "EEA":
        videoThread = OLEDRecordingThread.myThread(
            (str(serialControlObj.r['Scenario Num']) + '#' + str(p + 1) + serialControlObj.r['Test Scenario'] + '_' +
             serialControlObj.r['Reload Type'] + '_' + str(1)),
            serialControlObj.videoPath)
        videoThread.start()
        serialControlObj.Switch_ONN_Relay(5, 2)  # B5:R2 - ON
        serialControlObj.Switch_ONN_Relay(5, 6)  # B5:R6 - ON
        serialControlObj.wait(5)
        ser = serial.Serial(serialControlObj.BlackBoxComPort, 9600)
        ############# READ ###################
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

        # Turning ON EEA Reload One Wire
        my_Serthread.clearQue()
        serialControlObj.wait(5)
        serialControlObj.ConnectingEEAReload()
        serialControlObj.wait(5)
        Timestamps, Strings_from_PowerPack = ReadQue(1000, my_Serthread.readQue)
        serialControl.convertListtoLogFile(Strings_from_PowerPack, str(videoPath + '\\TotalLog.txt'), fileOpenMode='a')

        if serialControlObj.r['Ship cap Present'] == "Yes":
            Strings_to_Compare = locateStringsToCompareFromEvent('EEA RELOAD Connected with Ship cap',
                                                                 Length=serialControlObj.r.get('Reload Diameter(mm)'),
                                                                 Color=serialControlObj.r.get('Reload Color'))
            result = Compare('EEA RELOAD Connected', Strings_to_Compare, Strings_from_PowerPack)
            serialControlObj.Tilt_Recovery_items_Test_Results.append('EEA RELOAD Connected:' + result)
        elif serialControlObj.r['Ship cap Present'] == "No":
            Strings_to_Compare = locateStringsToCompareFromEvent('EEA RELOAD Connected without Ship cap',
                                                                 Length=serialControlObj.r.get('Reload Diameter(mm)'),
                                                                 Color=serialControlObj.r.get('Reload Color'))
            result = Compare('EEA RELOAD Connected', Strings_to_Compare, Strings_from_PowerPack)
            serialControlObj.Tilt_Recovery_items_Test_Results.append('EEA RELOAD Connected:' + result)

        print("Step: EEA Reload Connected")
        print(serialControlObj.Tilt_Recovery_items_Test_Results)
        serialControlObj.wait(3)

        ## STEP 16: Extension of Trocar
        my_Serthread.clearQue()
        serialControlObj.wait(5)
        serialControlObj.Switch_ONN_Relay(2, 4)  # B2:R5 - ON
        serialControlObj.wait(10)
        serialControlObj.Switch_OFF_Relay(2, 4)  # B2:R5 - OFF

        Timestamps, Strings_from_PowerPack = ReadQue(1000, my_Serthread.readQue)
        serialControl.convertListtoLogFile(Strings_from_PowerPack, str(videoPath + '\\TotalLog.txt'), fileOpenMode='a')
        Strings_to_Compare = locateStringsToCompareFromEvent('EEA Trocar Extention with Reload')
        result = Compare('EEA Trocar Extention with Reload', Strings_to_Compare, Strings_from_PowerPack)
        serialControlObj.Test_Results.append('EEA Trocar Extention with Reload:' + result)

        ## STEP 17: Clamping on Tissue - Retraction of Trocar Until Clamp GAP is reached
        my_Serthread.clearQue()
        serialControlObj.wait(5)
        cf = serialControlObj.EEAForceDecode(clampingForce)
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

        Timestamps, Strings_from_PowerPack = ReadQue(1000, my_Serthread.readQue)
        serialControl.convertListtoLogFile(Strings_from_PowerPack, str(videoPath + '\\TotalLog.txt'), fileOpenMode='a')
        Strings_to_Compare = locateStringsToCompareFromEvent('EEA Clamping on Tissue')
        result = Compare('EEA Clamping on Tissue', Strings_to_Compare, Strings_from_PowerPack)
        serialControlObj.Test_Results.append('EEA Clamping on Tissue:' + result)
        print("Step: EEA Clamping on Tissue")
        print(serialControlObj.Tilt_Recovery_items_Test_Results)

        my_Serthread.clearQue()
        serialControlObj.wait(5)
        serialControlObj.Switch_OFF_Relay(2, 5)  # B2:R5 - OFF

        # STEP 18: Safety Key Acknowledgement
        serialControlObj.GreenKeyAck()
        serialControlObj.wait(2)
        Timestamps, Strings_from_PowerPack = ReadQue(200, my_Serthread.readQue)
        serialControl.convertListtoLogFile(Strings_from_PowerPack, str(videoPath + '\\TotalLog.txt'), fileOpenMode='a')
        Strings_to_Compare = locateStringsToCompareFromEvent('EEA Green Key Ack')
        result = Compare('EEA Green Key Ack', Strings_to_Compare, Strings_from_PowerPack)
        serialControlObj.Tilt_Recovery_items_Test_Results.append('EEA Green Key Ack:' + result)
        print("Step: Acknowledged Safety Key (Green LED) for firing")
        print(serialControlObj.Tilt_Recovery_items_Test_Results)

        ## STEP 19: Firing
        # ff = serialControlObj.EEAForceDecode(firingForce)
        with nidaqmx.Task() as task:
            task.ao_channels.add_ao_voltage_chan('Dev1/ao0')
            print('1 Channel 1 Sample Write: ')
            print(task.write(3.25))

        my_Serthread.clearQue()
        serialControlObj.wait(5)
        serialControlObj.Switch_ONN_Relay(4, 1)
        serialControlObj.Switch_ONN_Relay(4, 2)  # To turn on Linear actuator
        serialControlObj.wait(3)
        serialControlObj.Switch_ONN_Relay(2, 5)  # B2:R5 - ON
        serialControlObj.wait(0.5)
        serialControlObj.Switch_OFF_Relay(2, 5)  # B2:R5 - OFF  # Need to test Manoj Vadali

        serialControlObj.wait(4)
        serialControlObj.Switch_OFF_Relay(4, 1)
        serialControlObj.Switch_OFF_Relay(4, 2)  # To turn on Linear actuator
        serialControlObj.wait(1)
        with nidaqmx.Task() as task:
            task.ao_channels.add_ao_voltage_chan('Dev1/ao0')
            print('1 Channel 1 Sample Write: ')
            print(task.write(0))

        serialControlObj.Switch_ONN_Relay(4, 3)
        serialControlObj.Switch_ONN_Relay(4, 4)  # To turn on Linear actuator at full power

        # Remove Adapter when 2nd EEA Stapling In Progress
        serialControlObj.Switch_OFF_Relay(1, 8)  # B1:R8 - Turning Off - Adapter Clutch Disengaged
        serialControlObj.removeAdapter()

        serialControlObj.wait(5)  # need to optimize based on firing duration
        serialControlObj.Switch_OFF_Relay(4, 3)
        serialControlObj.Switch_OFF_Relay(4, 4)
        serialControlObj.wait(.5)
        serialControlObj.Switch_ONN_Relay(4, 5)
        serialControlObj.Switch_ONN_Relay(4, 6)
        serialControlObj.wait(30)

        Timestamps, Strings_from_PowerPack = ReadQue(1000, my_Serthread.readQue)
        serialControl.convertListtoLogFile(Strings_from_PowerPack, str(videoPath + '\\TotalLog.txt'),
                                           fileOpenMode='a')

        Strings_to_Compare = locateStringsToCompareFromEvent('Remove Adapter When 2nd EEA Stapling In Progress')
        result = Compare('Remove Adapter When 2nd EEA Stapling In Progress', Strings_to_Compare, Strings_from_PowerPack)
        serialControlObj.Tilt_Recovery_items_Test_Results.append('Recovery Adapter When 2nd EEA Stapling In Progress:' + result)
        print("Step: Remove Adapter When 2nd EEA Stapling In Progress")
        print(serialControlObj.Tilt_Recovery_items_Test_Results)
        serialControlObj.wait(7)

        ## STEP 20: Verifying Recovery ID data
        # From Adapter EEPROM
        RecoveryIDEeprom = GetAdapterEEPROMRecoveryIdData(FtdiUartComPort)
        RecoveryStateString = AdapterRecoveryStates(RecoveryIDEeprom)
        print("Recovery ID After Removing Adapter During 2nd EEA Stapling In Progress : ", RecoveryStateString)
        serialControlObj.Test_Results.append(RecoveryStateString + ":" + RecoveryIDEeprom)
        print(serialControlObj.Test_Results)

        # Engaging the Adapter
        serialControlObj.Switch_ONN_Relay(1, 8)
        serialControlObj.wait(7)
        print("EEA Adapter Engaged to Power Pack Mechanically")

        RecoveryIdHighByte, RecoveryIdLowByte = GetAdapterOnewireRecoveryIdData(BlackBoxComPort)

        RecoveryIdOnewire = int((RecoveryIdLowByte, 16)) * 256 + int(RecoveryIdHighByte, 16)

        # Recovery State Verifying in the Adapter onewire and Capturing into the Test Results
        serialControlObj.Test_Results.append("5th to Last Byte : " + RecoveryIdHighByte)
        serialControlObj.Test_Results.append("4th to Last Byte : " + RecoveryIdLowByte)
        print(serialControlObj.Test_Results)

        if RecoveryIDEeprom == RecoveryIdOnewire:
            pass

        ## STEP 11: Re-Attaching the Adapter to the Power Pack
        my_Serthread.clearQue()
        serialControlObj.wait(5)
        serialControlObj.ConnectAdapter()
        print("Step: EEA Adapter Re-Connected")

        serialControlObj.wait(40)

        Timestamps, Strings_from_PowerPack = ReadQue(1000, my_Serthread.readQue)
        serialControl.convertListtoLogFile(Strings_from_PowerPack, str(videoPath + '\\TotalLog.txt'), fileOpenMode='a')
        Strings_to_Compare = locateStringsToCompareFromEvent('EEA Adapter Re-Connected After Stapling In Progress')
        result = Compare('EEA Adapter Re-Connected After Stapling In Progress', Strings_to_Compare,
                         Strings_from_PowerPack)
        serialControlObj.Test_Results.append('EEA Adapter Re-Connected After Stapling In Progress:' + result)
        print(serialControlObj.Test_Results)

        ## STEP 11: Performing Rotation, Articulation and Close Operation
        my_Serthread.clearQue()

        # Right CW Rotation
        serialControlObj.Switch_ONN_Relay(2, 7)  # B2:R7 - ON
        serialControlObj.wait(5)
        serialControlObj.Switch_OFF_Relay(2, 7)  # B2:R7 - OFF

        # Left Articulation
        my_Serthread.clearQue()
        serialControlObj.wait(5)
        serialControlObj.Switch_ONN_Relay(2, 3)  # B2:R3 - ON
        serialControlObj.wait(7)
        serialControlObj.Switch_OFF_Relay(2, 3)  # B2:R3 - OFF

        # Close Key Operation
        my_Serthread.clearQue()
        serialControlObj.wait(5)
        serialControlObj.Switch_ONN_Relay(2, 5)  # B2:R5 - ON
        serialControlObj.wait(10)
        serialControlObj.Switch_OFF_Relay(2, 5)  # B2:R5 - OFF

        Timestamps, Strings_from_PowerPack = ReadQue(1000, my_Serthread.readQue)
        serialControl.convertListtoLogFile(Strings_from_PowerPack, str(videoPath + '\\TotalLog.txt'),
                                           fileOpenMode='a')
        Strings_to_Compare = locateStringsToCompareFromEvent('Rotation & Articulation & Close Operation During SP IP')
        result = Compare('Rotation & Articulation & Close Operation During SP IP', Strings_to_Compare,
                         Strings_from_PowerPack)
        serialControlObj.Test_Results.append('Rotation & Articulation & Close Operation During SP IP:' + result)
        print(serialControlObj.Test_Results)

        ## STEP 12: Holding Rotation Buttons
        serialControlObj.Switch_ONN_Relay(2, 1)  # B2:R7 - ON
        serialControlObj.Switch_ONN_Relay(2, 2)  # B2:R8 - ON
        serialControlObj.Switch_ONN_Relay(2, 7)  # B2:R1 - ON
        serialControlObj.Switch_ONN_Relay(2, 8)  # B2:R2 - ON

        serialControlObj.wait(4)

        serialControlObj.Switch_OFF_Relay(2, 8)  # B2:R7 - OFF
        serialControlObj.Switch_OFF_Relay(2, 7)  # B2:R8 - OFF
        serialControlObj.Switch_OFF_Relay(2, 2)  # B2:R1 - OFF
        serialControlObj.Switch_OFF_Relay(2, 1)  # B2:R2 - OFF

        Timestamps, Strings_from_PowerPack = ReadQue(1000, my_Serthread.readQue)
        serialControl.convertListtoLogFile(Strings_from_PowerPack, str(videoPath + '\\TotalLog.txt'), fileOpenMode='a')
        Strings_to_Compare = locateStringsToCompareFromEvent('Rotation Operation During SP IP')
        result = Compare('Rotation Operation During SP IP', Strings_to_Compare, Strings_from_PowerPack)
        serialControlObj.Test_Results.append('Rotation Operation During SP IP:' + result)
        print("Step: Rotation Operation During SP IP")
        print(serialControlObj.Test_Results)

        ## STEP 13: Staples Detected Exit State - Fully open position
        my_Serthread.clearQue()
        serialControlObj.wait(5)

        # Handling here, No staples detected State Exit, Full Open position, SSE.
        serialControlObj.EEANoStaplesDetectedStateExit()

        Timestamps, Strings_from_PowerPack = ReadQue(1000, my_Serthread.readQue)
        serialControl.convertListtoLogFile(Strings_from_PowerPack, str(videoPath + '\\TotalLog.txt'), fileOpenMode='a')
        Strings_to_Compare = locateStringsToCompareFromEvent('No Staples Detected State Exit')
        result = Compare('No Staples Detected State Exit', Strings_to_Compare, Strings_from_PowerPack)
        serialControlObj.Test_Results.append('No Staples Detected State Exit:' + result)
        print("No Staples Detected State Exit")
        print(serialControlObj.Test_Results)

        ## STEP 14: Remove Reload
        my_Serthread.clearQue()
        serialControlObj.wait(5)
        serialControlObj.DisconnectingEEAReload()

        Timestamps, Strings_from_PowerPack = ReadQue(1000, my_Serthread.readQue)
        serialControl.convertListtoLogFile(Strings_from_PowerPack, str(videoPath + '\\TotalLog.txt'), fileOpenMode='a')
        Strings_to_Compare = locateStringsToCompareFromEvent('EEA Remove Reload Enter SSE')
        result = Compare('EEA Remove Reload Enter SSE', Strings_to_Compare, Strings_from_PowerPack)
        serialControlObj.Tilt_Recovery_items_Test_Results.append('EEA Remove Reload Enter SSE:' + result)
        print("EEA Remove Reload Enter SSE")
        print(serialControlObj.Tilt_Recovery_items_Test_Results)

        ## STEP 15: Surgical Site Extraction (SSE)
        my_Serthread.clearQue()
        serialControlObj.wait(5)

        # Surgical Site Extraction Exit
        serialControlObj.EEASurgicalSiteExtractionStateExit()

        Timestamps, Strings_from_PowerPack = ReadQue(1000, my_Serthread.readQue)
        serialControl.convertListtoLogFile(Strings_from_PowerPack, str(videoPath + '\\TotalLog.txt'), fileOpenMode='a')
        Strings_to_Compare = locateStringsToCompareFromEvent('SSE Exit')
        result = Compare('SSE Exit', Strings_to_Compare, Strings_from_PowerPack)
        serialControlObj.Test_Results.append('SSE Exit:' + result)
        print("Step:SSE Exit")
        print(serialControlObj.Test_Results)

        ## STEP 16: Remove Adapter
        my_Serthread.clearQue()
        serialControlObj.wait(5)
        serialControlObj.removeAdapter()
        serialControlObj.Switch_OFF_Relay(1, 8) # Dis Engaging the Adapter Clutch

        Timestamps, Strings_from_PowerPack = ReadQue(1000, my_Serthread.readQue)
        serialControl.convertListtoLogFile(Strings_from_PowerPack, str(videoPath + '\\TotalLog.txt'), fileOpenMode='a')
        Strings_to_Compare = locateStringsToCompareFromEvent('Remove EEA Adapter')
        result = Compare('Remove EEA Adapter', Strings_to_Compare, Strings_from_PowerPack)
        serialControlObj.Test_Results.append('Remove EEA Adapter:' + result)
        print("Remove EEA Adapter")
        print(serialControlObj.Test_Results)

        ## STEP 17: Record Adapter usage Counts - Adapter Firing and Procedure Count Incremented by 1
        # For capturing Adapter Usage Counts - Adapter needs to be connected Mechanically
        # Engaging the Adapter - Controlling the stepper motor
        serialControlObj.Switch_ONN_Relay(1, 8)
        serialControlObj.wait(7)
        print("EEA Adapter Engaged to Power Pack Mechanically")

        MCPThread.readingPowerPack.exitFlag = True
        serPP.close()
        serialControlObj.wait(2)

        # Reading Adapter EEPROM Usage Counts
        AdapterEeProcedureCount, AdapterEeFireCount = GetAdapterEepromUsageCounts(FtdiUartComPort)

        # For capturing Onewire Usage counts from the Adapter via BB, below relays should be ON.
        serialControlObj.Switch_ONN_Relay(5, 8)  # B5:R8 - ON
        serialControlObj.Switch_ONN_Relay(6, 1)  # B6:R1 - ON

        # Reading Adapter One-Wire usage Counts
        AdapterOwProcedureCount, AdapterOwFireCount = GetAdapterOnewireUsageCounts(BlackBoxComPort)

        serialControlObj.Switch_OFF_Relay(6, 1)  # B6:R1 - OFF
        serialControlObj.Switch_OFF_Relay(5, 8)  # B5:R8 - OFF

        print('Adapter Eeprom Fire Count:' + str(AdapterEeFireCount),
              'Adapter Eeprom Procedure Count:' + str(AdapterEeProcedureCount))
        print('Adapter Onewire Fire Count:' + str(AdapterOwFireCount),
              'Adapter Onewire Procedure Count:' + str(AdapterOwProcedureCount))

        ## STEP 28: DisEngage the Adapter Clutch
        serialControlObj.Switch_OFF_Relay(1, 8)
        print('Adapter Clutch Disengaged')

        ## STEP 25: Remove Clamshell
        my_Serthread.clearQue()
        serialControlObj.Switch_OFF_Relay(1, 5)
        serialControlObj.wait(5)
        Timestamps, Strings_from_PowerPack = ReadQue(100, my_Serthread.readQue)
        serialControl.convertListtoLogFile(Strings_from_PowerPack, str(videoPath + '\\TotalLog.txt'), fileOpenMode='a')
        Strings_to_Compare = locateStringsToCompareFromEvent('Remove Clamshell')
        result = Compare('Remove Clamshell', Strings_to_Compare, Strings_from_PowerPack)
        serialControlObj.Test_Results.append('Remove Clamshell:' + result)
        print("Step: Removed Clamshell")
        print(serialControlObj.Test_Results)
        serialControlObj.wait(2)

        for item in serialControlObj.Test_Results:
            # print(item)
            temp2 = 'PASS'
            try:
                if (((str.split(item, ':', 1))[1]) == 'PASS'):
                    # serialControlObj.Test_Results.append(serialControlObj.Tilt_Recovery_items_Test_Results[0] + ':FAIL')
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

        my_Serthread.clearQue()
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

        ## STEP 26: Placing Power pack on the Charger
        serialControlObj.PlacingPowerPackOnCharger()
        print('Power Pack Placed on Charger')
        print('------------------- End of Test Scenario --------------')
        serialControlObj.wait(30)
        print('------------------- EEA Firing Recovery Requirements Case 1 End --------------')

##################################################################################################################################################
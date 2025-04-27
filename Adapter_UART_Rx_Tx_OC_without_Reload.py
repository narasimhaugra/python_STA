""" Written by Manoj Vadali, Date: 20-Jan-2022
Purpose: Adapter UART Rx Tx OC error inwithout reload"""

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
from ReadingQue import ReadingQue
from RelayControlBytes import *
from Serial_Control import serialControl


def Adapter_UART_Rx_Tx_OC_without_Reload(r, SULU_EEPROM_command_byte, MULU_EEPROM_command_byte, CARTRIDGE_EEPROM_command_byte,
                                   NCDComPort,
                                   PowerPackComPort, BlackBoxComPort, USB6351ComPort, ArduinoUNOComPort, OUTPUT_PATH,
                                   videoPath, p):
    # print('r['Num of Firings in Procedure']', r['Num Times to Execute'], r['Reload Type'])
    print('Adapter UART Rx Tx Open Circuit without Reload', r, SULU_EEPROM_command_byte, MULU_EEPROM_command_byte,
          CARTRIDGE_EEPROM_command_byte)

    # below steps are for Adapter 1W Open Circuit in Firing Mode

    # Steps:
    # Initialize the class
    # Open the associated Serial Connection
    # Perform Accessories connection enter fire mode
    #  Perform firing for 2 seconds and disconnect adapter 1W (Open circuit)
    # Complete the firing and retracting
    # Disconnect the serial connection
    # r, SULU_EEPROM_command_byte, MULU_EEPROM_command_byte, CARTRIDGE_EEPROM_command_byte, NCDComPort, PowerPackComPort, BlackBoxComPort, USB6351ComPort, ArduinoUNOComPort, OUTPUT_PATH, videoPath

    serialControlObj = serialControl(r, SULU_EEPROM_command_byte, MULU_EEPROM_command_byte,
                                     CARTRIDGE_EEPROM_command_byte, NCDComPort, PowerPackComPort, BlackBoxComPort,
                                     USB6351ComPort, ArduinoUNOComPort, OUTPUT_PATH, videoPath, p)
    serialControlObj.OpenSerialConnection()
    Adapter_UART_Rx_Tx_Open_Circuit_without_Reload(serialControlObj, SULU_EEPROM_command_byte, MULU_EEPROM_command_byte, CARTRIDGE_EEPROM_command_byte,
                                   NCDComPort,
                                   PowerPackComPort, BlackBoxComPort, USB6351ComPort, ArduinoUNOComPort, OUTPUT_PATH,
                                   videoPath, p)
    # time.sleep(5)
    #
    serialControlObj.disconnectSerialConnection()


# Purpose-To perform Firing with Adapter 1W open circuit
def Adapter_UART_Rx_Tx_Open_Circuit_without_Reload(serialControlObj, SULU_EEPROM_command_byte, MULU_EEPROM_command_byte, CARTRIDGE_EEPROM_command_byte,
                                   NCDComPort,
                                   PowerPackComPort, BlackBoxComPort, USB6351ComPort, ArduinoUNOComPort, OUTPUT_PATH,
                                   videoPath, p):
    TestBatteryLevelMax = serialControlObj.r['Battery RSOC Max Level']
    TestBatteryLevelMin = serialControlObj.r['Battery RSOC Min Level']
    clampingForce = serialControlObj.r['Clamping Force']
    firingForce = serialControlObj.r['Firing Force']
    articulationStateinFiring = serialControlObj.r['Articulation State for clamping & firing']
    numberOfFiringsinProcedure = serialControlObj.r['Num of Firings in Procedure']
    retractionForce = serialControlObj.r['Retraction Force']
    print(TestBatteryLevelMax, TestBatteryLevelMin, clampingForce, firingForce, articulationStateinFiring,
          numberOfFiringsinProcedure)
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

    # MCPThread.readingPowerPack.exitFlag = True

    if (read_battery_RSOC(25,
                          PowerPackComPort) > TestBatteryLevelMax):  # and (read_battery_RSOC(25, PowerPackComPort) > TestBatteryLevelMin):
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
                                 PowerPackComPort)) > TestBatteryLevelMax:  # and (read_battery_RSOC(25, PowerPackComPort) > TestBatteryLevelMin):
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
        serialControlObj.wait(5)
        while (read_battery_RSOC(50,
                                 PowerPackComPort) < TestBatteryLevelMin):  # and (read_battery_RSOC(25, PowerPackComPort) <= TestBatteryLevelMax):
            pass
            # serialControlObj.wait(0.1)
            # read_battery_RSOC(10, PowerPackComPort)

    # if read_battery_RSOC(10, PowerPackComPort) == TestBatteryLevel:
    #      pass
    serialControlObj.wait(20)
    print("----------Placing Power Pack on Charger for startup Test--------------")
    serialControlObj.Switch_ONN_Relay(3, 7)
    serialControlObj.wait(.2)
    serialControlObj.Switch_ONN_Relay(3, 8)
    serialControlObj.wait(60)
    print("----------Removing Power Pack from Charger for startup Test--------------")
    serialControlObj.Switch_OFF_Relay(3, 7)
    serialControlObj.wait(.2)
    serialControlObj.Switch_OFF_Relay(3, 8)
    OLEDRecordingThread.exitFlag = False
    videoThread = OLEDRecordingThread.myThread(
        (str(serialControlObj.r['Scenario Num']) + '#' + str(p + 1) + serialControlObj.r['Test Scenario']), serialControlObj.videoPath)
    videoThread.start()
    # serialControlObj.send_decimal_bytes(TURN_OFF_ALL_RELAYS_IN_ALL_BANKS[0])
    # strPort = 'SigniaPowerHandle'

    # while True:
    #     # seriallistData = serial.tools.list_ports.comports()
    #     # print(seriallistData)
    #     singiaPowerFound = False
    #     lp = serial.tools.list_ports.comports()
    #     for singlePort in lp:
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
    #     break
    while True:
        # seriallistData = serial.tools.list_ports.comports()
        # print(seriallistData)
        singiaPowerFound = False
        if any("SigniaPowerHandle" in s for s in serial.tools.list_ports.comports()):
            singiaPowerFound = True
        else:
            print('Signia Com Port Closed')
            singiaPowerFound = False
            break

    # serialControlObj.wait(4)
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
                print(ports[i], 'Available')
                break
    serialControlObj.wait(7)

    ################################################################################################################
    # TEST STEP: Remove Signia Power Handle from Charger
    # serialControlObj.send_decimal_bytes(TURN_OFF_ALL_RELAYS_IN_ALL_BANKS[0])
    # print("Step: Remove Signia Power Handle from Charger")
    # based on the functionality of signals on bank 4, 5 6 this may need to be optimized to check the relay status con control
    # serialControlObj.wait(7)

    # serialControlObj.wait(60)
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
    # print(sys.argv[0], end=" ")

    serialControlObj.Test_Results.append(
        str(serialControlObj.r['Scenario Num']) + '#' + str(p + 1) + "@" + serialControlObj.r[
            'Test Scenario'])  # + str(i+1))

    serialControlObj.wait(60)
    searchFlag = True

    Timestamps, Strings_from_PowerPack, data_path = ReadingQue(my_Serthread.readQue, searchFlag)
    serialControl.convertListtoLogFile(Strings_from_PowerPack, (videoPath + '\\StartUpLog.txt'), fileOpenMode='w')
    serialControl.convertListtoLogFile(Strings_from_PowerPack, 'TotalLog.txt', fileOpenMode='a')
    '''Strings_to_Compare = ['GUI_NewState: WELCOME_SCREEN', 'Piezo: All Good', 'Initialization complete',
                          'SM_NewSystemEventAlert: INIT_COMPLETE', 'systemCheckCompleted complete',
                          'GUI_NewState: PROCEDURES_REMAINING', 'GUI_NewState: REQUEST_CLAMSHELL',
                          'Going to standby', 'Turning off OLED']'''
    Strings_to_Compare = locateStringsToCompareFromEvent('Remove Signia Power Handle from Charger')
    # print(Strings_from_PowerPack)

    result = Compare('Remove Signia Power Handle from Charger', Strings_to_Compare, Strings_from_PowerPack)
    # serialControlObj.Test_Results.append('Remove Signia Power Handle from Charger:')
    # serialControlObj.Test_Results.append(result)
    data_path = "None" if not data_path else data_path
    serialControlObj.Test_Results.append('Eventlog:' + data_path)
    serialControlObj.Test_Results.append('Remove Signia Power Handle from Charger:' + result)

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
    serialControl.convertListtoLogFile(Strings_from_PowerPack, str(videoPath + '\\TotalLog.txt'), fileOpenMode='a')
    Strings_to_Compare = locateStringsToCompareFromEvent('Clamshell Connected')
    result = Compare('Clamshell Connected', Strings_to_Compare, Strings_from_PowerPack)

    rlist = {'Test Step': ['Clamshell Connected'], 'Test Result': [result]}  # df can be deleted
    df = pd.DataFrame(rlist)

    serialControlObj.Test_Results.append('Connected Clamshell:'+ result)
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
    serialControl.convertListtoLogFile(Strings_from_PowerPack, str(videoPath + '\\TotalLog.txt'), fileOpenMode='a')
    '''Strings_to_Compare = ['  1Wire Device Adapter authenticated and identified',
                          ' GUI_NewState: ADAPTER_DETECTED',
                          ' GUI_NewState: EGIA_ADAPTER_CALIBRATING',
                          ' SM_NewSystemEventAlert: ADAPTER_FULLY_CALIBRATED',
                          ' Piezo: All Good',
                          ' GUI_NewState: EGIA_REQUEST_RELOAD']'''
    Strings_to_Compare = locateStringsToCompareFromEvent('Adapter Connected')
    result = Compare('Adapter Connected', Strings_to_Compare, Strings_from_PowerPack)
    serialControlObj.Test_Results.append('Adapter Connected:' + result)
    print(serialControlObj.Test_Results)

    rlist = {'Test Step': ['Adapter Connected'], 'Test Result': [result]}
    df = df.append(pd.DataFrame(rlist))

    # Adapter Rotation Test

    serialControlObj.wait(5)



    my_Serthread.clearQue()
    serialControlObj.wait(5)
    print("Open Circuiting Adapter UART Rx Tx")
    serialControlObj.Switch_OFF_Relay(1, 3)
    serialControlObj.wait(0.2)
    serialControlObj.Switch_OFF_Relay(1, 4)
    serialControlObj.wait(5)
    Timestamps, Strings_from_PowerPack = ReadingQue(my_Serthread.readQue)
    serialControl.convertListtoLogFile(Strings_from_PowerPack, str(videoPath + '\\TotalLog.txt'), fileOpenMode='a')
    Strings_to_Compare = locateStringsToCompareFromEvent('Adapter UART Rx Tx OC without Reload')
    result = Compare('Adapter UART Rx Tx OC without Reload', Strings_to_Compare, Strings_from_PowerPack)
    serialControlObj.Test_Results.append('Adapter UART Rx Tx OC without Reload:' + result)
    print("Step: Adapter UART Rx Tx OC without Reload")
    print(serialControlObj.Test_Results)
    rlist = {'Test Step': ['Adapter UART Rx Tx OC without Reload:'], 'Test Result': [result]}
    df = df.append(pd.DataFrame(rlist))


    serialControlObj.send_decimal_bytes(TURN_OFF_ALL_RELAYS_IN_ALL_BANKS[0])
    serialControlObj.wait(20)

    for item in serialControlObj.Test_Results:
        # print(item)
        temp2 = 'PASS'
        try:
            if (((str.split(item, ':', 1))[1]) == 'PASS'):
                # serialControlObj.Test_Results.append(serialControlObj.Normal_Firing_Test_Results[0] + ':FAIL')
                pass
            elif (((str.split(item, ':', 1))[1]) == 'FAIL'):
                temp2 = 'FAIL'
                #print(str((serialControlObj.Test_Results[0] + ':  Failed')))
                break
        except:
            pass
    if temp2 == 'PASS':
        iterPass = int(iterPass) + 1
        print(serialControlObj.r['Test Scenario'] + '% of Successful Executions: ' + str(
            100 * ((iterPass) / (serialControlObj.r['Num Times to Execute']))))

    # Iteration_Results.append()
    results_path = serialControlObj.OUTPUT_PATH + '\\Results.xlsx'
    df.to_excel(results_path)
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
    serialControlObj.PlacingPowerPackOnCharger()
    print('Power Pack Placed on Charger')
    print('------------------- End of Test Scenario --------------')
    serialControlObj.wait(30)
    # serialControlObj.disconnectSerialConnection()


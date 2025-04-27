
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
from EventsStrings import locateStringsToCompareFromEvent
from Prepare_Output_Json_File import *
from ReadBatteryRSOC import read_battery_RSOC
from ReadStatusVariables import ReadStatusVariables
from Read_Handle_Fire_Count import GetHandleUseCount
from ReadingQue import ReadingQue
from RelayControlBytes import *
from Serial_Control import serialControl


def EGIAISNormalFire(r, SULU_EEPROM_command_byte, MULU_EEPROM_command_byte, CARTRIDGE_EEPROM_command_byte,NCDComPort,
                 PowerPackComPort, BlackBoxComPort, USB6351ComPort, ArduinoUNOComPort, OUTPUT_PATH, videoPath, p):
    #print('normal firing', r, SULU_EEPROM_command_byte, MULU_EEPROM_command_byte, CARTRIDGE_EEPROM_command_byte, i)
    #Test_Results = []

    print("-----------------EGIA IS 01 G-------------------")
    serialControlObj = serialControl(r, SULU_EEPROM_command_byte, MULU_EEPROM_command_byte, CARTRIDGE_EEPROM_command_byte, NCDComPort, PowerPackComPort, BlackBoxComPort, USB6351ComPort, ArduinoUNOComPort, OUTPUT_PATH, videoPath)
    serialControlObj.OpenSerialConnection()
    #Normal_Firing(serialControlObj) #, PowerPackComPort)
    EGIA_IS_Normal_Fire(serialControlObj,SULU_EEPROM_command_byte, MULU_EEPROM_command_byte, CARTRIDGE_EEPROM_command_byte, NCDComPort,
                 PowerPackComPort, BlackBoxComPort, USB6351ComPort, ArduinoUNOComPort, OUTPUT_PATH, videoPath, p)
    serialControlObj.disconnectSerialConnection()


# Purpose-To perform Normal Firing Scenarios
def EGIA_IS_Normal_Fire(serialControlObj, SULU_EEPROM_command_byte, MULU_EEPROM_command_byte, CARTRIDGE_EEPROM_command_byte, NCDComPort,
                 PowerPackComPort, BlackBoxComPort, USB6351ComPort, ArduinoUNOComPort, OUTPUT_PATH, videoPath, p):
        # r = getrow('C:\Python\Test_Configurator.xlsx', 0)
    PowerPackComPort = PowerPackComPort
    SULU_EEPROM = [2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0,
                       0,
                       0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    MULU_EEPROM = [2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0,
                       0,
                       0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    CARTRIDGE_EEPROM = [2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                            0, 0,
                            0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                            0, 0]

    iterPass = 0
    firePass = 0
    TestBatteryLevelMax = serialControlObj.r['Battery RSOC Max Level']
    TestBatteryLevelMin = serialControlObj.r['Battery RSOC Min Level']

    # with nidaqmx.Task() as task:
    #     task.ao_channels.add_ao_voltage_chan('Dev1/ao0')
    #     print('1 Channel 1 Sample Write: ')
    #     print(task.write(0.25))

    serialControlObj.send_decimal_bytes(TURN_OFF_ALL_RELAYS_IN_ALL_BANKS[0])
    serialControlObj.wait(0.5)
    serialControlObj.Switch_ONN_Relay(3, 8)

    serialControlObj.wait(0.5)
    serialControlObj.Switch_ONN_Relay(3, 7)

    serialControlObj.wait(60)

    serialControlObj.send_decimal_bytes(TURN_OFF_ALL_RELAYS_IN_ALL_BANKS[0])
    print("Step: Remove Signia Power Handle from Charger")
    serialControlObj.wait(40)

    # MCPThread.readingPowerPack.exitFlag = True

    if (read_battery_RSOC(25, PowerPackComPort) > TestBatteryLevelMax): #and (read_battery_RSOC(25, PowerPackComPort) > TestBatteryLevelMin):
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
        while (read_battery_RSOC(25, PowerPackComPort)) > TestBatteryLevelMax:# and (read_battery_RSOC(25, PowerPackComPort) > TestBatteryLevelMin):
            serialControlObj.Switch_ONN_Relay(2, 5)  # B2:R5 - ON -- some operations battery discharge
            serialControlObj.wait(7)
            serialControlObj.Switch_OFF_Relay(2, 5)  # B2:R5 - ON
            serialControlObj.Switch_ONN_Relay(2, 4)  # B2:R5 - ON
            serialControlObj.wait(7)
            serialControlObj.Switch_OFF_Relay(2, 4)  # B2:R5 - ON

        serialControlObj.Switch_OFF_Relay(3, 1)  # B3:R1 - OFF
        serialControlObj.Switch_OFF_ALL_Relays_In_Each_Bank(1)
        serialControlObj.wait(10)
    if (read_battery_RSOC(25, PowerPackComPort) < TestBatteryLevelMin):# and (read_battery_RSOC(25, PowerPackComPort) <= TestBatteryLevelMax):
        # print('entered elif loop')
        serialControlObj.Switch_ONN_Relay(3, 7)  # battery charge
        serialControlObj.wait(0.5)
        serialControlObj.Switch_ONN_Relay(3, 8)
        # need to optimize this delay so that handle does not go to sleep or does not result communciation
        serialControlObj.wait(5)
        while (read_battery_RSOC(50, PowerPackComPort) < TestBatteryLevelMin): #  and (read_battery_RSOC(25, PowerPackComPort) <= TestBatteryLevelMax):
            pass
            #serialControlObj.wait(0.1)
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
    #serialControlObj.send_decimal_bytes(TURN_OFF_ALL_RELAYS_IN_ALL_BANKS[0])
    #strPort = 'SigniaPowerHandle'

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

    #serialControlObj.wait(4)
    strPort ='None'
    #serialControlObj.wait(2)
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

    #serialControlObj.wait(60)
    PPnotReady = True
    while PPnotReady:
        try:

            serPP = serial.Serial(serialControlObj.PowerPackComPort, 115200, bytesize=8, parity='N', stopbits=1, timeout=0.05, xonxoff=0)
            my_Serthread = MCPThread.readingPowerPack(serPP, 1000)
            my_Serthread.clearQue()
            MCPThread.readingPowerPack.exitFlag = False
            my_Serthread.start()
            PPnotReady = False
            #print(sys.argv[0], end=" ")
        except:
            pass

    serialControlObj.Test_Results.append(
            str(serialControlObj.r['Scenario Num']) + '#' + str(p+1) + "@" + serialControlObj.r['Test Scenario']) #+ str(i+1))


    serialControlObj.wait(60)
    searchFlag = True

    #tone_names = []

    # tone_thread = Audio_Tone_Decoding_Thread.ToneDecoding(100)
    # tone_thread.clearToneQue()
    # Audio_Tone_Decoding_Thread.ToneDecoding.exitFlag = False
    # tone_thread.start()



    Timestamps, Strings_from_PowerPack, data_path = ReadingQue(my_Serthread.readQue, searchFlag)
    serialControl.convertListtoLogFile(Strings_from_PowerPack, (videoPath +'\\StartUpLog.txt'), fileOpenMode='w')
    serialControl.convertListtoLogFile(Strings_from_PowerPack, 'TotalLog.txt', fileOpenMode='a')
    '''Strings_to_Compare = ['GUI_NewState: WELCOME_SCREEN', 'Piezo: All Good', 'Initialization complete',
                          'SM_NewSystemEventAlert: INIT_COMPLETE', 'systemCheckCompleted complete',
                          'GUI_NewState: PROCEDURES_REMAINING', 'GUI_NewState: REQUEST_CLAMSHELL',
                          'Going to standby', 'Turning off OLED']'''
    Strings_to_Compare = locateStringsToCompareFromEvent('Remove Signia Power Handle from Charger')
    #print(Strings_from_PowerPack)
    result = Compare('Remove Signia Power Handle from Charger', Strings_to_Compare, Strings_from_PowerPack)
    #serialControlObj.Test_Results.append('Remove Signia Power Handle from Charger:')
    #serialControlObj.Test_Results.append(result)
    data_path = "None" if not data_path else data_path
    serialControlObj.Test_Results.append('Eventlog:' + data_path)
    serialControlObj.Test_Results.append('Remove Signia Power Handle from Charger:' + result)

    # ListTones = ReadToneQue(100, tone_thread.readToneQue)
    # Tones_to_Compare = locateStringsToCompareFromEvent('Piezo: Remove Signia Power Handle from Charger')
    # tone_result = Compare('Piezo: Remove Signia Power Handle from Charger', Tones_to_Compare, ListTones)
    # print('tone_result:', tone_result)
    # serialControlObj.Test_Results.append('Piezo - Remove Signia Power Handle from Charger:' + tone_result)


    # appending data_path, post checking the value of data_path with None

        ## Engaging the Adapter - Controlling the stepper motor
    serialControlObj.Switch_ONN_Relay(1, 8)
    serialControlObj.wait(7)
    print("Adapter Engaged to Power Pack Mechanically")


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
    #print(command_byte)
    serialControlObj.Switch_ONN_Relay(5, 1)  # B5:R1 - ON
    serialControlObj.Switch_ONN_Relay(5, 5)  # B5:R5 - ON
    ser = serial.Serial(serialControlObj.BlackBoxComPort, 9600)
    serialControlObj.wait(5)
    ############# READ ###################
    command = bytes(command_byte)
    print('Clamshell ResetByte array', command)
    ser.write(command)
    serialControlObj.wait(3)
    #ser.write(command)
    serialControlObj.wait(5)
    #print(command)
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
    my_Serthread.clearQue()
    serialControlObj.wait(5)

    serialControlObj.connectClamshell()
    print("Step: Clamshell Connected")
    serialControlObj.wait(5)
    Timestamps, Strings_from_PowerPack = ReadingQue(my_Serthread.readQue)
    #serialControl.convertListtoLogFile(Strings_from_PowerPack, 'TotalLog.txt', fileOpenMode='a')
    serialControl.convertListtoLogFile(Strings_from_PowerPack, str(videoPath + '\\TotalLog.txt'), fileOpenMode='a')
    Strings_to_Compare = locateStringsToCompareFromEvent('Clamshell Connected')
    result = Compare('Clamshell Connected', Strings_to_Compare, Strings_from_PowerPack)

    # rlist = {'Test Step': ['Clamshell Connected'], 'Test Result': [result]}
    # df = pd.DataFrame(rlist)

    serialControlObj.Test_Results.append('Connected Clamshell:' + result)
    print(serialControlObj.Test_Results)

    tone_names = []
    #tone_thread = Audio_Tone_Decoding_Thread.ToneDecoding(100)

    #tone_thread.clearToneQue()

    #Audio_Tone_Decoding_Thread.ToneDecoding.exitFlag = False
    #tone_thread.start()

    my_Serthread.clearQue()
    serialControlObj.wait(5)
    # TEST STEP: Attach the EGIA Adapter
    serialControlObj.Switch_ONN_ALL_Relays_In_Each_Bank(1)  # B1 - ALL ON
    print("Step: Adapter Connected")
    serialControlObj.wait(15)
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

    # ListTones = ReadToneQue(100, tone_thread.readToneQue)
    # Tones_to_Compare = locateStringsToCompareFromEvent('Piezo: Adapter Connected')
    # tone_result = Compare('Piezo: Adapter Connected', Tones_to_Compare, ListTones)
    # print('tone_result:', tone_result)
    # serialControlObj.Test_Results.append('Piezo - Adapter Connected:' + tone_result)

    # rlist = {'Test Step': ['Adapter Connected'], 'Test Result': [result]}
    # df = df.append(pd.DataFrame(rlist))



    for i in range(serialControlObj.r['Total number of firings']):
        MCPThread.readingPowerPack.exitFlag = True
        serPP.close()
        serialControlObj.wait(2)
        #print(serialControlObj.Test_Results)
        HandleFireCount1, HandleProcedureCount = GetHandleUseCount(PowerPackComPort)
        print('Before Firing Handle Fire Count:' + str(HandleFireCount1), 'Handle Procedure Count:' + str(HandleProcedureCount))
        serialControlObj.wait(2)
        StatusVariables1 = ReadStatusVariables(PowerPackComPort)
        StatusVariables1 = StatusVariables1[13:61]
        StatusVariables1 = StatusVariables1[4:8] + StatusVariables1[12:16] + StatusVariables1[20:24] + StatusVariables1[28:32]  +StatusVariables1[36:40] + StatusVariables1[44:48]
        print('Before Firing Status Variables: ', StatusVariables1)
        serPP = serial.Serial(serialControlObj.PowerPackComPort, 115200, bytesize=8, parity='N', stopbits=1,
                              timeout=0.05, xonxoff=0)
        MCPThread.readingPowerPack.exitFlag = False
        my_Serthread = MCPThread.readingPowerPack(serPP, 1000)
        my_Serthread.clearQue()
        my_Serthread.start()

        serialControlObj.Normal_Firing_Test_Results = []
        serialControlObj.Normal_Firing_Test_Results.append('Firing =' + str(i + 1))
        OLEDRecordingThread.exitFlag = False

        fireN = 'Fire' + str(i+1)

        clampingForce = serialControlObj.r[fireN]['Clamping Force']
        firingForce = serialControlObj.r[fireN]['Firing Force']
        articulationStateinFiring = serialControlObj.r[fireN]['Articulation State for clamping & firing']
        numberOfFiringsinProcedure = serialControlObj.r[fireN]['Num of Firings in Procedure']
        retractionForce = serialControlObj.r[fireN]['Retraction Force']
        print(TestBatteryLevelMax, TestBatteryLevelMin, clampingForce, firingForce, articulationStateinFiring,
              numberOfFiringsinProcedure)



        if serialControlObj.r[fireN]['Reload Type'] == "Tri-Staple":
            #print(serialControlObj.videoPath)
            videoThread = OLEDRecordingThread.myThread((str(serialControlObj.r['Scenario Num']) + '#' + str(p+1) + serialControlObj.r['Test Scenario'] + '_' +
                                                        serialControlObj.r[fireN]['Reload Type'] + '_'+ fireN), serialControlObj.videoPath)
            videoThread.start()
            my_Serthread.clearQue()
            serialControlObj.wait(5)
            serialControlObj.ConnectingLegacyReload()
            serialControlObj.wait(5)
            Timestamps, Strings_from_PowerPack = ReadingQue(my_Serthread.readQue)
            serialControl.convertListtoLogFile(Strings_from_PowerPack, str(videoPath + '\\TotalLog.txt'), fileOpenMode='a')
            Strings_to_Compare = locateStringsToCompareFromEvent('Tri-Staple Connected')
            result = Compare('Tri-Staple Connected', Strings_to_Compare, Strings_from_PowerPack)
            serialControlObj.Normal_Firing_Test_Results.append('Tri-Staple Connected:'+ result)
            print("Step: Tri-Staple Reload Connected")
            print(serialControlObj.Normal_Firing_Test_Results)
            serialControlObj.wait(3)


        if serialControlObj.r[fireN]['Reload Type'] == "SULU" or 'Radial':
            videoThread = OLEDRecordingThread.myThread((str(serialControlObj.r['Scenario Num']) + '#' + str(p + 1) +
                                                        serialControlObj.r['Test Scenario'] + '_' +
                                                        serialControlObj.r[fireN][
                                                            'Reload Type'] + '_' + fireN),
                                                       serialControlObj.videoPath)
            videoThread.start()



            if serialControlObj.r[fireN]['Reload Length(mm)'] == 30:
                SULU_EEPROM[1] = 1
                SULU_EEPROM[2] = 0x0C
                # SULU_EEPROM[2] = 0x18
                SULU_EEPROM[22] = 1

            elif serialControlObj.r[fireN]['Reload Length(mm)'] == 45:
                SULU_EEPROM[1] = 2
                SULU_EEPROM[2] = 0x0C
                # SULU_EEPROM[2] = 0x18
                SULU_EEPROM[22] = 1

            elif serialControlObj.r[fireN]['Reload Length(mm)'] == 60:
                SULU_EEPROM[1] = 3
                SULU_EEPROM[2] = 0x0C
                # SULU_EEPROM[2] = 0x18
                SULU_EEPROM[22] = 1

            if serialControlObj.r[fireN]['Reload Color'] == 'UNKNOWN':
                SULU_EEPROM[34] = 0
            elif serialControlObj.r[fireN]['Reload Color'] == 'White':
                SULU_EEPROM[34] = 1
            elif serialControlObj.r[fireN]['Reload Color'] == 'Tan':
                SULU_EEPROM[34] = 2
            elif serialControlObj.r[fireN]['Reload Color'] == 'Purple':
                SULU_EEPROM[34] = 3
            elif serialControlObj.r[fireN]['Reload Color'] == 'Black':
                SULU_EEPROM[34] = 4
            elif serialControlObj.r[fireN]['Reload Color'] == 'Gray':
                SULU_EEPROM[34] = 5
            # if data['Reload/Cartridge Color'] == 'UNKNOWN':
            #     SULU_EEPROM[34] = 0

            if serialControlObj.r[fireN]['Reload Length(mm)'] == 72:
                SULU_EEPROM[1] = 3
                SULU_EEPROM[2] = 0x14
                # SULU_EEPROM[2] = 0x18
                SULU_EEPROM[22] = 0

            crc_value = CRC16(0x00, SULU_EEPROM)
            crc_value = hex(crc_value)
            # print('Original CRC: ', crc_value)
            l = len(crc_value)
            crc_second_byte = crc_value[2:(l - 2)]
            crc_first_byte = crc_value[(l - 2):]

            SULU_EEPROM.append(int(crc_first_byte, 16))
            SULU_EEPROM.append(int(crc_second_byte, 16))

            SULU_byte_lst = [170, 69, 2, 1] + SULU_EEPROM
            # print(byte_lst)
            crc_value = calc(bytes(SULU_byte_lst))
            crc_value = int(crc_value, 16)
            SULU_byte_lst.append(crc_value)
            command = bytes(SULU_byte_lst)

            # print('SULU EEPROM', SULU_EEPROM)

            serialControlObj.Switch_ONN_Relay(5, 2)  # B5:R2 - ON
            serialControlObj.Switch_ONN_Relay(5, 6)  # B5:R6 - ON
            serialControlObj.wait(5)
            ser = serial.Serial(serialControlObj.BlackBoxComPort, 9600)
            ############# READ ###################
            #command = bytes(serialControlObj.SULU_EEPROM_command_byte)
            #command = bytes(SULU_EEPROM_command_byte)

            print('SULU command', command)
            ser.write(command)
            serialControlObj.wait(5)
            # print(command)
            s = ser.read(2)
            s = list(s)
            packet_size = s[1]
            read_data = ser.read(packet_size - 2)
            read_data = list(read_data)
            print("==== SULU Reset READ DATA ====")
            print(read_data[1:-1])
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
            serialControl.convertListtoLogFile(Strings_from_PowerPack, str(videoPath + '\\TotalLog.txt'), fileOpenMode='a')
            '''Strings_to_Compare = [' 1Wire Device Reload attached on 1WireBus Reload',
                                  ' P_SIG_RELOAD_SWITCH_EVENT: switch closed',
                                  ' ReloadConnected: Type=SULU, Length=45, Color=Purple',
                                  ' Smart reload', ' SM_NewSystemEventAlert: RELOAD_INSTALLED',
                                  ' EGIA Reload Values, ReloadID(1) Color(3) OneWireID(3074)',
                                  ' GUI_NewState: EGIA_WAIT_FOR_CLAMP_CYCLE_CLOSE']'''
            if serialControlObj.r[fireN]['Reload Type'] == "SULU":
                Strings_to_Compare = locateStringsToCompareFromEvent('SULU Connected',
                                                                 Length=serialControlObj.r[fireN].get('Reload Length(mm)'),
                                                                 Color=serialControlObj.r[fireN].get('Reload Color'))
            elif serialControlObj.r[fireN]['Reload Type'] == "Radial":
                Strings_to_Compare = locateStringsToCompareFromEvent('SULU Connected',
                                                                 Length=60,
                                                                 Color=serialControlObj.r[fireN].get('Reload Color'))

            result = Compare('SULU Connected', Strings_to_Compare, Strings_from_PowerPack)
            serialControlObj.Normal_Firing_Test_Results.append('SULU Connected:'+ result)
            print("Step: SULU Reload Connected")
            print(serialControlObj.Normal_Firing_Test_Results)
            serialControlObj.wait(3)



        if serialControlObj.r[fireN]['Reload Type'] == "MULU":

            videoThread = OLEDRecordingThread.myThread((str(serialControlObj.r['Scenario Num']) + '#' + str(p + 1) +
                                                        serialControlObj.r['Test Scenario'] + '_' +
                                                        serialControlObj.r[fireN][
                                                            'Reload Type'] + '_' + fireN), serialControlObj.videoPath)
            videoThread.start()


            if str(serialControlObj.r[fireN]['Reload Length(mm)']) == 30:
                MULU_EEPROM[1] = 1
                MULU_EEPROM[2] = 0x10
                # MULU_EEPROM[19] = (max(data.get('Num of Firings in Procedure'), 12))
                MULU_EEPROM[19] = 50
                MULU_EEPROM[22] = 1
                CARTRIDGE_EEPROM[1] = 1
                CARTRIDGE_EEPROM[2] = 0x18
            elif serialControlObj.r[fireN]['Reload Length(mm)'] == 45:
                MULU_EEPROM[1] = 2
                MULU_EEPROM[2] = 0x10
                # MULU_EEPROM[19] = (max(data.get('Num of Firings in Procedure'), 12))
                MULU_EEPROM[19] = 12
                # print(value, 'value')
                MULU_EEPROM[22] = 1
                CARTRIDGE_EEPROM[1] = 2
                CARTRIDGE_EEPROM[2] = 0x18

            elif serialControlObj.r[fireN]['Reload Length(mm)'] == 60:
                MULU_EEPROM[1] = 3
                MULU_EEPROM[2] = 0x10
                MULU_EEPROM[22] = 1
                CARTRIDGE_EEPROM[1] = 3
                CARTRIDGE_EEPROM[2] = 0x18
                MULU_EEPROM[19] = 12
                # try:
                #     MULU_EEPROM[19] = (max(data.get('Num of Firings in Procedure'), 12))
                # except:
                #     pass

            if serialControlObj.r[fireN]['Cartridge Color'] == 'UNKNOWN':
                CARTRIDGE_EEPROM[26] = 0
            elif serialControlObj.r[fireN]['Cartridge Color'] == 'White':
                CARTRIDGE_EEPROM[26] = 1
            elif serialControlObj.r[fireN]['Cartridge Color'] == 'Tan':
                CARTRIDGE_EEPROM[26] = 2
            elif serialControlObj.r[fireN]['Cartridge Color'] == 'Purple':
                CARTRIDGE_EEPROM[26] = 3
            elif serialControlObj.r[fireN]['Cartridge Color'] == 'Black':
                CARTRIDGE_EEPROM[26] = 4
            elif serialControlObj.r[fireN]['Cartridge Color'] == 'Gray':
                CARTRIDGE_EEPROM[26] = 5

                ############# MULU CRC ##########################
            crc_value = CRC16(0x00, MULU_EEPROM)
            # print(crc_value)
            # print(type(crc_value), 'type of crc')
            crc_value = hex(crc_value)
            # print('Original CRC: ', crc_value)
            l = len(crc_value)
            if l == 5:
                crc_value = crc_value[:2] + "0" + crc_value[2:]
            crc_second_byte = crc_value[2:4]
            crc_first_byte = crc_value[4:]

        # crc_second_byte = crc_value[2:4]
            # crc_first_byte = crc_value[4:]
            # # print(crc_first_byte)
            # print(crc_second_byte)
            MULU_EEPROM.append(int(crc_first_byte, 16))
            MULU_EEPROM.append(int(crc_second_byte, 16))
            # print(byte_data)
            # print(len(byte_data))
            ######################################
            MULU_byte_lst = [170, 69, 2, 1] + MULU_EEPROM
            # print(byte_lst)
            crc_value = calc(bytes(MULU_byte_lst))
            crc_value = int(crc_value, 16)
            MULU_byte_lst.append(crc_value)
            MULU_command_byte = (MULU_byte_lst)

            crc_value = CRC16(0x00, CARTRIDGE_EEPROM)
            crc_value = hex(crc_value)
            # print('Original CRC: ', crc_value)
            l = len(crc_value)

            if l == 5:
                crc_value = crc_value[:2] + "0" + crc_value[2:]
            crc_second_byte = crc_value[2:4]
            crc_first_byte = crc_value[4:]

            # print(crc_first_byte)
            # print(crc_second_byte)
            CARTRIDGE_EEPROM.append(int(crc_first_byte, 16))
            CARTRIDGE_EEPROM.append(int(crc_second_byte, 16))
            # print(byte_data)
            # print(len(byte_data))
            ######################################
            CARTRIDGE_byte_lst = [170, 69, 2, 1] + CARTRIDGE_EEPROM
            # print(byte_lst)
            crc_value = calc(bytes(CARTRIDGE_byte_lst))
            crc_value = int(crc_value, 16)
            CARTRIDGE_byte_lst.append(crc_value)
            CARTRIDGE_command_byte = (CARTRIDGE_byte_lst)

            # print('MULU EEPROM', MULU_EEPROM)
            # print('CARTRIDGE EEPROM', CARTRIDGE_EEPROM)


            # videoThread = OLEDRecordingThread.myThread(
            #     (serialControlObj.r['Test Scenario'] + '_' + serialControlObj.r['Reload Type'] + '_' + str(i+1)), serialControlObj.videoPath)
            # videoThread.start()
            serialControlObj.Switch_ONN_Relay(5, 2)  # B5:R2 - ON
            serialControlObj.Switch_ONN_Relay(5, 6)  # B5:R6 - ON
            serialControlObj.Switch_OFF_Relay(5, 8)  # B5:R8 - OFF
            serialControlObj.wait(5)
            ser = serial.Serial(serialControlObj.BlackBoxComPort, 9600)
            ############# READ ###################
            command = bytes(MULU_command_byte)
            #                command = bytes(MULU_EEPROM_command_byte)

            print('MULU Commnad', command)
            ser.write(command)
            serialControlObj.wait(5)
            ser.write(command)
            serialControlObj.wait(5)
            ser.write(command)
            serialControlObj.wait(5)
            # print(command)
            s = ser.read(2)
            s = list(s)
            packet_size = s[1]
            read_data = ser.read(packet_size - 2)
            read_data = list(read_data)
            print("==== MULU Reset READ DATA ====")
            print(read_data[1:-1])
            ser.close()
            serialControlObj.Switch_OFF_Relay(5, 2)  # B5:R2 - OFF
            serialControlObj.Switch_OFF_Relay(5, 6)  # B5:R6 - OFF
            serialControlObj.wait(5)

            my_Serthread.clearQue()
            serialControlObj.wait(5)

            if serialControlObj.r[fireN]["Attach Reload & Cartridge Together"] == "Yes":
                my_Serthread.clearQue()
                serialControlObj.wait(5)
                serialControlObj.ConnectingCartridge(CARTRIDGE_command_byte, BlackBoxComPort)
                serialControlObj.ConnectingMULUReload()
                serialControlObj.wait(5)
                Timestamps, Strings_from_PowerPack = ReadingQue(my_Serthread.readQue)
                serialControl.convertListtoLogFile(Strings_from_PowerPack, str(videoPath + '\\TotalLog.txt'),
                                                   fileOpenMode='a')
                '''Strings_to_Compare = [' 1Wire Device Reload attached on 1WireBus Reload',
                                      ' P_SIG_RELOAD_SWITCH_EVENT: switch closed',
                                      ' ReloadConnected: Type=MULU, Length=45, Color=Purple',
                                      ' Smart reload', ' SM_NewSystemEventAlert: RELOAD_INSTALLED',
                                      ' EGIA Reload Values, ReloadID(1) Color(3) OneWireID(3074)',
                                      ' GUI_NewState: EGIA_WAIT_FOR_CLAMP_CYCLE_CLOSE']'''
                Strings_to_Compare = locateStringsToCompareFromEvent('MULU Connected',
                                                                     Length=serialControlObj.r[fireN].get('Reload Length(mm)'))

                result = Compare('MULU Connected', Strings_to_Compare, Strings_from_PowerPack)
                serialControlObj.Normal_Firing_Test_Results.append('MULU Connected:' + result)
                print("Step: MULU Reload Connected")
                print(serialControlObj.Normal_Firing_Test_Results)
                # rlist = {'Test Step': ['MULU Reload Connected'], 'Test Result': [result]}
                # df = df.append(pd.DataFrame(rlist))
                # Timestamps, Strings_from_PowerPack = ReadingQue(my_Serthread.readQue)
                # serialControl.convertListtoLogFile(Strings_from_PowerPack, str(videoPath + '\\TotalLog.txt'),
                #                                    fileOpenMode='a')
                Strings_to_Compare = locateStringsToCompareFromEvent('Cartridge Connected',
                                                                     Length=serialControlObj.r[fireN].get('Reload Length(mm)'),
                                                                     Color=serialControlObj.r[fireN].get('Cartridge Color'))
                result = Compare('Cartridge Connected', Strings_to_Compare, Strings_from_PowerPack)
                serialControlObj.Normal_Firing_Test_Results.append('Cartridge Connected:' + result)
                print("Step: Cartridge Connected")
                print(serialControlObj.Normal_Firing_Test_Results)
                # rlist = {'Test Step': ['Cartridge Connected'], 'Test Result': [result]}
                # df = df.append(pd.DataFrame(rlist))

            if serialControlObj.r[fireN]["Attach Reload & Cartridge Together"] == "No":
                serialControlObj.ConnectingMULUReload()
                serialControlObj.wait(5)
                Timestamps, Strings_from_PowerPack = ReadingQue(my_Serthread.readQue)
                serialControl.convertListtoLogFile(Strings_from_PowerPack, str(videoPath + '\\TotalLog.txt'),
                                                   fileOpenMode='a')
                '''Strings_to_Compare = [' 1Wire Device Reload attached on 1WireBus Reload',
                                      ' P_SIG_RELOAD_SWITCH_EVENT: switch closed',
                                      ' ReloadConnected: Type=MULU, Length=45, Color=Purple',
                                      ' Smart reload', ' SM_NewSystemEventAlert: RELOAD_INSTALLED',
                                      ' EGIA Reload Values, ReloadID(1) Color(3) OneWireID(3074)',
                                      ' GUI_NewState: EGIA_WAIT_FOR_CLAMP_CYCLE_CLOSE']'''
                Strings_to_Compare = locateStringsToCompareFromEvent('MULU Connected',
                                                                     Length=serialControlObj.r[fireN].get(
                                                                         'Reload Length(mm)'))

                result = Compare('MULU Connected', Strings_to_Compare, Strings_from_PowerPack)
                serialControlObj.Normal_Firing_Test_Results.append('MULU Connected:' + result)
                print("Step: MULU Reload Connected")
                print(serialControlObj.Normal_Firing_Test_Results)
                # rlist = {'Test Step': ['MULU Reload Connected'], 'Test Result': [result]}
                # df = df.append(pd.DataFrame(rlist))
                serialControlObj.wait(3)
                if serialControlObj.r[fireN]["Clamp Cycle Test with Cartridge"] == "Yes":
                    my_Serthread.clearQue()
                    serialControlObj.wait(5)
                    serialControlObj.ConnectingCartridge(CARTRIDGE_command_byte, BlackBoxComPort)
                    serialControlObj.wait(5)
                    Timestamps, Strings_from_PowerPack = ReadingQue(my_Serthread.readQue)
                    serialControl.convertListtoLogFile(Strings_from_PowerPack, str(videoPath + '\\TotalLog.txt'),
                                                       fileOpenMode='a')
                    Strings_to_Compare = locateStringsToCompareFromEvent('Cartridge Connected',
                                                                         Length=serialControlObj.r[fireN].get(
                                                                             'Reload Length(mm)'),
                                                                         Color=serialControlObj.r[fireN].get(
                                                                             'Cartridge Color'))
                    result = Compare('Cartridge Connected', Strings_to_Compare, Strings_from_PowerPack)
                    serialControlObj.Normal_Firing_Test_Results.append('Cartridge Connected:' + result)
                    print("Step: Cartridge Connected")
                    print(serialControlObj.Normal_Firing_Test_Results)
                    # rlist = {'Test Step': ['Cartridge Connected'], 'Test Result': [result]}
                    # df = df.append(pd.DataFrame(rlist))

            with nidaqmx.Task() as task:
                task.ao_channels.add_ao_voltage_chan('Dev1/ao0')
                print('1 Channel 1 Sample Write: ')
                print(task.write(1.5))

            # Audio_Tone_Decoding_Thread.ToneDecoding.exitFlag = False
            # tone_thread.start()
            serialControlObj.wait(2)

            my_Serthread.clearQue()
            # tone_thread.clearToneQue()

            serialControlObj.wait(5)
            serialControlObj.Switch_ONN_Relay(2, 5)  # B2:R5 - ON
            serialControlObj.wait(10)
            serialControlObj.Switch_OFF_Relay(2, 5)  # B2:R5 - OFF

            Timestamps, Strings_from_PowerPack = ReadingQue(my_Serthread.readQue)
            serialControl.convertListtoLogFile(Strings_from_PowerPack, str(videoPath + '\\TotalLog.txt'),
                                               fileOpenMode='a')
            '''Strings_to_Compare = [' ****  ENTERING AO EGIA Clamp STATE  ****',
                                  ' SM_NewSystemEventAlert: FULLY_CLAMPED',
                                  ' Piezo: Fully Clamped',
                                  ' GUI_NewState: EGIA_WAIT_FOR_CLAMP_CYCLE_OPEN']'''
            Strings_to_Compare = locateStringsToCompareFromEvent('Clamp Cycle Test Clamping')
            result = Compare('Clamp Cycle Test Clamping', Strings_to_Compare, Strings_from_PowerPack)
            serialControlObj.Normal_Firing_Test_Results.append('Clamp Cycle Test Clamping:' + result)
            print("Step: Clamp Cycle Test Clamping Performed")

            # ListTones = ReadToneQue(100, tone_thread.readToneQue)
            # Tones_to_Compare = locateStringsToCompareFromEvent('Piezo: Clamp Cycle Test Clamping')
            # tone_result = Compare('Piezo: Clamp Cycle Test Clamping', Tones_to_Compare, ListTones)
            # print('tone_result:', tone_result)
            # serialControlObj.Test_Results.append('Piezo - Clamp Cycle Test Clamping:' + tone_result)

            # Audio_Tone_Decoding_Thread.ToneDecoding.exitFlag = True

            with nidaqmx.Task() as task:
                task.ao_channels.add_ao_voltage_chan('Dev1/ao0')
                print('1 Channel 1 Sample Write: ')
                print(task.write(0.0))

            # Audio_Tone_Decoding_Thread.ToneDecoding.exitFlag = False
            # tone_thread.start()
            serialControlObj.wait(2)

            # serialControlObj.wait(3)
            print(serialControlObj.Normal_Firing_Test_Results)
            # rlist = {'Test Step': ['Clamp Cycle Test: Clamping'], 'Test Result': [result]}
            # df = df.append(pd.DataFrame(rlist))

            my_Serthread.clearQue()
            # tone_thread.clearToneQue()

            serialControlObj.wait(5)
            serialControlObj.Switch_ONN_Relay(2, 4)  # B2:R4 - ON
            serialControlObj.wait(10)
            serialControlObj.Switch_OFF_Relay(2, 4)  # B2:R4 - OFF

            Timestamps, Strings_from_PowerPack = ReadingQue(my_Serthread.readQue)
            serialControl.convertListtoLogFile(Strings_from_PowerPack, str(videoPath + '\\TotalLog.txt'),
                                               fileOpenMode='a')
            '''Strings_to_Compare = [' ****  ENTERING AO EGIA Unclamp STATE  ****',
                                  ' EGIA FireRod, FULLY OPEN',
                                  ' SM_NewSystemEventAlert: CLAMPCYCLE_DONE',
                                  ' Piezo: Ready Tone']'''
            if serialControlObj.r[fireN]["Clamp Cycle Test with Cartridge"] == "Yes":
                Strings_to_Compare = locateStringsToCompareFromEvent('Clamp Cycle Test Un-Clamping')

            else:
                Strings_to_Compare = locateStringsToCompareFromEvent('Clamp Cycle Test Un-Clamping')[:-1]

            result = Compare('Clamp Cycle Test Un-Clamping', Strings_to_Compare, Strings_from_PowerPack)
            serialControlObj.Normal_Firing_Test_Results.append('Clamp Cycle Test Un-Clamping:' + result)
            print("Step: Clamp Cycle Test Un-Clamping Performed")
            # rlist = {'Test Step': ['Clamp Cycle Test: Un-Clamping'], 'Test Result': [result]}
            # df = df.append(pd.DataFrame(rlist))

            # ListTones = ReadToneQue(100, tone_thread.readToneQue)
            # Tones_to_Compare = locateStringsToCompareFromEvent('Piezo: Clamp Cycle Test Un-Clamping')
            # tone_result = Compare('Piezo: Clamp Cycle Test Un-Clamping', Tones_to_Compare, ListTones)
            # print('tone_result:', tone_result)
            # serialControlObj.Test_Results.append('Piezo - Clamp Cycle Test Un-Clamping:' + tone_result)
            #
            # Audio_Tone_Decoding_Thread.ToneDecoding.exitFlag = True

            serialControlObj.wait(5)
            print(serialControlObj.Normal_Firing_Test_Results)

            if serialControlObj.r[fireN]["Clamp Cycle Test with Cartridge"] == "No":
                my_Serthread.clearQue()
                serialControlObj.wait(5)
                serialControlObj.ConnectingCartridge(CARTRIDGE_command_byte, BlackBoxComPort)
                serialControlObj.wait(5)
                Timestamps, Strings_from_PowerPack = ReadingQue(my_Serthread.readQue)
                serialControl.convertListtoLogFile(Strings_from_PowerPack, str(videoPath + '\\TotalLog.txt'),
                                                   fileOpenMode='a')
                Strings_to_Compare = locateStringsToCompareFromEvent('Cartridge Connected',
                                                                     Length=serialControlObj.r[fireN].get(
                                                                         'Reload Length(mm)'),
                                                                     Color=serialControlObj.r[fireN].get(
                                                                         'Cartridge Color'))
                result = Compare('Cartridge Connected', Strings_to_Compare, Strings_from_PowerPack)
                serialControlObj.Normal_Firing_Test_Results.append('Cartridge Connected:' + result)
                print("Step: Cartridge Connected")
                print(serialControlObj.Normal_Firing_Test_Results)
                # rlist = {'Test Step': ['Cartridge Connected'], 'Test Result': [result]}
                # df = df.append(pd.DataFrame(rlist))

            # else:
            #     my_Serthread.clearQue()
            #     serialControlObj.wait(5)
            #     serialControlObj.ConnectingCartridge(CARTRIDGE_command_byte, BlackBoxComPort)
            #     serialControlObj.wait(5)
            #     Timestamps, Strings_from_PowerPack = ReadingQue(my_Serthread.readQue)
            #     serialControl.convertListtoLogFile(Strings_from_PowerPack, str(videoPath + '\\TotalLog.txt'),
            #                                        fileOpenMode='a')
            #     Strings_to_Compare = locateStringsToCompareFromEvent('Cartridge Connected',
            #                                                          Length=serialControlObj.r[fireN].get(
            #                                                              'Reload Length(mm)'),
            #                                                          Color=serialControlObj.r[fireN].get(
            #                                                              'Cartridge Color'))
            #     result = Compare('Cartridge Connected', Strings_to_Compare, Strings_from_PowerPack)
            #     serialControlObj.Normal_Firing_Test_Results.append('Cartridge Connected:' + result)
            #     print("Step: Cartridge Connected")
            #     print(serialControlObj.Normal_Firing_Test_Results)
            #     # rlist = {'Test Step': ['Cartridge Connected'], 'Test Result': [result]}
            #     # df = df.append(pd.DataFrame(rlist))

        # Adapter rotation Test

        my_Serthread.clearQue()
        serialControlObj.wait(5)
        serialControlObj.Switch_ONN_Relay(2, 7)  # B2:R7 - ON
        serialControlObj.wait(5)
        serialControlObj.Switch_OFF_Relay(2, 7)  # B2:R7 - OFF
        Timestamps, Strings_from_PowerPack = ReadingQue(my_Serthread.readQue)
        serialControl.convertListtoLogFile(Strings_from_PowerPack, str(videoPath + '\\TotalLog.txt'),
                                           fileOpenMode='a')
        '''Strings_to_Compare = [' ****  ENTERING AO EGIA Rotate CW STATE  ****',
                              ' ****  ENTERING AO EGIA Idle STATE  ****']'''
        Strings_to_Compare = locateStringsToCompareFromEvent('Adapter CW Rotated')
        result = Compare('Adapter CW Rotated', Strings_to_Compare, Strings_from_PowerPack)
        serialControlObj.Test_Results.append('Adapter CW Rotated:' + result)
        print(serialControlObj.Test_Results)
        # rlist = {'Test Step': ['Adapter Rotation'], 'Test Result': [result]}
        # df = df.append(pd.DataFrame(rlist))

        serialControlObj.wait(2)

        # Adapter Right CCW Rotation Test
        my_Serthread.clearQue()
        serialControlObj.wait(5)
        serialControlObj.Switch_ONN_Relay(2, 8)  # B2:R8 - ON
        serialControlObj.wait(5)
        serialControlObj.Switch_OFF_Relay(2, 8)  # B2:R8 - OFF

        Timestamps, Strings_from_PowerPack = ReadingQue(my_Serthread.readQue)
        serialControl.convertListtoLogFile(Strings_from_PowerPack, str(videoPath + '\\TotalLog.txt'),
                                           fileOpenMode='a')
        Strings_to_Compare = locateStringsToCompareFromEvent('Adapter CCW Rotated')

        result = Compare('Adapter CW Rotated', Strings_to_Compare, Strings_from_PowerPack)
        serialControlObj.Test_Results.append('Adapter CCW Rotated:' + result)
        print(serialControlObj.Test_Results)
        #

        # #serialControlObj.wait(2)
        # Adapter Left CW Rotation Test
        my_Serthread.clearQue()
        serialControlObj.wait(5)
        serialControlObj.Switch_ONN_Relay(2, 1)  # B2:R1 - ON
        serialControlObj.wait(5)
        serialControlObj.Switch_OFF_Relay(2, 1)  # B2:R1 - OFF
        Timestamps, Strings_from_PowerPack = ReadingQue(my_Serthread.readQue)
        serialControl.convertListtoLogFile(Strings_from_PowerPack, str(videoPath + '\\TotalLog.txt'),
                                           fileOpenMode='a')
        '''Strings_to_Compare = [' ****  ENTERING AO EGIA Rotate CW STATE  ****',
                              ' ****  ENTERING AO EGIA Idle STATE  ****']'''
        Strings_to_Compare = locateStringsToCompareFromEvent('Adapter CW Rotated')
        result = Compare('Adapter CW Rotated', Strings_to_Compare, Strings_from_PowerPack)
        serialControlObj.Test_Results.append('Adapter CW Rotated:' + result)
        print(serialControlObj.Test_Results)
        # rlist = {'Test Step': ['Adapter Rotation'], 'Test Result': [result]}
        # df = df.append(pd.DataFrame(rlist))

        serialControlObj.wait(2)

        # Adapter Left CCW Rotation Test
        my_Serthread.clearQue()
        serialControlObj.wait(5)
        serialControlObj.Switch_ONN_Relay(2, 2)  # B2:R2 - ON
        serialControlObj.wait(5)
        serialControlObj.Switch_OFF_Relay(2, 2)  # B2:R2 - OFF

        Timestamps, Strings_from_PowerPack = ReadingQue(my_Serthread.readQue)
        serialControl.convertListtoLogFile(Strings_from_PowerPack, str(videoPath + '\\TotalLog.txt'),
                                           fileOpenMode='a')
        Strings_to_Compare = locateStringsToCompareFromEvent('Adapter CCW Rotated')

        result = Compare('Adapter CW Rotated', Strings_to_Compare, Strings_from_PowerPack)
        serialControlObj.Test_Results.append('Adapter CCW Rotated:' + result)
        print(serialControlObj.Test_Results)

        # TEST STEP: Reload Articulation

        if serialControlObj.r[fireN]['Reload Length(mm)'] != 72:
            serialControlObj.Switch_ONN_Relay(2, 6)  # B2:R6 - ON
            serialControlObj.wait(5)
            serialControlObj.Switch_OFF_Relay(2, 6)  # B2:R6 - OFF

            Timestamps, Strings_from_PowerPack = ReadingQue(my_Serthread.readQue)
            serialControl.convertListtoLogFile(Strings_from_PowerPack, str(videoPath + '\\TotalLog.txt'),
                                               fileOpenMode='a')
            Strings_to_Compare = locateStringsToCompareFromEvent('Right Articulation')
            result = Compare('Right Articulation', Strings_to_Compare, Strings_from_PowerPack)
            serialControlObj.Normal_Firing_Test_Results.append('Right Articulation:' + result)
            print(serialControlObj.Normal_Firing_Test_Results)
            #
            my_Serthread.clearQue()
            serialControlObj.wait(5)
            serialControlObj.Switch_ONN_Relay(2, 4)  # B2:R4 - ON
            serialControlObj.wait(7)
            serialControlObj.Switch_OFF_Relay(2, 4)  # B2:R4 - OFF
            Timestamps, Strings_from_PowerPack = ReadingQue(my_Serthread.readQue)
            serialControl.convertListtoLogFile(Strings_from_PowerPack, str(videoPath + '\\TotalLog.txt'),
                                               fileOpenMode='a')
            Strings_to_Compare = locateStringsToCompareFromEvent('Centering Articulation')
            result = Compare('Centering Articulation', Strings_to_Compare, Strings_from_PowerPack)
            serialControlObj.Normal_Firing_Test_Results.append('Centering Articulation:' + result)
            print(serialControlObj.Normal_Firing_Test_Results)
            #
            #
            my_Serthread.clearQue()
            serialControlObj.wait(5)
            serialControlObj.Switch_ONN_Relay(2, 3)  # B2:R3 - ON
            serialControlObj.wait(7)
            serialControlObj.Switch_OFF_Relay(2, 3)  # B2:R3 - OFF

            Timestamps, Strings_from_PowerPack = ReadingQue(my_Serthread.readQue)
            serialControl.convertListtoLogFile(Strings_from_PowerPack, str(videoPath + '\\TotalLog.txt'),
                                               fileOpenMode='a')
            Strings_to_Compare = locateStringsToCompareFromEvent('Left Articulation')
            result = Compare('Left Articulation', Strings_to_Compare, Strings_from_PowerPack)
            serialControlObj.Normal_Firing_Test_Results.append('Left Articulation:' + result)
            print(serialControlObj.Normal_Firing_Test_Results)

            my_Serthread.clearQue()
            serialControlObj.wait(5)
            serialControlObj.Switch_ONN_Relay(2, 4)  # B2:R4 - ON
            serialControlObj.wait(7)
            serialControlObj.Switch_OFF_Relay(2, 4)  # B2:R4 - OFF
            Timestamps, Strings_from_PowerPack = ReadingQue(my_Serthread.readQue)
            serialControl.convertListtoLogFile(Strings_from_PowerPack, str(videoPath + '\\TotalLog.txt'),
                                               fileOpenMode='a')
            Strings_to_Compare = locateStringsToCompareFromEvent('Centering Articulation')
            result = Compare('Centering Articulation', Strings_to_Compare, Strings_from_PowerPack)
            serialControlObj.Normal_Firing_Test_Results.append('Centering Articulation:' + result)
            print(serialControlObj.Normal_Firing_Test_Results)
            serialControlObj.wait(2)
            print("Step: Articulation Done")

        # TEST STEP: Perform Clamp Cycle Test
        if serialControlObj.r[fireN]['Reload Type'] == "SULU" or serialControlObj.r[fireN]['Reload Type'] == "Tri-Staple":
            # TEST STEP: Clamp Cycle Test

            my_Serthread.clearQue()
            serialControlObj.wait(5)

            with nidaqmx.Task() as task:
                task.ao_channels.add_ao_voltage_chan('Dev1/ao0')
                print('1 Channel 1 Sample Write: ')
                print(task.write(1.5))

            # Audio_Tone_Decoding_Thread.ToneDecoding.exitFlag = False
            # tone_thread.start()
            serialControlObj.wait(2)

            # tone_thread.clearToneQue()
            my_Serthread.clearQue()
            serialControlObj.wait(5)
            serialControlObj.Switch_ONN_Relay(2, 5)  # B2:R5 - ON
            serialControlObj.wait(10)
            serialControlObj.Switch_OFF_Relay(2, 5)  # B2:R5 - OFF

            Timestamps, Strings_from_PowerPack = ReadingQue(my_Serthread.readQue)
            serialControl.convertListtoLogFile(Strings_from_PowerPack, str(videoPath + '\\TotalLog.txt'), fileOpenMode='a')
            '''Strings_to_Compare = [' ****  ENTERING AO EGIA Clamp STATE  ****',
                                  ' SM_NewSystemEventAlert: FULLY_CLAMPED',
                                  ' Piezo: Fully Clamped',
                                  ' GUI_NewState: EGIA_WAIT_FOR_CLAMP_CYCLE_OPEN']'''
            Strings_to_Compare = locateStringsToCompareFromEvent('Clamp Cycle Test Clamping')
            result = Compare('Clamp Cycle Test Clamping', Strings_to_Compare, Strings_from_PowerPack)
            serialControlObj.Normal_Firing_Test_Results.append('Clamp Cycle Test Clamping:' + result)
            print("Step: Clamp Cycle Test Clamping Performed")
            # serialControlObj.wait(3)

            # ListTones = ReadToneQue(100, tone_thread.readToneQue)
            # Tones_to_Compare = locateStringsToCompareFromEvent('Piezo: Clamp Cycle Test Clamping:')
            # tone_result = Compare('Piezo: Clamp Cycle Test Clamping:', Tones_to_Compare, ListTones)
            # print('tone_result:', tone_result)
            # serialControlObj.Test_Results.append('Piezo - Clamp Cycle Test Clamping:' + tone_result)
            #
            # Audio_Tone_Decoding_Thread.ToneDecoding.exitFlag = True

            print(serialControlObj.Normal_Firing_Test_Results)

            # rlist = {'Test Step': ['Clamp Cycle Test: Clamping'], 'Test Result': [result]}
            # df = df.append(pd.DataFrame(rlist))
            with nidaqmx.Task() as task:
                task.ao_channels.add_ao_voltage_chan('Dev1/ao0')
                print('1 Channel 1 Sample Write: ')
                print(task.write(0))

            # Audio_Tone_Decoding_Thread.ToneDecoding.exitFlag = False
            # tone_thread.start()
            serialControlObj.wait(2)

            my_Serthread.clearQue()
            # tone_thread.clearToneQue()

            serialControlObj.wait(5)
            serialControlObj.Switch_ONN_Relay(2, 4)  # B2:R4 - ON
            serialControlObj.wait(10)
            serialControlObj.Switch_OFF_Relay(2, 4)  # B2:R4 - OFF

            Timestamps, Strings_from_PowerPack = ReadingQue(my_Serthread.readQue)
            serialControl.convertListtoLogFile(Strings_from_PowerPack, str(videoPath + '\\TotalLog.txt'), fileOpenMode='a')
            '''Strings_to_Compare = [' ****  ENTERING AO EGIA Unclamp STATE  ****',
                                  ' EGIA FireRod, FULLY OPEN',
                                  ' SM_NewSystemEventAlert: CLAMPCYCLE_DONE',
                                  ' Piezo: Ready Tone']'''
            Strings_to_Compare = locateStringsToCompareFromEvent('Clamp Cycle Test Un-Clamping')
            result = Compare('Clamp Cycle Test Un-Clamping', Strings_to_Compare, Strings_from_PowerPack)
            serialControlObj.Normal_Firing_Test_Results.append('Clamp Cycle Test Un-Clamping:' + result)

            # ListTones = ReadToneQue(100, tone_thread.readToneQue)
            # Tones_to_Compare = locateStringsToCompareFromEvent('Piezo: Clamp Cycle Test Un-Clamping')
            # tone_result = Compare('Piezo: Clamp Cycle Test Un-Clamping', Tones_to_Compare, ListTones)
            # print('tone_result:', tone_result)
            # serialControlObj.Test_Results.append('Piezo - Clamp Cycle Test Un-Clamping:' + tone_result)


            print("Step: Clamp Cycle Test Un-Clamping Performed")
            # rlist = {'Test Step': ['Clamp Cycle Test: Un-Clamping'], 'Test Result': [result]}
            # df = df.append(pd.DataFrame(rlist))
            serialControlObj.wait(5)
            print(serialControlObj.Normal_Firing_Test_Results)

            # Audio_Tone_Decoding_Thread.ToneDecoding.exitFlag = True


        # Test Step: Clamping on Tissue

        cf = serialControlObj.ForceDecode(clampingForce)
        with nidaqmx.Task() as task:
            task.ao_channels.add_ao_voltage_chan('Dev1/ao0')
            print('1 Channel 1 Sample Write:')
            print(task.write(cf))

        # my_Serthread.clearQue()
        # serialControlObj.wait(5)
        # serialControlObj.Switch_ONN_Relay(2, 5)  # B2:R5 - ON
        # serialControlObj.wait(15)

        #
        #
        if articulationStateinFiring == 'Right':
            serialControlObj.Switch_ONN_Relay(2, 6)  # B2:R6 - ON
            serialControlObj.wait(10)
            serialControlObj.Switch_OFF_Relay(2, 6)  # B2:R6 - OFF
        elif articulationStateinFiring == 'Left':
            serialControlObj.Switch_ONN_Relay(2, 3)  # B2:R3 - ON
            serialControlObj.wait(10)
            serialControlObj.Switch_OFF_Relay(2, 3)  # B2:R3 - OFF

        # Audio_Tone_Decoding_Thread.ToneDecoding.exitFlag = False
        #tone_thread.start()
        serialControlObj.wait(2)

        my_Serthread.clearQue()
        # tone_thread.clearToneQue()

        serialControlObj.wait(5)
        serialControlObj.Switch_ONN_Relay(2, 5)  # B2:R5 - OFF
        serialControlObj.wait(30)
        serialControlObj.Switch_OFF_Relay(2, 5)  # B2:R5 - OFF

        Timestamps, Strings_from_PowerPack = ReadingQue(my_Serthread.readQue)
        serialControl.convertListtoLogFile(Strings_from_PowerPack, str(videoPath + '\\TotalLog.txt'), fileOpenMode='a')
        '''Strings_to_Compare = [' SM_NewSystemEventAlert: FULLY_CLAMPED',
                              ' GUI_NewState: EGIA_RELOAD_FULLY_CLAMPED',
                              ' Get Allowed To Fire:', '   YES: allowed to fire', ' clampDialIndex = 2',
                              ' LED_On', ' Piezo: Fully Clamped'
                              # part of string can be searched ? value associated is different
                              ]'''
        Strings_to_Compare = locateStringsToCompareFromEvent('Clamping on Tissue')
        result = Compare('Clamping on Tissue', Strings_to_Compare, Strings_from_PowerPack)
        serialControlObj.Normal_Firing_Test_Results.append('Clamping on Tissue:' + result)

        # ListTones = ReadToneQue(1000, tone_thread.readToneQue)
        # Tones_to_Compare = locateStringsToCompareFromEvent('Piezo: Clamping on Tissue')
        # tone_result = Compare('Piezo: Clamping on Tissue', Tones_to_Compare, ListTones)
        # print('tone_result:', tone_result)
        # serialControlObj.Test_Results.append('Piezo - Clamping on Tissue:' + tone_result)

        serialControlObj.wait(2)

        print("Step: Clamping on Tissue")
        print(serialControlObj.Normal_Firing_Test_Results)

        # rlist = {'Test Step': ['Clamping'], 'Test Result': [result]}
        # df = df.append(pd.DataFrame(rlist))

        # TEST STEP: Acknowledge Safety Key (Green LED) for firing
        my_Serthread.clearQue()
        # tone_thread.clearToneQue()

        serialControlObj.wait(5)
        serialControlObj.GreenKeyAck()
        serialControlObj.wait(2)
        Timestamps, Strings_from_PowerPack = ReadingQue(my_Serthread.readQue)
        serialControl.convertListtoLogFile(Strings_from_PowerPack, str(videoPath + '\\TotalLog.txt'), fileOpenMode='a')
        '''Strings_to_Compare = [' P_SIG_GREEN_KEY_PRESS: entering fire mode',
                              ' LED_Blink', ' GUI_NewState: EGIA_ENTERED_FIRE_MODE', 
                              ' clampDialIndex = 2', ' ****  ENTERING AO EGIA Fire Idle STATE  ****',
                              ' Piezo: Enter Fire Mode',
                              ]'''
        Strings_to_Compare = locateStringsToCompareFromEvent('Green Key Ack')
        result = Compare('Green Key Ack', Strings_to_Compare, Strings_from_PowerPack)
        serialControlObj.Normal_Firing_Test_Results.append('Green Key Ack:' + result)
        print("Step: Acknowledged Safety Key (Green LED) for firing")

        # ListTones = ReadToneQue(1000, tone_thread.readToneQue)
        # Tones_to_Compare = locateStringsToCompareFromEvent('Piezo: Green Key Ack')
        # tone_result = Compare('Piezo: Green Key Ack', Tones_to_Compare, ListTones)
        # print('tone_result:', tone_result)
        # serialControlObj.Test_Results.append('Piezo - Green Key Ack:' + tone_result)

        print(serialControlObj.Normal_Firing_Test_Results)
        # rlist = {'Test Step': ['Safety Key: Acknowledged'], 'Test Result': [result]}
        # df = df.append(pd.DataFrame(rlist))

        # TEST STEP: Firing

        # Audio_Tone_Decoding_Thread.ToneDecoding.exitFlag = True


        ff = serialControlObj.ForceDecode(firingForce)
        with nidaqmx.Task() as task:
            task.ao_channels.add_ao_voltage_chan('Dev1/ao0')
            print('1 Channel 1 Sample Write: ')
            print(task.write(ff))

        # Audio_Tone_Decoding_Thread.ToneDecoding.exitFlag = False
        #tone_thread.start()
        serialControlObj.wait(2)

        my_Serthread.clearQue()
        # tone_thread.clearToneQue()

        serialControlObj.wait(5)
        serialControlObj.Switch_ONN_Relay(2, 5)  # B2:R5 - ON
        serialControlObj.wait(30)
        serialControlObj.Switch_OFF_Relay(2, 5)  # B2:R5 - OFF
        Timestamps, Strings_from_PowerPack = ReadingQue(my_Serthread.readQue)
        serialControl.convertListtoLogFile(Strings_from_PowerPack, str(videoPath + '\\TotalLog.txt'), fileOpenMode='a')
        '''Strings_to_Compare = [' GUI_NewState: EGIA_FIRING',
                              ' forceindex = 0', ' GUI_NewState: EGIA_FIRE_COMPLETE',
                              ' Piezo: Complete Fire'
                              ]'''
        Strings_to_Compare = locateStringsToCompareFromEvent('Firing')
        result = Compare('Firing', Strings_to_Compare, Strings_from_PowerPack)
        serialControlObj.Normal_Firing_Test_Results.append('Firing on Tissue:'+ result)
        # rlist = {'Test Step': ['Firing'], 'Test Result': [result]}
        # df = df.append(pd.DataFrame(rlist))

        print("Step: Firing Done")

        # ListTones = ReadToneQue(1000, tone_thread.readToneQue)
        # Tones_to_Compare = locateStringsToCompareFromEvent('Piezo: Firing Complete')
        # tone_result = Compare('Piezo: Firing Complete', Tones_to_Compare, ListTones)
        # print('tone_result:', tone_result)
        # serialControlObj.Test_Results.append('Piezo - Firing Complete:' + tone_result)

        print(serialControlObj.Normal_Firing_Test_Results)
        serialControlObj.wait(7)

        # TEST STEP: Retracting
        rf = serialControlObj.RetractionForceDecode(retractionForce)
        # serialControlObj.wait(1)
        # rf = 0.2*int(rf)
        # Audio_Tone_Decoding_Thread.ToneDecoding.exitFlag = True


        with nidaqmx.Task() as task:
            task.ao_channels.add_ao_voltage_chan('Dev1/ao0')
            print('1 Channel 1 Sample Write: ')
            print(task.write(rf))

        my_Serthread.clearQue()
        serialControlObj.wait(5)
        serialControlObj.Retracting()
        Timestamps, Strings_from_PowerPack = ReadingQue(my_Serthread.readQue)
        serialControl.convertListtoLogFile(Strings_from_PowerPack, str(videoPath + '\\TotalLog.txt'), fileOpenMode='a')
        '''Strings_to_Compare = [' ****  ENTERING AO EGIA Retract STATE  ****',
                              ' GUI_NewState: EGIA_RETRACT_COMPLETE', ' LED_On',
                              ]'''
        Strings_to_Compare = locateStringsToCompareFromEvent('Retracting')
        result = Compare('Retracting', Strings_to_Compare, Strings_from_PowerPack)
        serialControlObj.Normal_Firing_Test_Results.append('Retracting:'+ result)
        print("Step: Retracting Done")
        print(serialControlObj.Normal_Firing_Test_Results)
        serialControlObj.wait(3)
        # rlist = {'Test Step': ['Retraction'], 'Test Result': [result]}
        # df = df.append(pd.DataFrame(rlist))

        with nidaqmx.Task() as task:
            task.ao_channels.add_ao_voltage_chan('Dev1/ao0')
            print('Releasing Brake: ')
            print(task.write(0))

        # TEST STEP: Unclamping
        my_Serthread.clearQue()
        serialControlObj.wait(5)
        serialControlObj.Switch_ONN_Relay(2, 4)  # B2:R4 - ON
        serialControlObj.wait(25)
        serialControlObj.Switch_OFF_Relay(2, 4)  # B2:R4 - OFF
        Timestamps, Strings_from_PowerPack = ReadingQue(my_Serthread.readQue)
        serialControl.convertListtoLogFile(Strings_from_PowerPack, str(videoPath + '\\TotalLog.txt'), fileOpenMode='a')
        '''Strings_to_Compare = [' ****  ENTERING AO EGIA Unclamp STATE  ****',
                              ' EGIA FireRod, FULLY OPEN', ' ****  ENTERING AO EGIA Idle STATE  ****', ' LED_Off'
                              ]'''
        Strings_to_Compare = locateStringsToCompareFromEvent('Unclamping')
        result = Compare('Unclamping', Strings_to_Compare, Strings_from_PowerPack)
        serialControlObj.Normal_Firing_Test_Results.append('Unclamping:' + result)
        print("Step: Unclamping Done")
        print(serialControlObj.Normal_Firing_Test_Results)

        # rlist = {'Test Step': ['Un-Clamping'], 'Test Result': [result]}
        # df = df.append(pd.DataFrame(rlist))
        # TEST STEP: Remove Reload
        #OLEDRecordingThread.exitFlag = True

        if serialControlObj.r[fireN]['Reload Type'] == "SULU" or serialControlObj.r[fireN]['Reload Type'] == "Tri-Staple" :
            my_Serthread.clearQue()
            serialControlObj.wait(5)
            serialControlObj.RemovingSULUReload()
            serialControlObj.wait(5)
            Timestamps, Strings_from_PowerPack = ReadingQue(my_Serthread.readQue)
            serialControl.convertListtoLogFile(Strings_from_PowerPack, str(videoPath + '\\TotalLog.txt'), fileOpenMode='a')
            # Strings_to_Compare = [' GUI_NewState: EGIA_REQUEST_RELOAD']
            Strings_to_Compare = locateStringsToCompareFromEvent('Remove Reload')
            result = Compare('Remove Reload', Strings_to_Compare, Strings_from_PowerPack)
            serialControlObj.Normal_Firing_Test_Results.append('Remove Reload:' + result)
            print("Step: Removed Reload")
            print(serialControlObj.Normal_Firing_Test_Results)
            serialControlObj.wait(2)
            OLEDRecordingThread.exitFlag = True
            serialControlObj.wait(5)

        if serialControlObj.r[fireN]['Reload Type'] == "MULU":
            my_Serthread.clearQue()
            serialControlObj.wait(5)
            serialControlObj.Switch_OFF_Relay(3, 3)  # B3:R3 - OFF
            serialControlObj.Switch_OFF_Relay(3, 4)  # B3:R4 - OFF
            serialControlObj.wait(5)
            Timestamps, Strings_from_PowerPack = ReadingQue(my_Serthread.readQue)
            serialControl.convertListtoLogFile(Strings_from_PowerPack, str(videoPath + '\\TotalLog.txt'), fileOpenMode='a')
            Strings_to_Compare = locateStringsToCompareFromEvent('Remove Cartridge')
            result = Compare('Remove Cartridge', Strings_to_Compare, Strings_from_PowerPack)
            serialControlObj.Normal_Firing_Test_Results.append('Remove Cartridge:' + result)
            print("Step: Cartridge Removed")
            print(serialControlObj.Normal_Firing_Test_Results)
            serialControlObj.wait(2)
            OLEDRecordingThread.exitFlag = True
            serialControlObj.wait(5)

            serialControlObj.RemovingMULUReload()
            serialControlObj.wait(5)



        for item in serialControlObj.Normal_Firing_Test_Results:
            # print(item)
            temp = 'PASS'
            try:
                if (((str.split(item, ':', 1))[1]) == 'PASS'):
                    #serialControlObj.Test_Results.append(serialControlObj.Normal_Firing_Test_Results[0] + ':FAIL')
                    pass
                elif (((str.split(item, ':', 1))[1]) == 'FAIL'):
                    temp ='FAIL'
                    #print(str('Firing =' + str(i + 1) + ':  Failed'))
                    break
            except:
                pass
        if temp == 'PASS':
            firePass = firePass+1
        print('% of Successful Firings: ', int(100*(firePass)/(i+1)))
        #serialControlObj.Test_Results.append(temp)

        MCPThread.readingPowerPack.exitFlag = True
        serPP.close()
        print(serialControlObj.Test_Results)
        HandleFireCount2, HandleProcedureCount = GetHandleUseCount(PowerPackComPort)
        print('After Firing Handle Fire Count:' + str(HandleFireCount2), 'Handle Procedure Count:' + str(HandleProcedureCount))
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
        serialControlObj.wait(1)
        MCPThread.readingPowerPack.exitFlag = False
        my_Serthread = MCPThread.readingPowerPack(serPP, 1000)
        my_Serthread.clearQue()
        my_Serthread.start()

        if (HandleFireCount2-HandleFireCount1) == 1 and (StatusVariables1 == StatusVariables2):
            temp = 'PASS'
        serialControlObj.Test_Results.append('Firing =' + str(i + 1) + ':' + temp)



    # TEST STEP: Remove Adapter
    #serialControlObj.RemovingMULUReload()
    my_Serthread.clearQue()
    serialControlObj.wait(5)
    serialControlObj.removeAdapter()
    serialControlObj.wait(10)
    Timestamps, Strings_from_PowerPack = ReadingQue(my_Serthread.readQue)
    serialControl.convertListtoLogFile(Strings_from_PowerPack, str(videoPath + '\\TotalLog.txt'), fileOpenMode='a')
    Strings_to_Compare = locateStringsToCompareFromEvent('Remove Adapter')
    result = Compare('Remove Adapter', Strings_to_Compare, Strings_from_PowerPack)
    serialControlObj.Test_Results.append('Remove Adapter:' + result)
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
        print(serialControlObj.r['Test Scenario'] + ' % of Successful Executions: ' + str(100 * ((iterPass) / (serialControlObj.r['Num Times to Execute']))))

    #Iteration_Results.append()
    #results_path = serialControlObj.OUTPUT_PATH + '\\Results.xlsx'
    #df.to_excel(results_path)
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
    #serialControlObj.disconnectSerialConnection()

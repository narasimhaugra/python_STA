# @ Updated to include the common Class Call i.e. Serial_Control.py by Varun Pandey on Dec 23, 2021
#@ Updated to include auto searching code for Singia Port by Manoj Vadali 20 Jan 2022
import time

import serial.tools.list_ports

import MCPThread
import OLEDRecordingThread
from Compare import Compare
from EventsStrings import locateStringsToCompareFromEvent
from ReadingQue import ReadingQue
from RelayControlBytes import *
from Serial_Control import serialControl

OnOffChargeCycle_Results = []

def ChargeCycle(r, PowerPackComPort, NCDComPort, results_path,videoPath):
    serialControlObj = serialControl(r=r, NCDComPort=NCDComPort, PowerPackComPort=PowerPackComPort, videoPath=videoPath)
    serialControlObj.OpenSerialConnection()
    serialControlObj.send_decimal_bytes(TURN_OFF_ALL_RELAYS_IN_ALL_BANKS[0])
    #time.sleep(25)
    #print('r', r)
    OnChargerDuration = r['On Charger Duration (Sec)']
    OffChargerDuration = r['Off Charger Duration (Sec)']

    serPP = serial.Serial(PowerPackComPort, 115200, bytesize=8, parity='N', stopbits=1, timeout=0.05, xonxoff=0)
    my_Serthread = MCPThread.readingPowerPack(serPP, 1000)
    my_Serthread.start()

    for i in range(1, r['Num Times to Execute']):
        OLEDRecordingThread.exitFlag = False
        videoThread = OLEDRecordingThread.myThread(r['Test Scenario'] + '_' + '_' + str(i), videoPath)
        videoThread.start()
        my_Serthread.clearQue()
        time.sleep(5)
        serialControlObj.Switch_ONN_Relay(3, 7)
        serialControlObj.Switch_ONN_Relay(3, 8)
        time.sleep(OnChargerDuration+5)

        Timestamps, Strings_from_PowerPack = ReadingQue(my_Serthread.readQue)
        serialControl.convertListtoLogFile(Strings_from_PowerPack, str(videoPath + '\\TotalLog.txt'), fileOpenMode='a')
        Strings_to_Compare = locateStringsToCompareFromEvent('On-Charger')
        result = Compare('On-Charger', Strings_to_Compare, Strings_from_PowerPack)
        OnOffChargeCycle_Results.append('Placed Power Pack on charger iteration:' + str(i))
        OnOffChargeCycle_Results.append(result)
        print(OnOffChargeCycle_Results)

        #MCPThread.readingPowerPack.exitFlag = True

        my_Serthread.clearQue()
        serialControlObj.Switch_OFF_Relay(3, 7)
        serialControlObj.Switch_OFF_Relay(3, 8)

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

        serialControlObj.wait(20)
        Timestamps, Strings_from_PowerPack = ReadingQue(my_Serthread.readQue)
        serialControl.convertListtoLogFile(Strings_from_PowerPack, str(videoPath + '\\TotalLog.txt'), fileOpenMode='a')
        Strings_to_Compare = locateStringsToCompareFromEvent('Remove Signia Power Handle from Charger - Charge Cycle')
        result = Compare('Remove Signia Power Pack from Charger', Strings_to_Compare, Strings_from_PowerPack )
        OnOffChargeCycle_Results.append('Remove  Power from Charger iteration:' + str(i))
        OnOffChargeCycle_Results.append(result)
        print(OnOffChargeCycle_Results)
        time.sleep(OffChargerDuration)

        OLEDRecordingThread.exitFlag = True

    with open("C:\\Python\\sample_result.txt", 'a') as datalog:
        datalog.write('\n'.join(serialControlObj.Test_Results))

    serialControlObj.Switch_ONN_Relay(3, 7)
    serialControlObj.Switch_ONN_Relay(3, 8)
    time.sleep(30)
    serialControlObj.disconnectSerialConnection()
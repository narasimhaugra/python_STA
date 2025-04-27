# @ Updated to include the common Class Call i.e. Serial_Control.py by Varun Pandey on Dec 23, 2021
import time

import serial.tools.list_ports

import MCPThread
import OLEDRecordingThread
# from Read import READ_PowerPack
from Compare import Compare
from EventsStrings import locateStringsToCompareFromEvent
from ReadingQue import ReadingQue
# from NCDSerialConnection import *
from RelayControlBytes import *
from Serial_Control import serialControl as NCD

ShipMode_Results = []

def ShipMode(r, PowerPackComPort, results_path,videoPath):
    serialControlObj = NCD(r=r, PowerPackComPort=PowerPackComPort,videoPath=videoPath)
    serialControlObj.OpenSerialConnection()
    serialControlObj.send_decimal_bytes(TURN_OFF_ALL_RELAYS_IN_ALL_BANKS[0])
    time.sleep(25)
    OnChargerDuration = r['On Charger Duration (Sec)']
    serPP = serial.Serial(PowerPackComPort, 115200, bytesize=8, parity='N', stopbits=1, timeout=0.05, xonxoff=0)
    my_Serthread = MCPThread.readingPowerPack(serPP, 1000)
    OLEDRecordingThread.exitFlag = False
    videoThread = OLEDRecordingThread.myThread(r['Test Scenario'], videoPath)
    videoThread.start()

    for i in range(1,r['Num Times to Execute']):

        my_Serthread.start()
        my_Serthread.clearQue()
        time.sleep(5)

        serialControlObj.Switch_ONN_Relay(2, 5)
        time.sleep(.2)
        serialControlObj.Switch_OFF_Relay(2, 5)
        time.sleep(.2)
        serialControlObj.Switch_ONN_Relay(2, 4)
        serialControlObj.Switch_OFF_Relay(2, 4)
        time.sleep(.2)

        serialControlObj.Switch_ONN_Relay(2, 5)
        time.sleep(.2)
        serialControlObj.Switch_OFF_Relay(2, 5)
        time.sleep(.2)
        serialControlObj.Switch_ONN_Relay(2, 4)
        serialControlObj.Switch_OFF_Relay(2, 4)
        time.sleep(.2)

        serialControlObj.Switch_ONN_Relay(2, 5)
        time.sleep(.2)
        serialControlObj.Switch_OFF_Relay(2, 5)
        time.sleep(.2)
        serialControlObj.Switch_ONN_Relay(2, 4)
        serialControlObj.Switch_OFF_Relay(2, 4)
        time.sleep(.2)

        serialControlObj.Switch_ONN_Relay(3, 5)
        time.sleep(.2)
        serialControlObj.Switch_OFF_Relay(3, 5)
        time.sleep(.2)
        serialControlObj.Switch_ONN_Relay(3, 5)
        serialControlObj.Switch_OFF_Relay(3, 5)
        time.sleep(.2)
        time.sleep(1) # need to update this delay based on delay between ship mode key press and com port failing or keep this loop in try catch logic
        MCPThread.readingPowerPack.exitFlag = True
        # can we read the que after exiting the threat ?
        Timestapms, Strings_from_PowerPack = ReadingQue(my_Serthread.readQue)
        '''Strings_to_Compare = [' SM_NewSystemEventAlert: SYSTEM_SHUTDOWN',
                              ' Piezo: Shut Down',
                              ' Powering off the motorpack!',
                              ]'''
        Strings_to_Compare = locateStringsToCompareFromEvent('Ship Mode')
        result = Compare('Ship Mode', Strings_to_Compare, Strings_from_PowerPack)
        ShipMode_Results.append('Ship Mode iteration:' + str(i))
        ShipMode_Results.append(result)
        print("Step: Ship Mode")
        print(ShipMode_Results)
        time.sleep(3)

        print('Putting Power Pack on Charger to wakeup from Ship Mode')
        serialControlObj.Switch_ONN_Relay(3, 7)
        serialControlObj.Switch_ONN_Relay(3, 8)
        time.sleep(OnChargerDuration + 5)
        serialControlObj.Switch_OFF_Relay(3, 7)
        serialControlObj.Switch_OFF_Relay(3, 8)
        strPort = 'None'
        while (not 'SigniaPowerHandle' in strPort):
            ports = serial.tools.list_ports.comports()
            # strPort = 'None'
            numConnection = len(ports)
            for i in range(0, numConnection):
                port = ports[i]
                strPort = str(port)
                if 'SigniaPowerHandle' in strPort:
                    print(ports[i])

        print('Power Pack removed from Charger')
        MCPThread.readingPowerPack.exitFlag = False
        my_Serthread.start()
        time.sleep(20)
        Timestapms, Strings_from_PowerPack = ReadingQue(my_Serthread.readQue)
        '''Strings_to_Compare = [' GUI_NewState: WELCOME_SCREEN', ' Piezo: All Good', ' Initialization complete',
                              ' SM_NewSystemEventAlert: INIT_COMPLETE', ' systemCheckCompleted complete',
                              ' GUI_NewState: PROCEDURES_REMAINING', ' GUI_NewState: REQUEST_CLAMSHELL',
                              ' Going to standby', ' Turning off OLED']'''
        Strings_to_Compare = locateStringsToCompareFromEvent('Power Pack wakeup from Ship Mode')
        result = Compare('Power Pack wakeup from Ship Mode', Strings_to_Compare, Strings_from_PowerPack)
        ShipMode_Results.append('Power Pack wakeup from Ship Mode iteration:' + str(i))
        ShipMode_Results.append(result)
        print(ShipMode_Results)

        #time.sleep(25)

    serialControlObj.Switch_ONN_Relay(3, 7)
    serialControlObj.Switch_ONN_Relay(3, 8)
    serialControlObj.disconnectSerialConnection()
    MCPThread.readingPowerPack.exitFlag = True
    OLEDRecordingThread.exitFlag = True

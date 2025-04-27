# author - Manoj Vadali
# Ver # 1
# Purpose - To Reset Power Pack
#import serial
import time

import serial.tools.list_ports
from NCDSerialConnection import *
from NCDSerialConnection import serial_control as NCD

import MCPThread
# from Read import READ_PowerPack
from Compare import Compare
from ReadingQue import ReadingQue
from RelayControlBytes import TURN_OFF_ALL_RELAYS_IN_ALL_BANKS

ResettingPP_Results = []

def ResetPP(r, PowerPackComPort, results_path):
    NCD().OpenSerialConnection()
    NCD().send_decimal_bytes(TURN_OFF_ALL_RELAYS_IN_ALL_BANKS[0])
    time.sleep(25)
    OnChargerDuration = r[12]
    serPP = serial.Serial(PowerPackComPort, 115200, bytesize=8, parity='N', stopbits=1, timeout=0.05, xonxoff=0)
    my_Serthread = MCPThread.readingPowerPack(serPP, 1000)

    for i in range (1,r[2]):
        my_Serthread.start()
        my_Serthread.clearQue()
        time.sleep(5)
        NCD().Switch_ONN_Relay(3, 5)
        NCD().Switch_ONN_Relay(3, 6)
        time.sleep(5)
        NCD().Switch_OFF_Relay(3, 5)
        NCD().Switch_OFF_Relay(3, 6)

        time.sleep(1) # need to update this delay based on delay between ship mode key press and com port failing or keep this loop in try catch logic
        MCPThread.readingPowerPack.exitFlag = True

        Timestapms, Strings_from_PowerPack = ReadingQue(my_Serthread.readQue)
        Strings_to_Compare = [' Turning off OLED',
                              ' CTRL-ALT-DEL: Resetting CPU']

        result = Compare('Resetting Power Pack', Strings_to_Compare, Strings_from_PowerPack)
        ResettingPP_Results.append('Resetting Power Pack iteration:',i)
        ResettingPP_Results.append(result)
        print("Step: Ship Mode")
        print(ResettingPP_Results)
        time.sleep(3)

        print('Putting Power Pack on Charger to wakeup from Ship Mode')
        NCD().Switch_ONN_Relay(3, 7)
        NCD().Switch_ONN_Relay(3, 8)
        time.sleep(OnChargerDuration + 5)
        NCD().Switch_OFF_Relay(3, 7)
        NCD().Switch_OFF_Relay(3, 8)
        print('Power Pack removed from Charger')
        time.sleep(25)
        MCPThread.readingPowerPack.exitFlag = True
    NCD().Switch_ONN_Relay(3, 7)
    NCD().Switch_ONN_Relay(3, 8)
    NCD().disconnectSerialConnection()
    MCPThread.readingPowerPack.exitFlag = True

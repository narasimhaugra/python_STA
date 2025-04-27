'''Created by:Manoj Vadali Date: 29- Apr -2022
Ver:1 Function: Placing on charger (disconnects all components and places power pack on charger'''
from Serial_Control import serialControl
from RelayControlBytes import *
import serial
import serial.tools
from ReadStatusVariables import ReadStatusVariables
from StatusVariableOutput import decodeStatusVariable
import time
import nidaqmx
def Power_Pack_Placing_on_Charger(PowerPackComPort, NCDComPort):
    serialControlObj = serialControl(PowerPackComPort=PowerPackComPort, NCDComPort=NCDComPort)
    serialControlObj.OpenSerialConnection()
    with nidaqmx.Task() as task:
        task.ao_channels.add_ao_voltage_chan('Dev1/ao0')
        #print('Releasing the Particle Brake')
        print(task.write(0))

    ports = serial.tools.list_ports.comports()
    numConnection = len(ports)
    for i in range(0, numConnection):
        port = ports[i]
        strPort = str(port)
        if ('SigniaPowerHandle' in strPort):
            # print(ports[i])
            #serialControlObj.disconnectSerialConnection()
            statusListdata = ReadStatusVariables(PowerPackComPort)
            #print(statusListdata, 'statusListdata')
            #serialControlObj.OpenSerialConnection()
            #if statusListdata != 'None':
            if len(statusListdata) != 0:
                returnStatusDataDict= decodeStatusVariable(statusListdata)
                if returnStatusDataDict['Reload_Connected'] == True:
                    print('Unclamping & Disconnecting Reload')
                    serialControlObj.Switch_OFF_ALL_Relays_In_Each_Bank(2)
                    serialControlObj.wait(0.5)
                    serialControlObj.Switch_OFF_ALL_Relays_In_Each_Bank(6)
                    serialControlObj.wait(0.5)
                    serialControlObj.Switch_OFF_Relay(3, 5)
                    serialControlObj.Switch_OFF_Relay(3, 6)
                    serialControlObj.Switch_ONN_Relay(2, 4)
                    serialControlObj.wait(20)
                    serialControlObj.Switch_OFF_Relay(2, 4)
                    serialControlObj.RemovingMULUReload()
                    serialControlObj.RemovingSULUReload()
                    serialControlObj.wait(10)

                if returnStatusDataDict['Adapter_Connected'] == True:
                    #print('Disconnecting Adapter')
                    serialControlObj.Switch_OFF_ALL_Relays_In_Each_Bank(2) # '''can be deleted'''
                    serialControlObj.Switch_OFF_ALL_Relays_In_Each_Bank(1)
                    serialControlObj.wait(10)

                if returnStatusDataDict['Clamshell_Connected'] == True:
                    #print('Disconnecting Clamshell')
                    serialControlObj.Switch_OFF_ALL_Relays_In_Each_Bank(2) # '''can be deleted'''
                    serialControlObj.Switch_OFF_ALL_Relays_In_Each_Bank(1)
                    serialControlObj.wait(10)
            break

    #statusListdata = ReadStatusVariables(PowerPackComPort, NCDComPort)
    #
    # serialControlObj = serialControl(PowerPackComPort=PowerPackComPort, NCDComPort=NCDComPort)
    # serialControlObj.OpenSerialConnection()
    serialControlObj.send_decimal_bytes(TURN_OFF_ALL_RELAYS_IN_ALL_BANKS[0])
    print('Disconnecting all relays')
    serialControlObj.wait(2)
    print('Placing Power Pack On Charger')
    serialControlObj.Switch_ONN_Relay(3, 7)
    time.sleep(.5)
    serialControlObj.Switch_ONN_Relay(3, 8)
    serialControlObj.wait(60)
    serialControlObj.disconnectSerialConnection()
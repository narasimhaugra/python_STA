'''Created by:Manoj Vadali Date: 14- Jan -2022
Ver:1 Function: Reading the status of Power Pack and accessories and reseting it to initial condition before starting the test'''
import os
import time

import nidaqmx
import serial
import serial.tools
import wmi

from ReadStatusVariables import ReadStatusVariables
from RelayControlBytes import *
from Serial_Relay_Control import serialControl
from StatusVariableOutput import decodeStatusVariable

''' EEA Recovery State Information '''
''''***********  Adapter Recovery States  *********************
EEA_REC_INIT                  0  // Adapter Recovery State - Initial State
EEA_REC_CALIBRATE             1  // Adapter Recovery State - Calibrate (OBSOLETE as of Fixed Trocar)
EEA_REC_PRE CLAMP             2  // Adapter Recovery State - Pre-Clamp Home
EEA_REC_CLAMP_STARTED         3  // Adapter Recovery State - Full Open Clamp
EEA_REC_CLAMPING_COMPLETE     4  // Adapter Recovery State - All Clamping Complete
EEA_REC_STAPLE_STARTED        5  // Adapter Recovery State - Staple Started
EEA_REC_STAPLE_COMPLETE       6  // Adapter Recovery State - Staple Complete
EEA_REC_CUT_COMPLETE          7  // Adapter Recovery State - Cut Complete
EEA_REC_TILT_COMPLETE         8  // Adapter Recovery State - Tilt Complete
EEA_REC_TILT_OPEN_STARTED     9  // Adapter Recovery State - Tilt Open Started
EEA_REC_FIRE_RETRACT         10  // Adapter Recovery State - Fire Retract
EEA_REC_SURGSITE_EXTRACT     11  // Adapter Recovery State - Surgical Site Extraction
EEA_REC_LOCKUP               12  // Adapter Recovery State - Lock Up
EEA_REC_ERROR                13  // Adapter Recovery State - Error
'''
EEA_REC_INIT = 0
EEA_REC_CALIBRATE = 1
EEA_REC_PRE_CLAMP = 2
EEA_REC_CLAMP_STARTED = 3
EEA_REC_CLAMPING_COMPLETE = 4
EEA_REC_STAPLE_STARTED = 5
EEA_REC_STAPLE_COMPLETE = 6
EEA_REC_CUT_COMPLETE = 7
EEA_REC_TILT_COMPLETE = 8
EEA_REC_TILTOPEN_STARTED = 9
EEA_REC_FIRE_RETRACT = 10
EEA_REC_SURGSITE_EXTRACT = 11
EEA_REC_LOCKUP = 12
EEA_REC_ERROR = 13

command_PING = b'\xAA\x06\x00\x01\x00\x19'
command_ONEWIRE_GET_CONNECTED = b'\xAA\x06\x00\x45\x00\x2A'

command_ONEWIRE_READ_ADAPTER = b'\xAA\x07\x00\x49\x03\x6E\xFD'


def close_ports():
    # Initializing the wmi constructor
    f = wmi.WMI()

    # Iterating through all the running processes
    for process in f.Win32_Process():

        if process.Name in ["Base.exe", "MasterControlPanel.exe"]:
            print(f"{process.ProcessId}\t{process.Name}")
            print(process.Name)
            result = os.system(f"taskkill /f /im {process.Name}")
            if result == 0:
                print(f'{process.Name} is terminated successfully!')
            else:
                print(f'could not terminate the process: {process.Name}!')
    time.sleep(2)
    pass


def PowerPackInitialization(PowerPackComPort, NCDComPort, FtdiUartComPort, PowerSupplyComPort, test):
    global AdapterState, AdapterRecoveryState
    serialControlObj = serialControl(PowerPackComPort=PowerPackComPort, NCDComPort=NCDComPort,
                                     DCPowerSupplyComPort=PowerSupplyComPort)
    close_ports()

    serialControlObj.OpenSerialConnection()

    with nidaqmx.Task() as task:
        task.ao_channels.add_ao_voltage_chan('Dev1/ao0')
        print('Releasing the Particle Brake')
        print(task.write(0))

    serialControlObj.Switch_OFF_ALL_Relays_In_Each_Bank(4)
    # # # making Initial position to Linear Actuator
    serialControlObj.output_on_off(True, serialControlObj.DcPowerSupplyComPort)

    serialControlObj.applyLoadViaVoltage(8, serialControlObj.DcPowerSupplyComPort)
    serialControlObj.Switch_ONN_Relay(4, 5)
    serialControlObj.Switch_ONN_Relay(4, 6)
    serialControlObj.wait(15)
    serialControlObj.Switch_OFF_Relay(4, 5)
    serialControlObj.Switch_OFF_Relay(4, 6)
    serialControlObj.applyLoadViaVoltage(0, serialControlObj.DcPowerSupplyComPort)
    serialControlObj.output_on_off(False, serialControlObj.DcPowerSupplyComPort)

    # #########################################################################################
    # # Adding Code here is, sometimes Status variables are not coming, so not sure whether
    # # adapter and reload is connected or not
    # # Irrespective of devices connected or not performing adapter reset.
    # ##########################################################################################
    # serObj = serial.Serial(PowerPackComPort, 115200, bytesize=8, parity='N', stopbits=1,
    #                              timeout=3,
    #                              xonxoff=0)
    #
    # if 'EEA' in test:
    #     # ## Reading Adapter Recovery State from the Onewire EEPROM
    #     serObj.write(command_PING)
    #     serObj.write(command_ONEWIRE_GET_CONNECTED)
    #
    #     serObj.write(command_ONEWIRE_READ_ADAPTER)
    #
    #     for retry in range(5):
    #         readData = serObj.read(2)
    #         readData = readData + serObj.read(readData[1] - 2)
    #         readData = [hex(x)[2:].zfill(2) for x in readData]
    #         # print(" One wie read response ", readData)
    #         if (int(readData[3], 16) == 73) and (int(readData[4], 16) == 3):
    #             AdapterState = (((int(readData[65], 16)) * 256) + (int(readData[66], 16)))
    #             break
    #
    #     if AdapterState != EEA_REC_INIT:
    #         print(f'Adapter is in  : state {AdapterState}, performing SSE !')
    #
    #         ## Holding Toogle UP Key to extract the trocar
    #         serialControlObj.Switch_ONN_Relay(2, 4)
    #         serialControlObj.wait(24)
    #         serialControlObj.Switch_OFF_Relay(2, 4)
    #         ## Remove Reload
    #         serialControlObj.Switch_OFF_Relay(5, 8)  # B5:R8 - OFF
    #         serialControlObj.Switch_OFF_Relay(3, 2)  # B3:R2 - OFF
    #         serialControlObj.Switch_OFF_Relay(3, 3)  # B3:R3 - OFF
    #         serialControlObj.wait(2)  # Delay
    #         ## Performing SSE
    #         serialControlObj.Switch_ONN_Relay(2, 1)
    #         serialControlObj.Switch_ONN_Relay(2, 2)
    #         serialControlObj.Switch_ONN_Relay(2, 7)
    #         serialControlObj.Switch_ONN_Relay(2, 8)
    #         serialControlObj.wait(5)
    #         serialControlObj.Switch_OFF_Relay(2, 1)
    #         serialControlObj.Switch_OFF_Relay(2, 2)
    #         serialControlObj.Switch_OFF_Relay(2, 7)
    #         serialControlObj.Switch_OFF_Relay(2, 8)
    #         serialControlObj.wait(30)
    # serObj.close()


    ports = serial.tools.list_ports.comports()
    numConnection = len(ports)
    # print("Num Connections ", numConnection)
    for i in range(0, numConnection):
        port = ports[i]
        strPort = str(port)
        if 'SigniaPowerHandle' in strPort:
            # print(ports[i])
            # serialControlObj.disconnectSerialConnection()
            print("entering into the read status variables")
            statusListdata = ReadStatusVariables(PowerPackComPort)
            print(statusListdata, 'statusListdata')
            # serialControlObj.OpenSerialConnection()
            # if statusListdata != 'None':
            if len(statusListdata) != 0:
                returnStatusDataDict = decodeStatusVariable(statusListdata)
                if returnStatusDataDict['Adapter_Connected']:
                    serPowerPack = serial.Serial(PowerPackComPort, 115200, bytesize=8, parity='N', stopbits=1,
                                                 timeout=3,
                                                 xonxoff=False)
                    if 'EGIA' in test:
                        command_Adapter_1W_Read = b'\xAA\x07\x00\x49\x03\x6E\xFD'
                        serPowerPack.flush()
                        serPowerPack.write(command_Adapter_1W_Read)

                        for s in range(0, 2):
                            try:
                                s = serPowerPack.readline(2)
                                packet_size = s[1]
                                read_data = serPowerPack.read(packet_size - 2)
                                print(read_data, 'read_data')
                                read_data = s + read_data
                                hex_array = [hex(x)[2:] for x in read_data]
                                print('Read_data', s, hex_array)
                                print(int(hex_array[1], 16), int(hex_array[2], 16))
                                time.sleep(.05)
                                if ((int(hex_array[1], 16) == 71) and (int(hex_array[3], 16) == 48)):
                                    # statusListdata = hex_array
                                    # serPP.write(STATUS_STOP)
                                    print('Detected EEA adapter')
                                    print('Resetting the state to Tip Protector Detection')
                                break

                            except:
                                pass

                    if 'EEA' in test:
                        # ## Reading Adapter Recovery State from the Onewire EEPROM
                        serPowerPack.write(command_PING)
                        serPowerPack.write(command_ONEWIRE_GET_CONNECTED)

                        serPowerPack.write(command_ONEWIRE_READ_ADAPTER)

                        for retry in range(5):
                            readData = serPowerPack.read(2)
                            readData = readData + serPowerPack.read(readData[1] - 2)
                            readData = [hex(x)[2:].zfill(2) for x in readData]
                            # print(" One wie read response ", readData)
                            if (int(readData[3], 16) == 73) and (int(readData[4], 16) == 3):
                                AdapterRecoveryState = (((int(readData[65], 16)) * 256) + (int(readData[66], 16)))
                                break

                        # print("AdapterRecoveryState", AdapterRecoveryState)

                        # If Adapter is not in the initial state, then performing SSE
                        if AdapterRecoveryState == EEA_REC_STAPLE_STARTED or \
                                AdapterRecoveryState == EEA_REC_STAPLE_COMPLETE:
                            print(f'Adapter is in  : state {AdapterRecoveryState}, performing recovery !')
                            ## NoStaples Detected State Exit
                            # serialControlObj.EEANoStaplesDetectedStateExit()
                            serialControlObj.Switch_ONN_Relay(2, 4)
                            serialControlObj.wait(24)
                            serialControlObj.Switch_OFF_Relay(2, 4)
                            ## Remove Reload
                            serialControlObj.Switch_OFF_Relay(5, 8)  # B5:R8 - OFF
                            serialControlObj.Switch_OFF_Relay(3, 2)  # B3:R2 - OFF
                            serialControlObj.Switch_OFF_Relay(3, 3)  # B3:R3 - OFF
                            serialControlObj.wait(2)  # Delay
                            ## Performing SSE
                            serialControlObj.Switch_ONN_Relay(2, 1)
                            serialControlObj.Switch_ONN_Relay(2, 2)
                            serialControlObj.Switch_ONN_Relay(2, 7)
                            serialControlObj.Switch_ONN_Relay(2, 8)
                            serialControlObj.wait(5)
                            serialControlObj.Switch_OFF_Relay(2, 1)
                            serialControlObj.Switch_OFF_Relay(2, 2)
                            serialControlObj.Switch_OFF_Relay(2, 7)
                            serialControlObj.Switch_OFF_Relay(2, 8)
                            serialControlObj.wait(30)
                        elif AdapterRecoveryState != EEA_REC_INIT:
                            print(f'Adapter is in  : state {AdapterRecoveryState}, performing SSE !')

                            # Remove Reload
                            # serialControlObj.DisconnectingEEAReload()
                            serialControlObj.Switch_OFF_Relay(5, 8)  # B5:R8 - OFF
                            serialControlObj.Switch_OFF_Relay(3, 2)  # B3:R2 - OFF
                            serialControlObj.Switch_OFF_Relay(3, 3)  # B3:R3 - OFF
                            serialControlObj.wait(2)

                            serialControlObj.Switch_ONN_Relay(2, 1)
                            serialControlObj.Switch_ONN_Relay(2, 2)
                            serialControlObj.Switch_ONN_Relay(2, 7)
                            serialControlObj.Switch_ONN_Relay(2, 8)
                            serialControlObj.wait(5)
                            serialControlObj.Switch_OFF_Relay(2, 1)
                            serialControlObj.Switch_OFF_Relay(2, 2)
                            serialControlObj.Switch_OFF_Relay(2, 7)
                            serialControlObj.Switch_OFF_Relay(2, 8)
                            serialControlObj.wait(30)

                    print('Disconnecting Adapter')
                    serialControlObj.Switch_OFF_ALL_Relays_In_Each_Bank(1)
                    serialControlObj.wait(10)

                if returnStatusDataDict['Reload_Connected']:
                    if 'EGIA' in test:
                        print('Un-clamping & Disconnecting Reload')
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
                        serialControlObj.wait(2)
                    if 'EEA' in test:
                        ## Remove Reload
                        # serialControlObj.DisconnectingEEAReload()
                        serialControlObj.Switch_OFF_Relay(5, 8)  # B5:R8 - OFF
                        serialControlObj.Switch_OFF_Relay(3, 2)  # B3:R2 - OFF
                        serialControlObj.Switch_OFF_Relay(3, 3)  # B3:R3 - OFF
                        serialControlObj.wait(2)  # Delay

                if returnStatusDataDict['Clamshell_Connected']:
                    print('Disconnecting Clamshell')
                    serialControlObj.Switch_OFF_ALL_Relays_In_Each_Bank(1)
                    serialControlObj.wait(10)
            break


    serialControlObj.send_decimal_bytes(TURN_OFF_ALL_RELAYS_IN_ALL_BANKS[0])
    print('Disconnecting all relays')
    serialControlObj.wait(2)
    print('Placing Power Pack On Charger for 60 Seconds')
    serialControlObj.Switch_ONN_Relay(3, 7)
    time.sleep(.5)
    serialControlObj.Switch_ONN_Relay(3, 8)
    serialControlObj.wait(10)

    print('Removing Power Pack from Charger')
    serialControlObj.Switch_OFF_Relay(3, 7)
    time.sleep(.5)
    serialControlObj.Switch_OFF_Relay(3, 8)

    '''strPort = 'SigniaPowerHandle'
    while ('SigniaPowerHandle' in strPort):
        ports = serial.tools.list_ports.comports()
        numConnection = len(ports)
        for i in range(0, numConnection):
            port = ports[i]
            strPort = str(port)
            if 'SigniaPowerHandle' in strPort:
                #print(ports[i])
                strPort = str(port)
                pass'''

    serialControlObj.wait(7)
    strPort = 'None'
    while not 'SigniaPowerHandle' in strPort:
        ports = serial.tools.list_ports.comports()
        # strPort = 'None'
        numConnection = len(ports)
        for i in range(0, numConnection):
            port = ports[i]
            strPort = str(port)
            if 'SigniaPowerHandle' in strPort:
                print(ports[i])
                break
    print('Power Pack Initialization Completed')
    serialControlObj.disconnectSerialConnection()

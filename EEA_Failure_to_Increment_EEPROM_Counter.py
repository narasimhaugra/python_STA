""" Name: EEATotalFiring; Function: Firing EEA adapter
from removing the handle from charger to, clamshell connecting, adapter connecting, tip protector detection, reload detection,
Created by Manoj Vadali, Date: 21-Sep-2022

Updated on 2-July-2024, by Ugra Narasimha : Code Optimization - (Re-factor code) """
import OLEDRecordingThread
from DownloadEventlogs import DownloadEventlogs
from Serial_Relay_Control import serialControl
import os, sys

import MCPThread
from Read_Handle_Fire_Count import GetHandleUseCount
from ReadStatusVariables import ReadStatusVariables
from AdapterReadWrite import *
from Prepare_Output_Json_File import *


def FailuretoIncrementEepromCounter_FiringRecoveryRequirements(json_data, NCDComPort,
                         PowerPackComPort, BlackBoxComPort, USB6351ComPort, ArduinoUNOComPort, FtdiUartComPort,
                         PowerSupplyComPort, OUTPUT_PATH, videoPath, itr, EEA_RELOAD_EEPROM_command_byte, passed_executions):
    print(f"-----------------    {json_data['Test Scenario']}  -------------------")
    serialControlObj = serialControl(json_data=json_data, NCDComPort=NCDComPort, PowerPackComPort=PowerPackComPort,
                                     BlackBoxComPort=BlackBoxComPort, FtdiUartComPort=FtdiUartComPort,
                                     USB6351ComPort=USB6351ComPort, ArduinoUNOComPort=ArduinoUNOComPort,
                                     DCPowerSupplyComPort=PowerSupplyComPort,
                                     OUTPUT_PATH=OUTPUT_PATH, videoPath=videoPath, itr=itr,
                                     EEA_RELOAD_EEPROM_command_byte=EEA_RELOAD_EEPROM_command_byte)
    serialControlObj.OpenSerialConnection()
    Failure_to_Increment_Eeprom_Counter_Firing_Recovery_Requirements(serialControlObj, videoPath, itr,
                                                                     passed_executions, PowerPackComPort, NCDComPort)
    serialControlObj.disconnectSerialConnection()


# Purpose-To perform Normal Firing Scenarios
def Failure_to_Increment_Eeprom_Counter_Firing_Recovery_Requirements(serialControlObj, videoPath, itr,
                                                                     passed_executions, PowerPackComPort, NCDComPort):
    success_flag = True

    serialControlObj.battery_level_check()

    serialControlObj.startup_log()


    scenario_number = serialControlObj.json_data['Scenario Num']
    test_scenario = serialControlObj.json_data['Test Scenario']

    print(f"-----------------    {scenario_number}_{test_scenario}  -------------------")

    video_name = f"{scenario_number}_{test_scenario}"
    videoThread = OLEDRecordingThread.myThread(video_name, videoPath)
    videoThread.start()
    serialControlObj.video_thread = videoThread

    serialControlObj.connectClamshellTest(success_flag=success_flag)

    serialControlObj.connect_adapter_test()

    serialControlObj.wait(10)

    serialControlObj.EEA_adapter_reset()

    serialControlObj.Switch_OFF_Relay(2, 1)
    serialControlObj.Switch_OFF_Relay(2, 2)
    serialControlObj.Switch_OFF_Relay(2, 7)
    serialControlObj.Switch_OFF_Relay(2, 8)

    serialControlObj.wait(15)

    serialControlObj.removeAdapter_DV()

    serialControlObj.wait(4)

    # Record Power Pack and Adapter usage counts
    serialControlObj.Switch_ONN_Relay(1, 8)
    serialControlObj.wait(7)
    print("EEA Adapter Engaged to Power Pack Mechanically")

    MCPThread.readingPowerPack.exitFlag = True
    # serialControlObj.serPP.close()
    serialControlObj.wait(2)

    # Reading Power Pack Usage Counts
    PowerPackFiringCount, PowerPackProcedureCount = GetHandleUseCount(serialControlObj.PowerPackComPort)
    print("PowerPackFiringCount : , PowerPackProcedureCount : ", PowerPackFiringCount, PowerPackProcedureCount)

    # Reading Adapter EEPROM Usage Counts
    AdapterEEPROMProcedureCount, AdapterEEPROMFireCount = GetAdapterEepromUsageCounts(serialControlObj.FtdiUartComPort)
    print("AdapterEEPROMProcedureCount : , AdapterEEPROMFireCount : ", AdapterEEPROMProcedureCount, AdapterEEPROMFireCount)

    # Reading Adapter One-Wire Usage Counts
    serialControlObj.Switch_ONN_Relay(5, 5)
    serialControlObj.Switch_ONN_Relay(6, 1)

    adapter_1w_eeprom_data = serialControlObj.read_eeprom_data()
    # print("Adapter Onewire EEPROM Data ", adapter_1w_eeprom_data)
    print(list(map(hex, adapter_1w_eeprom_data)))

    data = [hex(x)[2:].zfill(2) for x in adapter_1w_eeprom_data]
    fireCnt = data[3:5]
    precCnt = data[7:9]
    AdapterOwFireCount = convert_single_list_ele_to_two_byte_decimal(fireCnt)
    AdapterOwProcedureCount = convert_single_list_ele_to_two_byte_decimal(precCnt)

    serialControlObj.Switch_OFF_Relay(6, 1)
    serialControlObj.Switch_OFF_Relay(5, 5)

    print('Handle Fire Count:' + str(PowerPackFiringCount),
          'Handle Procedure Count:' + str(PowerPackProcedureCount))
    print('Adapter Eeprom Fire Count:' + str(AdapterEEPROMFireCount),
          'Adapter Eeprom Procedure Count:' + str(AdapterEEPROMProcedureCount))
    print('Adapter Onewire Fire Count:' + str(AdapterOwFireCount),
          'Adapter Onewire Procedure Count:' + str(AdapterOwProcedureCount))

    serialControlObj.wait(4)

    serialControlObj.connect_adapter_test()

    serialControlObj.wait(4)

    total_firings = 1
    try:
        total_firings = len(serialControlObj.json_data['Total number of firings'])
    except Exception as Ex:
        print(f"Exception Occurred! {Ex}")

    for i in range(total_firings):

        fireN = 'Fire' + str(i + 1)

        senario_number = serialControlObj.json_data['Scenario Num']
        test_scenario = serialControlObj.json_data['Test Scenario']
        try:
            # len(serialControlObj.json_data['Total firings'])
            data = serialControlObj.json_data[fireN]
        except Exception as Ex:
            print(f"It seems like Normal firing! {Ex}")
            data = serialControlObj.json_data

        reload_type = data['Reload Type']
        # video_name = (str(senario_number) + '#' + str(itr + 1) + test_scenario + '_' + reload_type + '_' + fireN)

        clampingForce = data['Clamping Force']
        firingForce = data['Firing Force']
        retractionForce = data['Retraction Force']

        reload_length = data['Reload Diameter(mm)']
        procedure_firings_count = data['Num of Firings in Procedure']
        ship_cap_status = data['Ship cap Present']

        #### Make Sense to remove this for EEA ? ## RU
        reload_color = None
        cartridge_color = None
        reload_state = "GOOD"
        cartridge_state = "GOOD"
        try:
            reload_state = data['Reload State']
        except Exception as Ex:
            print(f"Reload state is not present in the present firing configs. Hence by default reload_state is "
                  f"taken as GOOD \n{Ex}")

        reload_color = data['Reload Color']

        reload_parameters = {"firing_count": fireN, "reload_type": reload_type, "reload_length": reload_length,
                             "video_name": video_name, "reload_color": reload_color, "reload_state": reload_state,
                             "cartridge_state": cartridge_state, "cartridge_color": cartridge_color,
                             "procedure_firings_count": procedure_firings_count, "ship_cap_presence": ship_cap_status}

        # Firing Test
        serialControlObj.increment_Eeprom_counter_failuer_test(clampingForce=clampingForce, firingForce=firingForce,
                                     reload_parameters=reload_parameters)
    # # removing adapter
    # serialControlObj.removeAdapter()

    # removing clamshell
    serialControlObj.removeClamshell()

    serialControlObj.test_results_pass_percentage(passed_executions=passed_executions)

    # DownloadEventlogs(videoPath, PowerPackComPort, NCDComPort)


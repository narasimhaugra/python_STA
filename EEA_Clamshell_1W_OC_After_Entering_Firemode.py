""" Name: EEATotalFiring; Function: Firing EEA adapter
from removing the handle from charger to, clamshell connecting, adapter connecting, tip rpotector detection, remolad detection,
Created by Manoj Vadali, Date: 21-Sep-2022

Updated on 23-July-2024, by Ugra Narasimha : Code Optimization - (Re-factor code) """

import sys

import MCPThread
import OLEDRecordingThread
from DownloadEventlogs import DownloadEventlogs
from Prepare_Output_Json_File import *
from Serial_Relay_Control import serialControl


def EEA_Clamshell_1W_OC_After_Entering_Firemode(json_data, NCDComPort,
                                                PowerPackComPort, BlackBoxComPort, USB6351ComPort, ArduinoUNOComPort,
                                                FtdiUartComPort, PowerSupplyComPort, OUTPUT_PATH, videoPath, itr,
                                                EEA_RELOAD_EEPROM_command_byte, passed_executions):
    print(f"-----------------    {json_data['Test Scenario']}  -------------------")
    serialControlObj = serialControl(json_data=json_data, NCDComPort=NCDComPort, PowerPackComPort=PowerPackComPort,
                                     BlackBoxComPort=BlackBoxComPort, FtdiUartComPort=FtdiUartComPort,
                                     USB6351ComPort=USB6351ComPort, ArduinoUNOComPort=ArduinoUNOComPort,
                                     DCPowerSupplyComPort=PowerSupplyComPort,
                                     OUTPUT_PATH=OUTPUT_PATH, videoPath=videoPath, itr=itr,
                                     EEA_RELOAD_EEPROM_command_byte=EEA_RELOAD_EEPROM_command_byte)
    serialControlObj.OpenSerialConnection()
    EEA_Clamshell_1W_Open_Circuit_After_Entering_Firemode(serialControlObj, videoPath, itr,
                                                          passed_executions, PowerPackComPort, NCDComPort)
    serialControlObj.disconnectSerialConnection()


# Purpose-To perform Normal Firing Scenarios
def EEA_Clamshell_1W_Open_Circuit_After_Entering_Firemode(serialControlObj, videoPath, itr,
                                                          passed_executions, PowerPackComPort, NCDComPort):
    success_flag = True

    serialControlObj.battery_level_check()

    serialControlObj.startup_log()

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

    serialControlObj.connect_adapter_test()

    serialControlObj.wait(4)

    total_firings = 1
    try:
        # total_firings = len(serialControlObj.json_data['Total firings'])
        total_firings = len(serialControlObj.json_data['Total number of firings'])
    except Exception as Ex:
        # total_firings = serialControlObj.json_data['Num Times to Execute']
        print(f"Exception Occurred! {Ex}")

    for i in range(total_firings):

        fireN = 'Fire' + str(i + 1)

        scenario_number = serialControlObj.json_data['Scenario Num']
        test_scenario = serialControlObj.json_data['Test Scenario']
        try:
            # len(serialControlObj.json_data['Total firings'])
            data = serialControlObj.json_data[fireN]
        except Exception as Ex:
            print(f"It seems like Normal firing!")
            data = serialControlObj.json_data

        reload_type = data['Reload Type']
        video_name = (str(scenario_number) + '#' + str(itr + 1) + test_scenario + '_' + reload_type + '_' + fireN)

        clampingForce = data['Clamping Force']
        firingForce = data['Firing Force']
        articulationStateinFiring = None
        # numberOfFiringsinProcedure = data['Num of Firings in Procedure']
        retractionForce = data['Retraction Force']

        reload_length = data['Reload Diameter(mm)']
        procedure_firings_count = data['Num of Firings in Procedure']
        ship_cap_status = data['Ship cap Present']
        scenario = data['Test Scenario']

        reload_color = data['Reload Color']
        cartridge_color = None
        reload_state = "GOOD"
        cartridge_state = "GOOD"
        try:
            reload_state = data['Reload State']
        except Exception as Ex:
            print(f"Reload state is not present in the present firing configs. Hence by default reload_state is "
                  f"taken as GOOD \n{Ex}")

        reload_parameters = {"firing_count": fireN, "reload_type": reload_type, "reload_length": reload_length,
                             "video_name": video_name, "reload_color": reload_color, "reload_state": reload_state,
                             "cartridge_state": cartridge_state, "cartridge_color": cartridge_color,
                             "procedure_firings_count": procedure_firings_count, "ship_cap_presence": ship_cap_status}

        # Firing Test
        serialControlObj.clamshell_1w_OC_after_firing(clampingForce=clampingForce, firingForce=firingForce,
                                                      reload_parameters=reload_parameters)
    # removing adapter
    logs_to_compare = 'Remove EEA Adapter with Clamshell 1W Open Circuit'
    serialControlObj.removeAdapter(logs_to_compare)

    # removing clamshell
    logs_to_compare = 'Remove EEA Adapter with Clamshell 1W Open Circuit'
    serialControlObj.removeClamshell(logs_to_compare)

    serialControlObj.test_results_pass_percentage(passed_executions=passed_executions)

    #DownloadEventlogs(videoPath, PowerPackComPort, NCDComPort)

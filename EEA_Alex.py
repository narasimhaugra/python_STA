""" Name: EEATotalFiring; Function: Firing EEA adapter
from removing the handle from charger to, clamshell connecting, adapter connecting, tip protector detection, reload detection,
Created by Manoj Vadali, Date: 21-Sep-2022

Updated on 2-July-2024, by Ugra Narasimha : Code Optimization - (Re-factor code) """

import sys
import MCPThread
import OLEDRecordingThread
from Prepare_Output_Json_File import *
from Serial_Relay_Control import serialControl


def AlexEEA(json_data, NCDComPort,
                     PowerPackComPort, BlackBoxComPort, USB6351ComPort, ArduinoUNOComPort, OUTPUT_PATH, videoPath, itr,
                     EEA_RELOAD_EEPROM_command_byte, passed_executions):
    print(f"-----------------    {json_data['Test Scenario']}    -----------------")
    serialControlObj = serialControl(json_data=json_data, NCDComPort=NCDComPort, PowerPackComPort=PowerPackComPort,
                                     BlackBoxComPort=BlackBoxComPort,
                                     USB6351ComPort=USB6351ComPort, ArduinoUNOComPort=ArduinoUNOComPort,
                                     OUTPUT_PATH=OUTPUT_PATH, videoPath=videoPath, itr=itr,
                                     EEA_RELOAD_EEPROM_command_byte=EEA_RELOAD_EEPROM_command_byte)
    serialControlObj.OpenSerialConnection()
    # Normal_Firing(serialControlObj) #, PowerPackComPort)
    EEA_IS_Total_Firing(serialControlObj, videoPath, itr, passed_executions)
    serialControlObj.disconnectSerialConnection()


# Purpose-To perform Normal Firing Scenarios
def EEA_IS_Total_Firing(serialControlObj, videoPath, itr, passed_executions):
    success_flag = True

    serialControlObj.battery_level_check()

    serialControlObj.startup_log()

    serialControlObj.connectClamshellTest(success_flag=success_flag)

    serialControlObj.connect_adapter_test()

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
        video_name = (str(senario_number) + '#' + str(itr + 1) + test_scenario + '_' + reload_type + '_' + fireN)

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

        if reload_type.upper() != "MULU":
            reload_color = data['Reload Color']

        reload_parameters = {"firing_count": fireN, "reload_type": reload_type, "reload_length": reload_length,
                             "video_name": video_name, "reload_color": reload_color, "reload_state": reload_state,
                             "cartridge_state": cartridge_state, "cartridge_color": cartridge_color,
                             "procedure_firings_count": procedure_firings_count, "ship_cap_presence": ship_cap_status}

        # Firing Test
        serialControlObj.Alex_firing_test(clampingForce=clampingForce, firingForce=firingForce,
                                     retractionForce=retractionForce, reload_parameters=reload_parameters,
                                     articulationStateinFiring=None)
    # removing adapter
    serialControlObj.removeAdapter()

    # removing clamshell
    serialControlObj.removeClamshell()

    serialControlObj.test_results_pass_percentage(passed_executions=passed_executions)


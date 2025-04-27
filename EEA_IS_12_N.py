""" Name: EEA Recovery Requirements Function: Firing and Cutting RecoveryRequirements
Checks Performed During Stapling Recovery and Cutting Recovery Providing correct options
During firing recovery calibration fails or not,
Created by Ugra Narasimha, Date: 19-May-2024"""
import time

import sys

import OLEDRecordingThread
from Prepare_Output_Json_File import *
import MCPThread
from Serial_Relay_Control import serialControl


def T98_FiringRecovery_FiringRecoveryRequirements(json_data, SULU_EEPROM_command_byte,
                                                  MULU_EEPROM_command_byte,
                                                  CARTRIDGE_EEPROM_command_byte,
                                                  NCDComPort, PowerPackComPort, BlackBoxComPort,
                                                  USB6351ComPort,
                                                  ArduinoUNOComPort, OUTPUT_PATH, videoPath, itr,
                                                  EEA_RELOAD_EEPROM_command_byte,
                                                  passed_executions):
    print(f"-----------------    {json_data['Test Scenario']}  -------------------")
    print('------------------- EEA Recovery Items Verification Case 1 --------------')
    serialControlObj = serialControl(json_data=json_data, NCDComPort=NCDComPort, PowerPackComPort=PowerPackComPort,
                                     BlackBoxComPort=BlackBoxComPort,
                                     USB6351ComPort=USB6351ComPort, ArduinoUNOComPort=ArduinoUNOComPort,
                                     OUTPUT_PATH=OUTPUT_PATH, videoPath=videoPath, itr=itr,
                                     EEA_RELOAD_EEPROM_command_byte=EEA_RELOAD_EEPROM_command_byte)
    serialControlObj.OpenSerialConnection()
    T98_Firing_Recovery_Firing_Recovery_Requirements(serialControlObj, videoPath, itr,
                                                     passed_executions)
    serialControlObj.disconnectSerialConnection()


# Purpose-To perform recovery Items Failure Scenarios
def T98_Firing_Recovery_Firing_Recovery_Requirements(serialControlObj, videoPath, itr, passed_executions):
    """
    ###################################################################################################################
    ## CASE 1: Firing Recovery
    ###################################################################################################################
    """
    ## STEP 1: Removing Handle From The Charger
    success_flag = True
    serialControlObj.battery_level_check()
    serialControlObj.startup_log()

    ## STEP 2: Clamshell Connected
    serialControlObj.connectClamshellTest(success_flag=success_flag)

    ## STEP 3: Record Power Pack and Adapter usage Counts
    # For capturing Adapter Usage Counts - Adapter needs to be connected Mechanically
    # Engaging the Adapter - Controlling the stepper motor
    firingCount = 0
    serialControlObj.RecordPowerPackAndAdapterUsageCounts(firingCont=firingCount)

    ## STEP 4: Adapter Connected With INIT State.
    serialControlObj.connect_adapter_test()

    ## STEP 5: Connecting EEA Reload Along with Ship Cap Presence Check
    ## STEP 6: Extension of Trocar
    ## STEP 7: Clamping on Tissue - Retraction of Trocar Until Clamp GAP is reached
    ## STEP 8: Safety Key Acknowledgement
    ## STEP 9: Firing
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

        data = serialControlObj.json_data

        reload_type = data['Reload Type']
        video_name = (str(scenario_number) + '#' + str(itr + 1) + test_scenario + '_' + reload_type + '_' + fireN)

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

        reload_parameters = {"firing_count": fireN, "reload_type": reload_type, "reload_length": reload_length,
                             "video_name": video_name, "reload_color": reload_color, "reload_state": reload_state,
                             "cartridge_state": cartridge_state, "cartridge_color": cartridge_color,
                             "procedure_firings_count": procedure_firings_count, "ship_cap_presence": ship_cap_status}

        # Firing Test
        firingValue = 1
        during_1st_EEA_stapling = 1
        case_id = 1
        test_parameters = {"firing_number": firingValue, "adapter_removed_1st_eea_stapling": during_1st_EEA_stapling,
                           "case_id": case_id}
        serialControlObj.EEA_IS_12_N_Firing(test_parameters=test_parameters, reload_parameters=reload_parameters)

    ## STEP 10: Verifying Recovery ID data
    serialControlObj.VerifyRecoveryIDData()

    ## STEP 11: Re-Attaching the Adapter to the Power Pack
    serialControlObj.connect_adapter_test(adapter_type="sip In-progress")

    ## STEP 12: Performing Rotation, Articulation and Close Operation
    # Right CW Rotation
    serialControlObj.eea_right_clockwise_rotation()

    # Left Articulation
    serialControlObj.eea_left_articulation()

    # Close Key Operation
    serialControlObj.eea_close_key_operation()

    ## STEP 13: Holding Rotation Buttons
    occurrence = 12_1
    serialControlObj.EEASurgicalSiteExtractionStateExit(occurence=occurrence)

    ## STEP 14: Staples Detected Exit State - Fully open position
    # No staples detected State Exit, Full Open position, SSE.
    serialControlObj.EEANoStaplesDetectedStateExit()

    ## STEP 15: Remove Reload
    protocol_id = 12
    serialControlObj.DisconnectingEEAReload(protocol_id=protocol_id)

    ## STEP 16: Surgical Site Extraction (SSE)
    occurrence = 12_2
    serialControlObj.EEASurgicalSiteExtractionStateExit(occurence=occurrence)

    ## STEP 17: Remove Adapter
    serialControlObj.removeAdapter()

    ## STEP 18: Record Adapter usage Counts - Adapter Firing and Procedure Count Incremented by 1
    # For capturing Adapter Usage Counts - Adapter needs to be connected Mechanically
    # Engaging the Adapter - Controlling the stepper motor
    firingCount = 4
    serialControlObj.RecordPowerPackAndAdapterUsageCounts(firingCont=firingCount)

    ## STEP 19: Re-Connecting the adapter with INIT State
    serialControlObj.connect_adapter_test()

    ## STEP 20: Attaching EEA reload along with ship cap presence check
    ## STEP 21: Extension of Trocar
    ## STEP 22: Clamping on Tissue - Retraction of Trocar Until Clamp GAP is reached
    ## STEP 23: Safety Key Acknowledgement
    ## STEP 24: Firing
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

        data = serialControlObj.json_data

        reload_type = data['Reload Type']
        video_name = (str(scenario_number) + '#' + str(itr + 1) + test_scenario + '_' + reload_type + '_' + fireN)

        reload_length = data['Reload Diameter(mm)']
        procedure_firings_count = data['Num of Firings in Procedure']
        ship_cap_status = data['Ship cap Present']

        reload_color = None
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
        firingValue = 2
        during_2st_EEA_stapling = 2
        case_id = 1
        test_parameters = {"firing_number": firingValue, "adapter_removed_2nd_eea_stapling": during_2st_EEA_stapling,
                           "case_id": case_id}
        serialControlObj.EEA_IS_12_N_Firing(test_parameters=test_parameters, reload_parameters=reload_parameters)

    ## STEP 25: Verifying Recovery ID data
    serialControlObj.VerifyRecoveryIDData()

    ## STEP 26: Re-Attaching the Adapter to the Power Pack
    serialControlObj.connect_adapter_test(adapter_type="after sip In-progress")

    ## STEP 27: Performing Rotation, Articulation and Close Operation
    # Right CW Rotation
    serialControlObj.eea_right_clockwise_rotation()

    # Left Articulation
    serialControlObj.eea_left_articulation()

    # Close Key Operation
    serialControlObj.eea_close_key_operation()

    ## STEP 28: Holding Rotation Buttons
    occurrence = 12_1
    serialControlObj.EEASurgicalSiteExtractionStateExit(occurence=occurrence)

    ## STEP 29: Staples Detected Exit State - Fully open position
    serialControlObj.EEANoStaplesDetectedStateExit()

    ## STEP 30: Remove Reload
    protocol_id = 12
    serialControlObj.DisconnectingEEAReload(protocol_id=protocol_id)

    ## STEP 31: Surgical Site Extraction (SSE)
    occurrence = 12_2
    serialControlObj.EEASurgicalSiteExtractionStateExit(occurence=occurrence)

    ## STEP 32: Remove Adapter
    serialControlObj.removeAdapter()

    ## STEP 33: Record Adapter usage Counts - Adapter Firing and Procedure Count Incremented by 1
    # For capturing Adapter Usage Counts - Adapter needs to be connected Mechanically
    # Engaging the Adapter - Controlling the stepper motor
    firingCount = 4
    serialControlObj.RecordPowerPackAndAdapterUsageCounts(firingCont=firingCount)

    ## STEP 34: DisEngage the Adapter Clutch
    serialControlObj.Switch_OFF_Relay(1, 8)
    print('Adapter Clutch Disengaged')

    ## STEP 35: Remove Clamshell
    serialControlObj.removeClamshell()

    temp2 = 'PASS'
    for item in serialControlObj.Test_Results:
        try:
            if not item[0] == ' ':
                if ((item.split(":")[1]).strip()) == 'PASS':
                    # serialControlObj.Test_Results.append(serialControlObj.Normal_Firing_Test_Results[0] + ':FAIL')
                    pass
                elif ((item.split(":")[1]).strip()) == 'FAIL':
                    temp2 = 'FAIL'
                    print(f"Item = {item}")
                    # print(str((serialControlObj.Test_Results[0] + ':  Failed')))
                    break
        except Exception as Ex:
            print(f"Exception Occurred. {item} does not have the ':'. {Ex}")

    if temp2 == 'PASS':
        passed_executions[f"{serialControlObj.json_data['Test Scenario']}_{itr}"] = "PASS"

    print(serialControlObj.json_data['Test Scenario'] + ' % of Successful Executions: ' +
          str(100 * ((len(passed_executions)) / (serialControlObj.json_data['Num Times to Execute']))))

    serialControlObj.my_Serthread.clearQue()
    serialControlObj.wait(5)
    MCPThread.readingPowerPack.exitFlag = True
    serialControlObj.serPP.close()
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
    print('------------------- EEA Firing Recovery Requirements Case 1 End --------------')


##################################################################################################################################################

def T99_CuttingRecovery_FiringRecoveryRequirements(json_data, SULU_EEPROM_command_byte,
                                                   MULU_EEPROM_command_byte,
                                                   CARTRIDGE_EEPROM_command_byte,
                                                   NCDComPort, PowerPackComPort, BlackBoxComPort,
                                                   USB6351ComPort,
                                                   ArduinoUNOComPort, OUTPUT_PATH, videoPath, itr,
                                                   EEA_RELOAD_EEPROM_command_byte,
                                                   passed_executions):
    print(f"-----------------    {json_data['Test Scenario']}  -------------------")
    print('------------------- EEA Recovery Items Verification Case 1 --------------')
    serialControlObj = serialControl(json_data=json_data, NCDComPort=NCDComPort, PowerPackComPort=PowerPackComPort,
                                     BlackBoxComPort=BlackBoxComPort,
                                     USB6351ComPort=USB6351ComPort, ArduinoUNOComPort=ArduinoUNOComPort,
                                     OUTPUT_PATH=OUTPUT_PATH, videoPath=videoPath, itr=itr,
                                     EEA_RELOAD_EEPROM_command_byte=EEA_RELOAD_EEPROM_command_byte)
    serialControlObj.OpenSerialConnection()
    T99_Cutting_Recovery_Firing_Recovery_Requirements(serialControlObj, videoPath, itr,
                                                      passed_executions)
    serialControlObj.disconnectSerialConnection()


def T99_Cutting_Recovery_Firing_Recovery_Requirements(serialControlObj, videoPath, itr,
                                                      passed_executions):
    """
    ###################################################################################################################
    ## CASE 2: Cutting Recovery
    ###################################################################################################################
    """
    ## STEP 1: Removing Handle From The Charger
    success_flag = True
    serialControlObj.battery_level_check()
    serialControlObj.startup_log()

    ## STEP 2: Clamshell Connected
    serialControlObj.connectClamshellTest(success_flag=success_flag)

    ## STEP 3: Record Power Pack and Adapter usage Counts
    # For capturing Adapter Usage Counts - Adapter needs to be connected Mechanically
    # Engaging the Adapter - Controlling the stepper motor
    firingCount = 0
    serialControlObj.RecordPowerPackAndAdapterUsageCounts(firingCont=firingCount)

    ## STEP 4: Adapter Connected With INIT State.
    serialControlObj.connect_adapter_test()

    ## STEP 5: Connecting EEA Reload Along with Ship Cap Presence Check
    ## STEP 6: Extension of Trocar
    ## STEP 7: Clamping on Tissue - Retraction of Trocar Until Clamp GAP is reached
    ## STEP 8: Safety Key Acknowledgement
    ## STEP 9: Firing
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

        data = serialControlObj.json_data

        reload_type = data['Reload Type']
        video_name = (str(scenario_number) + '#' + str(itr + 1) + test_scenario + '_' + reload_type + '_' + fireN)

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

        reload_parameters = {"firing_count": fireN, "reload_type": reload_type, "reload_length": reload_length,
                             "video_name": video_name, "reload_color": reload_color, "reload_state": reload_state,
                             "cartridge_state": cartridge_state, "cartridge_color": cartridge_color,
                             "procedure_firings_count": procedure_firings_count, "ship_cap_presence": ship_cap_status}

        # Firing Test
        firingValue = 3
        remove_adapter_cutting_Starts = 3
        case_id = 2
        test_parameters = {"firing_number": firingValue, "adapter_removed_cutting_starts": remove_adapter_cutting_Starts,
                           "case_id": case_id}
        serialControlObj.EEA_IS_12_N_Firing(test_parameters=test_parameters, reload_parameters=reload_parameters)

    ## STEP 10: Verifying Recovery ID data
    serialControlObj.VerifyRecoveryIDData()

    ## STEP 11: Re-Attaching the Adapter to the Power Pack
    serialControlObj.connect_adapter_test(adapter_type="after cut recovery In-progress")

    ## STEP 12: Performing Rotation, Articulation and Close Operation
    # Right CW Rotation
    serialControlObj.eea_right_clockwise_rotation()

    # Left Articulation
    serialControlObj.eea_left_articulation()

    # Close Key Operation
    serialControlObj.eea_close_key_operation()

    ## STEP 13: Holding Rotation Buttons
    occurrence = 12_1
    serialControlObj.EEASurgicalSiteExtractionStateExit(occurence=occurrence)

    ## STEP 14: Staples Detected Exit State - Fully open position
    serialControlObj.EEANoStaplesDetectedStateExit()

    ## STEP 15: Remove Reload
    protocol_id = 12
    serialControlObj.DisconnectingEEAReload(protocol_id=protocol_id)

    ## STEP 16: Surgical Site Extraction (SSE)
    occurrence = 12_2
    serialControlObj.EEASurgicalSiteExtractionStateExit(occurence=occurrence)

    ## STEP 17: Remove Adapter
    serialControlObj.removeAdapter()

    ## STEP 18: Record Adapter usage Counts - Adapter Firing and Procedure Count Incremented by 1
    # For capturing Adapter Usage Counts - Adapter needs to be connected Mechanically
    # Engaging the Adapter - Controlling the stepper motor
    firingCount = 4
    serialControlObj.RecordPowerPackAndAdapterUsageCounts(firingCont=firingCount)

    ## STEP 19: Re-Connecting the adapter with INIT State
    serialControlObj.connect_adapter_test()

    ## STEP 20: Attaching EEA reload along with ship cap presence check
    ## STEP 21: Extension of Trocar
    ## STEP 22: Clamping on Tissue - Retraction of Trocar Until Clamp GAP is reached
    ## STEP 23: Safety Key Acknowledgement
    ## STEP 24: Firing
    total_firings = 1
    try:
        total_firings = len(serialControlObj.json_data['Total number of firings'])
    except Exception as Ex:
        # total_firings = serialControlObj.json_data['Num Times to Execute']
        print(f"Exception Occurred! {Ex}")

    for i in range(total_firings):

        fireN = 'Fire' + str(i + 1)

        scenario_number = serialControlObj.json_data['Scenario Num']
        test_scenario = serialControlObj.json_data['Test Scenario']

        data = serialControlObj.json_data

        reload_type = data['Reload Type']
        video_name = (str(scenario_number) + '#' + str(itr + 1) + test_scenario + '_' + reload_type + '_' + fireN)

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

        reload_parameters = {"firing_count": fireN, "reload_type": reload_type, "reload_length": reload_length,
                             "video_name": video_name, "reload_color": reload_color, "reload_state": reload_state,
                             "cartridge_state": cartridge_state, "cartridge_color": cartridge_color,
                             "procedure_firings_count": procedure_firings_count, "ship_cap_presence": ship_cap_status}

        # Firing Test
        firingValue = 4
        cut_recovery_entry = 2
        case_id = 2
        test_parameters = {"firing_number": firingValue, "adapter_removed_cut_recovery": cut_recovery_entry,
                           "case_id": case_id}
        serialControlObj.EEA_IS_12_N_Firing(test_parameters=test_parameters, reload_parameters=reload_parameters)

    ## STEP 20: Verifying Recovery ID data

    ## STEP 11: Re-Attaching the Adapter to the Power Pack

    ## STEP 11: Performing Rotation, Articulation and Close Operation

    ## STEP 12: Holding Rotation Buttons

    ## STEP 13: Staples Detected Exit State - Fully open position

    ## STEP 14: Remove Reload

    ## STEP 15: Surgical Site Extraction (SSE)

    ## STEP 16: Remove Adapter

    ## STEP 17: Record Adapter usage Counts - Adapter Firing and Procedure Count Incremented by 1
    # For capturing Adapter Usage Counts - Adapter needs to be connected Mechanically
    # Engaging the Adapter - Controlling the stepper motor

    ## STEP 28: DisEngage the Adapter Clutch
    serialControlObj.Switch_OFF_Relay(1, 8)
    print('Adapter Clutch Disengaged')

    ## STEP 25: Remove Clamshell
    serialControlObj.removeClamshell()

    temp2 = 'PASS'
    for item in serialControlObj.Test_Results:
        try:
            if not item[0] == ' ':
                if ((item.split(":")[1]).strip()) == 'PASS':
                    # serialControlObj.Test_Results.append(serialControlObj.Normal_Firing_Test_Results[0] + ':FAIL')
                    pass
                elif ((item.split(":")[1]).strip()) == 'FAIL':
                    temp2 = 'FAIL'
                    print(f"Item = {item}")
                    # print(str((serialControlObj.Test_Results[0] + ':  Failed')))
                    break
        except Exception as Ex:
            print(f"Exception Occurred. {item} does not have the ':'. {Ex}")

    if temp2 == 'PASS':
        passed_executions[f"{serialControlObj.json_data['Test Scenario']}_{itr}"] = "PASS"

    print(serialControlObj.json_data['Test Scenario'] + ' % of Successful Executions: ' +
          str(100 * ((len(passed_executions)) / (serialControlObj.json_data['Num Times to Execute']))))

    serialControlObj.my_Serthread.clearQue()
    serialControlObj.wait(5)
    MCPThread.readingPowerPack.exitFlag = True
    serialControlObj.serPP.close()
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
    print('------------------- EEA Cutting Recovery Requirements Case 1 End --------------')

##################################################################################################################################################

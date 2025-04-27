""" Name: EEA Recovery Items Verification; Function: EEARecoveryFailureIncrementCounts
from removing the handle from charger to, clamshell connecting, adapter connecting, tip protector detection, reload detection,
Created by Ugra Narasimha, Date: 10-May-2024"""

import sys

import OLEDRecordingThread
from Prepare_Output_Json_File import *
import MCPThread
from Serial_Relay_Control import serialControl


def T308_FailuretoIncrement1WireCounters_RecoveryItemsVerificationSystem(json_data, SULU_EEPROM_command_byte,
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
    T308_Failure_to_Increment_1Wire_Counters_Recovery_Items_Verification_System(serialControlObj, videoPath, itr,
                                                                                passed_executions)
    serialControlObj.disconnectSerialConnection()


# Purpose-To perform Recovery_items Firing Scenarios
def T308_Failure_to_Increment_1Wire_Counters_Recovery_Items_Verification_System(serialControlObj, videoPath, itr,
                                                                                passed_executions):
    """
    ###################################################################################################################
    ## CASE 1: Failure to Increment 1-Wire Counters
    ## Description : These scenarios testing during firing conditions
    ## 1. During Firing disconnecting the Adapter Onewire, and Verifying the Adapter ( 1W and EEPROM ) Usage counts.
    ## 2. By restoring the Adapter Onewire performing firing and Verifying the Adapter ( 1W and EEPROM ) Usage counts
    ###################################################################################################################
    """
    ## STEP 1: Removing Handle From Changer
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

    ## STEP 4: Adapter Connected
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
        disconnecting_adapter_onewire = 1
        test_parameters = {"firing_number": firingValue, "adapter_1W_failure": disconnecting_adapter_onewire}
        serialControlObj.EEA_IS_40_E_Firing(test_parameters=test_parameters, reload_parameters=reload_parameters)

        # STEP 10: Perform Tilt Operation ( Unlock the Anvil )
        # Perform Tilt and TILT_Open Operation ( Unlock the Anvil ) of the Anvil
        # Tilt Prompt Open - Along with Adapter ERROR

    ## STEP 11: Remove Adapter along with Reload
    serialControlObj.removeAdapter()

    ## STEP 12: Disconnecting reload
    serialControlObj.DisconnectingEEAReload()

    ## STEP 13: Record Power Pack and Adapter usage Counts After Firing
    # Reading Power Pack Usage Counts, output of this stage is
    # Adapter 1-Wire Fire Count and Procedure Count unchanged
    # Adapter EEPROM Fire Count and procedure Count increased by 1
    firingCount = 1
    serialControlObj.RecordPowerPackAndAdapterUsageCounts(firingCont=firingCount)

    ## STEP 14: Re-Connecting the adapter
    # Turning ON the Adapter One Wire - Restoring adapter onewire
    serialControlObj.connect_adapter_test()

    ## STEP 15: Attaching EEA reload along with ship cap presence check
    ## STEP 16: Extension of Trocar
    ## STEP 17: Clamping on Tissue - Retraction of Trocar Until Clamp GAP is reached
    ## STEP 18: Safety Key Acknowledgement
    ## STEP 19: Firing
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
        firingValue = 2
        test_parameters = {"firing_number": firingValue}
        serialControlObj.EEA_IS_40_E_Firing(test_parameters=test_parameters, reload_parameters=reload_parameters)

        ## STEP 20: Perform Tilt Operation ( Unlock the Anvil )
        # Tilt Operation of Anvil
        # Tilt Prompt Open

    ## STEP 21: Disconnecting Reload
    serialControlObj.DisconnectingEEAReload()

    ## STEP 22: Remove Adapter
    serialControlObj.removeAdapter()

    ## STEP 23: Record Power Pack and Adapter usage Counts ( By Engaging the Adapter )
    firingCount = 2
    serialControlObj.RecordPowerPackAndAdapterUsageCounts(firingCont=firingCount)

    ## STEP 24: DisEngage the Adapter Clutch
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
    print('------------------- EEA Recovery Items Verification Case 1 End --------------')


##################################################################################################################################################

def T309_FailuretoIncrementEEPROMCounters_RecoveryItemsVerificationSystem(json_data, SULU_EEPROM_command_byte,
                                                                          MULU_EEPROM_command_byte,
                                                                          CARTRIDGE_EEPROM_command_byte,
                                                                          NCDComPort, PowerPackComPort, BlackBoxComPort,
                                                                          USB6351ComPort,
                                                                          ArduinoUNOComPort, OUTPUT_PATH, videoPath,
                                                                          itr,
                                                                          EEA_RELOAD_EEPROM_command_byte,
                                                                          passed_executions):
    print(f"-----------------    {json_data['Test Scenario']}  -------------------")
    print('------------------- EEA Recovery Items Verification Case 2 --------------')
    serialControlObj = serialControl(json_data=json_data, NCDComPort=NCDComPort, PowerPackComPort=PowerPackComPort,
                                     BlackBoxComPort=BlackBoxComPort,
                                     USB6351ComPort=USB6351ComPort, ArduinoUNOComPort=ArduinoUNOComPort,
                                     OUTPUT_PATH=OUTPUT_PATH, videoPath=videoPath, itr=itr,
                                     EEA_RELOAD_EEPROM_command_byte=EEA_RELOAD_EEPROM_command_byte)
    serialControlObj.OpenSerialConnection()
    T309_Failure_to_Increment_EEPROM_Counters_Recovery_Items_Verification_System(serialControlObj, videoPath, itr,
                                                                                 passed_executions)
    serialControlObj.disconnectSerialConnection()


# Purpose-To perform recovery Items Failure Scenarios
def T309_Failure_to_Increment_EEPROM_Counters_Recovery_Items_Verification_System(serialControlObj, videoPath, itr,
                                                                                 passed_executions):
    """
    ###################################################################################################################
    ## CASE 2: Failure to Increment EEPROM Counters
    ## Description : These scenarios testing during firing conditions
    ## 1. During Firing disconnecting the Adapter Onewire, and Verifying the Adapter ( 1W and EEPROM ) Usage counts.
    ## 2. By restoring the Adapter Onewire performing firing and Verifying the Adapter ( 1W and EEPROM ) Usage counts
    ###################################################################################################################
    """
    ## STEP 1: Removing Handle From Changer
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

    ## STEP 4: Adapter Connected
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
        disconnecting_adapter_UART_Rx_or_Tx = 2
        test_parameters = {"firing_number": firingValue, "adapter_UART_failure": disconnecting_adapter_UART_Rx_or_Tx}
        serialControlObj.EEA_IS_40_E_Firing(test_parameters=test_parameters, reload_parameters=reload_parameters)

        # STEP 10: Perform Tilt Operation ( Unlock the Anvil )
        # Perform Tilt and TILT_Open Operation ( Unlock the Anvil ) of the Anvil
        # Tilt Prompt Open - Along with Adapter ERROR

    ## STEP 11: Remove Adapter along with Reload
    serialControlObj.removeAdapter()

    ## STEP 12: Record Power Pack and Adapter usage Counts After Firing
    # Reading Power Pack Usage Counts, output of this stage is
    # Adapter 1-Wire Fire Count and Procedure Count unchanged
    # Adapter EEPROM Fire Count and procedure Count increased by 1
    firingCount = 1
    serialControlObj.RecordPowerPackAndAdapterUsageCounts(firingCont=firingCount)

    ## STEP 13: Re-Connecting the adapter
    # Turning ON the Adapter UART Connection - Restoring UART Rx/Tx
    serialControlObj.connect_adapter_test(adapter_type='UART Restored')

    ## STEP 14: Full Open Position
    serialControlObj.FullOpenPosition()

    ## STEP 15: Remove Reload and Anvil - SSE Prompt
    serialControlObj.RemoveEEAReloadWithSSEPrompt()

    ## STEP 16: Holding Rotation Buttons - To Exit SSE Mode
    protocol_id = 40
    serialControlObj.EEASurgicalSiteExtractionStateExit(protocol_id=protocol_id)

    ## STEP 17: Remove Adapter
    serialControlObj.removeAdapter()

    ## STEP 18: Re-Connecting the adapter
    serialControlObj.connect_adapter_test()

    ## STEP 19: Attaching EEA reload along with ship cap presence check
    ## STEP 20: Extension of Trocar
    ## STEP 21: Clamping on Tissue - Retraction of Trocar Until Clamp GAP is reached
    ## STEP 22: Safety Key Acknowledgement
    ## STEP 23: Firing
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
        firingValue = 4
        test_parameters = {"firing_number": firingValue}
        serialControlObj.EEA_IS_40_E_Firing(test_parameters=test_parameters, reload_parameters=reload_parameters)

        ## STEP 24: Perform Tilt Operation ( Unlock the Anvil )
        # Tilt Operation of Anvil
        # Tilt Prompt Open

    ## STEP 25: Remove Adapter and Re-connect the Clutch for Recording usage Counts
    serialControlObj.DisconnectingEEAReload()
    serialControlObj.removeAdapter()

    ## STEP 26: Record Power Pack and Adapter usage Counts ( By Engaging the Adapter )
    firingCount = 3
    serialControlObj.RecordPowerPackAndAdapterUsageCounts(firingCont=firingCount)

    ## STEP 27: DisEngage the Adapter Clutch
    serialControlObj.Switch_OFF_Relay(1, 8)
    print('Adapter Clutch Disengaged')

    ## STEP 28: Remove Clamshell
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
    print('------------------- EEA Recovery Items Verification Case 2 End --------------')

######################################################################################################################################################################

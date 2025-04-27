
import sys

import MCPThread
import OLEDRecordingThread
from Prepare_Output_Json_File import *
from Serial_Relay_Control import serialControl


# import serial.tools.list_ports_windows


def EGIAISNormalFiring(json_data, SULU_EEPROM_command_byte, MULU_EEPROM_command_byte, CARTRIDGE_EEPROM_command_byte,NCDComPort,
                       PowerPackComPort, BlackBoxComPort, USB6351ComPort, ArduinoUNOComPort, OUTPUT_PATH, videoPath, itr,
                       passed_executions):
    #print('normal firing', r, SULU_EEPROM_command_byte, MULU_EEPROM_command_byte, CARTRIDGE_EEPROM_command_byte, i)
    #Test_Results = []

    print(f"-----------------    {json_data['Test Scenario']}  -------------------")
    serialControlObj = serialControl(json_data, SULU_EEPROM_command_byte, MULU_EEPROM_command_byte,
                                     CARTRIDGE_EEPROM_command_byte, NCDComPort, PowerPackComPort, BlackBoxComPort,
                                     USB6351ComPort, ArduinoUNOComPort, OUTPUT_PATH, videoPath, itr=itr)
    serialControlObj.OpenSerialConnection()
    # Normal_Firing(serialControlObj) #, PowerPackComPort)
    EGIA_IS_Normal_Firing(serialControlObj, videoPath, itr, passed_executions)
    serialControlObj.disconnectSerialConnection()


# Purpose-To perform Normal Firing Scenarios
def EGIA_IS_Normal_Firing(serialControlObj, videoPath, itr, passed_executions):

    success_flag = True

    serialControlObj.startup_log()

    serialControlObj.connectClamshellTest(success_flag=success_flag)

    serialControlObj.connect_adapter_test()

    total_firings = 1
    try:
        # total_firings = len(serialControlObj.json_data['Total firings'])
        total_firings = len(serialControlObj.json_data['Total number of firings'])
    except Exception as Ex:
        # total_firings = serialControlObj.json_data['Num Times to Execute']
        print(f"Exception Occurred! {Ex}")

    for i in range(total_firings):

        fireN = 'Fire' + str(i + 1)

        senario_number = serialControlObj.json_data['Scenario Num']
        test_scenario = serialControlObj.json_data['Test Scenario']
        try:
            # len(serialControlObj.json_data['Total firings'])
            data = serialControlObj.json_data[fireN]
        except Exception as Ex:
            print(f"It seems like Normal firing!")
            data = serialControlObj.json_data

        reload_type = data['Reload Type']
        video_name = (str(senario_number) + '#' + str(itr + 1) + test_scenario + '_' + reload_type + '_' + fireN)

        clampingForce = data['Clamping Force']
        firingForce = data['Firing Force']
        articulationStateinFiring = data['Articulation State for clamping & firing']
        # numberOfFiringsinProcedure = data['Num of Firings in Procedure']
        retractionForce = data['Retraction Force']

        reload_length = data['Reload Length(mm)']
        procedure_firings_count = data['Num of Firings in Procedure']
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

        is_reload_cartridge_attached_together = "No"
        is_clamp_cycle_test_with_cartridge = "No"
        if reload_type.upper() == "MULU":
            cartridge_color = data['Cartridge Color']
            try:
                is_reload_cartridge_attached_together = data[
                    "Attach Reload & Cartridge Together"]
            except Exception as Ex:
                print(f"Exception Occurred, the key is not available in JSON File! {Ex}")
            try:
                is_clamp_cycle_test_with_cartridge = data[
                    "Clamp Cycle Test with Cartridge"]
            except Exception as Ex:
                print(f"Exception Occurred, the key is not available in JSON File! {Ex}")
            try:
                cartridge_state = data['Cartridge State']
            except Exception as Ex:
                print(f"Reload state is not present in the present firing configs. Hence by default "
                      f"cartridge_state is taken as GOOD \n{Ex}")

        reload_parameters = {"firing_count": fireN, "reload_type": reload_type, "reload_length": reload_length,
                             "video_name": video_name, "reload_color": reload_color, "reload_state": reload_state,
                             "cartridge_state": cartridge_state, "cartridge_color": cartridge_color,
                             "is_reload_cartridge_attached_together": is_reload_cartridge_attached_together,
                             "is_clamp_cycle_test_with_cartridge": is_clamp_cycle_test_with_cartridge,
                             "procedure_firings_count": procedure_firings_count}

        # Firing Test
        serialControlObj.firing_test(clampingForce=clampingForce, firingForce=firingForce,
                                     articulationStateinFiring=articulationStateinFiring,
                                     retractionForce=retractionForce, reload_parameters=reload_parameters)
    # removing adapter
    serialControlObj.removeAdapter()

    # TEST STEP: Remove Clamshell
    serialControlObj.removeClamshell()

    temp2 = 'PASS'
    for item in serialControlObj.Test_Results:
        # print(item)

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

    #Iteration_Results.append()
    #results_path = serialControlObj.OUTPUT_PATH + '\\Results.xlsx'
    #df.to_excel(results_path)
    serialControlObj.my_Serthread.clearQue()
    serialControlObj.wait(5)
    MCPThread.readingPowerPack.exitFlag = True
    serialControlObj.serPP.close()
    OLEDRecordingThread.exitFlag = True
    with open(str((videoPath + '\\sample_result.txt')), 'a') as datalog:
            datalog.write('\n'.join(serialControlObj.Test_Results) + '\n')
    CS = [sys.argv[index+1] for index, ele in enumerate(sys.argv) if ele == "-c" or ele == "--changeset"]
    TT = [sys.argv[index+1] for index, ele in enumerate(sys.argv) if ele == "-t" or ele == "--test"]
    INTG = '--integration' in sys.argv
    RP = [sys.argv[index + 1] for index, ele in enumerate(sys.argv) if ele == "-r" or ele == "--root"]
    calculatePassFail(str((videoPath + '\\sample_result.txt')), str(RP[0] + '\\Test_Configurator.json'), str((videoPath +'\\StartUpLog.txt')), str(TT[0]), str(CS[0]), str(INTG))
    serialControlObj.PlacingPowerPackOnCharger()
    print('Power Pack Placed on Charger')
    print('------------------- End of Test Scenario --------------')
    serialControlObj.wait(30)
    #serialControlObj.disconnectSerialConnection()

""" Name: EEA Recovery/Init Mode - R2146-1036 Signia System Firings Engineering Test Protocol – V40.2.1 – Special Cases Part 2
Protocol ID  Reference - RE00359465
Implemented on 11-February-2025, by Ugra Narasimha : DV Protocols Development """
import time

import OLEDRecordingThread
from Serial_Relay_Control import serialControl


def EEADVMaxCutForce_359465(json_data, NCDComPort,
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
    EEA_DV_Max_Cut_Force_359465(serialControlObj, videoPath, itr, passed_executions)
    serialControlObj.disconnectSerialConnection()


# Purpose-To perform Normal Firing Scenarios
def EEA_DV_Max_Cut_Force_359465(serialControlObj, videoPath, itr, passed_executions):
    success_flag = True

    serialControlObj.battery_level_check()

    # 5.1.1. Remove the Signia Powerpack from the Signia Single Bay Charger and allow the handle
    # to turn on and complete the motor test.
    serialControlObj.startup_log()

    scenario_number = serialControlObj.json_data['Scenario Num']
    test_scenario = serialControlObj.json_data['Test Scenario']

    print(f"-----------------    {scenario_number}_{test_scenario}  -------------------")

    video_name = f"{scenario_number}_{test_scenario}"
    videoThread = OLEDRecordingThread.myThread(video_name, videoPath)
    videoThread.start()
    serialControlObj.video_thread = videoThread

    # 5.1.2.	Insert the powerpack into the back handle of a Signia PowerShell
    # and close the front handle to assemble the system.
    serialControlObj.connectClamshellTest(success_flag=success_flag)

    screen_name = "GreenSwimLane_ProcedureCount"
    folder_name = "GreenSwimLane_ProcedureCount"
    file_name   = "GreenSwimLane_ProcedureCount"

    # 5.1.3. Confirm that the screen shows a powerpack in a green swimlane with a count of procedures remaining
    # for the handle.
    serialControlObj.handle_screen(videoPath=videoPath, screen_name=screen_name, folder_name=folder_name,
                                   file_name=file_name, is_static_image=True)

    # 5.1.4. Attach the Circular Adapter to the clamshell of the Powered assembly and allow to calibrate.
    # The system shall recognize that an adapter is attached and the type of adapter.
    # 5.1.5. The handle shall indicate the adapter is ready to accept a reload.
    serialControlObj.connect_adapter_test()

    total_firings = 1
    try:
        total_firings = len(serialControlObj.json_data['Total number of firings'])
    except Exception as Ex:
        print(f"Exception Occurred! {Ex}")

    for i in range(total_firings):

        fireN = 'Fire' + str(i + 1)

        scenario_number = serialControlObj.json_data['Scenario Num']
        test_scenario = serialControlObj.json_data['Test Scenario']
        try:
            data = serialControlObj.json_data[fireN]
        except Exception as Ex:
            print(f"It seems like Normal firing! {Ex}")
            data = serialControlObj.json_data

        reload_type = data['Reload Type']
        video_name = (str(scenario_number) + '#' + str(itr + 1) + test_scenario + '_' + reload_type + '_' + fireN)

        clampingForce = data['Clamping Force']
        firingForce = data['Firing Force']
        retractionForce = data['Retraction Force']

        reload_length = data['Reload Diameter(mm)']
        procedure_firings_count = data['Num of Firings in Procedure']
        ship_cap_status = data['Ship cap Present']
        reload_color = data['Reload Color']

        reload_state = "GOOD"
        try:
            reload_state = data['Reload State']
        except Exception as Ex:
            print(f"Reload state is not present in the present firing configs. Hence by default reload_state is "
                  f"taken as GOOD \n{Ex}")

        reload_parameters = {"firing_count": fireN, "reload_type": reload_type, "reload_length": reload_length,
                             "video_name": video_name, "reload_color": reload_color, "reload_state": reload_state,
                             "procedure_firings_count": procedure_firings_count, "ship_cap_presence": ship_cap_status}

        # Firing Test
        serialControlObj.DV_Cut_Max_Force_359465(clampingForce=clampingForce, firingForce=firingForce,
                     reload_parameters=reload_parameters)
    # removing adapter
    serialControlObj.removeAdapter()
    serialControlObj.wait(5)

    # removing clamshell
    serialControlObj.removeClamshell()

    OLEDRecordingThread.exitFlag = True
    time.sleep(2)

    serialControlObj.test_results_pass_percentage(passed_executions=passed_executions)

    # 5.2.18. At the end of all testing in this section, remove the handle from the shell and place on a charger.
    # serialControlObj.PlacingPowerPackOnCharger()
    # print('Power Pack Placed on Charger')

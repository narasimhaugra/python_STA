""" Name: EEA Recovery Mode - Signia System Firings Engineering Test Protocol - V 40.2.1 - Recovery Mode Performed on different stages.
Clamping, Stapling Started, Stapling Completed, Cut Completed, Tilt Prompt Open.
Protocol ID  Reference - RE00460333
Updated on 21-October-2024, by Ugra Narasimha : Recovery Mode Defect Fix """
import time

import OLEDRecordingThread
from Serial_Relay_Control import serialControl


def EEADVRecoveryMode_400860(json_data, NCDComPort,
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
    # Normal_Firing(serialControlObj) #, PowerPackComPort)
    EEA_DV_Recovery_Mode_400860(serialControlObj, videoPath, itr, passed_executions, PowerPackComPort, NCDComPort)
    serialControlObj.disconnectSerialConnection()


# Purpose-To perform Normal Firing Scenarios
def EEA_DV_Recovery_Mode_400860(serialControlObj, videoPath, itr, passed_executions, PowerPackComPort, NCDComPort):
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

    # Step - 5.1.2 Confirm software version is v40.2.1.
    # Step - 5.1.1.	Insert handle into a clamshell.
    test_step_number = '5.1.1'
    serialControlObj.connectClamshellTest(success_flag=success_flag, test_step_number=test_step_number)

    # Step - 5.1.3 Install the PEEA adapter onto the clamshell and wait for the
    # adapter to complete the calibration.
    serialControlObj.connect_adapter_test()

    screen_name = "Request_Reload"
    folder_name = "Request_Reload"
    file_name =  "Request_Reload"
    serialControlObj.handle_screen(videoPath=videoPath, screen_name=screen_name, folder_name=folder_name,
                                   file_name=file_name, is_static_image=True)

    # Step - 5.1.5.	Press and hold the four rotation buttons until the handle begins to rest itself.
    # The trocar should fully extend after the reset
    serialControlObj.EEA_adapter_reset()

    screen_name = "Trocar_Fully_Extended"
    folder_name = "Trocar_Fully_Extended"
    file_name =  "Trocar_Fully_Extended"
    serialControlObj.handle_screen(videoPath=videoPath, screen_name=screen_name, folder_name=folder_name,
                                   file_name=file_name, is_static_image=True)

    serialControlObj.Switch_OFF_Relay(2, 1)
    serialControlObj.Switch_OFF_Relay(2, 2)
    serialControlObj.Switch_OFF_Relay(2, 7)
    serialControlObj.Switch_OFF_Relay(2, 8)

    # 5.1.6. After the trocar is fully extended, press the toggle button up down and up and confirm whether a lock screen (Figure 3)
    # is displayed when pressing the toggle button (248943).
    ''' 248943	The HANDLE shall indicate PEEA_ADAPTER is locked upon successful RE-INITIALIZATION. '''
    serialControlObj.checkLockScreenPresent()

    screen_name = "Device Lock Display"
    folder_name = "Device_Lock_Display"
    file_name =  "Device_Lock_Display"
    is_static_image = True
    serialControlObj.handle_screen(videoPath=videoPath, screen_name=screen_name, folder_name=folder_name,
                                   file_name=file_name, is_static_image=is_static_image)

    serialControlObj.Switch_OFF_Relay(2, 4)
    serialControlObj.Switch_OFF_Relay(2, 5)
    serialControlObj.Switch_OFF_Relay(2, 4)

    # 5.1.7. Detach PEEA adapter from clamshell.
    serialControlObj.removeAdapter_DV()
    serialControlObj.wait(5)
    # 5.1.8. Wait a few seconds and then reattach adapter to clamshell. Wait for the adapter to complete the calibration and
    # indicate that the adapter is ready to accept PEEA Reload
    serialControlObj.connect_adapter_test()

    # 5.1.9. Detach PEEA adapter from clamshell.
    serialControlObj.removeAdapter_DV()
    serialControlObj.wait(5)

    # 5.1.10. Wait a few seconds and then reattach adapter to clamshell. Wait for the adapter to complete the calibration and
    # indicate that the adapter is ready to accept PEEA Reload (249780). See Screen 1.
    ''' 249780	In RECOVERY_MODE, the HANDLE shall return to previous indication that PEEA_ADAPTER is ready 
    to accept PEEA_RELOAD if calibrated PEEA_ADAPTER without PEEA_RELOAD is attached prior to fully clamped.'''
    serialControlObj.connect_adapter_test()

    screen_name = "Request_Reload"
    folder_name = "Request_Reload"
    file_name =  "Request_Reload"
    serialControlObj.handle_screen(videoPath=videoPath, screen_name=screen_name, folder_name=folder_name,
                                   file_name=file_name, is_static_image=True)

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
        serialControlObj.DV_firing_400860(clampingForce=clampingForce, firingForce=firingForce,
                                   retractionForce=retractionForce, reload_parameters=reload_parameters,
                                   articulationStateinFiring=None)
    # removing adapter
    serialControlObj.removeAdapter()

    # removing clamshell
    serialControlObj.removeClamshell()

    OLEDRecordingThread.exitFlag = True
    time.sleep(2)

    serialControlObj.test_results_pass_percentage(passed_executions=passed_executions)

   # DownloadEventlogs(videoPath, PowerPackComPort, NCDComPort)

""" Name: Engineering Build 40.4.0.3 EEA Adapter INIT Position - Adapter Extends Clean ability Position
Protocol ID  Reference - EEA_Adapter_INIT_40_4_0_3
Updated on 24-02-2025, by Ugra Narasimha : Adapter Init State Verification Multiple times"""
import OLEDRecordingThread
from Serial_Relay_Control import serialControl
#from image_comparision.image_comparision import get_similar_images



def EEAAdapterINIT40_4_0_3(json_data, NCDComPort,
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

    EEA_Adapter_INIT_40_4_0_3(serialControlObj, videoPath, itr, passed_executions)

    serialControlObj.disconnectSerialConnection()


# Purpose-To perform Normal Firing Scenarios
def EEA_Adapter_INIT_40_4_0_3(serialControlObj, videoPath, itr, passed_executions):
    success_flag = True

    serialControlObj.battery_level_check()

    serialControlObj.startup_log()
    video_name = f'EEA_Adapter_INIT_40_4_0_3'
    videoThread = OLEDRecordingThread.myThread(video_name, videoPath)
    videoThread.start()
    serialControlObj.video_thread = videoThread

    # Clamshell Connected
    serialControlObj.connectClamshellTest(success_flag=success_flag)

    # Adapter Connected
    serialControlObj.connect_adapter_test()

    total_firings = 1

    for i in range(total_firings):

        fireN = 'Fire' + str(i + 1)

        senario_number = serialControlObj.json_data['Scenario Num']
        test_scenario = serialControlObj.json_data['Test Scenario']
        try:
            # len(serialControlObj.json_data['Total firings'])
            data = serialControlObj.json_data[fireN]
        except Exception as Ex:
            # print(f"It seems like Normal firing! {Ex}")
            data = serialControlObj.json_data

        reload_type = data['Reload Type']
        video_name = (str(senario_number) + '#' + str(itr + 1) + test_scenario + '_' + reload_type + '_' + fireN)

        clampingForce = data['Clamping Force']
        firingForce = data['Firing Force']
        retractionForce = data['Retraction Force']

        reload_length = data['Reload Diameter(mm)']
        procedure_firings_count = data['Num of Firings in Procedure']
        ship_cap_status = data['Ship cap Present']

        reload_color = None
        cartridge_color = None
        reload_state = "GOOD"
        cartridge_state = "GOOD"

        if reload_type.upper() != "MULU":
            reload_color = data['Reload Color']

        reload_parameters = {"firing_count": fireN, "reload_type": reload_type, "reload_length": reload_length,
                             "video_name": video_name, "reload_color": reload_color, "reload_state": reload_state,
                             "cartridge_state": cartridge_state, "cartridge_color": cartridge_color,
                             "procedure_firings_count": procedure_firings_count, "ship_cap_presence": ship_cap_status}

        # pre-defined random number
        loop_count = 250
        while loop_count :
            # Press and hold the four rotation buttons until the handle begins to rest itself.
            # The trocar should fully extend after the reset ( Adapter extends to clean ability position)
            serialControlObj.EEA_adapter_reset()

            serialControlObj.Switch_OFF_Relay(2, 1)
            serialControlObj.Switch_OFF_Relay(2, 2)
            serialControlObj.Switch_OFF_Relay(2, 7)
            serialControlObj.Switch_OFF_Relay(2, 8)

            serialControlObj.wait(15)

            # Detach PEEA adapter from clamshell.
            serialControlObj.removeAdapter()

            serialControlObj.wait(4)

            # Wait a few seconds and then reattach adapter to clamshell. Wait for the adapter to complete the calibration and
            # indicate that the adapter is ready to accept PEEA Reload
            serialControlObj.connect_adapter_test()

            # As of now running 50 times later we can update proper logic
            loop_count = loop_count - 1

            print("left loop_count ", loop_count )
            # After connecting adapter waiting few seconds
            serialControlObj.wait(5)

     # removing adapter
    serialControlObj.removeAdapter()

    # removing clamshell
    serialControlObj.removeClamshell()

    # OLED task exits
    OLEDRecordingThread.exitFlag = True

    # Test results and placing handle on the charger
    serialControlObj.test_results_pass_percentage(passed_executions=passed_executions)

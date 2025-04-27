""" Name: EEA Recovery Mode - Signia System Firings Engineering Test Protocol - V 40.2.1 - Recovery Mode Performed on different stages.
Clamping, Stapling Started, Stapling Completed, Cut Completed, Tilt Prompt Open.
Protocol ID  Reference - RE00460333
Updated on 21-October-2024, by Ugra Narasimha : Recovery Mode Defect Fix """
import OLEDRecordingThread
from AdapterReadWrite import GetAdapterEepromUsageCounts
from DownloadEventlogs import DownloadEventlogs
from Serial_Relay_Control import serialControl
#from image_comparision.image_comparision_old import get_similar_images


def EEASSEEntryDueToReloadWithoutStaples(json_data, NCDComPort,
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
    EEA_SSE_Entry_Due_To_Reload_Without_Staples(serialControlObj, videoPath, itr, passed_executions, PowerPackComPort, NCDComPort)
    serialControlObj.disconnectSerialConnection()


# Purpose-To perform Normal Firing Scenarios
def EEA_SSE_Entry_Due_To_Reload_Without_Staples(serialControlObj, videoPath, itr, passed_executions, PowerPackComPort, NCDComPort):
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
        total_firings = len(serialControlObj.json_data['Total number of firings'])
    except Exception as Ex:
        print(f"Exception Occurred! {Ex}")

    for i in range(total_firings):

        fireN = 'Fire' + str(i + 1)

        try:
            # len(serialControlObj.json_data['Total firings'])
            data = serialControlObj.json_data[fireN]
        except Exception as Ex:
            print(f"It seems like Normal firing! {Ex}")
            data = serialControlObj.json_data

        scenario_number = serialControlObj.json_data['Scenario Num']
        scenario_name = serialControlObj.json_data['Test Scenario']

        reload_type = data['Reload Type']
        video_name = (str(scenario_number) + '#' + str(itr + 1) + scenario_name + '_' + reload_type + '_' + fireN)

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
        try:
            reload_state = data['Reload State']
        except Exception as Ex:
            print(f"Reload state is not present in the present firing configs. Hence by default reload_state is "
                  f"taken as GOOD \n{Ex}")

        reload_color = data['Reload Color']

        reload_parameters = {"firing_count": fireN, "reload_type": reload_type, "reload_length": reload_length,
                             "video_name": video_name, "reload_color": reload_color, "reload_state": reload_state,
                             "cartridge_state": cartridge_state, "cartridge_color": cartridge_color,
                             "procedure_firings_count": procedure_firings_count, "ship_cap_presence": ship_cap_status,
                             "scenario_title":scenario_name}

        # Firing Test
        serialControlObj.stapling_recovery_test(clampingForce=clampingForce, firingForce=firingForce,
                                     retractionForce=retractionForce, reload_parameters=reload_parameters,
                                     articulationStateinFiring=None)
    # removing adapter
    serialControlObj.removeAdapter()

    # removing clamshell
    serialControlObj.removeClamshell()

    serialControlObj.test_results_pass_percentage(passed_executions=passed_executions)

   # DownloadEventlogs(videoPath, PowerPackComPort, NCDComPort)
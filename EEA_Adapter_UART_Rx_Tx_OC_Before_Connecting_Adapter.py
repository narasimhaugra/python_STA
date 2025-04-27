""" Name: EEATotalFiring; Function: Firing EEA adapter
from removing the handle from charger to, clamshell connecting, adapter connecting, tip rpotector detection, remolad detection,
Created by Manoj Vadali, Date: 21-Sep-2022

Updated on 24-July-2024, by Ugra Narasimha : Code Optimization - (Re-factor code)    """

import sys

import MCPThread
import OLEDRecordingThread
from DownloadEventlogs import DownloadEventlogs
from Prepare_Output_Json_File import *
from Serial_Relay_Control import serialControl


def EEA_Adapter_UART_Rx_Tx_OC_Before_Connecting_Adapter(json_data, NCDComPort,
                                                    PowerPackComPort, BlackBoxComPort, USB6351ComPort,
                                                    ArduinoUNOComPort,
                                                    FtdiUartComPort, PowerSupplyComPort, OUTPUT_PATH, videoPath, itr,
                                                    EEA_RELOAD_EEPROM_command_byte, passed_executions):
    serialControlObj = serialControl(json_data=json_data, NCDComPort=NCDComPort, PowerPackComPort=PowerPackComPort,
                                         BlackBoxComPort=BlackBoxComPort, FtdiUartComPort=FtdiUartComPort,
                                         USB6351ComPort=USB6351ComPort, ArduinoUNOComPort=ArduinoUNOComPort,
                                         DCPowerSupplyComPort=PowerSupplyComPort,
                                         OUTPUT_PATH=OUTPUT_PATH, videoPath=videoPath, itr=itr,
                                         EEA_RELOAD_EEPROM_command_byte=EEA_RELOAD_EEPROM_command_byte)
    serialControlObj.OpenSerialConnection()
    EEA_Adapter_UART_Rx_Tx_Open_Circuit_Before_Connecting_Adapter(serialControlObj, videoPath, itr,
                                                                  passed_executions, PowerPackComPort, NCDComPort)
    serialControlObj.disconnectSerialConnection()


# Purpose-To perform Normal Firing Scenarios
def EEA_Adapter_UART_Rx_Tx_Open_Circuit_Before_Connecting_Adapter(serialControlObj, videoPath, itr,
                                                                  passed_executions, PowerPackComPort, NCDComPort):
    success_flag = True

    fire_pass = 0
    firings = 1

    scenario_number = serialControlObj.json_data['Scenario Num']
    test_scenario = serialControlObj.json_data['Test Scenario']

    print(f"-----------------    {scenario_number}_{test_scenario}  -------------------")

    serialControlObj.battery_level_check()

    serialControlObj.startup_log()

    video_name = f"{scenario_number}_{test_scenario}"
    videoThread = OLEDRecordingThread.myThread(video_name, videoPath)
    videoThread.start()
    serialControlObj.video_thread = videoThread

    serialControlObj.connectClamshellTest(success_flag=success_flag)

    serialControlObj.connect_Adapter_Without_Uart()

    # removing adapter
    serialControlObj.removeAdapter()

    # removing clamshell
    serialControlObj.removeClamshell()

    OLEDRecordingThread.exitFlag = True

    serialControlObj.is_firing_test_passed(procedure_firing=firings-1, fire_pass=fire_pass, firing_count='Fire_1')

    # temp = 'PASS'
    #
    # for item in serialControlObj.Test_Results:
    #     try:
    #         if ((str.split(item, ':', 1))[1].strip()) == 'PASS':
    #             pass
    #         elif ((str.split(item, ':', 1))[1].strip()) == 'FAIL':
    #             temp = 'FAIL'
    #             break
    #     except Exception as Ex:
    #         print(f"Exception Occurred! {Ex}")
    #
    # if temp == 'PASS':
    #     fire_pass = fire_pass + 1
    # print(f'% of Successful Procedures in firing : ', int(100 * fire_pass / firings))
    # # Close MCP port
    #
    # serialControlObj.Test_Results.append(f"Firing=Fire1_iteration_{firings}" +
    #                          ':' + temp)
    # print(serialControlObj.Test_Results)

    serialControlObj.test_results_pass_percentage(passed_executions=passed_executions)

   # DownloadEventlogs(videoPath, PowerPackComPort, NCDComPort)

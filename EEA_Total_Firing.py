import argparse
import os
import sys
import time

import OLEDRecordingThread
from Prepare_Output_Json_File import *
from RelayControlBytes import TURN_OFF_ALL_RELAYS_IN_ALL_BANKS
from Serial_Relay_Control import serialControl


# Function to handle the command-line inputs
def parse_arguments():
    parser = argparse.ArgumentParser(description="EEA Test Fixture Validation")

    # Adding command line arguments
    parser.add_argument("NCDComPort", type=str, help="COM port number of NCD Relay module")
    parser.add_argument("ArduinoUNOComPort", type=str,
                        help="COM port number of Arduino UNO board connected to Time of Flight Sensor")
    parser.add_argument("PowerPackComPort", type=str, help="COM port number of Power Pack (MCP Port)")
    parser.add_argument("BlackBoxComPort", type=str, help="COM port number of 1-wire Black box")
    parser.add_argument("PowerSupplyComPort", type=str, help="COM port number of DC-PowerSupply for Load Simulation")
    parser.add_argument("reload_diameter", type=float, help="Reload Diameter")
    parser.add_argument("reload_color", type=str, help="Reload Color")
    parser.add_argument("clamping_force", type=str, choices=["Low", "Medium"], help="Clamping Force (Low or Medium)")
    parser.add_argument("firing_force", type=str, choices=["Low", "Medium"], help="Firing Force (Low or Medium)")
    parser.add_argument("blob_path", type=str, help="Blob path")
    parser.add_argument("results_path", type=str, help="Results path")

    # Parse the arguments
    arguments = parser.parse_args()
    return arguments


def EEATotalFiring_FixtureValidation(NCDComPort, ArduinoUNOComPort, PowerPackComPort, BlackBoxComPort, PowerSupplyComPort,
                                     reload_diameter, reload_color, clamping_force, firing_force, blob_path, results_path):
    print("----------------- EEA Total Firing for Test Fixture Validation -------------------")

    serialControlObj = serialControl(NCDComPort=NCDComPort,
                                     ArduinoUNOComPort=ArduinoUNOComPort,
                                     PowerPackComPort=PowerPackComPort,
                                     BlackBoxComPort=BlackBoxComPort,
                                     DCPowerSupplyComPort=PowerSupplyComPort,
                                     videoPath=results_path,   ### This is store the total log.txt
                                     OUTPUT_PATH=results_path, blobPath=blob_path,
                                     EEA_RELOAD_EEPROM_command_byte=None)

    serialControlObj.OpenSerialConnection()
    archive_path = None

    # print(f'DCPowerSupplyComPor : {PowerSupplyComPort}')

    today = datetime.datetime.today()
    date_time = today.strftime("%Y-%m-%d %H-%M-%S")

    # Results Path - storing the results along with the video capture
    results_path = os.path.join(results_path, date_time)

    if not os.path.exists(results_path):
        os.makedirs(results_path)

    serialControlObj.OUTPUT_PATH = results_path

    # Video Capturing for Results Evidence
    video_name = f'EEA_Total_Firing'
    videoThread = OLEDRecordingThread.myThread(video_name, results_path)
    videoThread.start()
    serialControlObj.video_thread = videoThread
    time.sleep(5)

    ## Step 1: Blob Uploading to Signia Power Handle
    # BlobUpload(PowerPackComPort, NCDComPort, blob_path, archive_path, results_path)
    # time.sleep(70)

    # Prepare the 'data' dictionary based on the command-line inputs
    data = {
        'Reload Diameter(mm)': reload_diameter,
        'Reload Color': reload_color,
        'Clamping Force': clamping_force,
        'Firing Force': firing_force,
        'Blob Path': blob_path,
        'Results Path ': results_path ### Video Path
    }

    # Call the firing test function
    EEA_Total_Firing(serialControlObj, video_name, data)
    serialControlObj.disconnectSerialConnection()


def EEA_Total_Firing(serialControlObj, video_name, data):
    success_flag = True
    fixture_validation = True

    serialControlObj.send_decimal_bytes(TURN_OFF_ALL_RELAYS_IN_ALL_BANKS[0])

    # # making Initial position to Linear Actuator
    serialControlObj.output_on_off(True, serialControlObj.DcPowerSupplyComPort)
    serialControlObj.applyLoadViaVoltage(8, serialControlObj.DcPowerSupplyComPort)
    serialControlObj.Switch_ONN_Relay(4, 5)
    serialControlObj.Switch_ONN_Relay(4, 6)
    serialControlObj.wait(15)
    serialControlObj.Switch_OFF_Relay(4, 5)
    serialControlObj.Switch_OFF_Relay(4, 6)
    serialControlObj.output_on_off(False, serialControlObj.DcPowerSupplyComPort)

    # NI MAX Applying to Zero
    serialControlObj.apply_load_force(0, fixture_validation_req=fixture_validation)  #### For Low 2, For Medium 5

    # Start MCP Connection
    serialControlObj.startMCP()

    # Step 2: Clamshell Connected
    serialControlObj.connectClamshellTest(success_flag=success_flag, fixture_validation=fixture_validation)

    # Step 3: Adapter Connected
    serialControlObj.connect_adapter_test(fixture_validation=fixture_validation)

    clampingForce = data['Clamping Force']
    firingForce = data['Firing Force']
    reloadLength = data['Reload Diameter(mm)']
    reloadColor = data['Reload Color']

    reload_parameters = {
        "reload_length": reloadLength,
        "reload_color": reloadColor
    }

    # Perform Firing Test
    serialControlObj.EEA_firing_FV(clampingForce=clampingForce, firingForce=firingForce,
                                 reload_parameters=reload_parameters, videoName=video_name, fixtureValidation=fixture_validation)

    # # Remove Adapter and Clamshell
    # serialControlObj.removeAdapter()
    # serialControlObj.removeClamshell(fixtureValidation=fixture_validation)

    OLEDRecordingThread.exitFlag = True



    print('------------------- End of Test Scenario --------------')

# Main entry point of the script
if __name__ == "__main__":
    # Parse command line arguments
    args = parse_arguments()

    # Call the function with the parsed arguments
    EEATotalFiring_FixtureValidation(args.NCDComPort, args.ArduinoUNOComPort, args.PowerPackComPort, args.BlackBoxComPort,
                                     args.PowerSupplyComPort, args.reload_diameter, args.reload_color, args.clamping_force, args.firing_force, args.blob_path,
                                     args.results_path)
    sys.exit(0)

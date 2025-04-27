import getopt
import os
import shutil
import sys
from pathlib import Path

from Adapter_1W_OC_Before_Fire_Mode import Adapter_1W_OC_Before_Fire_Mode
from Adapter_1W_OC_in_Fire_Mode import Adapter_1W_OC_in_Fire_Mode
from Adapter_1W_SC_Before_Fire_Mode import Adapter_1W_SC_Before_Fire_Mode
from Adapter_1W_SC_in_Fire_Mode import Adapter_1W_SC_in_Fire_Mode
from Adapter_UART_Rx_Tx_OC_Before_Fire_Mode import Adapter_UART_Rx_Tx_OC_Before_Fire_Mode
from Adapter_UART_Rx_Tx_OC_in_Fire_Mode import Adapter_UART_Rx_Tx_OC_in_Fire_Mode
from Clamshell_1W_OC_Before_Fire_Mode import Clamshell_1W_OC_Before_Fire_Mode
from Clamshell_1W_OC_in_Fire_Mode import Clamshell_1W_OC_in_Fire_Mode
from Clamshell_1W_SC_Before_Fire_Mode import Clamshell_1W_SC_Before_Fire_Mode
from Clamshell_1W_SC_in_Fire_Mode import Clamshell_1W_SC_in_Fire_Mode
from DV_Cut_Knife_Missing_RE00359465 import EEADVCutKnifeMissing_359465
from DV_Max_Cut_Force_RE00359465 import EEADVMaxCutForce_359465
from DV_Recovery_Mode_RE00460333 import EEADVRecoveryMode_460333
from DV_Staple_Missing_RE00359465 import EEADVStapleMissing_359465
from DownloadEventlogs import DownloadEventlogs
from EEA_Adapter_INIT_40_4_0_3 import EEAAdapterINIT40_4_0_3
from EEA_Adapter_Issue_450475 import EEAIsTotalFiring_450475
from EEA_Adapter_UART_Rx_Tx_OC_After_Entering_Firemode import EEA_Adapter_UART_Rx_Tx_OC_After_Entering_Firemode
from EEA_Failure_to_Increment_1w_Counter import FailuretoIncrement1Wcounter_FiringRecoveryRequirements
from EEA_Failure_to_Increment_EEPROM_Counter import FailuretoIncrementEepromCounter_FiringRecoveryRequirements
from EEA_Firing_Cutting_Recovery import EEAFiringCuttingRecovery
from EEA_Firing_Stapling_Recovery import EEAFiringStaplingRecovery
from EEA_IS_Total_Firing import EEAIsTotalFiring
from EEA_Multiple_Recovery_Mode_400860 import EEADVRecoveryMode_400860
from EEA_Reload_CRC_Failure_Recovery_Mode_450524 import EEADVRecoveryMode_450524
from EmergencyRetraction import EmergencyRetraction
from Issue_417349 import EEAIsTotalFiring_417349
from Low_Battery_Normal_Firing import LowBatteryNormalFiring
from MULU_Clamp_Cycle_Test_Without_Cartridge import MULUClampCycleTestwithoutCartridge
from NormalFiring import NormalFiring
from NormalFiringCondensed import NormalFiringCondensed
from OnOffChargeCycle import ChargeCycle
from Placing_on_Charger import Power_Pack_Placing_on_Charger
from PowerPackInitialization import PowerPackInitialization
from Random_Key_Presses_During_Retraction import RandomKeyPressDuringRetraction
from RapidReloadInsRem import RapidReloadInsRem
from Rapid_Switching_Between_Legacy_and_Smart_Reloads import RapidSwitchingBetweenLegacyandSmartReloads
from Read_Device_Properties import ReadDeviceProperties
# from ShipMode import ShipMode
# import system
from ShipMode import *

# from Serial_Control import *

argumentList = sys.argv[1:]
from EEATotalFiring import EEATotalFiring

from EEACondensedFiring import EEACondensedFiring
from EEA_Adapter_1W_OC_After_Entering_Firemode import EEA_Adapter_1W_OC_After_Entering_Fire_Mode
from EEA_Adapter_1W_SC_After_Entering_Firemode import EEA_Adapter_1W_SC_After_Entering_Firemode

from EEA_Adapter_1W_SC_Before_Entering_Firemode import EEA_Adapter_1W_SC_Before_Entering_Firemode
from EEA_Adapter_1W_OC_Before_Entering_Firemode import EEA_Adapter_1W_OC_Before_Entering_Firemode
from EEA_Adapter_UART_Rx_Tx_OC_Before_Connecting_Adapter import EEA_Adapter_UART_Rx_Tx_OC_Before_Connecting_Adapter
from EEA_Adapter_UART_Rx_Tx_OC_Before_Entering_Firemode import EEA_Adapter_UART_Rx_Tx_OC_Before_Entering_Firemode
from EEA_Random_Key_Presses_during_Firing import EEA_Random_Key_Presses_during_Firing
from EEA_Clamshell_1W_OC_After_Entering_Firemode import EEA_Clamshell_1W_OC_After_Entering_Firemode
from EEA_Clamshell_1W_OC_Before_Entering_Firemode import EEA_Clamshell_1W_OC_Before_Entering_Firemode
from EEA_Clamshell_1W_SC_After_Entering_Firemode import EEA_Clamshell_1W_SC_After_Entering_Firemode
from EEA_Clamshell_1W_SC_Before_Entering_Firemode import EEA_Clamshell_1W_SC_Before_Entering_Firemode
from Smoke_Test import *
from EEA_IS_12_N import T98_FiringRecovery_FiringRecoveryRequirements, T99_CuttingRecovery_FiringRecoveryRequirements
from EEA_Alex import AlexEEA

# Options
# options = "hbcota:"
options = "hbctap:"

# Long options
# long_options = ["blob_path=", "integration", "changeset=", "root=", "output=", "test=", "help", "ver", "Help", "archive_path="]
long_options = ["blob_path=", "integration", "changeset=", "root=", "test=", "help", "ver", "Help", "archive_path=",
                "project="]

BLOB_PATH = 'Not Defined'
CHANGESET = 'Not Defined'
OUTPUT_PATH = 'Not Defined'
TEST = 'Not Defined'
ROOT_PATH = 'Not Defined'
ARCHIVE_PATH = 'Not Defined'
PROJECT_NAME = 'Not Defined'

try:
    # Parsing argument
    arguments, values = getopt.getopt(argumentList, options, long_options)

    # checking each argument
    for currentArgument, currentValue in arguments:

        if currentArgument in ("-h", "--Help", "--help"):
            print("Displaying Help")

        elif currentArgument in ("-b", "--blob_path"):
            BLOB_PATH = currentValue
            print("Blob Path:", BLOB_PATH)

        elif currentArgument in ("-c", "--changeset"):
            CHANGESET = currentValue
            print("Changeset:", CHANGESET)

        elif currentArgument in ("-o", "--out_put"):
            OUTPUT_PATH = currentValue
            print("Output Path:", OUTPUT_PATH)

        elif currentArgument in ("-t", "--test"):
            TEST = currentValue
            print("Test:", TEST)

        elif currentArgument in ("-r", "--root"):
            ROOT_PATH = currentValue
            print("Root Path:", ROOT_PATH)

        elif currentArgument in ("-a", "--archive_path"):
            ARCHIVE_PATH = currentValue
            ARCHIVE_PATH = ARCHIVE_PATH.split(':')[
                0]  # added to accomodate "Archieve path :/ added in Jenkins by Andrew
            print("Archive Path:", ARCHIVE_PATH)

        elif currentArgument in ("-p", "--project"):
            PROJECT_NAME = currentValue
            print("Project Name:", PROJECT_NAME)
    print(ROOT_PATH)
    #    if ROOT_PATH == 'Not Defined' or OUTPUT_PATH == 'Not Defined' or CHANGESET == 'Not Defined' or TEST == 'Not Defined' or BLOB_PATH == 'Not Defined' or ARCHIVE_PATH == 'Not Defined':
    if ROOT_PATH == 'Not Defined' or CHANGESET == 'Not Defined' or TEST == 'Not Defined' or BLOB_PATH == 'Not Defined' or ARCHIVE_PATH == 'Not Defined' or PROJECT_NAME == 'Not Defined':

        print('Required Arguments are not Supplied')
        print('Missing arguments are:')
        if ROOT_PATH == 'Not Defined':
            print('ROOT_PATH')
        if BLOB_PATH == 'Not Defined':
            print('BLOB_PATH')
        # if OUTPUT_PATH == 'Not Defined':
        #     print('OUTPUT_PATH')
        if CHANGESET == 'Not Defined':
            print('CHANGESET')
        if TEST == 'Not Defined':
            print('TEST')
        if ARCHIVE_PATH == 'Not Defined':
            print('ARCHIVE_PATH')
        if PROJECT_NAME == 'Not Defined':
            print('PROJECT_NAME')
        sys.exit(0)

    else:
        pass
except getopt.error as err:
    # output error, and return with an error code
    print(str(err))
# sys.stdout = open("test1.txt", "w")


# SULU_EEPROM = [2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
# MULU_EEPROM = [2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
# CARTRIDGE_EEPROM = [2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]


testType = TEST
# results_path = OUTPUT_PATH

BLOB_FILE_NAME = (os.path.basename(BLOB_PATH))
blob_path = BLOB_PATH.replace(BLOB_FILE_NAME, '')
# full_path = "C:\Program Files\Python37\lib\pathlib.py"
# print(Path(full_path).parents[0])
# print(Path(full_path).parents[1])
# print(Path(full_path).parents[2])
# print(Path(full_path).parents[3])


# OUTPUT_PATH = os.path.splitdrive(blob_path)[1]
#
# OUTPUT_PATH = 'C:' + OUTPUT_PATH
# print(OUTPUT_PATH)

# res_path = Path(blob_path).parents[1]
# res_path = str(res_path) + '/'+ TEST + '/CS-'+CHANGESET
print(PROJECT_NAME)
CHANGESET = 'CS-' + CHANGESET
res_path = os.path.join(PROJECT_NAME, TEST, CHANGESET)
print('res_path', res_path)
#
# if not os.path.exists(OUTPUT_PATH):
#      os.mkdir(OUTPUT_PATH)


today = datetime.datetime.today()
# date_time = today.strftime("%d-%m-%Y-%H-%M") # Manoj Vadali edited to change the Date Formating to match with Build date format
date_time = today.strftime("%Y-%m-%d %H-%M-%S")

# videoPath = OUTPUT_PATH+date_time

# res_path = res_path + '/'+ date_time

res_path = os.path.join(res_path, date_time)
print('res_path', res_path)

# OUTPUT_PATH = 'C:'+ os.path.splitdrive(res_path)[1]
OUTPUT_PATH = os.path.join("C:\\", res_path)
videoPath = OUTPUT_PATH
print("video path :", videoPath)
if not os.path.exists(videoPath):
    os.makedirs(videoPath)

global data
json_data = []
print('ROOT_PATH', ROOT_PATH)
InputJSON = str(ROOT_PATH + '\\Test_Configurator.json')

json_file = open(InputJSON)

# json_file = open('C:\Python\Test_Configurator.json')
json_data = json.load(json_file)
# print(json_data)


NCDComPort = json_data['COM Setting']['NCD IO relay module']
PowerPackComPort = json_data['COM Setting']['Signia Power Pack']
BlackBoxComPort = json_data['COM Setting']['1-wire Black box']
USB6351ComPort = json_data['COM Setting']['NI-USB6351']
ArduinoUNOComPort = json_data['COM Setting']['Arduino Uno']
FtdiUartComPort = json_data['COM Setting']['FTDI Com Port']
PowerSupplyComPort = json_data['COM Setting']['DC Power Supply']
print(NCDComPort, PowerPackComPort, BlackBoxComPort, USB6351ComPort, ArduinoUNOComPort, FtdiUartComPort, PowerSupplyComPort)
serialControl().Test_Results.append(testType)
print('')
print('------------Initialization of Power Pack------------')
# print("Test data ", TEST)
PowerPackInitialization(PowerPackComPort, NCDComPort, FtdiUartComPort, PowerSupplyComPort, TEST)  # Commented for ESD
time.sleep(60)  # For ESD
print('--------------Uploading Blob------------------------------')
#
# BlobUpload(PowerPackComPort, NCDComPort, BLOB_PATH, ARCHIVE_PATH, OUTPUT_PATH)
print('-----------------Power Pack Initialization Post Blob Upload--------------------')
while True:
    # seriallistData = serial.tools.list_ports.comports()
    # print(seriallistData)
    singiaPowerFound = False
    if any("SigniaPowerHandle" in s for s in serial.tools.list_ports.comports()):
        singiaPowerFound = True
    else:
        # print('break from here')
        singiaPowerFound = False
        break
# strPort = 'None'
# while ('SigniaPowerHandle' in strPort):
#     ports = serial.tools.list_ports.comports()
#     numConnection = len(ports)
#     for i in range(0, numConnection):
#         port = ports[i]
#         strPort = str(port)
#         if 'SigniaPowerHandle' in strPort:
#             # print(ports[i])
#             break
#
# while True:
#     # seriallistData = serial.tools.list_ports.comports()
#     # print(seriallistData)
#     singiaPowerFound = False
#     lp = serial.tools.list_ports.comports()
#     for singlePort in lp:
#         # print(str(singlePort))
#         if 'SigniaPowerHandle' in str(singlePort):
#             singiaPowerFound = True
#             continue
#     if singiaPowerFound:
#         continue
#     else:
#         print('break from here')
#         singiaPowerFound = False
#         break

strPort = 'None'
while (not 'SigniaPowerHandle' in strPort):
    ports = serial.tools.list_ports.comports()
    # strPort = 'None'
    numConnection = len(ports)
    for i in range(0, numConnection):
        port = ports[i]
        strPort = str(port)
        if 'SigniaPowerHandle' in strPort:
            print(ports[i])
            break
    break
print('Power Pack Initialization Completed')

# time.sleep(25)
print(testType)
# print(type(testType))
for data in json_data[testType]['Test Scenarios']:
    # print('data:',data)
    print("---------------------------------------------------------------------------------------------")
    SULU_EEPROM = [2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                   0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    MULU_EEPROM = [2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                   0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    CARTRIDGE_EEPROM = [2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    EEA_RELOAD_EEPROM = [2, 3, 0x1C, 0x31, 0x32, 0x33, 0x34, 0x35, 0x36, 0x37, 0x38, 0x39, 0x31, 0x32, 0x33, 0x34, 0x35,
                         0x36, 4, 4, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                         0x1D, 0x80, 0x78, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1]

    # updated the structure to if-elif statement
    if data.get('Reload Type') == "MULU":
        if str(data.get('Reload Length(mm)')) == 30:
            MULU_EEPROM[1] = 1
            MULU_EEPROM[2] = 0x10
            # MULU_EEPROM[19] = (max(data.get('Num of Firings in Procedure'), 12))
            MULU_EEPROM[19] = 12
            MULU_EEPROM[22] = 1
            CARTRIDGE_EEPROM[1] = 1
            CARTRIDGE_EEPROM[2] = 0x18
        elif data.get('Reload Length(mm)') == 45:
            MULU_EEPROM[1] = 2
            MULU_EEPROM[2] = 0x10
            # MULU_EEPROM[19] = (max(data.get('Num of Firings in Procedure'), 12))
            MULU_EEPROM[19] = 12
            # print(value, 'value')
            MULU_EEPROM[22] = 1
            CARTRIDGE_EEPROM[1] = 2
            CARTRIDGE_EEPROM[2] = 0x18

        elif data.get('Reload Length(mm)') == 60:
            MULU_EEPROM[1] = 3
            MULU_EEPROM[2] = 0x10
            MULU_EEPROM[22] = 1
            CARTRIDGE_EEPROM[1] = 3
            CARTRIDGE_EEPROM[2] = 0x18
            MULU_EEPROM[19] = 12
            # try:
            #     MULU_EEPROM[19] = (max(data.get('Num of Firings in Procedure'), 12))
            # except:
            #     pass

        if data.get('Cartridge Color') == 'UNKNOWN':
            CARTRIDGE_EEPROM[26] = 0
        elif data.get('Cartridge Color') == 'White':
            CARTRIDGE_EEPROM[26] = 1
        elif data.get('Cartridge Color') == 'Tan':
            CARTRIDGE_EEPROM[26] = 2
        elif data.get('Cartridge Color') == 'Purple':
            CARTRIDGE_EEPROM[26] = 3
        elif data.get('Cartridge Color') == 'Black':
            CARTRIDGE_EEPROM[26] = 4
        elif data.get('Cartridge Color') == 'Gray':
            CARTRIDGE_EEPROM[26] = 5

    if data.get('Reload Type') == 'SULU':
        if data.get('Reload Length(mm)') == 30:
            SULU_EEPROM[1] = 1
            SULU_EEPROM[2] = 0x0C
            # SULU_EEPROM[2] = 0x18
            SULU_EEPROM[22] = 1

        elif data.get('Reload Length(mm)') == 45:
            SULU_EEPROM[1] = 2
            SULU_EEPROM[2] = 0x0C
            # SULU_EEPROM[2] = 0x18
            SULU_EEPROM[22] = 1

        elif data.get('Reload Length(mm)') == 60:
            SULU_EEPROM[1] = 3
            SULU_EEPROM[2] = 0x0C
            # SULU_EEPROM[2] = 0x18
            SULU_EEPROM[22] = 1

        if data.get('Reload Color') == 'UNKNOWN':
            SULU_EEPROM[34] = 0
        elif data.get('Reload Color') == 'White':
            SULU_EEPROM[34] = 1
        elif data.get('Reload Color') == 'Tan':
            SULU_EEPROM[34] = 2
        elif data.get('Reload Color') == 'Purple':
            SULU_EEPROM[34] = 3
        elif data.get('Reload Color') == 'Black':
            SULU_EEPROM[34] = 4
        elif data.get('Reload Color') == 'Gray':
            SULU_EEPROM[34] = 5
        # if data['Reload/Cartridge Color'] == 'UNKNOWN':
        #     SULU_EEPROM[34] = 0

    if data.get('Reload Length(mm)') == 72:
        SULU_EEPROM[1] = 3
        SULU_EEPROM[2] = 0x14
        # SULU_EEPROM[2] = 0x18
        SULU_EEPROM[22] = 0

    if data.get('Reload Type') == 'EEA':
        if data.get('Reload Diameter(mm)') == 21:
            EEA_RELOAD_EEPROM[1] = 1  # To be updated Manoj Vadali

        elif data.get('Reload Diameter(mm)') == 25:
            EEA_RELOAD_EEPROM[1] = 2  # To be updated Manoj Vadali

        elif data.get('Reload Diameter(mm)') == 28:
            EEA_RELOAD_EEPROM[1] = 3  # To be updated Manoj Vadali

        elif data.get('Reload Diameter(mm)') == 31:
            EEA_RELOAD_EEPROM[1] = 4  # To be updated Manoj Vadali

        elif data.get('Reload Diameter(mm)') == 33:
            EEA_RELOAD_EEPROM[1] = 5  # To be updated Manoj Vadali

        if data.get('Reload Color') == 'Purple':
            EEA_RELOAD_EEPROM[19] = 3  # To be updated Manoj Vadali
        elif data.get('Reload Color') == 'Black':
            EEA_RELOAD_EEPROM[19] = 4  # To be updated Manoj Vadali

        if data.get('Ship cap Present') == 'Yes':
            EEA_RELOAD_EEPROM[18] = 5  # To be updated Manoj Vadali
        elif data.get('Ship cap Present') == 'No':
            EEA_RELOAD_EEPROM[18] = 4  # To be updated Manoj Vadali

    ############# MULU CRC ##########################
    crc_value = CRC16(0x00, MULU_EEPROM)
    # print(crc_value)
    # print(type(crc_value), 'type of crc')
    crc_value = hex(crc_value)
    # print('Original CRC: ', crc_value)
    l = len(crc_value)
    if l == 5:
        crc_value = crc_value[:2] + "0" + crc_value[2:]
    crc_second_byte = crc_value[2:4]
    crc_first_byte = crc_value[4:]

    # crc_second_byte = crc_value[2:4]
    # crc_first_byte = crc_value[4:]
    # # print(crc_first_byte)
    # print(crc_second_byte)
    MULU_EEPROM.append(int(crc_first_byte, 16))
    MULU_EEPROM.append(int(crc_second_byte, 16))
    # print(byte_data)
    # print(len(byte_data))
    ######################################
    MULU_byte_lst = [170, 69, 2, 1] + MULU_EEPROM
    # print(byte_lst)
    crc_value = calc(bytes(MULU_byte_lst))
    crc_value = int(crc_value, 16)
    MULU_byte_lst.append(crc_value)
    MULU_command_byte = (MULU_byte_lst)

    crc_value = CRC16(0x00, CARTRIDGE_EEPROM)
    crc_value = hex(crc_value)
    # print('Original CRC: ', crc_value)
    l = len(crc_value)

    if l == 5:
        crc_value = crc_value[:2] + "0" + crc_value[2:]
    crc_second_byte = crc_value[2:4]
    crc_first_byte = crc_value[4:]

    # print(crc_first_byte)
    # print(crc_second_byte)
    CARTRIDGE_EEPROM.append(int(crc_first_byte, 16))
    CARTRIDGE_EEPROM.append(int(crc_second_byte, 16))
    # print(byte_data)
    # print(len(byte_data))
    ######################################
    CARTRIDGE_byte_lst = [170, 69, 2, 1] + CARTRIDGE_EEPROM
    # print(byte_lst)
    crc_value = calc(bytes(CARTRIDGE_byte_lst))
    crc_value = int(crc_value, 16)
    CARTRIDGE_byte_lst.append(crc_value)
    CARTRIDGE_command_byte = (CARTRIDGE_byte_lst)

    # print('MULU EEPROM', MULU_EEPROM)
    # print('CARTRIDGE EEPROM', CARTRIDGE_EEPROM)

    crc_value = CRC16(0x00, SULU_EEPROM)
    crc_value = hex(crc_value)
    # print('Original CRC: ', crc_value)
    l = len(crc_value)
    crc_second_byte = crc_value[2:(l - 2)]
    crc_first_byte = crc_value[(l - 2):]

    # print(crc_first_byte)
    # print(crc_second_byte)
    # SULU_EEPROM.append(int(crc_first_byte, 16))
    # SULU_EEPROM.append(int(crc_second_byte, 16))
    # print('type', type(crc_first_byte))
    SULU_EEPROM.append(int(crc_first_byte, 16))
    SULU_EEPROM.append(int(crc_second_byte, 16))
    # print(byte_data)
    # print(len(byte_data))
    ######################################
    SULU_byte_lst = [170, 69, 2, 1] + SULU_EEPROM
    # print(byte_lst)
    crc_value = calc(bytes(SULU_byte_lst))
    crc_value = int(crc_value, 16)
    SULU_byte_lst.append(crc_value)

    # print('SULU EEPROM', SULU_EEPROM)

    ############# EEA RELOAD CRC ##########################
    crc_value = CRC16(0x00, EEA_RELOAD_EEPROM)
    # print(crc_value)
    # print(type(crc_value), 'type of crc')
    crc_value = hex(crc_value)
    # print('Original CRC: ', crc_value)
    l = len(crc_value)
    if l == 5:
        crc_value = crc_value[:2] + "0" + crc_value[2:]
    crc_second_byte = crc_value[2:4]
    crc_first_byte = crc_value[4:]
    EEA_RELOAD_EEPROM.append(int(crc_first_byte, 16))
    EEA_RELOAD_EEPROM.append(int(crc_second_byte, 16))
    # print(byte_data)
    # print(len(byte_data))
    ######################################
    EEA_RELOAD_byte_lst = [170, 69, 2, 1] + EEA_RELOAD_EEPROM
    # print(byte_lst)
    crc_value = calc(bytes(EEA_RELOAD_byte_lst))
    crc_value = int(crc_value, 16)
    EEA_RELOAD_byte_lst.append(crc_value)
    EEA_RELOAD_command_byte = (EEA_RELOAD_byte_lst)
    ################################################
    # NormalFiring()
    if data['Test Scenario'] == "Normal Firing":
        # print('data['No of Times to Execute']', range(data['No of Times to Execute']))
        for i in range(data['Num Times to Execute']):
            NormalFiring(data, SULU_byte_lst, MULU_byte_lst, CARTRIDGE_byte_lst, NCDComPort, PowerPackComPort,
                         BlackBoxComPort, USB6351ComPort, ArduinoUNOComPort, OUTPUT_PATH, videoPath, i)

    elif data['Test Scenario'] == "Putting Power Pack on Charger and Removing":
        ChargeCycle(data, PowerPackComPort, NCDComPort, OUTPUT_PATH, videoPath)

    elif data['Test Scenario'] == "Normal Firing Condensed":
        # print('data['No of Times to Execute']', range(data['No of Times to Execute']))
        for i in range(data['Num Times to Execute']):
            NormalFiringCondensed(data, SULU_byte_lst, MULU_byte_lst, CARTRIDGE_byte_lst, NCDComPort, PowerPackComPort,
                                  BlackBoxComPort, USB6351ComPort, ArduinoUNOComPort, OUTPUT_PATH, videoPath, i)

    elif data['Test Scenario'] == "Adapter 1W Open Circuit in Fire Mode":
        for i in range(data['Num Times to Execute']):
            Adapter_1W_OC_in_Fire_Mode(data, SULU_byte_lst, MULU_byte_lst, CARTRIDGE_byte_lst, NCDComPort,
                                       PowerPackComPort,
                                       BlackBoxComPort, USB6351ComPort, ArduinoUNOComPort, OUTPUT_PATH, videoPath, i)

    elif data['Test Scenario'] == "Adapter 1W Open Circuit before Fire Mode":
        for i in range(data['Num Times to Execute']):
            Adapter_1W_OC_Before_Fire_Mode(data, SULU_byte_lst, MULU_byte_lst, CARTRIDGE_byte_lst, NCDComPort,
                                           PowerPackComPort,
                                           BlackBoxComPort, USB6351ComPort, ArduinoUNOComPort, OUTPUT_PATH, videoPath,
                                           i)

    elif data['Test Scenario'] == "Adapter 1W Short Circuit before Fire Mode":
        for i in range(data['Num Times to Execute']):
            Adapter_1W_SC_Before_Fire_Mode(data, SULU_byte_lst, MULU_byte_lst, CARTRIDGE_byte_lst, NCDComPort,
                                           PowerPackComPort,
                                           BlackBoxComPort, USB6351ComPort, ArduinoUNOComPort, OUTPUT_PATH, videoPath,
                                           i)

    elif data['Test Scenario'] == "Adapter 1W Short Circuit in Fire Mode":
        for i in range(data['Num Times to Execute']):
            Adapter_1W_SC_in_Fire_Mode(data, SULU_byte_lst, MULU_byte_lst, CARTRIDGE_byte_lst, NCDComPort,
                                       PowerPackComPort,
                                       BlackBoxComPort, USB6351ComPort, ArduinoUNOComPort, OUTPUT_PATH, videoPath, i)

    elif data['Test Scenario'] == "Adapter UART Open Circuit in Fire Mode":
        for i in range(data['Num Times to Execute']):
            Adapter_UART_Rx_Tx_OC_in_Fire_Mode(data, SULU_byte_lst, MULU_byte_lst, CARTRIDGE_byte_lst, NCDComPort,
                                               PowerPackComPort,
                                               BlackBoxComPort, USB6351ComPort, ArduinoUNOComPort, OUTPUT_PATH,
                                               videoPath, i)

    elif data['Test Scenario'] == "Adapter UART Open Circuit before Fire Mode":
        for i in range(data['Num Times to Execute']):
            Adapter_UART_Rx_Tx_OC_Before_Fire_Mode(data, SULU_byte_lst, MULU_byte_lst, CARTRIDGE_byte_lst, NCDComPort,
                                                   PowerPackComPort, BlackBoxComPort, USB6351ComPort, ArduinoUNOComPort,
                                                   OUTPUT_PATH, videoPath, i)

    elif data['Test Scenario'] == "Adapter UART Open Circuit without Reload":
        for i in range(data['Num Times to Execute']):
            Adapter_UART_Rx_Tx_OC_Before_Fire_Mode(data, SULU_byte_lst, MULU_byte_lst, CARTRIDGE_byte_lst, NCDComPort,
                                                   PowerPackComPort,
                                                   BlackBoxComPort, USB6351ComPort, ArduinoUNOComPort, OUTPUT_PATH,
                                                   videoPath)

    elif data['Test Scenario'] == "Clamshell 1W Open Circuit in Fire Mode":
        for i in range(data['Num Times to Execute']):
            Clamshell_1W_OC_in_Fire_Mode(data, SULU_byte_lst, MULU_byte_lst, CARTRIDGE_byte_lst, NCDComPort,
                                         PowerPackComPort,
                                         BlackBoxComPort, USB6351ComPort, ArduinoUNOComPort, OUTPUT_PATH, videoPath, i)

    elif data['Test Scenario'] == "Clamshell 1W Open Circuit before Fire Mode":
        for i in range(data['Num Times to Execute']):
            Clamshell_1W_OC_Before_Fire_Mode(data, SULU_byte_lst, MULU_byte_lst, CARTRIDGE_byte_lst, NCDComPort,
                                             PowerPackComPort,
                                             BlackBoxComPort, USB6351ComPort, ArduinoUNOComPort, OUTPUT_PATH, videoPath,
                                             i)

    elif data['Test Scenario'] == "Clamshell 1W Short Circuit before Fire Mode":
        for i in range(data['Num Times to Execute']):
            Clamshell_1W_SC_Before_Fire_Mode(data, SULU_byte_lst, MULU_byte_lst, CARTRIDGE_byte_lst, NCDComPort,
                                             PowerPackComPort,
                                             BlackBoxComPort, USB6351ComPort, ArduinoUNOComPort, OUTPUT_PATH, videoPath,
                                             i)

    elif data['Test Scenario'] == "Clamshell 1W Short Circuit in Fire Mode":
        for i in range(data['Num Times to Execute']):
            Clamshell_1W_SC_in_Fire_Mode(data, SULU_byte_lst, MULU_byte_lst, CARTRIDGE_byte_lst, NCDComPort,
                                         PowerPackComPort,
                                         BlackBoxComPort, USB6351ComPort, ArduinoUNOComPort, OUTPUT_PATH, videoPath, i)

    elif data['Test Scenario'] == "Ship Mode":
        ShipMode(data, PowerPackComPort, OUTPUT_PATH, videoPath)
        pass

    elif data['Test Scenario'] == "Rapid Reload Insertion & Removal":
        # pass
        RapidReloadInsRem(data, SULU_byte_lst, MULU_byte_lst, CARTRIDGE_byte_lst, NCDComPort, PowerPackComPort,
                          BlackBoxComPort, USB6351ComPort, ArduinoUNOComPort, OUTPUT_PATH, videoPath,
                          data['Num Times to Execute'])

    elif data['Test Scenario'] == "Rapid Switching Between Legacy and Smart Reloads":
        # pass
        RapidSwitchingBetweenLegacyandSmartReloads(data, SULU_byte_lst, MULU_byte_lst, CARTRIDGE_byte_lst, NCDComPort,
                                                   PowerPackComPort,
                                                   BlackBoxComPort, USB6351ComPort, ArduinoUNOComPort, OUTPUT_PATH,
                                                   videoPath, data['Num Times to Execute'])

    elif data['Test Scenario'] == "Adapter UART RX Error":
        for i in range(data['Num Times to Execute']):
            pass
    elif data['Test Scenario'] == "Emergency Retracting":
        for i in range(data['Num Times to Execute']):
            pass
            EmergencyRetraction(data, SULU_byte_lst, MULU_byte_lst, CARTRIDGE_byte_lst, NCDComPort, PowerPackComPort,
                                BlackBoxComPort, USB6351ComPort, ArduinoUNOComPort, OUTPUT_PATH, videoPath, i)
    elif data['Test Scenario'] == "Random Key Press During Retraction":
        # print('data['No of Times to Execute']', range(data['No of Times to Execute']))
        for i in range(data['Num Times to Execute']):
            RandomKeyPressDuringRetraction(data, SULU_byte_lst, MULU_byte_lst, CARTRIDGE_byte_lst, NCDComPort,
                                           PowerPackComPort,
                                           BlackBoxComPort, USB6351ComPort, ArduinoUNOComPort, OUTPUT_PATH, videoPath,
                                           i)


    elif data['Test Scenario'] == "Low Battery Normal Firing":
        # print('data['No of Times to Execute']', range(data['No of Times to Execute']))
        for i in range(data['Num Times to Execute']):
            LowBatteryNormalFiring(data, SULU_byte_lst, MULU_byte_lst, CARTRIDGE_byte_lst, NCDComPort, PowerPackComPort,
                                   BlackBoxComPort, USB6351ComPort, ArduinoUNOComPort, OUTPUT_PATH, videoPath, i)

    elif data['Test Scenario'] == "MULU Clamp Cycle Test without Cartridge":
        # print('data['No of Times to Execute']', range(data['No of Times to Execute']))
        for i in range(data['Num Times to Execute']):
            MULUClampCycleTestwithoutCartridge(data, SULU_byte_lst, MULU_byte_lst, CARTRIDGE_byte_lst, NCDComPort,
                                               PowerPackComPort,
                                               BlackBoxComPort, USB6351ComPort, ArduinoUNOComPort, OUTPUT_PATH,
                                               videoPath, i)


    elif data['Test Scenario'] == "EEA Total Firing":
        # print('data['No of Times to Execute']', range(data['No of Times to Execute']))
        passed_executions = {}
        for i in range(data['Num Times to Execute']):
            # EEATotalFiring(data, SULU_byte_lst, MULU_byte_lst, CARTRIDGE_byte_lst, NCDComPort, PowerPackComPort,
            #                BlackBoxComPort, USB6351ComPort, ArduinoUNOComPort, OUTPUT_PATH, videoPath, i
            #                )
            EEAIsTotalFiring(data, NCDComPort, PowerPackComPort,
                             BlackBoxComPort, USB6351ComPort, ArduinoUNOComPort, FtdiUartComPort, PowerSupplyComPort, OUTPUT_PATH,
                             videoPath, i, EEA_RELOAD_byte_lst, passed_executions)

    elif data['Test Scenario'] == "Adapter Swimlane Tilt Open 450475":
        # print('data['No of Times to Execute']', range(data['No of Times to Execute']))
        passed_executions = {}
        for i in range(data['Num Times to Execute']):
            # EEATotalFiring(data, SULU_byte_lst, MULU_byte_lst, CARTRIDGE_byte_lst, NCDComPort, PowerPackComPort,
            #                BlackBoxComPort, USB6351ComPort, ArduinoUNOComPort, OUTPUT_PATH, videoPath, i,
            #                EEA_RELOAD_byte_lst)
            EEAIsTotalFiring_450475(data, NCDComPort, PowerPackComPort,
                                    BlackBoxComPort, USB6351ComPort, ArduinoUNOComPort, FtdiUartComPort, PowerSupplyComPort,
                                    OUTPUT_PATH,
                                    videoPath, i, EEA_RELOAD_byte_lst, passed_executions)
    elif data['Test Scenario'] == "EEA Total Firing 417349":
        # print('data['No of Times to Execute']', range(data['No of Times to Execute']))
        passed_executions = {}
        for i in range(data['Num Times to Execute']):
            # EEATotalFiring(data, SULU_byte_lst, MULU_byte_lst, CARTRIDGE_byte_lst, NCDComPort, PowerPackComPort,
            #                BlackBoxComPort, USB6351ComPort, ArduinoUNOComPort, OUTPUT_PATH, videoPath, i,
            #                EEA_RELOAD_byte_lst)


            EEAIsTotalFiring_417349(data, NCDComPort, PowerPackComPort,
                                    BlackBoxComPort, USB6351ComPort, ArduinoUNOComPort, FtdiUartComPort, OUTPUT_PATH,
                                    videoPath, i, EEA_RELOAD_byte_lst, passed_executions)

    elif data['Test Scenario'] == "Firing Recovery":
        # print('data['No of Times to Execute']', range(data['No of Times to Execute']))
        passed_executions = {}
        for i in range(data['Num Times to Execute']):
            EEAFiringStaplingRecovery(data, NCDComPort, PowerPackComPort,
                                    BlackBoxComPort, USB6351ComPort, ArduinoUNOComPort, FtdiUartComPort, PowerSupplyComPort,
                                     OUTPUT_PATH,videoPath, i, EEA_RELOAD_byte_lst, passed_executions)


    elif data['Test Scenario'] == "Cut Recovery":
        # print('data['No of Times to Execute']', range(data['No of Times to Execute']))
        passed_executions = {}
        for i in range(data['Num Times to Execute']):
            EEAFiringCuttingRecovery(data, NCDComPort, PowerPackComPort,
                                    BlackBoxComPort, USB6351ComPort, ArduinoUNOComPort, FtdiUartComPort, PowerSupplyComPort,
                                     OUTPUT_PATH,videoPath, i, EEA_RELOAD_byte_lst, passed_executions)

    elif data['Test Scenario'] == "Multiple Recovery Mode 400860":
        # print('data['No of Times to Execute']', range(data['No of Times to Execute']))
        passed_executions = {}
        for i in range(data['Num Times to Execute']):
            EEADVRecoveryMode_400860(data, NCDComPort, PowerPackComPort,
                                    BlackBoxComPort, USB6351ComPort, ArduinoUNOComPort, FtdiUartComPort, PowerSupplyComPort,
                                     OUTPUT_PATH,videoPath, i, EEA_RELOAD_byte_lst, passed_executions)

    elif data['Test Scenario'] == "EEA DV Recovery Mode 460333":
        # print('data['No of Times to Execute']', range(data['No of Times to Execute']))
        passed_executions = {}
        for i in range(data['Num Times to Execute']):
            EEADVRecoveryMode_460333(data, NCDComPort, PowerPackComPort,
                                     BlackBoxComPort, USB6351ComPort, ArduinoUNOComPort, FtdiUartComPort,
                                     PowerSupplyComPort,
                                     OUTPUT_PATH, videoPath, i, EEA_RELOAD_byte_lst, passed_executions)

    elif data['Test Scenario'] == "EEA DV Staple Missing 359465":
        # print('data['No of Times to Execute']', range(data['No of Times to Execute']))
        passed_executions = {}
        for i in range(data['Num Times to Execute']):
            print("passed_executions", passed_executions)
            EEADVStapleMissing_359465(data, NCDComPort, PowerPackComPort,
                                     BlackBoxComPort, USB6351ComPort, ArduinoUNOComPort, FtdiUartComPort,
                                     PowerSupplyComPort,
                                     OUTPUT_PATH, videoPath, i, EEA_RELOAD_byte_lst, passed_executions)

    elif data['Test Scenario'] == "EEA DV Cut Knife Missing 359465":
        # print('data['No of Times to Execute']', range(data['No of Times to Execute']))
        passed_executions = {}
        for i in range(data['Num Times to Execute']):
            EEADVCutKnifeMissing_359465(data, NCDComPort, PowerPackComPort,
                                     BlackBoxComPort, USB6351ComPort, ArduinoUNOComPort, FtdiUartComPort,
                                     PowerSupplyComPort,
                                     OUTPUT_PATH, videoPath, i, EEA_RELOAD_byte_lst, passed_executions)

    elif data['Test Scenario'] == "EEA DV Maximum Cut Force 359465":
        # print('data['No of Times to Execute']', range(data['No of Times to Execute']))
        passed_executions = {}
        for i in range(data['Num Times to Execute']):
            EEADVMaxCutForce_359465(data, NCDComPort, PowerPackComPort,
                                     BlackBoxComPort, USB6351ComPort, ArduinoUNOComPort, FtdiUartComPort,
                                     PowerSupplyComPort,
                                     OUTPUT_PATH, videoPath, i, EEA_RELOAD_byte_lst, passed_executions)

    elif data['Test Scenario'] == "Reload CRC Failure 450524":
        # print('data['No of Times to Execute']', range(data['No of Times to Execute']))
        passed_executions = {}
        for i in range(data['Num Times to Execute']):
            EEADVRecoveryMode_450524(data, NCDComPort, PowerPackComPort,
                                    BlackBoxComPort, USB6351ComPort, ArduinoUNOComPort, FtdiUartComPort, PowerSupplyComPort,
                                    OUTPUT_PATH, videoPath, i, EEA_RELOAD_byte_lst, passed_executions)

    elif data['Test Scenario'] == "EEA Adapter INIT 40.4.0.3":
        # print('data['No of Times to Execute']', range(data['No of Times to Execute']))
        passed_executions = {}
        for i in range(data['Num Times to Execute']):
            EEAAdapterINIT40_4_0_3(data, NCDComPort, PowerPackComPort,
                                    BlackBoxComPort, USB6351ComPort, ArduinoUNOComPort, FtdiUartComPort, PowerSupplyComPort,
                                    OUTPUT_PATH, videoPath, i, EEA_RELOAD_byte_lst, passed_executions)



    elif data['Test Scenario'] == "EEA Condensed Firing":
        # print('data['No of Times to Execute']', range(data['No of Times to Execute']))
        for i in range(data['Num Times to Execute']):
            EEACondensedFiring(data, SULU_byte_lst, MULU_byte_lst, CARTRIDGE_byte_lst, NCDComPort, PowerPackComPort,
                               BlackBoxComPort, USB6351ComPort, ArduinoUNOComPort, OUTPUT_PATH, videoPath, i,
                               EEA_RELOAD_byte_lst)

    elif data['Test Scenario'] == "Alex EEA":
        # print('data['No of Times to Execute']', range(data['No of Times to Execute']))
        for i in range(data['Num Times to Execute']):
            AlexEEA(data, NCDComPort, PowerPackComPort,
                    BlackBoxComPort, USB6351ComPort, ArduinoUNOComPort, OUTPUT_PATH, videoPath, i,
                    EEA_RELOAD_byte_lst, passed_executions={})


    elif data['Test Scenario'] == "EEA Adapter 1W OC after entering fire mode":
        passed_executions = {}
        for i in range(data['Num Times to Execute']):
            EEA_Adapter_1W_OC_After_Entering_Fire_Mode(data, NCDComPort, PowerPackComPort,
                                            BlackBoxComPort, USB6351ComPort, ArduinoUNOComPort, FtdiUartComPort,
                                            PowerSupplyComPort,
                                            OUTPUT_PATH, videoPath, i, EEA_RELOAD_byte_lst, passed_executions)
            # EEA_Adapter_1W_OC_After_Entering_Fire_Mode(data, SULU_byte_lst, MULU_byte_lst, CARTRIDGE_byte_lst,
            #                                           NCDComPort, PowerPackComPort,
            #                                           BlackBoxComPort, USB6351ComPort, ArduinoUNOComPort,
            #                                           OUTPUT_PATH,
            #                                           videoPath, i)

    elif data['Test Scenario'] == "EEA Adapter 1W SC after entering fire mode":
        passed_executions = {}
        for i in range(data['Num Times to Execute']):
            EEA_Adapter_1W_SC_After_Entering_Firemode(data, NCDComPort, PowerPackComPort,
                                            BlackBoxComPort, USB6351ComPort, ArduinoUNOComPort, FtdiUartComPort,
                                            PowerSupplyComPort,
                                            OUTPUT_PATH, videoPath, i, EEA_RELOAD_byte_lst, passed_executions)
            # EEA_Adapter_1W_SC_After_Entering_Firemode(data, SULU_byte_lst, MULU_byte_lst, CARTRIDGE_byte_lst,
            #                                            NCDComPort, PowerPackComPort,
            #                                            BlackBoxComPort, USB6351ComPort, ArduinoUNOComPort,
            #                                            OUTPUT_PATH,
            #                                            videoPath, i)

    elif data['Test Scenario'] == "EEA Adapter 1W SC before entering fire mode":
        passed_executions = {}
        for i in range(data['Num Times to Execute']):
            EEA_Adapter_1W_SC_Before_Entering_Firemode(data, NCDComPort, PowerPackComPort,
                                            BlackBoxComPort, USB6351ComPort, ArduinoUNOComPort, FtdiUartComPort,
                                            PowerSupplyComPort,
                                            OUTPUT_PATH, videoPath, i, EEA_RELOAD_byte_lst, passed_executions)
            # EEA_Adapter_1W_SC_Before_Entering_Firemode(data, SULU_byte_lst, MULU_byte_lst, CARTRIDGE_byte_lst,
            #                                            NCDComPort, PowerPackComPort,
            #                                            BlackBoxComPort, USB6351ComPort, ArduinoUNOComPort,
            #                                            OUTPUT_PATH,
            #                                            videoPath, i)

    elif data['Test Scenario'] == "EEA Adapter 1W OC before entering fire mode":
        passed_executions = {}
        for i in range(data['Num Times to Execute']):
            EEA_Adapter_1W_OC_Before_Entering_Firemode(data, NCDComPort, PowerPackComPort,
                                            BlackBoxComPort, USB6351ComPort, ArduinoUNOComPort, FtdiUartComPort,
                                            PowerSupplyComPort,
                                            OUTPUT_PATH, videoPath, i, EEA_RELOAD_byte_lst, passed_executions)
            # EEA_Adapter_1W_OC_Before_Entering_Firemode(data, SULU_byte_lst, MULU_byte_lst, CARTRIDGE_byte_lst,
            #                                                     NCDComPort, PowerPackComPort,
            #                                                     BlackBoxComPort, USB6351ComPort, ArduinoUNOComPort,
            #                                                     OUTPUT_PATH,
            #                                                     videoPath, i)

    elif data['Test Scenario'] == "EEA Adapter UART Rx Tx OC after entering fire mode":
        passed_executions = {}
        for i in range(data['Num Times to Execute']):
            EEA_Adapter_UART_Rx_Tx_OC_After_Entering_Firemode(data, NCDComPort, PowerPackComPort,
                                            BlackBoxComPort, USB6351ComPort, ArduinoUNOComPort, FtdiUartComPort,
                                            PowerSupplyComPort,
                                            OUTPUT_PATH, videoPath, i, EEA_RELOAD_byte_lst, passed_executions)
            # EEA_Adapter_UART_Rx_Tx_OC_After_Entering_Firemode(data, SULU_byte_lst, MULU_byte_lst, CARTRIDGE_byte_lst,
            #                                                     NCDComPort, PowerPackComPort,
            #                                                     BlackBoxComPort, USB6351ComPort, ArduinoUNOComPort,
            #                                                     OUTPUT_PATH,
            #                                                     videoPath, i)


    elif data['Test Scenario'] == "EEA Adapter UART Rx Tx OC before connecting adapter":
        passed_executions = {}
        for i in range(data['Num Times to Execute']):
            EEA_Adapter_UART_Rx_Tx_OC_Before_Connecting_Adapter(data, NCDComPort, PowerPackComPort,
                                            BlackBoxComPort, USB6351ComPort, ArduinoUNOComPort, FtdiUartComPort,
                                            PowerSupplyComPort,
                                            OUTPUT_PATH, videoPath, i, EEA_RELOAD_byte_lst, passed_executions)
            # EEA_Adapter_UART_Rx_Tx_OC_Before_Connecting_Adapter(data, SULU_byte_lst, MULU_byte_lst, CARTRIDGE_byte_lst,
            #                                                    NCDComPort, PowerPackComPort,
            #                                                    BlackBoxComPort, USB6351ComPort, ArduinoUNOComPort,
            #                                                    OUTPUT_PATH,
            #                                                    videoPath, i)


    elif data['Test Scenario'] == "EEA Adapter UART Rx Tx OC before entering fire mode":
        passed_executions = {}
        for i in range(data['Num Times to Execute']):
            EEA_Adapter_UART_Rx_Tx_OC_Before_Entering_Firemode(data, NCDComPort, PowerPackComPort,
                                            BlackBoxComPort, USB6351ComPort, ArduinoUNOComPort, FtdiUartComPort,
                                            PowerSupplyComPort,
                                            OUTPUT_PATH, videoPath, i, EEA_RELOAD_byte_lst, passed_executions)
            # EEA_Adapter_UART_Rx_Tx_OC_Before_Entering_Firemode(data, SULU_byte_lst, MULU_byte_lst, CARTRIDGE_byte_lst,
            #                                              NCDComPort, PowerPackComPort,
            #                                              BlackBoxComPort, USB6351ComPort, ArduinoUNOComPort,
            #                                              OUTPUT_PATH,
            #                                              videoPath, i)

    elif data['Test Scenario'] == "EEA Random Key Presses during Firing":
        passed_executions = {}
        for i in range(data['Num Times to Execute']):
            EEA_Random_Key_Presses_during_Firing(data, NCDComPort, PowerPackComPort,
                                            BlackBoxComPort, USB6351ComPort, ArduinoUNOComPort, FtdiUartComPort,
                                            PowerSupplyComPort,
                                            OUTPUT_PATH, videoPath, i, EEA_RELOAD_byte_lst, passed_executions)

    elif data['Test Scenario'] == "EEA Clamshell 1W OC after entering fire mode":
        passed_executions = {}
        for i in range(data['Num Times to Execute']):
            EEA_Clamshell_1W_OC_After_Entering_Firemode(data, NCDComPort, PowerPackComPort,
                                            BlackBoxComPort, USB6351ComPort, ArduinoUNOComPort, FtdiUartComPort,
                                            PowerSupplyComPort,
                                            OUTPUT_PATH, videoPath, i, EEA_RELOAD_byte_lst, passed_executions)
            # EEA_Clamshell_1W_OC_After_Entering_Firemode(data, SULU_byte_lst, MULU_byte_lst, CARTRIDGE_byte_lst, NCDComPort, PowerPackComPort,
            #                BlackBoxComPort, USB6351ComPort, ArduinoUNOComPort, OUTPUT_PATH, videoPath, i)




    elif data['Test Scenario'] == "EEA Clamshell 1W OC before entering fire mode":
        passed_executions = {}
        for i in range(data['Num Times to Execute']):
            EEA_Clamshell_1W_OC_Before_Entering_Firemode(data, NCDComPort, PowerPackComPort,
                                            BlackBoxComPort, USB6351ComPort, ArduinoUNOComPort, FtdiUartComPort,
                                            PowerSupplyComPort,
                                            OUTPUT_PATH, videoPath, i, EEA_RELOAD_byte_lst, passed_executions)

            # EEA_Clamshell_1W_OC_Before_Entering_Firemode(data, SULU_byte_lst, MULU_byte_lst, CARTRIDGE_byte_lst,
            #                                             NCDComPort, PowerPackComPort,
            #                                             BlackBoxComPort, USB6351ComPort, ArduinoUNOComPort, OUTPUT_PATH,
            #                                             videoPath, i)

    elif data['Test Scenario'] == "EEA Clamshell 1W SC after entering fire mode":
        passed_executions = {}
        for i in range(data['Num Times to Execute']):
            EEA_Clamshell_1W_SC_After_Entering_Firemode(data, NCDComPort, PowerPackComPort,
                                            BlackBoxComPort, USB6351ComPort, ArduinoUNOComPort, FtdiUartComPort,
                                            PowerSupplyComPort,
                                            OUTPUT_PATH, videoPath, i, EEA_RELOAD_byte_lst, passed_executions)
            # EEA_Clamshell_1W_SC_After_Entering_Firemode(data, SULU_byte_lst, MULU_byte_lst, CARTRIDGE_byte_lst,
            #                                             NCDComPort, PowerPackComPort,
            #                                             BlackBoxComPort, USB6351ComPort, ArduinoUNOComPort, OUTPUT_PATH,
            #                                             videoPath, i)

    elif data['Test Scenario'] == "EEA Clamshell 1W SC before entering fire mode":
        passed_executions = {}
        for i in range(data['Num Times to Execute']):
            EEA_Clamshell_1W_SC_Before_Entering_Firemode(data, NCDComPort, PowerPackComPort,
                                            BlackBoxComPort, USB6351ComPort, ArduinoUNOComPort, FtdiUartComPort,
                                            PowerSupplyComPort,
                                            OUTPUT_PATH, videoPath, i, EEA_RELOAD_byte_lst, passed_executions)
            # EEA_Clamshell_1W_SC_Before_Entering_Firemode(data, SULU_byte_lst, MULU_byte_lst, CARTRIDGE_byte_lst,
            #                                             NCDComPort, PowerPackComPort,
            #                                             BlackBoxComPort, USB6351ComPort, ArduinoUNOComPort, OUTPUT_PATH,
            #                                             videoPath, i)



    elif data['Test Scenario'] == "Failure to increment 1W counters":
        for i in range(data['Num Times to Execute']):
            passed_executions = {}
            FailuretoIncrement1Wcounter_FiringRecoveryRequirements(data, NCDComPort, PowerPackComPort,
                                            BlackBoxComPort, USB6351ComPort, ArduinoUNOComPort, FtdiUartComPort,
                                            PowerSupplyComPort,
                                            OUTPUT_PATH, videoPath, i, EEA_RELOAD_byte_lst, passed_executions)
    elif data['Test Scenario'] == "Failure to increment EEPROM counters":
        for i in range(data['Num Times to Execute']):
            passed_executions = {}
            FailuretoIncrementEepromCounter_FiringRecoveryRequirements(data, NCDComPort, PowerPackComPort,
                                                                   BlackBoxComPort, USB6351ComPort,
                                                                   ArduinoUNOComPort, FtdiUartComPort,
                                                                   PowerSupplyComPort,
                                                                   OUTPUT_PATH, videoPath, i, EEA_RELOAD_byte_lst,
                                                                   passed_executions)

    elif data['Test Scenario'] == "Firing Recovery Firing Recovery Requirements":
        for i in range(data['Num Times to Execute']):
            T98_FiringRecovery_FiringRecoveryRequirements(data, SULU_byte_lst, MULU_byte_lst, CARTRIDGE_byte_lst,
                                                          NCDComPort, PowerPackComPort,
                                                          BlackBoxComPort, USB6351ComPort, ArduinoUNOComPort,
                                                          FtdiUartComPort, OUTPUT_PATH, videoPath, i,
                                                          EEA_RELOAD_byte_lst)

    elif data['Test Scenario'] == "Cutting Recovery Firing Recovery Requirements":
            for i in range(data['Num Times to Execute']):
                T99_CuttingRecovery_FiringRecoveryRequirements(data, SULU_byte_lst, MULU_byte_lst, CARTRIDGE_byte_lst,
                                                           NCDComPort, PowerPackComPort,
                                                           BlackBoxComPort, USB6351ComPort, ArduinoUNOComPort,
                                                           FtdiUartComPort, OUTPUT_PATH, videoPath, i,
                                                           EEA_RELOAD_byte_lst)

    elif data['Test Scenario'] == "Smoke Test":
        # print('data['No of Times to Execute']', range(data['No of Times to Execute']))
        for i in range(data['Num Times to Execute']):
            SmokeTest(data, SULU_byte_lst, MULU_byte_lst, CARTRIDGE_byte_lst, NCDComPort, PowerPackComPort,
                      BlackBoxComPort, USB6351ComPort, ArduinoUNOComPort, OUTPUT_PATH, videoPath, i,
                      EEA_RELOAD_byte_lst)

PowerPackInitialization(PowerPackComPort, NCDComPort, FtdiUartComPort, PowerSupplyComPort, TEST)
time.sleep(30)
A, B, C, D, E, F, G, H = ReadDeviceProperties(PowerPackComPort)
try:
    B = B.replace('Rev', '')
    B = B.strip()
except:
    pass

try:
    C = C.replace('Rev', '')
    C = C.strip()
except:
    pass

try:
    D = D.replace('Rev', '')
    D = D.strip()
except:
    pass

try:
    E = E.replace('Rev', '')
    E = E.strip()
except:
    pass

try:
    F = F.replace('Rev', '')
    F = F.strip()
except:
    pass

try:
    G = G.replace('Rev', '')
    G = G.strip()
except:
    pass
str_date_time = str(date_time)
T = str_date_time.split()
T1 = (T[1])
T1 = T1.split('-')
T1 = T1[0] + ':' + T1[1] + ':' + T1[2]
T = str_date_time
print(T)

# update_SW_Config_Dict(TestDate=str(date_time), BuildDate=A, BlobVersion=B, PowerPackVersion=C,
#                       PowerPackBootloaderVersion=D,
#  AdapterEGIAVersion=E, AdapterEEAVersion=F, AdapterBootloaderVersion=G)

update_SW_Config_Dict(ProjectName=PROJECT_NAME, TestDate=T, BuildDate=A, BlobVersion=B, PowerPackVersion=C,
                      PowerPackBootloaderVersion=D,
                      AdapterEGIAVersion=E, AdapterEEAVersion=F, AdapterBootloaderVersion=G)

time.sleep(5)

DownloadEventlogs(videoPath, PowerPackComPort, NCDComPort)

# return (Blob_date, System_Version, PP_Blob_version, PP_Boot_version, Adapter_EGIA_version, Adapter_EEA_version, Adapter_Boot_version, Agile_Part_Number)
src = videoPath + '/test_automation_results.json'
print(TEST)
print(CHANGESET)

try:
    # res_path = res_path.replace('\\', '/')
    res_path = ARCHIVE_PATH + ':\\' + res_path
    res_path = res_path.replace('/', '\\')

    print(res_path)
    if not os.path.exists(res_path):
        os.makedirs(res_path)

    # dp = 'Z:/Signia-Legacy' + '/' + TEST + '/'+ "CS-"+ CHANGESET
    # if not os.path.exists(dp):
    #     os.makedirs(dp)
    src = src.replace('\\', '/')

    src = os.path.splitdrive(src)[1]
    # src = ARCHIVE_PATH +':'+ src
    src = ARCHIVE_PATH + ":\\" + src
    src = src.replace('\\', '/')
    src = src.replace('//', '/')
    fin_path = str(Path(res_path).parents[0])
    fin_path = fin_path.replace('\\', '/')
    if not os.path.exists(fin_path):
        os.makedirs(fin_path)

    # updating to match with Andrew's comment of updating latest path excluding the detailed path  by Manoj Vadali#
    # Z:/Harmony/Test-Regression-EGIA/CS-946/2022-06-29 14-47-55 (UTC)
    f = open((fin_path + '/test_automation_results_latest.txt'), 'w')
    # f = open((date_time +'/test_automation_results_latest.txt'), 'w')
    # f = open((videoPath +'/test_automation_results_latest.txt'), 'w')

    # =  EGIA_Sanity_Checks
    # f.write(src) # commented on 11th Aug by Manoj Vadali
    f.write((os.path.join(src.split('/')[-2], src.split('/')[-1])))
    # dst = blob_path + date_time
    # if not os.path.exists(dst):
    src = str(Path(src).parents[0])
    #     os.makedirs(dst)
    #     os.makedirs(dst)
    src = str(os.path.splitdrive(src)[1])
    src = 'C:' + src + '/test_automation_results.json'

    src = src.replace('\\', '/')
    dst = res_path
    # shutil.copy(src=str(src).replace('\\', '/'), dst=str(dst).replace('\\', '/'))
    shutil.copy(src=str(src), dst=str(dst).replace('\\', '/'))

    rfile = open(src)
    file_contents = rfile.read()
    print('================== Test Results Summary =============')
    print(file_contents)
    rfile.close()

    src = videoPath + '/TotalLog.txt'
    shutil.copy(src=src.replace('\\', '/'), dst=str(dst).replace('\\', '/'))

    src = videoPath + '/sample_result.txt'
    shutil.copy(src=src.replace('\\', '/'), dst=str(dst).replace('\\', '/'))

    print(TEST + "  completed with CS: " + CHANGESET)
    f.close()
except Exception as ex:
    print(f"exception occurred!!! {ex}")

json_file.close()

Power_Pack_Placing_on_Charger(PowerPackComPort, NCDComPort)
print('=============== End Of Test ===================')

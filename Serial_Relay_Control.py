# @ author - Varun Pandey
# Ver # 1, dated - Dec 22, 2021
# this code has been moved from NormalFiring.py - to properly organize the code structure
import datetime
import os
import sys
import traceback

import nidaqmx
import serial.tools.list_ports
from gtts import gTTS

import MCPThread
import OLEDRecordingThread
from AdapterReadWrite import *
from CRC16 import *
from Compare import *
from Different_Handle import Treating_different_handle
from EventsStrings import *
from Prepare_Output_Json_File import calculatePassFail
from ReadBatteryRSOC import read_battery_RSOC
from ReadStatusVariables import ReadStatusVariables
from Read_Handle_Fire_Count import GetHandleUseCount
from ReadingQue import ReadingQue
from RelayControlBytes import *
from export_results.update_results_to_excel import save_results_to_excel
from image_comparision.image_comparision.image_comparision import get_similar_images

# from image_comparision.image_comparision import get_similar_images

# from SigniaTestAutomation import logger

relay_operations = {
    # Right Articulation
    "R_ARTICULATION": {
        "Bank_Number": 2,
        "Relay_Number": 6
    },
    # Left Articulation
    "L_ARTICULATION": {
        "Bank_Number": 2,
        "Relay_Number": 3
    },
    # Center Articulation
    "C_ARTICULATION": {
        "Bank_Number": 2,
        "Relay_Number": 4
    },
    # Right Clock Wise Rotation
    "RCW_ROTATION": {
        "Bank_Number": 2,
        "Relay_Number": 7
    },
    # Left Clock Wise Rotation
    "LCW_ROTATION": {
        "Bank_Number": 2,
        "Relay_Number": 1
    },
    # Right Counter Clock Wise Rotation
    "RCCW_ROTATION": {
        "Bank_Number": 2,
        "Relay_Number": 8
    },
    # Left Counter Clock Wise Rotation
    "LCCW_ROTATION": {
        "Bank_Number": 2,
        "Relay_Number": 2
    },
    # Unclamp
    "UNCLAMP": {
        "Bank_Number": 2,
        "Relay_Number": 4
    },
    # clamp
    "CLAMP": {
        "Bank_Number": 2,
        "Relay_Number": 5
    },
    # clamp
    "FIRING": {
        "Bank_Number": 2,
        "Relay_Number": 5
    },
    # Green Key (Firing Acknowledgement key)
    "GREEN_KEY_ACK": {
        "Bank_Number": 3,
        "Relay_Number": 5
    },
    # Retract
    "RETRACT": {
        "Bank_Number": 2,
        "Relay_Number": 4
    },
    # Linear Actuator - For EEA
    "STAPLING_STARTED_ONE": {
        "Bank_Number": 4,
        "Relay_Number": 1
    },
    "STAPLING_STARTED_TWO": {
        "Bank_Number": 4,
        "Relay_Number": 2
    },
    "CUTTING_STARTED_ONE": {
        "Bank_Number": 4,
        "Relay_Number": 3
    },
    "CUTTING_STARTED_TWO": {
        "Bank_Number": 4,
        "Relay_Number": 4
    },
    "CUTTING_COMPLETED_ONE": {
        "Bank_Number": 4,
        "Relay_Number": 5
    },
    "CUTTING_COMPLETED_TWO": {
        "Bank_Number": 4,
        "Relay_Number": 6
    }
}

command_ONEWIRE_READ_ADAPTER = b'\xAA\x07\x00\x49\x03\x6E\xFD'

firing_default_delay = 25
articulate_default_delay = 10
rotate_default_delay = 5

normal_firing_ops = ['Non-intelligent Reload', 'Clamp Cycle Test Clamping', 'Clamp Cycle Test Un-Clamping',
                     'Right Articulation', 'Centering Articulation', 'Left Articulation', 'Centering Articulation',
                     'Clamping on Tissue', 'Green Key Ack', 'Firing on Tissue', 'Retracting', 'Unclamping',
                     'Remove Reload']

clsmshell_USED_byte_data = [0x02, 0x03, 0x04, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x01, 0x00, 0x00,
                            0x00, 0x60,
                            0x39, 0xDA, 0x01, 0x04, 0x03, 0x00, 0x00, 0x00, 0xCC, 0x38, 0x31, 0x17, 0x00, 0x00, 0x00,
                            0x00, 0x00,
                            0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                            0x00, 0x00,
                            0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x35]

clsmshell_UNSUPPORTED_byte_data = [0x03, 0x03, 0x04, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x01, 0x00,
                                   0x00, 0x00,
                                   0x60, 0x39, 0xDA, 0x01, 0x04, 0x03, 0x00, 0x00, 0x00, 0xCC, 0x38, 0x31, 0x17, 0x00,
                                   0x00, 0x00,
                                   0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                                   0x00, 0x00,
                                   0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x35]
clsmshell_UNKNOWN_byte_data = [0x02, 0xFF, 0xFF, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x01, 0x00, 0x00,
                               0x00,
                               0x60, 0x39, 0xDA, 0x01, 0x04, 0x03, 0x00, 0x00, 0x00, 0xCC, 0x38, 0x31, 0x17, 0x00, 0x00,
                               0x00,
                               0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                               0x00,
                               0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x35]

adapter_EOL_byte_data = []
adapter_procedure_EOL_byte_data = []
adapter_firing_EOL_byte_data = []
adapter_usable_byte_data = [0x02, 0x01, 0x08, 0x00, 0x00, 0x0F, 0x27, 0x00, 0x00, 0x0F, 0x27, 0x03, 0x04, 0x00, 0x00,
                            0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                            0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                            0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                            0x00, 0x2B]
adapter_unsupported_byte_data = []
adapter_unknown_byte_data = []
adapter_unauthenticated_byte_data = []


def connectClamshell(*args):
    serial_control = serialControl(NCDComPort='COM16', BlackBoxComPort="COM9")
    clamshell_UNUSED_byte_data = [2, 3, 4, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                                  0,
                                  0, 0,
                                  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                                  0]
    clamshell_type = clamshell_UNUSED_byte_data
    for arg in args:
        if type(arg) is str and arg.upper() == "USED":
            clamshell_type = clsmshell_USED_byte_data
    serial_control.wait(40)
    print("In connect clamshell")
    if not serial_control.serial_port.isOpen():
        serial_control.OpenSerialConnection()
    serial_control.configure_clamshell(clamshell_type)
    serial_control.wait(1)
    serial_control.Switch_ONN_Relay(1, 5)  # B1:R5 - ON
    serial_control.wait(3)
    if serial_control.serial_port.isOpen():
        serial_control.serial_port.close()
    serial_control.wait(5)


def ConnectAdapter(*args):
    print("In connect adapter")
    serial_control = serialControl(NCDComPort='COM16', BlackBoxComPort="COM9")
    serial_control.wait(1)
    if not serial_control.serial_port.isOpen():
        serial_control.OpenSerialConnection()
    serial_control.wait(1)
    serial_control.Switch_ONN_Relay(1, 8)  # B1:R7 - OFF
    serial_control.Switch_ONN_Relay(1, 1)  # B1:R1 - OFF
    serial_control.Switch_ONN_Relay(1, 2)  # B1:R2 - OFF
    serial_control.Switch_ONN_Relay(1, 3)  # B1:R3 - OFF
    serial_control.Switch_ONN_Relay(1, 4)  # B1:R4 - OFF
    serial_control.Switch_ONN_Relay(1, 7)  # B1:R7 - OFF
    serial_control.Switch_ONN_Relay(1, 6)  # B1:R7 - OFF
    if serial_control.serial_port.isOpen():
        serial_control.serial_port.close()
    mytext = 'Adapter-Connected'
    myobj = gTTS(text=mytext, lang='en', slow=False)
    myobj.save(f"output_{mytext}.mp3")
    os.system(f"start output_{mytext}.mp3")
    serial_control.wait(10)


def RotationTest(*args):
    serial_control = serialControl(NCDComPort='COM16', BlackBoxComPort="COM9")
    serial_control.wait(1)
    print("In rotation test")
    if not serial_control.serial_port.isOpen():
        serial_control.OpenSerialConnection()
    serial_control.wait(1)
    delay = 5
    direction = "CW"
    for arg in args:
        if type(arg) is int:
            delay = arg
        elif type(arg) is str and arg.upper() in ["CW", "CCW"]:
            direction = arg.upper()
    direction = "R" + direction
    rotation_dir = 'Clockwise'
    if direction == "RCCW":
        rotation_dir = "counterclockiwise"

    serial_control.rotation_with_direction(relay_switch_over_delay=delay, direction=direction)
    if serial_control.serial_port.isOpen():
        serial_control.serial_port.close()
    serial_control.wait(1)


def removeAdapter():
    print("In remove adapter")
    serial_control = serialControl(NCDComPort='COM16', BlackBoxComPort="COM9")
    serial_control.wait(1)
    if not serial_control.serial_port.isOpen():
        serial_control.OpenSerialConnection()
    serial_control.wait(1)
    serial_control.removeAdapter()
    if serial_control.serial_port.isOpen():
        serial_control.serial_port.close()
    serial_control.wait(5)


def PlacingPowerPackOnCharger():
    print("In PlacingPowerPackOnCharger")
    serial_control = serialControl(NCDComPort='COM16', BlackBoxComPort="COM9")
    serial_control.wait(1)
    if not serial_control.serial_port.isOpen():
        serial_control.OpenSerialConnection()
    serial_control.wait(1)
    serial_control.Switch_OFF_ALL_Relays_In_All_Banks(0)
    serial_control.wait(2)
    serial_control.PlacingPowerPackOnCharger()
    if serial_control.serial_port.isOpen():
        serial_control.serial_port.close()


def ConnectReload(*args):
    serial_control = serialControl(NCDComPort='COM16', BlackBoxComPort="COM9")
    if not serial_control.serial_port.isOpen():
        serial_control.OpenSerialConnection()
    serial_control.wait(1)
    print("In ConnectReload")
    reload_length = 30
    reload_type = "Non Intelligent"
    reload_color = "BLACK"
    for arg in args:
        if type(arg) is int:
            reload_length = arg
        elif type(arg) is str:
            if arg.upper() in ["SULU", "NON INTELLIGENT", "RADIAL", "MULU"]:
                reload_type = arg
            elif arg.upper() in ["WHITE", "BLACK", "TAN", "GRAY", "PURPLE"]:
                reload_color = arg
    if reload_type.upper() == "SULU":
        serial_control.connect_sulu_reload(reload_length, reload_color.capitalize())

    if serial_control.serial_port.isOpen():
        serial_control.serial_port.close()
    mytext = f"'{reload_length} mm, {reload_color} reload is connected"
    myobj = gTTS(text=mytext, lang='en', slow=False)
    myobj.save(f"output_reload_{reload_color}_{reload_length}.mp3")
    os.system(f"start output_reload_{reload_color}_{reload_length}.mp3")
    serial_control.wait(10)


def disconnect_reload():
    serial_control = serialControl(NCDComPort='COM16', BlackBoxComPort="COM9")
    if not serial_control.serial_port.isOpen():
        serial_control.OpenSerialConnection()
    serial_control.wait(1)
    print("In ConnectReload")
    serial_control.RemovingSULUReload()
    if serial_control.serial_port.isOpen():
        serial_control.serial_port.close()
    serial_control.wait(1)

# def get_similar_images(src_path:str, reference_images_path:str, dst_path:str, image_name:str='',
#                        announce:str='images are matched',mask_pos:str='None', mask_battery_pos:bool= True):

def process_images(src_path, reference_images_path, dst_path, image_name):
    """
    Process captured images to find similar images.
    """
    try:
        get_similar_images(src_path=src_path, reference_images_path=reference_images_path, dst_path=dst_path,
                           image_name=image_name)
    except Exception as ex:
        print(f'Exception Occurred: {ex}')


class serialControl:

    def __init__(self,
                 json_data=None, SULU_EEPROM_command_byte=None, MULU_EEPROM_command_byte=None,
                 CARTRIDGE_EEPROM_command_byte=None, NCDComPort=None, PowerPackComPort=None,
                 BlackBoxComPort=None, USB6351ComPort=None, ArduinoUNOComPort=None, FtdiUartComPort=None,
                 DCPowerSupplyComPort=None, OUTPUT_PATH=None, videoPath=None, blobPath=None, itr=0, EEA_RELOAD_EEPROM_command_byte=None):
        self.serRs232Supply = None
        self.xls_results = []
        self.is_firing_completed = False
        self.status_data_2 = None
        self.handle_fire_count_2 = None
        self.status_data_1 = None
        self.handle_fire_count_1 = None
        self.serial_port = serial.Serial()
        self.my_Serthread = None
        self.video_thread = None
        self.json_data = json_data  # Used in NormalFiring
        self.SULU_EEPROM_command_byte = SULU_EEPROM_command_byte
        self.MULU_EEPROM_command_byte = MULU_EEPROM_command_byte
        self.CARTRIDGE_EEPROM_command_byte = CARTRIDGE_EEPROM_command_byte
        self.EEA_RELOAD_EEPROM_command_byte = EEA_RELOAD_EEPROM_command_byte

        self.NCDComPort = NCDComPort
        self.PowerPackComPort = PowerPackComPort
        self.BlackBoxComPort = BlackBoxComPort
        self.USB6351ComPort = USB6351ComPort
        self.ArduinoUNOComPort = ArduinoUNOComPort
        self.FtdiUartComPort = FtdiUartComPort
        self.DcPowerSupplyComPort = DCPowerSupplyComPort
        self.OUTPUT_PATH = OUTPUT_PATH
        self.videoPath = videoPath
        self.blobPath = blobPath

        self.serPP = None
        self.serRS = None
        self.failuerCntr = 0

        self.itr = itr
        self.Test_Results = []
        self.Normal_Firing_Test_Results = []
        self.Adapter_1W_OC_In_Fire_Mode_Results = []
        # relay panel bank numbers and relay numbers
        self.right_articulation_bank_number = relay_operations['R_ARTICULATION']['Bank_Number']
        self.right_articulation_relay_number = relay_operations['R_ARTICULATION']['Relay_Number']
        self.left_articulation_bank_number = relay_operations['L_ARTICULATION']['Bank_Number']
        self.left_articulation_relay_number = relay_operations['L_ARTICULATION']['Relay_Number']

        self.center_articulation_bank_number = relay_operations['C_ARTICULATION']['Bank_Number']
        self.center_articulation_relay_number = relay_operations['C_ARTICULATION']['Relay_Number']
        self.RCW_ROTATION_bank_number = relay_operations['RCW_ROTATION']['Bank_Number']
        self.RCW_ROTATION_relay_number = relay_operations['RCW_ROTATION']['Relay_Number']

        self.LCW_ROTATION_bank_number = relay_operations['LCW_ROTATION']['Bank_Number']
        self.LCW_ROTATION_relay_number = relay_operations['LCW_ROTATION']['Relay_Number']
        self.RCCW_ROTATION_bank_number = relay_operations['RCCW_ROTATION']['Bank_Number']
        self.RCCW_ROTATION_relay_number = relay_operations['RCCW_ROTATION']['Relay_Number']

        self.LCCW_ROTATION_bank_number = relay_operations['LCCW_ROTATION']['Bank_Number']
        self.LCCW_ROTATION_relay_number = relay_operations['LCCW_ROTATION']['Relay_Number']
        self.unclamp_bank_number = relay_operations['UNCLAMP']['Bank_Number']
        self.unclamp_relay_number = relay_operations['UNCLAMP']['Relay_Number']

        self.CLAMP_bank_number = relay_operations['CLAMP']['Bank_Number']
        self.CLAMP_relay_number = relay_operations['CLAMP']['Relay_Number']
        self.FIRING_bank_number = relay_operations['FIRING']['Bank_Number']
        self.FIRING_relay_number = relay_operations['FIRING']['Relay_Number']

        self.GREEN_KEY_ACK_bank_number = relay_operations['GREEN_KEY_ACK']['Bank_Number']
        self.GREEN_KEY_ACK_relay_number = relay_operations['GREEN_KEY_ACK']['Relay_Number']
        self.RETRACT_bank_number = relay_operations['RETRACT']['Bank_Number']
        self.RETRACT_relay_number = relay_operations['RETRACT']['Relay_Number']

        self.EEA_STAPLING_ONE_bank_number = relay_operations['STAPLING_STARTED_ONE']['Bank_Number']
        self.EEA_STAPLING_ONE_relay_number = relay_operations['STAPLING_STARTED_ONE']['Relay_Number']

        self.EEA_STAPLING_TWO_bank_number = relay_operations['STAPLING_STARTED_TWO']['Bank_Number']
        self.EEA_STAPLING_TWO_relay_number = relay_operations['STAPLING_STARTED_TWO']['Relay_Number']

        self.EEA_CUTTING_ONE_bank_number = relay_operations['CUTTING_STARTED_ONE']['Bank_Number']
        self.EEA_CUTTING_ONE_relay_number = relay_operations['CUTTING_STARTED_ONE']['Relay_Number']

        self.EEA_CUTTING_TWO_bank_number = relay_operations['CUTTING_STARTED_TWO']['Bank_Number']
        self.EEA_CUTTING_TWO_relay_number = relay_operations['CUTTING_STARTED_TWO']['Relay_Number']

        self.EEA_CUTTING_COMPLETE_ONE_bank_number = relay_operations['CUTTING_COMPLETED_ONE']['Bank_Number']
        self.EEA_CUTTING_COMPLETE_ONE_relay_number = relay_operations['CUTTING_COMPLETED_ONE']['Relay_Number']

        self.EEA_CUTTING_COMPLETE_TWO_bank_number = relay_operations['CUTTING_COMPLETED_TWO']['Bank_Number']
        self.EEA_CUTTING_COMPLETE_TWO_relay_number = relay_operations['CUTTING_COMPLETED_TWO']['Relay_Number']

    def wait(self, number_of_seconds):

        if number_of_seconds >= 5:
            pass
           # print(f"Waiting for {number_of_seconds} seconds from {datetime.now().hour}:{datetime.now().minute}:"f"{datetime.now().second}")
        time.sleep(number_of_seconds)

    def batt_config(self, case):
        switch = {"Insufficient": 9,
                  "Low": 25,
                  "Full": 99,
                  "RSOC": 120,
                  }
        return switch.get(case)

    def OpenSerialConnection(self):
        # print(self.NCDComPort, self.PowerPackComPort, self.BlackBoxComPort, self.USB6351ComPort, self.ArduinoUNOComPort)
        # self.serial_port = serial.Serial()
        self.serial_port.baudrate = 115200
        # self.serial_port.port = 'COM6'
        # print(self.NCDComPort)
        self.serial_port.port = self.NCDComPort
        self.serial_port.parity = "N"
        self.serial_port.stopbits = 1
        self.serial_port.xonxoff = 0
        self.serial_port.timeout = 0.01
        self.serial_port.open()
        # print(self.serial_port)

    def disconnectSerialConnection(self):
        # serialControl.flush()
        # serialControl.reset_input_buffer()
        # serialControl.reset_output_buffer()
        serialControl.close_serial_port(self.serial_port)
        # while self.serial_port.is_open:
        #     self.serial_port.close()
        #     self.wait(0.5)
        # print("NCD Port Closed ")

    @staticmethod
    def close_serial_port(serial_port:serial.Serial):
        port_number = serial_port.port
        while serial_port.is_open:
            serial_port.close()
            if serial_port.is_open:
                print(f'Port Still Open {port_number}')
            time.sleep(0.5)
        print(f'Port Closed {port_number}')


    def send_decimal_bytes(self, decimal_bytes):
        # self.serial_port.flushInput()
        # self.serial_port.flushOutput()

        decimal_bytes = bytearray(decimal_bytes)
        self.serial_port.write(decimal_bytes)

    def receive_decimal_bytes(self):
        decimal_bytes = bytearray()
        # print(len(self.serial_port.read()))
        decimal_bytes.extend(self.serial_port.read())
        # logger.debug(f"Decimal bytes received successfully! {decimal_bytes}")
        print(decimal_bytes)
        print("RECEIVE SUCCESS")

    def ON_OFF_Relay_Response(self):
        self.receive_decimal_bytes()


    def Switch_ONN_Relay(self, Bank_number, Relay_number):
        self.send_decimal_bytes(TURN_ONN_INDIVIDUAL_RELAYS_IN_EACH_BANK[Bank_number - 1][Relay_number - 1])
        self.wait(.05)  # malla

    def Switch_OFF_Relay(self, Bank_number, Relay_number):
        self.send_decimal_bytes(
            TURN_OFF_INDIVIDUAL_RELAYS_IN_EACH_BANK[Bank_number - 1][Relay_number - 1])
        self.wait(.05)  # vadali updated from 1 to .01 need to minimize the delay between the relay turn on #malla

    def Switch_ONN_ALL_Relays_In_Each_Bank(self, Bank_number):
        self.send_decimal_bytes(TURN_ONN_ALL_RELAYS_IN_EACH_BANK[Bank_number - 1])
        self.wait(.1)

    def Switch_OFF_ALL_Relays_In_Each_Bank(self, Bank_number):
        self.send_decimal_bytes(TURN_OFF_ALL_RELAYS_IN_EACH_BANK[Bank_number - 1])
        self.wait(.1)

    def Switch_OFF_ALL_Relays_In_All_Banks(self, Bank_number):
        self.send_decimal_bytes(TURN_OFF_ALL_RELAYS_IN_ALL_BANKS[Bank_number])
        self.wait(.1)

    def ConnectingSULUReload(self, event_key, SuccessFlag, reload_length, reload_color, is_firing_test=True):
        if self.serPP is not None:
            self.my_Serthread.clearQue()

        self.Switch_ONN_Relay(3, 2)  # B3:R2 - ON
        self.wait(.2)
        # self.Switch_ONN_Relay(5, 8)  # B5:R8 - ON
        # self.wait(.2)
        # self.Switch_ONN_Relay(3, 3)  # B3:R3 - ON
        # self.wait(.2)
        self.Switch_ONN_Relay(3, 1)  # B3:R1 - ON
        self.wait(5)
        if self.serPP is not None:
            self.compare_logs(logs_to_compare=event_key, SuccessFlag=SuccessFlag, is_firing_test=is_firing_test,
                              reload_length=reload_length, reload_color=reload_color, event_name='Reload_Connected',
                              is_event_connecting=True)

        # print(self.Normal_Firing_Test_Results)

    def ConnectEEAReload(self, event_key, SuccessFlag, reload_length, reload_color, is_firing_test=True, fix_validation_req=False):
        if self.serPP is not None:
            self.my_Serthread.clearQue()
        self.Switch_ONN_Relay(3, 3)  # B3:R3 - ON
        self.wait(.2)
        self.Switch_ONN_Relay(3, 2)  # B3:R2 - ON
        self.wait(6)  # 26th -Changed to 0.2 to 5 sec

        if reload_length == 31 or reload_length == 33:
            event_key = 'EEA RELOAD Connected with Ship cap Diameter 31 or 33'

        if reload_length == 25:
            event_key = 'EEA RELOAD Connected with TAID'
            self.Switch_ONN_Relay(2, 4)  # B2:R4 - ON
            self.wait(.5)
            self.Switch_OFF_Relay(2, 4)  # B2:R4 - OFF
            self.wait(.5)
            self.Switch_ONN_Relay(2, 4)  # B2:R4 - ON
            self.wait(.5)
            self.Switch_OFF_Relay(2, 4)  # B2:R4 - OFF

        if fix_validation_req:
            print("EEA Reload Connected")
        if self.serPP is not None:
            self.compare_logs(logs_to_compare=event_key, SuccessFlag=SuccessFlag, is_firing_test=is_firing_test,
                              reload_length=reload_length, reload_color=reload_color, fixtureValidation=fix_validation_req)

    def ExtensionOfTrocar(self, logs_to_compare='EEA Trocar Extention with Reload', video_name=None, record_video=True,fix_validation_req=False):
        SuccessFlag = True
        is_firing_test = True
        # if record_video:
        #     videoThread = OLEDRecordingThread.myThread(video_name, self.videoPath)
        #     videoThread.start()
        #     self.video_thread = videoThread
        self.my_Serthread.clearQue()
        self.Switch_ONN_Relay(2, 4)  # B2:R4 - ON
        self.wait(20)
        self.Switch_OFF_Relay(2, 4)  # B2:R4 - OFF
        self.compare_logs(logs_to_compare=logs_to_compare, SuccessFlag=SuccessFlag, is_firing_test=is_firing_test,fixtureValidation=fix_validation_req)
        if fix_validation_req:
            pass
        else:
            print(f"Step: {logs_to_compare} Performed")

    def ExtensionOfTrocar_400860(self, logs_to_compare='EEA Trocar Extention with Reload', video_name=None, record_video=True,fix_validation_req=False):
        SuccessFlag = True
        is_firing_test = True
        if record_video:
            videoThread = OLEDRecordingThread.myThread(video_name, self.videoPath)
            videoThread.start()
            self.video_thread = videoThread
        self.my_Serthread.clearQue()
        self.Switch_ONN_Relay(2, 4)  # B2:R4 - ON
        self.wait(20)

        self.removeAdapter()
        self.wait(15)

        self.Connect_Adapter()
        self.wait(25)

        self.Switch_OFF_Relay(2, 4)  # B2:R4 - OFF
        self.compare_logs(logs_to_compare=logs_to_compare, SuccessFlag=SuccessFlag, is_firing_test=is_firing_test,fixtureValidation=fix_validation_req)
        if fix_validation_req:
            pass
        else:
            print(f"Step: {logs_to_compare} Performed")

    def ConnectingEEAReload(self):
        self.Switch_ONN_Relay(5, 8)  # B5:R8 - ON
        self.wait(.2)
        self.Switch_ONN_Relay(3, 2)  # B3:R2 - ON
        self.wait(.2)
        self.Switch_ONN_Relay(3, 3)  # B3:R3 - ON
        self.wait(.2)

    def ConnectingLegacyReload(self, logs_to_compare="Non-Intelligent Reload Connected", SuccessFlag=True):
        self.my_Serthread.clearQue()
        # self.Switch_ONN_Relay(5, 8)  # B5:R8 - ON
        # self.wait(.2)
        self.Switch_ONN_Relay(3, 1)  # B3:R1 - ON
        self.wait(3)
        self.compare_logs(logs_to_compare=logs_to_compare, SuccessFlag=SuccessFlag, is_firing_test=True,
                          event_name='Reload_Connected', is_event_connecting=True)

    def EEANoStaplesDetectedStateExit(self):
        logs_to_compare = 'No Staples Detected State Exit'
        self.Switch_ONN_Relay(2, 4)
        self.wait(1)  # Holding for 1 Second to Enter No Staples Exit Screen And High Speed Firing Recovery Screen Shows
        self.Switch_OFF_Relay(2, 4)
        self.wait(.2)
        self.Switch_ONN_Relay(2, 4)
        self.wait(3)  # Holding for 3 Seconds to Enter No Staples Exit Screen Shows Without Yellow Rectangle Segment
        self.Switch_OFF_Relay(2, 4)
        self.wait(.2)
        self.Switch_ONN_Relay(2, 4)
        self.wait(20)  # Holding for 20 Seconds to Trocar Extends to FULL Open Position - MAX_LIMIT
        self.Switch_OFF_Relay(2, 4)
        self.wait(.2)
        self.Switch_ONN_Relay(2, 5)
        self.wait(20)  # Holding for 20 Seconds to achieve CLAMP GAP.
        self.Switch_OFF_Relay(2, 5)
        self.wait(.2)
        self.Switch_ONN_Relay(2, 1)
        self.Switch_ONN_Relay(2, 2)
        self.Switch_ONN_Relay(2, 7)
        self.Switch_ONN_Relay(2, 8)
        self.wait(2)  # Holding for 2 Seconds to EEA Reload Removal Screen Shows along with SSE State.
        self.Switch_OFF_Relay(2, 8)
        self.Switch_OFF_Relay(2, 7)
        self.Switch_OFF_Relay(2, 2)
        self.Switch_OFF_Relay(2, 1)
        self.compare_logs(logs_to_compare=logs_to_compare, SuccessFlag=True, is_firing_test=True)

    def EEASurgicalSiteExtractionStateExit(self, logs_to_compare='EEA SSE Countdown Exit', occurrence=None):
        if 12_1 == occurrence:
            logs_to_compare = 'Rotation Operation During SP IP'
        elif 12_2 == occurrence:
            logs_to_compare = 'SSE Exit'
        # elif 40 == occurrence:
        #     logs_to_compare = 'EEA SSE Countdown Exit'

        self.Switch_ONN_Relay(2, 1)
        self.Switch_ONN_Relay(2, 2)
        self.Switch_ONN_Relay(2, 7)
        self.Switch_ONN_Relay(2, 8)
        self.wait(3)  # Holding for 3 Seconds to Exit SSE State.
        self.Switch_OFF_Relay(2, 8)
        self.Switch_OFF_Relay(2, 7)
        self.Switch_OFF_Relay(2, 2)
        self.Switch_OFF_Relay(2, 1)
        self.compare_logs(logs_to_compare=logs_to_compare, SuccessFlag=True, is_firing_test=True)

    def DisconnectingLegacyReload(self, exit_video_stream=True):
        # self.Switch_ONN_Relay(5, 8)  # B5:R8 - ON
        # self.wait(.2)
        self.Switch_OFF_Relay(3, 1)  # B3:R1 - ON
        self.wait(5)
        self.Normal_Firing_Test_Results.append("        Removing Non-Intelligent Reload: PASS")
        if exit_video_stream:
            OLEDRecordingThread.exitFlag = True

    def ConnectingMULUReload(self, logs_to_compare, SuccessFlag, reload_length):
        self.my_Serthread.clearQue()

        self.Switch_ONN_Relay(3, 2)  # B3:R2 - ON
        self.wait(.2)
        # self.Switch_ONN_Relay(5, 8)  # B5:R8 - ON
        # self.wait(.2)
        self.Switch_ONN_Relay(3, 1)  # B3:R1 - ON
        self.wait(5)
        self.compare_logs(logs_to_compare=logs_to_compare, SuccessFlag=SuccessFlag, is_firing_test=True,
                          reload_length=reload_length, event_name='Reload_Connected', is_event_connecting=True)

        print("Step: MULU Reload Connected")
        # print(self.Normal_Firing_Test_Results)

    def remove_cartridge(self, bypass_compare_logs=False):
        self.my_Serthread.clearQue()
        self.Switch_OFF_Relay(3, 3)  # B3:R3 - OFF
        self.Switch_OFF_Relay(3, 4)  # B3:R4 - OFF
        self.wait(5)
        if not bypass_compare_logs:
            self.compare_logs(logs_to_compare='Remove Cartridge', SuccessFlag=True, is_firing_test=True,
                              event_name='Cartidge_Connected', is_event_connecting=False)
        OLEDRecordingThread.exitFlag = True
        self.wait(1)

    def RemovingMULUReload(self, logs_to_compare='Remove Reload', bypass_compare_logs=False, exit_video_stream=True,
                           delay=5):
        self.my_Serthread.clearQue()
        self.Switch_OFF_Relay(3, 2)  # B3:R2 - ON
        self.wait(.2)
        self.Switch_OFF_Relay(3, 1)  # B3:R1 - ON
        self.wait(.2)
        self.Switch_OFF_Relay(5, 8)  # B5:R8 - ON
        self.wait(delay)
        if not bypass_compare_logs:
            self.compare_logs(logs_to_compare=logs_to_compare, SuccessFlag=True, is_firing_test=True,
                              event_name='Reload_Connected', is_event_connecting=False)
        OLEDRecordingThread.exitFlag = exit_video_stream
        self.wait(1)

    def DisconnectingEEAReload(self, logs_to_compare='EEA Remove Reload', protocol_id=None, exit_video=True, fixture_validation_required=False):
        if 12 == protocol_id:
            logs_to_compare = 'EEA Remove Reload Enter SSE'

        self.my_Serthread.clearQue()

        self.Switch_OFF_Relay(5, 8)  # B5:R8 - OFF
        self.wait(.2)
        self.Switch_OFF_Relay(3, 2)  # B3:R2 - OFF
        self.wait(.2)
        self.Switch_OFF_Relay(3, 3)  # B3:R3 - OFF
        self.wait(.2)
        print("Reload Removed")
        self.compare_logs(logs_to_compare=logs_to_compare, SuccessFlag=True, is_firing_test=True, fixtureValidation=fixture_validation_required)
        if fixture_validation_required:
            pass
        else:
            OLEDRecordingThread.exitFlag = exit_video

    def connect_reload(self, firing_count, reload_type, reload_length, video_name, reload_color=None,
                       reload_state="GOOD", cartridge_state="GOOD", cartridge_color=None, ship_cap_status=None,
                       is_reload_cartridge_attached_together="NO", SuccessFlag=True, record_video=True,
                       is_clamp_cycle_test_with_cartridge="NO", fixture_validation_required=False, videoDisabledFalg=False):

        if fixture_validation_required or videoDisabledFalg:
            pass
        else:
            print(f"------------------------{video_name}--------------------------")
            videoThread = OLEDRecordingThread.myThread(video_name, self.videoPath)
            videoThread.start()
            self.video_thread = videoThread

        self.handle_fire_count_1, self.status_data_1 = self.read_status_variables(fixture_validation_required=fixture_validation_required)
        self.Normal_Firing_Test_Results = []

        self.my_Serthread.clearQue()
        self.wait(5)

        if reload_type == 'EEA':
            if ship_cap_status == 'Yes':
                logs_to_compare = 'EEA RELOAD Connected with Ship cap'
            else:
                logs_to_compare = 'EEA RELOAD Connected without Ship cap'

            self.configure_eea_reload(reload_length=reload_length, reload_color=reload_color,
                                      ship_cap_status=ship_cap_status,
                                      reload_state=reload_state, fix_validation_req=fixture_validation_required)

            if not int(self.status_data_1["Reload_Connected"]):
                self.ConnectEEAReload(event_key=logs_to_compare, SuccessFlag=SuccessFlag,
                                      reload_length=reload_length,
                                      reload_color=reload_color, fix_validation_req=fixture_validation_required)
                # Press and hold the up toggle button until the trocar is fully extended.
                # Jan 6th 2025 - Revert this API with Original API
                # self.ExtensionOfTrocar_400860(video_name=video_name, record_video=record_video, fix_validation_req=fixture_validation_required)
                self.ExtensionOfTrocar(video_name=video_name, record_video=record_video, fix_validation_req=fixture_validation_required)

    def configure_cartridge(self, reload_length, cartridge_color, cartridge_state="USABLE"):
        CARTRIDGE_EEPROM = [2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                            0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        reload_lengths = enumerate([30, 45, 60, 72], 1)
        reload_and_cartridge_colors = enumerate(['UNKNOWN', 'White', 'Tan', 'Purple', 'Black', 'Gray'])

        if reload_length != 72:
            for number, length in reload_lengths:
                if length == reload_length:
                    CARTRIDGE_EEPROM[1] = number
                    CARTRIDGE_EEPROM[2] = 0x18
                    break
        if cartridge_state.upper() in ["USED", "EOL"]:
            CARTRIDGE_EEPROM[18] = 1

        for count, possible_color in reload_and_cartridge_colors:
            if possible_color == cartridge_color:
                CARTRIDGE_EEPROM[26] = count  # This will be 0 for UNKNOWN, 1 for White, 2 for Tan, 3 for Purple,
                # 4 for Black and 5 for Gray reload colors
                break

        self.connect_cartridge_to_ACC()

        self.write_eeprom_data(data_bytes=CARTRIDGE_EEPROM)

    def configure_mulu_reload(self, reload_length, reload_state="GOOD"):
        MULU_EEPROM = [2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                       0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        reload_lengths = enumerate([30, 45, 60, 72], 1)
        mulu_byte_19_data = [50, 12, 12]
        # if reload_state.upper() in ['USABLE', 'GOOD', 'Unused']:  # default state is 'GOOD' or 'USABLE' or 'Unused'
        if reload_length != 72:
            for number, length in reload_lengths:
                if length == reload_length:
                    MULU_EEPROM[1] = number
                    MULU_EEPROM[2] = 0x10
                    MULU_EEPROM[19] = mulu_byte_19_data[number - 1]
                    MULU_EEPROM[22] = 1
                    break
        if reload_state.upper() == "EOL":
            MULU_EEPROM[18] = 0X0C

        self.Switch_ONN_Relay(5, 5)  # B5:R5 - ON
        self.Switch_ONN_Relay(5, 2)  # B5:R2 - ON
        self.Switch_OFF_Relay(5, 8)  # B5:R8 - OFF
        self.wait(1)

        self.write_eeprom_data(data_bytes=MULU_EEPROM)

        self.Switch_OFF_Relay(5, 2)  # B5:R2 - OFF
        self.Switch_OFF_Relay(5, 5)  # B5:R6 - OFF
        self.wait(1)

    def configure_sulu_reload(self, reload_length, reload_color, reload_state=None):
        SULU_EEPROM = [2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                       0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        reload_lengths = enumerate([30, 45, 60, 72], 1)
        reload_and_cartridge_colors = enumerate(['UNKNOWN', 'White', 'Tan', 'Purple', 'Black', 'Gray'])
        if not reload_length == 72:
            for number, length in reload_lengths:
                if length == reload_length:
                    SULU_EEPROM[1] = number  # This will be 1 for 30mm, 2 for 45mm and 3 for 60mm reload lengths
                    SULU_EEPROM[2] = 0x0C
                    # SULU_EEPROM[2] = 0x18
                    SULU_EEPROM[22] = 1
                    break
        else:
            SULU_EEPROM[1] = 3
            SULU_EEPROM[2] = 0x14
            # SULU_EEPROM[2] = 0x18
            SULU_EEPROM[22] = 0

        for count, possible_color in reload_and_cartridge_colors:
            if possible_color == reload_color:
                SULU_EEPROM[34] = count  # This will be 0 for UNKNOWN, 1 for White, 2 for Tan, 3 for Purple,
                # 4 for Black and 5 for Gray reload colors
                break

        if reload_state is not None and reload_state.upper() in ["USED", "EOL"]:
            SULU_EEPROM[18] = 1

        self.Switch_ONN_Relay(5, 5)  # B5:R6 - ON
        self.wait(0.2)
        self.Switch_ONN_Relay(5, 2)  # B5:R2 - ON

        self.wait(1)
        # logger.debug(f"SULU data bytes after appending the CRC: {command}")

        self.write_eeprom_data(data_bytes=SULU_EEPROM)

        self.Switch_OFF_Relay(5, 2)  # B5:R1 - OFF
        self.wait(0.2)
        self.Switch_OFF_Relay(5, 5)  # B5:R2 - OFF
        self.wait(1)

    def connect_sulu_reload(self, reload_length, reload_color, event_key=None):
        self.configure_sulu_reload(reload_length=reload_length, reload_color=reload_color)
        self.ConnectingSULUReload(event_key=event_key, SuccessFlag=True, reload_color=reload_color,
                                  reload_length=reload_length, )

    def ConnectReload(self, *args):
        reload_length = 30
        reload_type = "Non Intelligent"
        reload_color = "BLACK"
        for arg in args:
            if type(arg) is int:
                reload_length = arg
            elif type(arg) is str:
                if arg.upper() in ["SULU", "NON Intelligent", "RADIAL", "MULU"]:
                    reload_type = arg
                elif arg.upper() in ["WHITE", "BLACK", "TAN", "GRAY", "PURPLE"]:
                    reload_color = arg
        if reload_type.uppter() == "SULU":
            self.connect_sulu_reload(reload_length, reload_color.capitalize())

    def connect_cartridge_to_ACC(self):
        # connecting to ACC#
        self.Switch_OFF_Relay(3, 4)  # B5:R4 - OFF
        self.wait(.2)
        self.Switch_OFF_Relay(3, 3)  # B3:R3 - OFF
        self.wait(.2)

        self.Switch_ONN_Relay(5, 5)  # B5:R4 - ON
        self.wait(.2)
        self.Switch_ONN_Relay(5, 3)  # B5:R6 - ON
        self.wait(1)

    def connect_cartridge(self):
        self.my_Serthread.clearQue()
        self.Switch_OFF_Relay(5, 3)  # B5:R1 - OFF
        self.wait(.2)
        self.Switch_OFF_Relay(5, 5)  # B5:R1 - OFF

        self.wait(10)

        self.Switch_ONN_Relay(3, 3)  # B3:R4 - ON
        self.wait(0.2)
        self.Switch_ONN_Relay(3, 4)  # B3:R4 - ON

        self.wait(0.5)

    def connect_cartridge_to_reload(self, logs_to_compare, SuccessFlag, reload_length, reload_color):
        self.my_Serthread.clearQue()
        # self.wait(1)
        self.Switch_OFF_Relay(5, 3)  # B5:R1 - OFF
        self.wait(0.2)
        self.Switch_OFF_Relay(5, 4)  # B5:R1 - OFF
        self.wait(1)
        self.Switch_ONN_Relay(3, 3)  # B3:R4 - ON
        self.wait(0.2)
        self.Switch_ONN_Relay(3, 4)  # B3:R4 - ON

        # self.Switch_OFF_Relay(5, 3)  # B5:R1 - OFF
        # self.Switch_OFF_Relay(5, 7)  # B5:R6 - OFF
        self.wait(10)

        self.compare_logs(logs_to_compare=logs_to_compare, SuccessFlag=SuccessFlag, is_firing_test=True,
                          reload_length=reload_length, reload_color=reload_color, event_name='Cartidge_Connected',
                          is_event_connecting=True)
        print("Step: Cartridge Connected")
        # print(self.Normal_Firing_Test_Results)

    def ConnectingCartridge(self, command):
        self.connect_cartridge_to_ACC()
        command = list(command)[3:-3]
        print(command)
        self.wait(10)
        self.write_eeprom_data(command)
        self.connect_cartridge()

    def compare_logs(self, logs_to_compare, SuccessFlag, is_firing_test=False, reload_length=None,
                     reload_color=None, event_name=None, is_event_connecting=None, action=None, fixtureValidation=False): #, step_num=None):
        if fixtureValidation:
            pass
        else:
            print(f"STEP : {logs_to_compare} START")
        event_status = None
        timestamps, strings_from_power_pack = ReadingQue(self.my_Serthread.readQue)

        if fixtureValidation:
            serialControl.convertListtoLogFile(strings_from_power_pack, str(self.OUTPUT_PATH + '\\TotalLog.txt'),
                                               fileOpenMode='a')
        else:
            print(simple_colors.blue(f'strings_from_power_pack for {logs_to_compare}: {strings_from_power_pack}'))
            serialControl.convertListtoLogFile(strings_from_power_pack, str(self.videoPath + '\\TotalLog.txt'),
                                           fileOpenMode='a')
        # print("logs_to_compare, length , color ", logs_to_compare, reload_length, reload_color)
        strings_to_compare = locateStringsToCompareFromEvent(logs_to_compare.strip(), Length=reload_length,
                                                             Color=reload_color)
        if fixtureValidation:
            pass
        else:
            print(simple_colors.magenta(f"strings_to_compare : {strings_to_compare}"))

        if logs_to_compare == 'Clamp Cycle Test Un-Clamping' and is_firing_test:
            strings_to_compare = strings_to_compare[:-1]
        # reading the status variable from the power pack, to verify the event if it is not none.
        if event_name is not None:
            status_data = self.read_status_variables(read_status_data_only=True, fixture_validation_required=fixtureValidation)
            event_status = int(status_data[event_name])
            if event_name == "Adapter_Connected":
                event_status = event_status and int(status_data['Adapter_Calibrated'])

        if fixtureValidation:
            pass
        else:
            print(simple_colors.yellow(f'event_name = {event_name}\nevent_status = {event_status}'))


        result, results_list = compare_with_test_status(Action_String=logs_to_compare, action=action, #, step_num=step_num,
                                                        Strings_to_Compare=strings_to_compare,
                                                        Strings_from_PowerPack=strings_from_power_pack,
                                                        event_status=event_status,
                                                        is_event_connecting=is_event_connecting,
                                                        test_status_flag=SuccessFlag, time_stamps=timestamps,
                                                        fix_vali_required=fixtureValidation)
        self.xls_results.append(results_list)

        if not is_firing_test:
            self.Test_Results.append(result)
            # logger.debug(simple_colors.blue(f"Test_Results :  {self.Test_Results}"))
            # print(f"Test_Results :  {self.Test_Results}")
        else:
            prefix = '      '
            self.Normal_Firing_Test_Results.append(prefix + result)
            # logger.debug(simple_colors.blue(f"Normal_Firing_Test_Results :  {self.Normal_Firing_Test_Results}"))
            if fixtureValidation:
                pass
            else:
                print(f"Normal_Firing_Test_Results :  {self.Normal_Firing_Test_Results}")

        if fixtureValidation:
            pass
        else:
            print(f"STEP : {logs_to_compare} Event Strings Capturing END")

    def apply_load_force(self, voltage, fixture_validation_req=False):
        if fixture_validation_req:
            pass
        else:
            print(simple_colors.yellow(f"Voltage : {voltage}"))
        with nidaqmx.Task() as task:
            task.ao_channels.add_ao_voltage_chan('Dev1/ao0')
            if fixture_validation_req:
                task.write(voltage)
                pass
            else:
                print('1 Channel 1 Sample Write: ')
                print(task.write(voltage))
            # self.wait(2)

    def ClampCycleTest(self, SuccessFlag):

        self.apply_load_force(1.5)
        self.Clamping(SuccessFlag=SuccessFlag, is_firing_test=True, logs_to_compare='Clamp Cycle Test Clamping')
        # self.Switch_ONN_Relay(Bank_number=clamp_bank_number, Relay_number=clamp_relay_number)  # B2:R5 - ON
        # self.wait(6)
        # self.Switch_OFF_Relay(Bank_number=clamp_bank_number, Relay_number=clamp_relay_number)  # B2:R5 - OFF
        self.apply_load_force(0)
        self.Unclamping(SuccessFlag=SuccessFlag, is_firing_test=True, logs_to_compare='Clamp Cycle Test Un-Clamping')
        # self.Switch_ONN_Relay(Bank_number=unclamp_bank_number, Relay_number=unclamp_relay_number)  # B2:R4 - ON
        # self.wait(6)
        # self.Switch_OFF_Relay(Bank_number=unclamp_bank_number, Relay_number=unclamp_relay_number)  # B2:R4 - OFF

    def Clamping(self, SuccessFlag=True, is_firing_test=False, logs_to_compare='Clamp Cycle Test Clamping'):
        # logs_to_compare = 'Clamp Cycle Test Clamping'
        self.apply_load_force(self.ForceDecode(self.json_data['Clamping Force']))
        self.my_Serthread.clearQue()
        self.Switch_ONN_Relay(Bank_number=self.CLAMP_bank_number, Relay_number=self.CLAMP_relay_number)  # B2:R5 - ON
        self.wait(10)
        self.Switch_OFF_Relay(Bank_number=self.CLAMP_bank_number, Relay_number=self.CLAMP_relay_number)  # B2:R5 - OFF
        self.compare_logs(logs_to_compare=logs_to_compare, SuccessFlag=SuccessFlag, is_firing_test=is_firing_test,
                          event_name='Reload_Clampled', is_event_connecting=True)
        # # # logger.info(f"Step: {logs_to_compare} Performed")
        print(f"Step: {logs_to_compare} Performed")

    def ClampingViaRangeSensor(self):
        self.serRS = serial.Serial(self.ArduinoUNOComPort, 115200, bytesize=8, parity='N', stopbits=1, timeout=0.05,
                                   xonxoff=0)
        self.my_Serthread.clearQue()
        self.wait(5)

        self.Switch_ONN_Relay(2, 5)  # B2:R5 - ON

        read_data1 = 200
        self.serRS.flush()
        while not 65 < read_data1 <= 80:
            try:
                ser_bytes1 = self.serRS.readline()
                read_data1 = float(ser_bytes1.decode('ascii'))
                print(read_data1)
            except:
                pass

        self.apply_load_force(2)
        self.wait(25)

    def EEAClamping(self, SuccessFlag=True, is_firing_test=False, logs_to_compare='EEA Clamping on Tissue',
                    clamp_force='Low', fire_force='Low', fixture_validation_req=False, protocol_id = None):
        self.serRS = serial.Serial(self.ArduinoUNOComPort, 115200, timeout=0.05)
        self.my_Serthread.clearQue()

        self.Switch_ONN_Relay(2, 5)  # B2:R5 - ON

        self.wait(3)
        # print("protocol_id", protocol_id)
        if fixture_validation_req:
            pass
        elif protocol_id == 400860:
            ### Added for 400860 testing during clamping
            self.Switch_OFF_Relay(2, 5)  # B2:R5 - OFF
            self.removeAdapter()
            self.wait(15)

            self.Connect_Adapter()
            self.wait(20)

            self.Switch_ONN_Relay(2, 5)  # B2:R5 - ON

        with self.serRS:
            self.serRS.flush()
            for _ in range(5):
                self.serRS.readline()
            ToF_data = 200
            while not 65 < ToF_data <= 80: #80
                try:
                    # print(f"65 < ToF_data <= 80: {65 < ToF_data <= 80}")
                    ser_bytes1 = self.serRS.readline()
                    read_data1 = ser_bytes1.decode('ascii')
                   # print(f"read_Data : {read_data1}")
                    data = read_data1.split(':')
                    if data[0].strip() == "ToF Sensor Distance in mm":
                        ToF_data = int(data[1].strip())
                    print(f"TOF Data : {ToF_data}")
                except Exception as ex:
                    print(f"Exception occurred :{ex}")

        if clamp_force == 'Low':
            self.apply_load_force(2, fixture_validation_req=fixture_validation_req)
        elif clamp_force == 'Medium':
            self.apply_load_force(3, fixture_validation_req=fixture_validation_req) #### For Low 2, For Medium 3
        print("Clamping on tissue ")

        self.wait(15)
        self.compare_logs(logs_to_compare=logs_to_compare, SuccessFlag=SuccessFlag, is_firing_test=is_firing_test, fixtureValidation=fixture_validation_req)

        if fixture_validation_req:
            pass
        else:
            print(f"Step: {logs_to_compare} Performed")

        self.Switch_OFF_Relay(2, 5)

        # self.serRS.close()
        # serialControl.close_serial_port(self.serRS)

    def GreenKeyAck(self, SuccessFlag=True, is_firing_test=True, is_emergency_retraction=False, fixture_validation_req=False):
        logs_to_compare = 'EEA Green Key Ack'
        if is_emergency_retraction:
            logs_to_compare = "Green Key Ack - Emergency Retraction"
        self.my_Serthread.clearQue()
        self.Switch_ONN_Relay(Bank_number=self.GREEN_KEY_ACK_bank_number, Relay_number=self.GREEN_KEY_ACK_relay_number)
        self.wait(1)
        self.Switch_OFF_Relay(Bank_number=self.GREEN_KEY_ACK_bank_number, Relay_number=self.GREEN_KEY_ACK_relay_number)
        self.wait(2)  # 26th added delay
        self.compare_logs(logs_to_compare, SuccessFlag=SuccessFlag, is_firing_test=is_firing_test, fixtureValidation=fixture_validation_req)

        if fixture_validation_req:
            pass
        else:
            print(f"Step: {logs_to_compare} Performed")

    # Function to send a command to the power supply
    def send_command(self, command, DcPowerSupplyComPort):
        self.serRs232Supply = serial.Serial(self.DcPowerSupplyComPort, 9600, bytesize=8, parity='N', stopbits=1, timeout=1,
                                   xonxoff=False)
        self.serRs232Supply.write((command + '\n').encode())
        time.sleep(0.1)
        response = self.serRs232Supply.readline().decode().strip()
        # self.serRs232Supply.close()
        # print("command sent")
        serialControl.close_serial_port(self.serRs232Supply)
        return response

    def applyLoadViaVoltage(self, voltage, PowerSupplyComPort):

        # Identification of the Power Supply
        command = '*IDN?'
        self.send_command(command, PowerSupplyComPort)
        # print(self.send_command(command, PowerSupplyComPort))

        # Setting Voltage for Stapling, Cutting, And Linear Actuator (while retracting)
        # print(self.send_command(f'VOLT {voltage}', PowerSupplyComPort))
        self.send_command(f'VOLT {voltage}', PowerSupplyComPort)

        # Read back for set value
        command = 'VOLT?'
        # print(self.send_command(command, PowerSupplyComPort))
        self.send_command(command, PowerSupplyComPort)

    # Function to turn on/off the output
    def output_on_off(self, state, PowerSupplyComPort):
        self.send_command(f'OUTP {"ON" if state else "OFF"}', PowerSupplyComPort)
        # print(f'Output {"ON" if state else "OFF"}')


    def GreenKeyAck_400860(self, SuccessFlag=True, is_firing_test=True, is_emergency_retraction=False):
        logs_to_compare = 'EEA Green Key Ack 400860'
        if is_emergency_retraction:
            logs_to_compare = "Green Key Ack - Emergency Retraction"
        self.my_Serthread.clearQue()
        self.wait(5)
        self.Switch_ONN_Relay(Bank_number=self.GREEN_KEY_ACK_bank_number, Relay_number=self.GREEN_KEY_ACK_relay_number)
        self.wait(1)
        self.Switch_OFF_Relay(Bank_number=self.GREEN_KEY_ACK_bank_number, Relay_number=self.GREEN_KEY_ACK_relay_number)
        self.wait(2)  # 26th added delay
        self.compare_logs(logs_to_compare, SuccessFlag=SuccessFlag, is_firing_test=is_firing_test)

        print(f"Step: {logs_to_compare} Performed")

    def Adapter_UART_RX_TX_OC_After_Entering_Firingmode(self, fire_force, logs_to_compare = 'EEA Adapter UART Rx & Tx Open Circuit'):

        fire_success_flag = True
        self.output_on_off(True, self.DcPowerSupplyComPort)
        if fire_force == 'Low':
            self.applyLoadViaVoltage(5, self.DcPowerSupplyComPort)
        elif fire_force == 'Medium':
            self.applyLoadViaVoltage(5.1, self.DcPowerSupplyComPort)

        print("Open Circuiting Adapter UART Rx & Tx After Entering FireMode")
        self.Switch_OFF_Relay(1, 3)
        self.Switch_OFF_Relay(1, 4)
        self.wait(10)

        self.compare_logs(logs_to_compare, SuccessFlag=fire_success_flag, is_firing_test=True)
        print(f'STEP : {logs_to_compare} performed!')

        logs_to_compare = 'EEA Firing with Adapter UART Rx Tx Open Circuit'
        self.my_Serthread.clearQue()
        self.wait(5)
        self.Switch_ONN_Relay(Bank_number=self.EEA_STAPLING_ONE_bank_number,
                              Relay_number=self.EEA_STAPLING_ONE_relay_number)  # B4:R1 - ON
        self.Switch_ONN_Relay(Bank_number=self.EEA_STAPLING_TWO_bank_number,
                              Relay_number=self.EEA_STAPLING_TWO_relay_number)  # B4:R2 - ON
        self.wait(4.5)#3)
        self.Switch_ONN_Relay(Bank_number=self.FIRING_bank_number, Relay_number=self.FIRING_relay_number)  # B2:R5 - ON
        self.wait(0.5)
        self.Switch_OFF_Relay(Bank_number=self.FIRING_bank_number, Relay_number=self.FIRING_relay_number)  # B2:R5 - OFF
        self.wait(4)

        self.Switch_OFF_Relay(Bank_number=self.EEA_STAPLING_ONE_bank_number,
                              Relay_number=self.EEA_STAPLING_ONE_relay_number)  # B4:R1 - OFF
        self.Switch_OFF_Relay(Bank_number=self.EEA_STAPLING_TWO_bank_number,
                              Relay_number=self.EEA_STAPLING_TWO_relay_number)  # B4:R2 - OFF

        print("Stapling Completed")

        # self.output_on_off(False, self.DcPowerSupplyComPort)
        #
        # self.wait(1)
        #
        # self.output_on_off(True, self.DcPowerSupplyComPort)
        # self.wait(1)
        self.apply_load_force(0)
        if fire_force == 'Low':
            self.applyLoadViaVoltage(9, self.DcPowerSupplyComPort)
        elif fire_force == 'Medium':
            self.applyLoadViaVoltage(9.1, self.DcPowerSupplyComPort)

        ## Cutting Relays Switched ON
        self.Switch_ONN_Relay(Bank_number=self.EEA_CUTTING_ONE_bank_number,
                              Relay_number=self.EEA_CUTTING_ONE_relay_number)  # B4:R3 - ON
        self.Switch_ONN_Relay(Bank_number=self.EEA_CUTTING_TWO_bank_number,
                              Relay_number=self.EEA_CUTTING_TWO_relay_number)  # B4:R4 - ON

        if fire_force == 'Low':
            self.wait(5)
        else:
            self.wait(10)

        self.Switch_OFF_Relay(Bank_number=self.EEA_CUTTING_ONE_bank_number,
                              Relay_number=self.EEA_CUTTING_ONE_relay_number)  # B4:R3 - OFF
        self.Switch_OFF_Relay(Bank_number=self.EEA_CUTTING_TWO_bank_number,
                              Relay_number=self.EEA_CUTTING_TWO_relay_number)  # B4:R4 - OFF

        self.wait(.5)
        self.Switch_ONN_Relay(Bank_number=self.EEA_CUTTING_COMPLETE_ONE_bank_number,
                              Relay_number=self.EEA_CUTTING_COMPLETE_ONE_relay_number)  # B4:R5 - ON
        self.Switch_ONN_Relay(Bank_number=self.EEA_CUTTING_COMPLETE_TWO_bank_number,
                              Relay_number=self.EEA_CUTTING_COMPLETE_TWO_relay_number)  # B4:R6 - ON
        self.wait(30)
        self.is_firing_completed = True
        self.compare_logs(logs_to_compare, SuccessFlag=fire_success_flag, is_firing_test=True)

        print("Cut Completed")

        self.output_on_off(False, self.DcPowerSupplyComPort)

        self.Switch_OFF_Relay(Bank_number=self.EEA_CUTTING_COMPLETE_ONE_bank_number,
                              Relay_number=self.EEA_CUTTING_COMPLETE_ONE_relay_number)  # B4:R5 - OFF
        self.Switch_OFF_Relay(Bank_number=self.EEA_CUTTING_COMPLETE_TWO_bank_number,
                              Relay_number=self.EEA_CUTTING_COMPLETE_TWO_relay_number)  # B4:R6 - OFF


    def Adapter_1W_SC_After_Entering_Firemode(self, fire_force, logs_to_compare = 'EEA Adapter 1W Short Circuit in Fire Mode'):
        fire_success_flag = True
        self.output_on_off(True, self.DcPowerSupplyComPort)
        if fire_force == 'Low':
            self.applyLoadViaVoltage(5, self.DcPowerSupplyComPort)
        elif fire_force == 'Medium':
            self.applyLoadViaVoltage(5.1, self.DcPowerSupplyComPort)

        print("Short Circuiting Adapter 1Wire")
        self.Switch_ONN_Relay(6, 6)
        self.wait(15)

        self.compare_logs(logs_to_compare, SuccessFlag=fire_success_flag, is_firing_test=True)
        print(f'STEP : {logs_to_compare} performed!')

        logs_to_compare = 'EEA Firing with Adapter 1W Short Circuit'
        self.my_Serthread.clearQue()
        self.wait(5)
        self.Switch_ONN_Relay(Bank_number=self.EEA_STAPLING_ONE_bank_number,
                              Relay_number=self.EEA_STAPLING_ONE_relay_number)  # B4:R1 - ON
        self.Switch_ONN_Relay(Bank_number=self.EEA_STAPLING_TWO_bank_number,
                              Relay_number=self.EEA_STAPLING_TWO_relay_number)  # B4:R2 - ON
        self.wait(4.5)#3)
        self.Switch_ONN_Relay(Bank_number=self.FIRING_bank_number, Relay_number=self.FIRING_relay_number)  # B2:R5 - ON
        self.wait(0.5)
        self.Switch_OFF_Relay(Bank_number=self.FIRING_bank_number, Relay_number=self.FIRING_relay_number)  # B2:R5 - OFF
        self.wait(4)

        self.Switch_OFF_Relay(Bank_number=self.EEA_STAPLING_ONE_bank_number,
                              Relay_number=self.EEA_STAPLING_ONE_relay_number)  # B4:R1 - OFF
        self.Switch_OFF_Relay(Bank_number=self.EEA_STAPLING_TWO_bank_number,
                              Relay_number=self.EEA_STAPLING_TWO_relay_number)  # B4:R2 - OFF

        print("Stapling Completed")

        # self.output_on_off(False, self.DcPowerSupplyComPort)
        #
        # self.wait(1)
        #
        # self.output_on_off(True, self.DcPowerSupplyComPort)
        # self.wait(1)
        self.wait(0)
        if fire_force == 'Low':
            self.applyLoadViaVoltage(9, self.DcPowerSupplyComPort)
        elif fire_force == 'Medium':
            self.applyLoadViaVoltage(9.1, self.DcPowerSupplyComPort)

        ## Cutting Relays Switched ON
        self.Switch_ONN_Relay(Bank_number=self.EEA_CUTTING_ONE_bank_number,
                              Relay_number=self.EEA_CUTTING_ONE_relay_number)  # B4:R3 - ON
        self.Switch_ONN_Relay(Bank_number=self.EEA_CUTTING_TWO_bank_number,
                              Relay_number=self.EEA_CUTTING_TWO_relay_number)  # B4:R4 - ON

        if fire_force == 'Low':
            self.wait(5)
        else:
            self.wait(10)

        self.Switch_OFF_Relay(Bank_number=self.EEA_CUTTING_ONE_bank_number,
                              Relay_number=self.EEA_CUTTING_ONE_relay_number)  # B4:R3 - OFF
        self.Switch_OFF_Relay(Bank_number=self.EEA_CUTTING_TWO_bank_number,
                              Relay_number=self.EEA_CUTTING_TWO_relay_number)  # B4:R4 - OFF

        self.wait(.5)
        self.Switch_ONN_Relay(Bank_number=self.EEA_CUTTING_COMPLETE_ONE_bank_number,
                              Relay_number=self.EEA_CUTTING_COMPLETE_ONE_relay_number)  # B4:R5 - ON
        self.Switch_ONN_Relay(Bank_number=self.EEA_CUTTING_COMPLETE_TWO_bank_number,
                              Relay_number=self.EEA_CUTTING_COMPLETE_TWO_relay_number)  # B4:R6 - ON
        self.wait(30)
        self.is_firing_completed = True
        self.compare_logs(logs_to_compare, SuccessFlag=fire_success_flag, is_firing_test=True)

        print("Cut Completed")

        self.output_on_off(False, self.DcPowerSupplyComPort)

        self.Switch_OFF_Relay(Bank_number=self.EEA_CUTTING_COMPLETE_ONE_bank_number,
                              Relay_number=self.EEA_CUTTING_COMPLETE_ONE_relay_number)  # B4:R5 - OFF
        self.Switch_OFF_Relay(Bank_number=self.EEA_CUTTING_COMPLETE_TWO_bank_number,
                              Relay_number=self.EEA_CUTTING_COMPLETE_TWO_relay_number)  # B4:R6 - OFF

    def Adapter_1W_OC_After_Entering_Firingmode(self,  fire_force, logs_to_compare = 'EEA Firing with Adapter 1W Open Circuit'):
        fire_success_flag = True
        self.output_on_off(True, self.DcPowerSupplyComPort)
        if fire_force == 'Low':
            self.applyLoadViaVoltage(5, self.DcPowerSupplyComPort)
        elif fire_force == 'Medium':
            self.applyLoadViaVoltage(5.1, self.DcPowerSupplyComPort)

        print('Open Circuiting Adapter 1W')
        self.Switch_OFF_Relay(1, 2)  # B1:R2 - OFF

        self.my_Serthread.clearQue()
        self.wait(5)
        self.Switch_ONN_Relay(Bank_number=self.EEA_STAPLING_ONE_bank_number,
                              Relay_number=self.EEA_STAPLING_ONE_relay_number)  # B4:R1 - ON
        self.Switch_ONN_Relay(Bank_number=self.EEA_STAPLING_TWO_bank_number,
                              Relay_number=self.EEA_STAPLING_TWO_relay_number)  # B4:R2 - ON
        self.wait(4.5)#3)
        self.Switch_ONN_Relay(Bank_number=self.FIRING_bank_number, Relay_number=self.FIRING_relay_number)  # B2:R5 - ON
        self.wait(0.5)
        self.Switch_OFF_Relay(Bank_number=self.FIRING_bank_number, Relay_number=self.FIRING_relay_number)  # B2:R5 - OFF
        self.wait(4)
        self.Switch_OFF_Relay(Bank_number=self.EEA_STAPLING_ONE_bank_number,
                              Relay_number=self.EEA_STAPLING_ONE_relay_number)  # B4:R1 - OFF
        self.Switch_OFF_Relay(Bank_number=self.EEA_STAPLING_TWO_bank_number,
                              Relay_number=self.EEA_STAPLING_TWO_relay_number)  # B4:R2 - OFF
        print("Staple Completed")

        # self.output_on_off(False, self.DcPowerSupplyComPort)
        #
        # self.wait(1)
        #
        # self.output_on_off(True, self.DcPowerSupplyComPort)
        # self.wait(1)
        self.apply_load_force(0)
        if fire_force == 'Low':
            self.applyLoadViaVoltage(9, self.DcPowerSupplyComPort)
        elif fire_force == 'Medium':
            self.applyLoadViaVoltage(9.1, self.DcPowerSupplyComPort)

        self.Switch_ONN_Relay(Bank_number=self.EEA_CUTTING_ONE_bank_number,
                              Relay_number=self.EEA_CUTTING_ONE_relay_number)  # B4:R3 - ON
        self.Switch_ONN_Relay(Bank_number=self.EEA_CUTTING_TWO_bank_number,
                              Relay_number=self.EEA_CUTTING_TWO_relay_number)  # B4:R4 - ON
        if fire_force == 'Low':
            self.wait(5)
        else:
            self.wait(10)

        self.Switch_OFF_Relay(Bank_number=self.EEA_CUTTING_ONE_bank_number,
                              Relay_number=self.EEA_CUTTING_ONE_relay_number)  # B4:R3 - OFF
        self.Switch_OFF_Relay(Bank_number=self.EEA_CUTTING_TWO_bank_number,
                              Relay_number=self.EEA_CUTTING_TWO_relay_number)  # B4:R4 - OFF
        self.wait(.5)
        self.Switch_ONN_Relay(Bank_number=self.EEA_CUTTING_COMPLETE_ONE_bank_number,
                              Relay_number=self.EEA_CUTTING_COMPLETE_ONE_relay_number)  # B4:R5 - ON
        self.Switch_ONN_Relay(Bank_number=self.EEA_CUTTING_COMPLETE_TWO_bank_number,
                              Relay_number=self.EEA_CUTTING_COMPLETE_TWO_relay_number)  # B4:R6 - ON
        self.wait(30)
        self.is_firing_completed = True
        self.compare_logs(logs_to_compare, SuccessFlag=fire_success_flag, is_firing_test=True)

        print("Cut Completed")

        self.output_on_off(False, self.DcPowerSupplyComPort)

        self.Switch_OFF_Relay(Bank_number=self.EEA_CUTTING_COMPLETE_ONE_bank_number,
                              Relay_number=self.EEA_CUTTING_COMPLETE_ONE_relay_number)  # B4:R5 - OFF
        self.Switch_OFF_Relay(Bank_number=self.EEA_CUTTING_COMPLETE_TWO_bank_number,
                              Relay_number=self.EEA_CUTTING_COMPLETE_TWO_relay_number)  # B4:R6 - OFF

    def Shell_1W_OC_After_Entering_Firemode(self, fire_force, logs_to_compare = 'EEA Firing'):
        fire_success_flag = True
        self.output_on_off(True, self.DcPowerSupplyComPort)
        if fire_force == 'Low':
            self.applyLoadViaVoltage(5, self.DcPowerSupplyComPort)
        elif fire_force == 'Medium':
            self.applyLoadViaVoltage(5.1, self.DcPowerSupplyComPort)

        print('Open Circuiting Clamshell 1W')
        self.Switch_OFF_Relay(1, 5)  # B1:R5 - OFF

        self.my_Serthread.clearQue()
        self.wait(5)
        self.Switch_ONN_Relay(Bank_number=self.EEA_STAPLING_ONE_bank_number,
                              Relay_number=self.EEA_STAPLING_ONE_relay_number)  # B4:R1 - ON
        self.Switch_ONN_Relay(Bank_number=self.EEA_STAPLING_TWO_bank_number,
                              Relay_number=self.EEA_STAPLING_TWO_relay_number)  # B4:R2 - ON
        self.wait(4.5)#3)
        self.Switch_ONN_Relay(Bank_number=self.FIRING_bank_number, Relay_number=self.FIRING_relay_number)  # B2:R5 - ON
        self.wait(0.5)
        self.Switch_OFF_Relay(Bank_number=self.FIRING_bank_number, Relay_number=self.FIRING_relay_number)  # B2:R5 - OFF
        self.wait(4)
        self.Switch_OFF_Relay(Bank_number=self.EEA_STAPLING_ONE_bank_number,
                              Relay_number=self.EEA_STAPLING_ONE_relay_number)  # B4:R1 - OFF
        self.Switch_OFF_Relay(Bank_number=self.EEA_STAPLING_TWO_bank_number,
                              Relay_number=self.EEA_STAPLING_TWO_relay_number)  # B4:R2 - OFF
        print("Staple Completed")

        # self.output_on_off(False, self.DcPowerSupplyComPort)
        #
        # self.wait(1)
        #
        # self.output_on_off(True, self.DcPowerSupplyComPort)
        # self.wait(1)
        self.apply_load_force(0)
        if fire_force == 'Low':
            self.applyLoadViaVoltage(9, self.DcPowerSupplyComPort)
        elif fire_force == 'Medium':
            self.applyLoadViaVoltage(9.1, self.DcPowerSupplyComPort)

        self.Switch_ONN_Relay(Bank_number=self.EEA_CUTTING_ONE_bank_number,
                              Relay_number=self.EEA_CUTTING_ONE_relay_number)  # B4:R3 - ON
        self.Switch_ONN_Relay(Bank_number=self.EEA_CUTTING_TWO_bank_number,
                              Relay_number=self.EEA_CUTTING_TWO_relay_number)  # B4:R4 - ON
        if fire_force == 'Low':
            self.wait(5)
        else:
            self.wait(10)

        self.Switch_OFF_Relay(Bank_number=self.EEA_CUTTING_ONE_bank_number,
                              Relay_number=self.EEA_CUTTING_ONE_relay_number)  # B4:R3 - OFF
        self.Switch_OFF_Relay(Bank_number=self.EEA_CUTTING_TWO_bank_number,
                              Relay_number=self.EEA_CUTTING_TWO_relay_number)  # B4:R4 - OFF
        self.wait(.5)
        self.Switch_ONN_Relay(Bank_number=self.EEA_CUTTING_COMPLETE_ONE_bank_number,
                              Relay_number=self.EEA_CUTTING_COMPLETE_ONE_relay_number)  # B4:R5 - ON
        self.Switch_ONN_Relay(Bank_number=self.EEA_CUTTING_COMPLETE_TWO_bank_number,
                              Relay_number=self.EEA_CUTTING_COMPLETE_TWO_relay_number)  # B4:R6 - ON
        self.wait(30)
        self.is_firing_completed = True
        self.compare_logs(logs_to_compare,SuccessFlag=fire_success_flag, is_firing_test=True)

        print("Cut Completed")

        self.output_on_off(False, self.DcPowerSupplyComPort)

        self.Switch_OFF_Relay(Bank_number=self.EEA_CUTTING_COMPLETE_ONE_bank_number,
                              Relay_number=self.EEA_CUTTING_COMPLETE_ONE_relay_number)  # B4:R5 - OFF
        self.Switch_OFF_Relay(Bank_number=self.EEA_CUTTING_COMPLETE_TWO_bank_number,
                              Relay_number=self.EEA_CUTTING_COMPLETE_TWO_relay_number)  # B4:R6 - OFF

    def Shell_1W_SC_After_Entering_Firemode(self, fire_force, logs_to_compare = 'EEA Firing'):
        fire_success_flag = True
        self.output_on_off(True, self.DcPowerSupplyComPort)
        if fire_force == 'Low':
            self.applyLoadViaVoltage(5, self.DcPowerSupplyComPort)
        elif fire_force == 'Medium':
            self.applyLoadViaVoltage(5.1, self.DcPowerSupplyComPort)

        print('Short Circuiting Clamshell 1W After Entering Fire Mode')
        self.Switch_OFF_Relay(6, 5)  # B1:R5 - OFF

        self.my_Serthread.clearQue()
        self.wait(5)
        self.Switch_ONN_Relay(Bank_number=self.EEA_STAPLING_ONE_bank_number,
                              Relay_number=self.EEA_STAPLING_ONE_relay_number)  # B4:R1 - ON
        self.Switch_ONN_Relay(Bank_number=self.EEA_STAPLING_TWO_bank_number,
                              Relay_number=self.EEA_STAPLING_TWO_relay_number)  # B4:R2 - ON
        self.wait(4.5)#3)
        self.Switch_ONN_Relay(Bank_number=self.FIRING_bank_number, Relay_number=self.FIRING_relay_number)  # B2:R5 - ON
        self.wait(0.5)
        self.Switch_OFF_Relay(Bank_number=self.FIRING_bank_number, Relay_number=self.FIRING_relay_number)  # B2:R5 - OFF
        self.wait(4)
        self.Switch_OFF_Relay(Bank_number=self.EEA_STAPLING_ONE_bank_number,
                              Relay_number=self.EEA_STAPLING_ONE_relay_number)  # B4:R1 - OFF
        self.Switch_OFF_Relay(Bank_number=self.EEA_STAPLING_TWO_bank_number,
                              Relay_number=self.EEA_STAPLING_TWO_relay_number)  # B4:R2 - OFF
        print("Staple Completed")

        # self.output_on_off(False, self.DcPowerSupplyComPort)
        #
        # self.wait(1)
        #
        # self.output_on_off(True, self.DcPowerSupplyComPort)
        # self.wait(1)
        self.apply_load_force(0)
        if fire_force == 'Low':
            self.applyLoadViaVoltage(9, self.DcPowerSupplyComPort)
        elif fire_force == 'Medium':
            self.applyLoadViaVoltage(9.1, self.DcPowerSupplyComPort)

        self.Switch_ONN_Relay(Bank_number=self.EEA_CUTTING_ONE_bank_number,
                              Relay_number=self.EEA_CUTTING_ONE_relay_number)  # B4:R3 - ON
        self.Switch_ONN_Relay(Bank_number=self.EEA_CUTTING_TWO_bank_number,
                              Relay_number=self.EEA_CUTTING_TWO_relay_number)  # B4:R4 - ON
        if fire_force == 'Low':
            self.wait(5)
        else:
            self.wait(10)

        self.Switch_OFF_Relay(Bank_number=self.EEA_CUTTING_ONE_bank_number,
                              Relay_number=self.EEA_CUTTING_ONE_relay_number)  # B4:R3 - OFF
        self.Switch_OFF_Relay(Bank_number=self.EEA_CUTTING_TWO_bank_number,
                              Relay_number=self.EEA_CUTTING_TWO_relay_number)  # B4:R4 - OFF
        self.wait(.5)
        self.Switch_ONN_Relay(Bank_number=self.EEA_CUTTING_COMPLETE_ONE_bank_number,
                              Relay_number=self.EEA_CUTTING_COMPLETE_ONE_relay_number)  # B4:R5 - ON
        self.Switch_ONN_Relay(Bank_number=self.EEA_CUTTING_COMPLETE_TWO_bank_number,
                              Relay_number=self.EEA_CUTTING_COMPLETE_TWO_relay_number)  # B4:R6 - ON
        self.wait(30)
        self.is_firing_completed = True
        self.compare_logs(logs_to_compare, SuccessFlag=fire_success_flag, is_firing_test=True)

        print("Cut Completed")

        self.output_on_off(False, self.DcPowerSupplyComPort)

        self.Switch_OFF_Relay(Bank_number=self.EEA_CUTTING_COMPLETE_ONE_bank_number,
                              Relay_number=self.EEA_CUTTING_COMPLETE_ONE_relay_number)  # B4:R5 - OFF
        self.Switch_OFF_Relay(Bank_number=self.EEA_CUTTING_COMPLETE_TWO_bank_number,
                              Relay_number=self.EEA_CUTTING_COMPLETE_TWO_relay_number)  # B4:R6 - OFF

    def EEAFiring_Fixture_Validation(self, logs_to_compare='EEA Firing', fixture_validation_req=True, fire_force=False):
        fire_success_flag = True
        # self.apply_load_force(3.25, fixture_validation_req=fixture_validation_req)
        # Apply Voltage Instead of Applying Load Force
        self.output_on_off(True, self.DcPowerSupplyComPort)
        if fire_force == 'Low':
            self.applyLoadViaVoltage(4.8, self.DcPowerSupplyComPort)
        elif fire_force == 'Medium':
            self.applyLoadViaVoltage(5, self.DcPowerSupplyComPort)
        self.my_Serthread.clearQue()
        self.wait(5)
        self.Switch_ONN_Relay(Bank_number=self.EEA_STAPLING_ONE_bank_number,
                              Relay_number=self.EEA_STAPLING_ONE_relay_number)  # B4:R1 - ON
        self.Switch_ONN_Relay(Bank_number=self.EEA_STAPLING_TWO_bank_number,
                              Relay_number=self.EEA_STAPLING_TWO_relay_number)  # B4:R2 - ON
        self.wait(3)
        self.Switch_ONN_Relay(Bank_number=self.FIRING_bank_number, Relay_number=self.FIRING_relay_number)  # B2:R5 - ON
        self.wait(0.5)
        self.Switch_OFF_Relay(Bank_number=self.FIRING_bank_number, Relay_number=self.FIRING_relay_number)  # B2:R5 - OFF
        self.wait(4)

        self.Switch_OFF_Relay(Bank_number=self.EEA_STAPLING_ONE_bank_number,
                              Relay_number=self.EEA_STAPLING_ONE_relay_number)  # B4:R1 - OFF
        self.Switch_OFF_Relay(Bank_number=self.EEA_STAPLING_TWO_bank_number,
                              Relay_number=self.EEA_STAPLING_TWO_relay_number)  # B4:R2 - OFF

        print("Stapling Completed")

        self.output_on_off(False, self.DcPowerSupplyComPort)

        self.wait(1)

        self.output_on_off(True, self.DcPowerSupplyComPort)
        self.wait(1)
        if fire_force == 'Low':
            self.applyLoadViaVoltage(8.8, self.DcPowerSupplyComPort)
        elif fire_force == 'Medium':
            self.applyLoadViaVoltage(9, self.DcPowerSupplyComPort)

        ### Added Here Manoj Instructions 24 Jan
        # self.Switch_OFF_Relay(Bank_number=self.EEA_CUTTING_ONE_bank_number,
        #                       Relay_number=self.EEA_CUTTING_ONE_relay_number)  # B4:R3 - OFF
        # self.Switch_OFF_Relay(Bank_number=self.EEA_CUTTING_TWO_bank_number,
        #                       Relay_number=self.EEA_CUTTING_TWO_relay_number)  # B4:R4 - OFF

        # self.wait(.5)
        # self.Switch_ONN_Relay(Bank_number=self.EEA_CUTTING_COMPLETE_ONE_bank_number,
        #                       Relay_number=self.EEA_CUTTING_COMPLETE_ONE_relay_number)  # B4:R5 - ON
        # self.Switch_ONN_Relay(Bank_number=self.EEA_CUTTING_COMPLETE_TWO_bank_number,
        #                       Relay_number=self.EEA_CUTTING_COMPLETE_TWO_relay_number)  # B4:R6 - ON
        # self.wait(2)
        #
        # ### 4,5 and 4,6 OFF
        # self.Switch_OFF_Relay(Bank_number=self.EEA_CUTTING_COMPLETE_ONE_bank_number,
        #                       Relay_number=self.EEA_CUTTING_COMPLETE_ONE_relay_number)  # B4:R5 - OFF
        # self.Switch_OFF_Relay(Bank_number=self.EEA_CUTTING_COMPLETE_TWO_bank_number,
        #                       Relay_number=self.EEA_CUTTING_COMPLETE_TWO_relay_number)  # B4:R6 - OFF
        #
        # self.wait(2)
        ## Cutting Relays Switched ON
        self.Switch_ONN_Relay(Bank_number=self.EEA_CUTTING_ONE_bank_number,
                              Relay_number=self.EEA_CUTTING_ONE_relay_number)  # B4:R3 - ON
        self.Switch_ONN_Relay(Bank_number=self.EEA_CUTTING_TWO_bank_number,
                              Relay_number=self.EEA_CUTTING_TWO_relay_number)  # B4:R4 - ON

        if fire_force == 'Low':
            self.wait(5)
        else:
            self.wait(10)

        self.Switch_OFF_Relay(Bank_number=self.EEA_CUTTING_ONE_bank_number,
                              Relay_number=self.EEA_CUTTING_ONE_relay_number)  # B4:R3 - OFF
        self.Switch_OFF_Relay(Bank_number=self.EEA_CUTTING_TWO_bank_number,
                              Relay_number=self.EEA_CUTTING_TWO_relay_number)  # B4:R4 - OFF

        self.wait(.5)
        self.Switch_ONN_Relay(Bank_number=self.EEA_CUTTING_COMPLETE_ONE_bank_number,
                              Relay_number=self.EEA_CUTTING_COMPLETE_ONE_relay_number)  # B4:R5 - ON
        self.Switch_ONN_Relay(Bank_number=self.EEA_CUTTING_COMPLETE_TWO_bank_number,
                              Relay_number=self.EEA_CUTTING_COMPLETE_TWO_relay_number)  # B4:R6 - ON
        self.wait(30)
        self.is_firing_completed = True
        self.compare_logs(logs_to_compare, SuccessFlag=fire_success_flag, is_firing_test=True, fixtureValidation=fixture_validation_req)

        print("Cut Completed")

        self.output_on_off(False, self.DcPowerSupplyComPort)

        self.Switch_OFF_Relay(Bank_number=self.EEA_CUTTING_COMPLETE_ONE_bank_number,
                              Relay_number=self.EEA_CUTTING_COMPLETE_ONE_relay_number)  # B4:R5 - OFF
        self.Switch_OFF_Relay(Bank_number=self.EEA_CUTTING_COMPLETE_TWO_bank_number,
                              Relay_number=self.EEA_CUTTING_COMPLETE_TWO_relay_number)  # B4:R6 - OFF

    def read_load_cell_data(self, command_bytes):
        # print(command_bytes)
        self.serial_port.reset_output_buffer()
        self.serial_port.reset_input_buffer()
        self.serial_port.flush()

        command_bytes = bytearray(command_bytes)
        self.serial_port.write(command_bytes)
        # Receive response
        decimal_bytes = self.serial_port.readline()
        print(decimal_bytes)
        adc_count = 0
        if len(decimal_bytes) != 0:
            adc_count = (decimal_bytes[2] << 8) | decimal_bytes[3]
        return adc_count

    def wait_till_reach_peak_load(self, peak_load: int):
        self.serRS = serial.Serial(self.ArduinoUNOComPort, 115200, timeout=0.05)
        print("Start Time: ", datetime.datetime.now())
        with self.serRS:
            while 1:  # 80
                try:
                    load_cell_data = 0
                    ser_bytes1 = self.serRS.readline()
                    # print("serial bytes: ", ser_bytes1)
                    read_data1 = ser_bytes1.decode('ascii')
                    # print("Reading data ", read_data1)
                    data = read_data1.split(':')
                    if data[0].strip() == "Load Cell Data":
                        load_cell_data = int(data[1])
                        print(f"load_cell_data: {load_cell_data}")

                    # if int(peak_load * 0.95) - 1 <= load_cell_data <= int(peak_load * 1.05) + 1: # tolerance 5%
                    #     break

                    if load_cell_data > peak_load :
                        break

                    # if self.my_Serthread.__log_to_be_found:
                    #     break

                except:
                    pass
            print("End time: ", datetime.datetime.now())


    def EEAFiring(self, fire_force, logs_to_compare='EEA Firing'):
        # #self.mcpobj: MCPThread.readingPowerPack = mcpobj
        # self.output_on_off(True, self.DcPowerSupplyComPort)
        # # self.applyLoadViaVoltage(4, self.DcPowerSupplyComPort)
        # #
        # #
        # # # turn on 4-1 and 4-2 relays
        # # self.Switch_ONN_Relay(4, 1)
        # # self.Switch_ONN_Relay(4, 2)
        # #
        # # # self.wait_till_reach_peak_load(15)
        # # self.wait(1)
        # #
        # # # turn off 4-1 and 4-2
        # # self.Switch_OFF_Relay(4, 1)
        # # self.Switch_OFF_Relay(4, 2)
        #
        # self.applyLoadViaVoltage(5.5, self.DcPowerSupplyComPort) #VMK changed to 5.5 from 7
        #
        # # self.my_Serthread.__log_to_be_found = '****  ENTERING OP LSS WRecID STAPLE COMPLETE STATE  ****'
        #
        #
        # # turn on 4-1 and 4-2 relays
        # self.Switch_ONN_Relay(4, 1)
        # self.Switch_ONN_Relay(4, 2)
        #
        # self.wait(10)
        #
        # # press close key
        # self.Switch_ONN_Relay(2, 5)
        # time.sleep(0.5)
        # self.Switch_OFF_Relay(2, 5)
        #
        #
        #
        # #if not self.my_Serthread.__is_log_found:
        # # self.wait_till_reach_peak_load(530)
        #
        # # self.my_Serthread.__log_to_be_found = '****  ENTERING OP LSC Advance Cut STATE  ****'
        # self.wait(4) # 4 to 2 VMK
        #
        # # turn off 4-1 and 4-2
        # self.Switch_OFF_Relay(4, 1)
        # self.Switch_OFF_Relay(4, 2)
        # # self.wait(0.1)
        # # self.applyLoadViaVoltage(7, self.DcPowerSupplyComPort)
        # # self.apply_load_force(0) #VMK commented
        # # turn on 4-5 and 4-6 relays
        # self.Switch_ONN_Relay(4, 5)
        # self.Switch_ONN_Relay(4, 6)
        #
        # # self.wait_till_reach_peak_load(3)
        # self.wait(1)
        #
        # # turn off 4-5 and 4-6 relays
        # self.Switch_OFF_Relay(4, 5)
        # self.Switch_OFF_Relay(4, 6)
        #
        #
        # self.applyLoadViaVoltage(7.5, self.DcPowerSupplyComPort) #VMK changed 9 to 6.5V
        # # self.wait(2) commented VMK
        # # turn on 4-1 and 4-2 relays
        # self.Switch_ONN_Relay(4, 1)
        # self.Switch_ONN_Relay(4, 2)
        # self.wait(2) #VMK added
        # self.apply_load_force(0) # VMK added
        #
        #
        # # #if not self.my_Serthread.__is_log_found:
        # # self.wait(1)
        # # # self.my_Serthread.__log_to_be_found = '****  ENTERING OP LSC Complete Cut STATE  ****'
        # # # self.wait_till_reach_peak_load(160)
        # #
        # # self.applyLoadViaVoltage(6, self.DcPowerSupplyComPort)
        # # self.wait(2)
        # # self.applyLoadViaVoltage(7, self.DcPowerSupplyComPort)
        # # self.wait(2)
        # # self.applyLoadViaVoltage(8, self.DcPowerSupplyComPort)
        # # # self.wait_till_reach_peak_load(380)
        # #
        # # # check for entry to complete cut state
        # # self.wait(2)
        # # self.applyLoadViaVoltage(9, self.DcPowerSupplyComPort)
        # # # self.wait_till_reach_peak_load(530)
        # # self.wait(2)
        # # self.applyLoadViaVoltage(10, self.DcPowerSupplyComPort)
        # # self.wait(2)
        # # # self.applyLoadViaVoltage(11, self.DcPowerSupplyComPort)
        # self.wait(3)
        # # turn off 4-1 and 4-2
        # self.Switch_OFF_Relay(4, 1)
        # self.Switch_OFF_Relay(4, 2)
        #
        # # turn on 4-5 and 4-6 relays
        # self.Switch_ONN_Relay(4, 5)
        # self.Switch_ONN_Relay(4, 6)
        #
        # self.wait(10)
        #
        # # turn off 4-5 and 4-6 relays
        # self.Switch_OFF_Relay(4, 5)
        # self.Switch_OFF_Relay(4, 6)
        #
        # # self.wait(10)
        # pass

        self.output_on_off(True, self.DcPowerSupplyComPort)
        string_to_found = ''
        self.applyLoadViaVoltage(4, self.DcPowerSupplyComPort)

        # turn on 4-1 and 4-2 relays
        self.Switch_ONN_Relay(4, 1)
        self.Switch_ONN_Relay(4, 2)

        # self.wait_till_reach_peak_load(15)
        self.wait(1)

        # turn off 4-1 and 4-2
        self.Switch_OFF_Relay(4, 1)
        self.Switch_OFF_Relay(4, 2)

        self.applyLoadViaVoltage(5.5, self.DcPowerSupplyComPort) #VMK changed to 5.5 from 7
        self.wait(1)

        # turn on 4-1 and 4-2 relays
        self.Switch_ONN_Relay(4, 1)
        self.Switch_ONN_Relay(4, 2)

        self.wait(4)

        # press close key
        self.Switch_ONN_Relay(2, 5)
        time.sleep(0.5)
        self.Switch_OFF_Relay(2, 5)



        string_to_found = 'GUI_NewState: EEA_STAPLE_26_38'
        # string_to_found = '****  ENTERING OP LSS WRecID STAPLE COMPLETE STATE  ****'
        self.my_Serthread.waitUntilString(string_to_found, timeout=10)
        # turn off 4-1 and 4-2
        self.Switch_OFF_Relay(4, 1)
        self.Switch_OFF_Relay(4, 2)

        # turn on 4-5 and 4-6 relays


        self.Switch_ONN_Relay(4, 5)
        self.Switch_ONN_Relay(4, 6)

        # self.wait_till_reach_peak_load(3)
        self.wait(2)

        # turn off 4-5 and 4-6 relays
        self.Switch_OFF_Relay(4, 5)
        self.Switch_OFF_Relay(4, 6)

        self.applyLoadViaVoltage(9, self.DcPowerSupplyComPort)

        # turn on 4-1 and 4-2 relays
        self.Switch_ONN_Relay(4, 1)
        self.Switch_ONN_Relay(4, 2)

        self.apply_load_force(0)

        print(f"finding: ****  ENTERING OP LSC Retract Cut STATE  ****")
        string_to_found = '****  ENTERING OP LSC Retract Cut STATE  ****'
        self.my_Serthread.waitUntilString(string_to_found, timeout=20)

        self.Switch_OFF_Relay(4, 1)
        self.Switch_OFF_Relay(4, 2)

        self.Switch_ONN_Relay(4, 5)
        self.Switch_ONN_Relay(4, 6)

        # self.wait_till_reach_peak_load(3)
        self.wait(7)

        # turn off 4-5 and 4-6 relays
        self.Switch_OFF_Relay(4, 5)
        self.Switch_OFF_Relay(4, 6)
        #
        #
        #
        #
        # # #if not self.my_Serthread.__is_log_found:
        # # self.wait(1)
        # # # self.my_Serthread.__log_to_be_found = '****  ENTERING OP LSC Complete Cut STATE  ****'
        #
        # # # self.wait_till_reach_peak_load(160)
        # #
        # # self.applyLoadViaVoltage(6, self.DcPowerSupplyComPort)
        # # self.wait(2)
        # # self.applyLoadViaVoltage(7, self.DcPowerSupplyComPort)
        # # self.wait(2)
        # # self.applyLoadViaVoltage(8, self.DcPowerSupplyComPort)
        # # # self.wait_till_reach_peak_load(380)
        # #
        # # # check for entry to complete cut state
        # # self.wait(2)
        # # self.applyLoadViaVoltage(9, self.DcPowerSupplyComPort)
        # # # self.wait_till_reach_peak_load(530)
        # # self.wait(2)
        # # self.applyLoadViaVoltage(10, self.DcPowerSupplyComPort)
        # # self.wait(2)
        # # # self.applyLoadViaVoltage(11, self.DcPowerSupplyComPort)
        # # self.wait(3)
        # # turn off 4-1 and 4-2
        # self.Switch_OFF_Relay(4, 1)
        # self.Switch_OFF_Relay(4, 2)
        #
        # # turn on 4-5 and 4-6 relays
        # self.Switch_ONN_Relay(4, 5)
        # self.Switch_ONN_Relay(4, 6)
        #
        # self.wait(10)
        #
        # # turn off 4-5 and 4-6 relays
        # self.Switch_OFF_Relay(4, 5)
        # self.Switch_OFF_Relay(4, 6)
        #
        # # self.wait(10)
        # pass

    # fire_success_flag = True
        # # self.apply_load_force(3.25, fixture_validation_req=fixture_validation_req)
        # # Apply Voltage Instead of Applying Load Force
        # self.output_on_off(True, self.DcPowerSupplyComPort)
        # # print(f'fire_force: {fire_force}, fire_force == "Low": {fire_force == 'Low'}')
        # if fire_force == 'Low':
        #     # print(f'Inside If fire_force: {fire_force}, fire_force == "Low": {fire_force == 'Low'}')
        #     self.applyLoadViaVoltage(5, self.DcPowerSupplyComPort)
        # elif fire_force == 'Medium':
        #     self.applyLoadViaVoltage(5.1, self.DcPowerSupplyComPort)
        #
        # self.Switch_ONN_Relay(Bank_number=self.EEA_STAPLING_ONE_bank_number,
        #                       Relay_number=self.EEA_STAPLING_ONE_relay_number)  # B4:R1 - ON
        # self.Switch_ONN_Relay(Bank_number=self.EEA_STAPLING_TWO_bank_number,
        #                       Relay_number=self.EEA_STAPLING_TWO_relay_number)  # B4:R2 - ON
        # self.wait(4.5)#3)
        # self.Switch_ONN_Relay(Bank_number=self.FIRING_bank_number, Relay_number=self.FIRING_relay_number)  # B2:R5 - ON
        # self.wait(0.5)
        # self.Switch_OFF_Relay(Bank_number=self.FIRING_bank_number, Relay_number=self.FIRING_relay_number)  # B2:R5 - OFF
        #
        # # #### Debug Purpose Added here ########################
        # # self.Switch_OFF_Relay(1,8)
        # # #######################################################
        # self.wait(4)
        #
        # self.Switch_OFF_Relay(Bank_number=self.EEA_STAPLING_ONE_bank_number,
        #                       Relay_number=self.EEA_STAPLING_ONE_relay_number)  # B4:R1 - OFF
        # self.Switch_OFF_Relay(Bank_number=self.EEA_STAPLING_TWO_bank_number,
        #                       Relay_number=self.EEA_STAPLING_TWO_relay_number)  # B4:R2 - OFF
        #
        # print("Stapling Completed")
        #
        # # self.output_on_off(False, self.DcPowerSupplyComPort)
        #
        # # self.wait(5)
        #
        # # self.output_on_off(True, self.DcPowerSupplyComPort)
        # #self.wait(1)
        # if fire_force == 'Low':
        #     self.applyLoadViaVoltage(9, self.DcPowerSupplyComPort)
        # elif fire_force == 'Medium':
        #     self.applyLoadViaVoltage(9.1, self.DcPowerSupplyComPort)
        #
        # self.apply_load_force(0)
        #
        # ## Cutting Relays Switched ON
        # self.Switch_ONN_Relay(Bank_number=self.EEA_CUTTING_ONE_bank_number,
        #                       Relay_number=self.EEA_CUTTING_ONE_relay_number)  # B4:R3 - ON
        # self.Switch_ONN_Relay(Bank_number=self.EEA_CUTTING_TWO_bank_number,
        #                       Relay_number=self.EEA_CUTTING_TWO_relay_number)  # B4:R4 - ON
        #
        # if fire_force == 'Low':
        #     self.wait(5)
        # else:
        #     self.wait(10)
        #
        # self.Switch_OFF_Relay(Bank_number=self.EEA_CUTTING_ONE_bank_number,
        #                       Relay_number=self.EEA_CUTTING_ONE_relay_number)  # B4:R3 - OFF
        # self.Switch_OFF_Relay(Bank_number=self.EEA_CUTTING_TWO_bank_number,
        #                       Relay_number=self.EEA_CUTTING_TWO_relay_number)  # B4:R4 - OFF
        #
        # self.wait(.5)
        # self.Switch_ONN_Relay(Bank_number=self.EEA_CUTTING_COMPLETE_ONE_bank_number,
        #                       Relay_number=self.EEA_CUTTING_COMPLETE_ONE_relay_number)  # B4:R5 - ON
        # self.Switch_ONN_Relay(Bank_number=self.EEA_CUTTING_COMPLETE_TWO_bank_number,
        #                       Relay_number=self.EEA_CUTTING_COMPLETE_TWO_relay_number)  # B4:R6 - ON
        # self.wait(30)
        # self.is_firing_completed = True
        # self.compare_logs(logs_to_compare, SuccessFlag=fire_success_flag, is_firing_test=True)
        #
        # print("Cut Completed")
        #
        # self.output_on_off(False, self.DcPowerSupplyComPort)
        #
        # self.Switch_OFF_Relay(Bank_number=self.EEA_CUTTING_COMPLETE_ONE_bank_number,
        #                       Relay_number=self.EEA_CUTTING_COMPLETE_ONE_relay_number)  # B4:R5 - OFF
        # self.Switch_OFF_Relay(Bank_number=self.EEA_CUTTING_COMPLETE_TWO_bank_number,
        #                       Relay_number=self.EEA_CUTTING_COMPLETE_TWO_relay_number)  # B4:R6 - OFF

    def EEAFiring_Stapling_Recovery_No_Staple_Exit_State(self, logs_to_compare='EEA Firing'):
        # EEA Firing
        self.output_on_off(True, self.DcPowerSupplyComPort)
        self.applyLoadViaVoltage(4, self.DcPowerSupplyComPort)

        # turn on 4-1 and 4-2 relays
        self.Switch_ONN_Relay(4, 1)
        self.Switch_ONN_Relay(4, 2)

        self.wait(1)

        # turn off 4-1 and 4-2
        self.Switch_OFF_Relay(4, 1)
        self.Switch_OFF_Relay(4, 2)

        self.applyLoadViaVoltage(5.5, self.DcPowerSupplyComPort)
        self.wait(1)

        # turn on 4-1 and 4-2 relays
        self.Switch_ONN_Relay(4, 1)
        self.Switch_ONN_Relay(4, 2)

        self.wait(4)

        # press close key
        self.Switch_ONN_Relay(2, 5)
        time.sleep(0.5)
        self.Switch_OFF_Relay(2, 5)

        string_to_found = 'GUI_NewState: EEA_STAPLE_11_25'
        self.my_Serthread.waitUntilString(string_to_found, timeout=10)
        # turn off 4-1 and 4-2
        self.Switch_OFF_Relay(4, 1)
        self.Switch_OFF_Relay(4, 2)

        # Detaching Adapter at 1st EEA Stapling In-Progress
        self.removeAdapter_DV()
        self.wait(5)

        self.Switch_ONN_Relay(4, 5)
        self.Switch_ONN_Relay(4, 6)

        self.wait(7)

        # turn off 4-5 and 4-6 relays
        self.Switch_OFF_Relay(4, 5)
        self.Switch_OFF_Relay(4, 6)

        # Reading Recovery ID's from the Adapter EEPROM And Adapter Onewire
        self.GetRecoveryIDData()
        self.wait(2)

        self.Connect_Adapter()
        self.wait(15)

        # Press and Hold Open Key for
        # - No Staple Detect State Exit, And
        # - Fully opened
        # - SSE Screen Display
        self.Switch_ONN_Relay(2,4)
        self.wait(15)
        self.Switch_OFF_Relay(2,4)

        self.Switch_ONN_Relay(2, 4)
        self.wait(20)
        self.Switch_OFF_Relay(2, 4)

        # Remove EEA Reload
        self.DisconnectingEEAReload(exit_video=False)
        self.wait(1)

        self.apply_load_force(0)

        # Perform Surgical Site Extraction Operation
        self.EEASurgicalSiteExtractionStateExit()
        self.wait(4)

        # Remove Adapter
        self.removeAdapter_DV()
        self.wait(3)

        # Read Adapter Usage Counts from EEPROM and One-wire NVM Flash
        self.Switch_ONN_Relay(1, 8)
        self.wait(5)

        MCPThread.readingPowerPack.exitFlag = True
        self.wait(2)

        # Reading Adapter EEPROM Usage Counts
        AdapterEEPROMProcedureCount, AdapterEEPROMFireCount =  GetAdapterEepromUsageCounts(self.FtdiUartComPort)

        # Reading Adapter Onewire Usage Counts
        AdapterOwFireCount, AdapterOwProcedureCount = self.GetAdapterNvmUsageCounts()

        print(f"Adapter EEPROM,  Fire Count: {AdapterEEPROMFireCount}, Procedure Count: {AdapterEEPROMProcedureCount}")
        print(f"Adapter Onewire, Fire Count: {AdapterOwFireCount}, Procedure Count: {AdapterOwProcedureCount}")

    def EEAFiring_Cutting_Recovery_Exit_State(self, logs_to_compare='EEA Firing'):
        self.output_on_off(True, self.DcPowerSupplyComPort)
        self.applyLoadViaVoltage(4, self.DcPowerSupplyComPort)

        # turn on 4-1 and 4-2 relays
        self.Switch_ONN_Relay(4, 1)
        self.Switch_ONN_Relay(4, 2)

        self.wait(1)

        # turn off 4-1 and 4-2
        self.Switch_OFF_Relay(4, 1)
        self.Switch_OFF_Relay(4, 2)

        self.applyLoadViaVoltage(5.5, self.DcPowerSupplyComPort)
        self.wait(1)

        # turn on 4-1 and 4-2 relays
        self.Switch_ONN_Relay(4, 1)
        self.Switch_ONN_Relay(4, 2)

        self.wait(3)

        # press close key
        self.Switch_ONN_Relay(2, 5)
        time.sleep(0.5)
        self.Switch_OFF_Relay(2, 5)

        string_to_found = 'GUI_NewState: EEA_STAPLE_26_38'
        self.my_Serthread.waitUntilString(string_to_found, timeout=10)
        # turn off 4-1 and 4-2
        self.Switch_OFF_Relay(4, 1)
        self.Switch_OFF_Relay(4, 2)

        # turn on 4-5 and 4-6 relays
        self.Switch_ONN_Relay(4, 5)
        self.Switch_ONN_Relay(4, 6)

        self.wait(2)

        # turn off 4-5 and 4-6 relays
        self.Switch_OFF_Relay(4, 5)
        self.Switch_OFF_Relay(4, 6)

        string_to_found = 'GUI_NewState: EEA_CUT_70'
        self.my_Serthread.waitUntilString(string_to_found, timeout=10)

        self.removeAdapter_DV()
        self.wait(10)

        # Reading Recovery ID's from the Adapter EEPROM And Adapter Onewire
        self.GetRecoveryIDData()
        self.wait(2)

        self.Connect_Adapter()
        self.wait(15)

        # Press and Hold Open Key for
        # - No Staple Detect State Exit, And
        # - Fully opened
        # - SSE Screen Display
        self.Switch_ONN_Relay(2, 4)
        self.wait(10)
        self.Switch_OFF_Relay(2, 4)

        self.Switch_ONN_Relay(2, 4)
        self.wait(20)
        self.Switch_OFF_Relay(2, 4)

        # Remove EEA Reload
        self.DisconnectingEEAReload(exit_video=False)
        self.wait(1)

        # Perform Surgical Site Extraction Operation
        self.EEASurgicalSiteExtractionStateExit()
        self.wait(2)

        # Remove Adapter
        self.removeAdapter_DV()
        self.wait(4)

        # Read Adapter Usage Counts in EEPROM and One-wire NVM Flash
        self.Switch_ONN_Relay(1, 8)
        self.wait(5)

        MCPThread.readingPowerPack.exitFlag = True
        self.wait(2)

        # Reading Adapter EEPROM Usage Counts
        AdapterEEPROMProcedureCount, AdapterEEPROMFireCount = GetAdapterEepromUsageCounts(self.FtdiUartComPort)

        # Reading Adapter Onewire Usage Counts
        AdapterOwFireCount, AdapterOwProcedureCount = self.GetAdapterNvmUsageCounts()

        print(f"Adapter EEPROM,  Fire Count: {AdapterEEPROMFireCount}, Procedure Count: {AdapterEEPROMProcedureCount}")
        print(f"Adapter Onewire, Fire Count: {AdapterOwFireCount}, Procedure Count: {AdapterOwProcedureCount}")

        self.output_on_off(False, self.DcPowerSupplyComPort)
    def EEAFiring_Stapling_Recovery(self, logs_to_compare='EEA Firing'):
        self.output_on_off(True, self.DcPowerSupplyComPort)
        self.applyLoadViaVoltage(4, self.DcPowerSupplyComPort)

        # turn on 4-1 and 4-2 relays
        self.Switch_ONN_Relay(4, 1)
        self.Switch_ONN_Relay(4, 2)

        self.wait(1)

        # turn off 4-1 and 4-2
        self.Switch_OFF_Relay(4, 1)
        self.Switch_OFF_Relay(4, 2)

        self.applyLoadViaVoltage(5.5, self.DcPowerSupplyComPort)
        self.wait(1)


        # turn on 4-1 and 4-2 relays
        self.Switch_ONN_Relay(4, 1)
        self.Switch_ONN_Relay(4, 2)

        self.wait(4)

        # press close key
        self.Switch_ONN_Relay(2, 5)
        time.sleep(0.5)
        self.Switch_OFF_Relay(2, 5)


        string_to_found = 'GUI_NewState: EEA_STAPLE_11_25'
        self.my_Serthread.waitUntilString(string_to_found, timeout=10)
        # turn off 4-1 and 4-2
        self.Switch_OFF_Relay(4, 1)
        self.Switch_OFF_Relay(4, 2)

        # Detach the Adapter - Prior to staple complete
        self.removeAdapter_DV()
        self.wait(5)

        self.Switch_ONN_Relay(4, 5)
        self.Switch_ONN_Relay(4, 6)

        self.wait(7)

        # turn off 4-5 and 4-6 relays
        self.Switch_OFF_Relay(4, 5)
        self.Switch_OFF_Relay(4, 6)

        # Connect Adapter
        self.Connect_Adapter()
        self.wait(15)

        # Green Key Acknowledgement
        self.Switch_ONN_Relay(3,5)
        self.wait(0.5)
        self.Switch_OFF_Relay(3,5)
        self.wait(15)

        self.EEAFiring(fire_force=None)

        self.output_on_off(False, self.DcPowerSupplyComPort)

    def EEAFiring_Cutting_Recovery(self, logs_to_compare='EEA Firing'):
        self.output_on_off(True, self.DcPowerSupplyComPort)
        self.applyLoadViaVoltage(4, self.DcPowerSupplyComPort)

        # turn on 4-1 and 4-2 relays
        self.Switch_ONN_Relay(4, 1)
        self.Switch_ONN_Relay(4, 2)

        self.wait(1)

        # turn off 4-1 and 4-2
        self.Switch_OFF_Relay(4, 1)
        self.Switch_OFF_Relay(4, 2)

        self.applyLoadViaVoltage(5.5, self.DcPowerSupplyComPort)
        self.wait(1)

        # turn on 4-1 and 4-2 relays
        self.Switch_ONN_Relay(4, 1)
        self.Switch_ONN_Relay(4, 2)

        self.wait(3)

        # press close key
        self.Switch_ONN_Relay(2, 5)
        time.sleep(0.5)
        self.Switch_OFF_Relay(2, 5)

        string_to_found = 'GUI_NewState: EEA_STAPLE_26_38'
        self.my_Serthread.waitUntilString(string_to_found, timeout=10)
        # turn off 4-1 and 4-2
        self.Switch_OFF_Relay(4, 1)
        self.Switch_OFF_Relay(4, 2)

        # turn on 4-5 and 4-6 relays
        self.Switch_ONN_Relay(4, 5)
        self.Switch_ONN_Relay(4, 6)

        self.wait(2)

        # turn off 4-5 and 4-6 relays
        self.Switch_OFF_Relay(4, 5)
        self.Switch_OFF_Relay(4, 6)

        string_to_found = 'GUI_NewState: EEA_CUT_70'
        self.my_Serthread.waitUntilString(string_to_found, timeout=10)

        self.removeAdapter_DV()
        self.wait(10)

        self.Connect_Adapter()
        self.wait(15)

        # self.GreenKeyAck_400860()
        self.Switch_ONN_Relay(3, 5)
        self.wait(0.5)
        self.Switch_OFF_Relay(3, 5)
        self.wait(15)

        self.apply_load_force(0)

        self.applyLoadViaVoltage(9, self.DcPowerSupplyComPort)
        # press close key
        self.Switch_ONN_Relay(2, 5)
        time.sleep(0.5)
        self.Switch_OFF_Relay(2, 5)

        # turn on 4-1 and 4-2 relays
        self.Switch_ONN_Relay(4, 1)
        self.Switch_ONN_Relay(4, 2)

        print(f"finding: GUI_NewState: EEA_CUT_70")
        string_to_found = 'GUI_NewState: EEA_CUT_70'
        self.my_Serthread.waitUntilString(string_to_found, timeout=20)

        self.Switch_OFF_Relay(4, 1)
        self.Switch_OFF_Relay(4, 2)

        self.Switch_ONN_Relay(4, 5)
        self.Switch_ONN_Relay(4, 6)

        self.wait(4)

        # turn off 4-5 and 4-6 relays
        self.Switch_OFF_Relay(4, 5)
        self.Switch_OFF_Relay(4, 6)

        self.output_on_off(False, self.DcPowerSupplyComPort)

    def EEA_Multiple_Recovery_Firing(self, logs_to_compare='EEA Firing'):
        self.output_on_off(True, self.DcPowerSupplyComPort)
        self.applyLoadViaVoltage(4, self.DcPowerSupplyComPort)

        # turn on 4-1 and 4-2 relays
        self.Switch_ONN_Relay(4, 1)
        self.Switch_ONN_Relay(4, 2)

        self.wait(1)

        # turn off 4-1 and 4-2
        self.Switch_OFF_Relay(4, 1)
        self.Switch_OFF_Relay(4, 2)

        self.applyLoadViaVoltage(5.5, self.DcPowerSupplyComPort)
        self.wait(1)


        # turn on 4-1 and 4-2 relays
        self.Switch_ONN_Relay(4, 1)
        self.Switch_ONN_Relay(4, 2)

        self.wait(4)

        # press close key
        self.Switch_ONN_Relay(2, 5)
        time.sleep(0.5)
        self.Switch_OFF_Relay(2, 5)


        string_to_found = 'GUI_NewState: EEA_STAPLE_11_25'
        self.my_Serthread.waitUntilString(string_to_found, timeout=10)
        # turn off 4-1 and 4-2
        self.Switch_OFF_Relay(4, 1)
        self.Switch_OFF_Relay(4, 2)

        self.removeAdapter_DV()
        self.wait(5)

        self.Switch_ONN_Relay(4, 5)
        self.Switch_ONN_Relay(4, 6)

        self.wait(7)

        # turn off 4-5 and 4-6 relays
        self.Switch_OFF_Relay(4, 5)
        self.Switch_OFF_Relay(4, 6)

        # Detach the Adapter - Prior to staple complete
        self.Connect_Adapter()
        self.wait(15)

        # self.GreenKeyAck_400860()
        self.Switch_ONN_Relay(3,5)
        self.wait(0.5)
        self.Switch_OFF_Relay(3,5)
        self.wait(15)

        string_to_found = ''
        self.applyLoadViaVoltage(4, self.DcPowerSupplyComPort)

        # turn on 4-1 and 4-2 relays
        self.Switch_ONN_Relay(4, 1)
        self.Switch_ONN_Relay(4, 2)

        # self.wait_till_reach_peak_load(15)
        self.wait(1)

        # turn off 4-1 and 4-2
        self.Switch_OFF_Relay(4, 1)
        self.Switch_OFF_Relay(4, 2)

        self.applyLoadViaVoltage(5.5, self.DcPowerSupplyComPort)
        self.wait(1)

        # turn on 4-1 and 4-2 relays
        self.Switch_ONN_Relay(4, 1)
        self.Switch_ONN_Relay(4, 2)

        self.wait(4)

        # press close key
        self.Switch_ONN_Relay(2, 5)
        time.sleep(0.5)
        self.Switch_OFF_Relay(2, 5)

        string_to_found = 'GUI_NewState: EEA_STAPLE_26_38'
        self.my_Serthread.waitUntilString(string_to_found, timeout=10)
        # turn off 4-1 and 4-2
        self.Switch_OFF_Relay(4, 1)
        self.Switch_OFF_Relay(4, 2)
        # self.applyLoadViaVoltage(9, self.DcPowerSupplyComPort)
        # turn on 4-5 and 4-6 relays
        self.Switch_ONN_Relay(4, 5)
        self.Switch_ONN_Relay(4, 6)

        self.wait(2)

        # turn off 4-5 and 4-6 relays
        self.Switch_OFF_Relay(4, 5)
        self.Switch_OFF_Relay(4, 6)

        """"""""""""""""""""""Cut Recovery """""''''''''''''''''''
        string_to_found = 'GUI_NewState: EEA_CUT_70'
        self.my_Serthread.waitUntilString(string_to_found, timeout=10)

        self.removeAdapter_DV()
        self.wait(10)

        self.Connect_Adapter()
        self.wait(13)

        self.Switch_ONN_Relay(4, 5)
        self.Switch_ONN_Relay(4, 6)

        self.wait(2)

        # turn off 4-5 and 4-6 relays
        self.Switch_OFF_Relay(4, 5)
        self.Switch_OFF_Relay(4, 6)

        # self.GreenKeyAck_400860()
        self.Switch_ONN_Relay(3, 5)
        self.wait(0.5)
        self.Switch_OFF_Relay(3, 5)
        self.wait(15)

        self.apply_load_force(0)

        self.applyLoadViaVoltage(9, self.DcPowerSupplyComPort)
        # press close key
        self.Switch_ONN_Relay(2, 5)
        time.sleep(0.5)
        self.Switch_OFF_Relay(2, 5)

        # turn on 4-1 and 4-2 relays
        self.Switch_ONN_Relay(4, 1)
        self.Switch_ONN_Relay(4, 2)

        print(f"finding: GUI_NewState: EEA_CUT_70")
        string_to_found = 'GUI_NewState: EEA_CUT_70'
        self.my_Serthread.waitUntilString(string_to_found, timeout=20)

        self.Switch_OFF_Relay(4, 1)
        self.Switch_OFF_Relay(4, 2)

        self.Switch_ONN_Relay(4, 5)
        self.Switch_ONN_Relay(4, 6)

        self.wait(7)

        # turn off 4-5 and 4-6 relays
        self.Switch_OFF_Relay(4, 5)
        self.Switch_OFF_Relay(4, 6)

        self.output_on_off(False, self.DcPowerSupplyComPort)

    def EEA_DV_Firing_400860(self, logs_to_compare='EEA Firing'):
        # fire_success_flag = True
        #
        # # Apply Voltage Instead of Applying Load Force
        # self.output_on_off(True, self.DcPowerSupplyComPort)
        # self.applyLoadViaVoltage(5, self.DcPowerSupplyComPort)
        # self.my_Serthread.clearQue()
        #
        # # 5.1.19.	Press the down toggle to initiate firing.
        # # Prior to staple complete (within a few seconds), detach the adapter from the clamshell.
        # self.Switch_ONN_Relay(Bank_number=self.EEA_STAPLING_ONE_bank_number,
        #                       Relay_number=self.EEA_STAPLING_ONE_relay_number)  # B4:R1 - ON
        # self.Switch_ONN_Relay(Bank_number=self.EEA_STAPLING_TWO_bank_number,
        #                       Relay_number=self.EEA_STAPLING_TWO_relay_number)  # B4:R2 - ON
        # self.wait(4.5)#3)
        # self.Switch_ONN_Relay(Bank_number=self.FIRING_bank_number, Relay_number=self.FIRING_relay_number)  # B2:R5 - ON
        # self.wait(0.5)
        # self.Switch_OFF_Relay(Bank_number=self.FIRING_bank_number, Relay_number=self.FIRING_relay_number)  # B2:R5 - OFF
        # self.wait(2)
        # self.Switch_OFF_Relay(Bank_number=self.EEA_STAPLING_ONE_bank_number,
        #                       Relay_number=self.EEA_STAPLING_ONE_relay_number)  # B4:R1 - OFF
        # self.Switch_OFF_Relay(Bank_number=self.EEA_STAPLING_TWO_bank_number,
        #                       Relay_number=self.EEA_STAPLING_TWO_relay_number)  # B4:R2 - OFF
        #
        # self.wait(1)
        #
        # # Detach the Adapter - Prior to staple complete
        # self.removeAdapter_DV()
        # self.wait(15)
        #
        # # 5.1.20.	Wait a few seconds and then reattach adapter to clamshell.
        # # Wait for the timer to complete and confirm that the handle indicates to resume stapling (249786).
        # '''249786	The HANDLE shall indicate for USER to resume stapling
        # when PEEA_ADAPTER is attached after initiating staple fire and prior to staple complete.'''
        # self.Connect_Adapter()
        # self.wait(15)
        #
        # # "Screen 5 - Resume Stapling "
        # # screen_name = "Resume_Stapling"
        # # folder_name = "Resume_Stapling"
        # # file_name = "Resume_Stapling"
        # # self.handle_screen(videoPath=self.videoPath, screen_name=screen_name, folder_name=folder_name,
        # #                    file_name=file_name, is_static_image=False)
        #
        # # 5.1.21 Press the green safety button.
        # self.GreenKeyAck_400860()
        # self.wait(15)
        #
        # # 5.1.22. Press the down toggle to resume stapling.
        # self.Switch_ONN_Relay(Bank_number=self.FIRING_bank_number, Relay_number=self.FIRING_relay_number)  # B2:R5 - ON
        # self.wait(.5)
        # self.Switch_OFF_Relay(Bank_number=self.FIRING_bank_number, Relay_number=self.FIRING_relay_number)  # B2:R5 - OFF
        #
        # self.Switch_ONN_Relay(Bank_number=self.EEA_STAPLING_ONE_bank_number,
        #                       Relay_number=self.EEA_STAPLING_ONE_relay_number)  # B4:R1 - ON
        # self.Switch_ONN_Relay(Bank_number=self.EEA_STAPLING_TWO_bank_number,
        #                       Relay_number=self.EEA_STAPLING_TWO_relay_number)  # B4:R2 - ON
        # self.wait(5)
        # self.Switch_OFF_Relay(Bank_number=self.EEA_STAPLING_ONE_bank_number,
        #                       Relay_number=self.EEA_STAPLING_ONE_relay_number)  # B4:R1 - OFF
        # self.Switch_OFF_Relay(Bank_number=self.EEA_STAPLING_TWO_bank_number,
        #                       Relay_number=self.EEA_STAPLING_TWO_relay_number)  # B4:R2 - OFF
        #
        # # self.output_on_off(False, self.DcPowerSupplyComPort)
        # #
        # # self.wait(1)
        # # self.output_on_off(True, self.DcPowerSupplyComPort)
        # self.apply_load_force(0)
        # self.applyLoadViaVoltage(9, self.DcPowerSupplyComPort)
        #
        # self.Switch_ONN_Relay(Bank_number=self.EEA_CUTTING_ONE_bank_number,
        #                       Relay_number=self.EEA_CUTTING_ONE_relay_number)  # B4:R3 - ON
        # self.Switch_ONN_Relay(Bank_number=self.EEA_CUTTING_TWO_bank_number,
        #                       Relay_number=self.EEA_CUTTING_TWO_relay_number)  # B4:R4 - ON
        # self.wait(5)
        #
        # self.Switch_OFF_Relay(Bank_number=self.EEA_CUTTING_ONE_bank_number,
        #                       Relay_number=self.EEA_CUTTING_ONE_relay_number)  # B4:R3 - OFF
        # self.Switch_OFF_Relay(Bank_number=self.EEA_CUTTING_TWO_bank_number,
        #                       Relay_number=self.EEA_CUTTING_TWO_relay_number)  # B4:R4 - OFF
        #
        # # Remove Adapter - Staple complete
        # # 5.1.23. After staple completes and within a few seconds after the start of cut,
        # # detach the adapter from the clamshell.
        # self.removeAdapter_DV()
        # self.wait(15)
        #
        # # 5.1.24. Wait a few seconds and then reattach adapter to a different handle-clamshell system.
        # # Wait for the timer to complete and confirm that the handle indicates to resume cutting (249790, 278486).
        # '''278486	PEEA_SYSTEM shall allow continuation of the PROCEDURE in the event of attachment to a different HANDLE.
        # 249790	The HANDLE shall indicate for USER to resume cutting when PEEA_ADAPTER is attached after initiating cut and prior to cut complete.'''
        # self.Connect_Adapter()
        # self.wait(15)
        #
        # # "Screen 6 - Resume Cutting "
        # # screen_name = "Resume_Cutting"
        # # folder_name = "Resume_Cutting"
        # # file_name = "Resume_Cutting"
        # # self.handle_screen(videoPath=self.videoPath, screen_name=screen_name, folder_name=folder_name,
        # #                    file_name=file_name, is_static_image=False)
        #
        #
        # ###### Added On 13th Nov 24 to apply more force while resuming cut recovery
        # ###### Move the linear actuator before cut resume
        # self.Switch_ONN_Relay(Bank_number=self.EEA_CUTTING_COMPLETE_ONE_bank_number,
        #                       Relay_number=self.EEA_CUTTING_COMPLETE_ONE_relay_number)  # B4:R5 - ON
        # self.Switch_ONN_Relay(Bank_number=self.EEA_CUTTING_COMPLETE_TWO_bank_number,
        #                       Relay_number=self.EEA_CUTTING_COMPLETE_TWO_relay_number)  # B4:R6 - ON
        # self.wait(2)
        # self.Switch_OFF_Relay(Bank_number=self.EEA_CUTTING_COMPLETE_ONE_bank_number,
        #                       Relay_number=self.EEA_CUTTING_COMPLETE_ONE_relay_number)  # B4:R5 - OFF
        # self.Switch_OFF_Relay(Bank_number=self.EEA_CUTTING_COMPLETE_TWO_bank_number,
        #                       Relay_number=self.EEA_CUTTING_COMPLETE_TWO_relay_number)  # B4:R6 - OFF
        #
        #
        # # 5.1.25. Press the green safety button.
        # self.GreenKeyAck_400860()
        # self.wait(15)
        #
        # self.Switch_ONN_Relay(Bank_number=self.EEA_CUTTING_ONE_bank_number,
        #                       Relay_number=self.EEA_CUTTING_ONE_relay_number)  # B4:R3 - ON
        # self.Switch_ONN_Relay(Bank_number=self.EEA_CUTTING_TWO_bank_number,
        #                       Relay_number=self.EEA_CUTTING_TWO_relay_number)  # B4:R4 - ON
        #
        # # 5.1.26. Press the down toggle to resume cutting.
        # self.Switch_ONN_Relay(2, 5)
        # self.wait(.5)
        # self.Switch_OFF_Relay(2, 5)
        # self.wait(2)
        #
        # # self.applyLoadViaVoltage(0, self.DcPowerSupplyComPort)
        #
        # # self.wait(3)
        # self.Switch_OFF_Relay(Bank_number=self.EEA_CUTTING_ONE_bank_number,
        #                       Relay_number=self.EEA_CUTTING_ONE_relay_number)  # B4:R3 - OFF
        # self.Switch_OFF_Relay(Bank_number=self.EEA_CUTTING_TWO_bank_number,
        #                       Relay_number=self.EEA_CUTTING_TWO_relay_number)  # B4:R4 - OFF
        # self.wait(.5)
        #
        # self.Switch_ONN_Relay(Bank_number=self.EEA_CUTTING_COMPLETE_ONE_bank_number,
        #                       Relay_number=self.EEA_CUTTING_COMPLETE_ONE_relay_number)  # B4:R5 - ON
        # self.Switch_ONN_Relay(Bank_number=self.EEA_CUTTING_COMPLETE_TWO_bank_number,
        #                       Relay_number=self.EEA_CUTTING_COMPLETE_TWO_relay_number)  # B4:R6 - ON
        # self.wait(30)
        # self.compare_logs(logs_to_compare, SuccessFlag=fire_success_flag, is_firing_test=True)
        # print(f'STEP : {logs_to_compare} performed!')
        # self.Switch_OFF_Relay(Bank_number=self.EEA_CUTTING_COMPLETE_ONE_bank_number,
        #                       Relay_number=self.EEA_CUTTING_COMPLETE_ONE_relay_number)  # B4:R5 - OFF
        # self.Switch_OFF_Relay(Bank_number=self.EEA_CUTTING_COMPLETE_TWO_bank_number,
        #                       Relay_number=self.EEA_CUTTING_COMPLETE_TWO_relay_number)  # B4:R6 - OFF
        #
        # self.output_on_off(False, self.DcPowerSupplyComPort)
        self.output_on_off(True, self.DcPowerSupplyComPort)
        self.applyLoadViaVoltage(4, self.DcPowerSupplyComPort)

        # turn on 4-1 and 4-2 relays
        self.Switch_ONN_Relay(4, 1)
        self.Switch_ONN_Relay(4, 2)

        self.wait(1)

        # turn off 4-1 and 4-2
        self.Switch_OFF_Relay(4, 1)
        self.Switch_OFF_Relay(4, 2)

        self.applyLoadViaVoltage(5.5, self.DcPowerSupplyComPort)  # VMK changed to 5.5 from 7

        # turn on 4-1 and 4-2 relays
        self.Switch_ONN_Relay(4, 1)
        self.Switch_ONN_Relay(4, 2)

        self.wait(3)

        # press close key
        self.Switch_ONN_Relay(2, 5)
        time.sleep(0.5)
        self.Switch_OFF_Relay(2, 5)

        self.wait(1)

        # turn off 4-1 and 4-2
        self.Switch_OFF_Relay(4, 1)
        self.Switch_OFF_Relay(4, 2)

        # Detach the Adapter - Prior to staple complete
        self.removeAdapter_DV()
        self.wait(15)

        self.Connect_Adapter()
        self.wait(15)

        self.GreenKeyAck_400860()
        self.wait(10)

        # self.Switch_ONN_Relay(4, 5)
        # self.Switch_ONN_Relay(4, 6)
        #
        # self.wait(1)
        #
        # # turn off 4-5 and 4-6 relays
        # self.Switch_OFF_Relay(4, 5)
        # self.Switch_OFF_Relay(4, 6)
        # turn on 4-1 and 4-2 relays
        self.Switch_ONN_Relay(4, 1)
        self.Switch_ONN_Relay(4, 2)

        # press close key
        self.Switch_ONN_Relay(2, 5)
        time.sleep(0.5)
        self.Switch_OFF_Relay(2, 5)

        self.wait(3)

        # turn off 4-1 and 4-2
        self.Switch_OFF_Relay(4, 1)
        self.Switch_OFF_Relay(4, 2)

        self.Switch_ONN_Relay(4, 5)
        self.Switch_ONN_Relay(4, 6)

        self.wait(1)

        # turn off 4-5 and 4-6 relays
        self.Switch_OFF_Relay(4, 5)
        self.Switch_OFF_Relay(4, 6)

        self.applyLoadViaVoltage(9, self.DcPowerSupplyComPort)

        # turn on 4-1 and 4-2 relays
        self.Switch_ONN_Relay(4, 1)
        self.Switch_ONN_Relay(4, 2)

        self.apply_load_force(0)

        self.wait(1)

        # turn off 4-1 and 4-2
        self.Switch_OFF_Relay(4, 1)
        self.Switch_OFF_Relay(4, 2)

        # Detach the Adapter - Prior to staple complete
        self.removeAdapter_DV()
        self.wait(15)

        self.Connect_Adapter()
        self.wait(15)

        self.GreenKeyAck_400860()
        self.wait(10)

        # press close key
        self.Switch_ONN_Relay(2, 5)
        time.sleep(0.5)
        self.Switch_OFF_Relay(2, 5)

        # turn on 4-1 and 4-2 relays
        self.Switch_ONN_Relay(4, 1)
        self.Switch_ONN_Relay(4, 2)

        self.wait(4)

        # turn off 4-1 and 4-2
        self.Switch_OFF_Relay(4, 1)
        self.Switch_OFF_Relay(4, 2)

        # turn on 4-5 and 4-6 relays
        self.Switch_ONN_Relay(4, 5)
        self.Switch_ONN_Relay(4, 6)

        self.wait(5)

        # turn off 4-5 and 4-6 relays
        self.Switch_OFF_Relay(4, 5)
        self.Switch_OFF_Relay(4, 6)

    def EEA_DV_Firing_Staple_Missing_359465(self, logs_to_compare='EEA Firing'):
        fire_success_flag = True

        # Apply Voltage Instead of Applying Load Force
        self.output_on_off(True, self.DcPowerSupplyComPort)
        self.applyLoadViaVoltage(4, self.DcPowerSupplyComPort)

        self.Switch_ONN_Relay(Bank_number=self.EEA_STAPLING_ONE_bank_number,
                              Relay_number=self.EEA_STAPLING_ONE_relay_number)  # B4:R1 - ON
        self.Switch_ONN_Relay(Bank_number=self.EEA_STAPLING_TWO_bank_number,
                              Relay_number=self.EEA_STAPLING_TWO_relay_number)  # B4:R2 - ON
        self.wait(3)
        # 5.2.11. Press the bottom toggle button once to fire.
        self.Switch_ONN_Relay(Bank_number=self.FIRING_bank_number, Relay_number=self.FIRING_relay_number)  # B2:R5 - ON
        self.wait(0.5)
        self.Switch_OFF_Relay(Bank_number=self.FIRING_bank_number, Relay_number=self.FIRING_relay_number)  # B2:R5 - OFF

        self.Switch_OFF_Relay(Bank_number=self.EEA_STAPLING_ONE_bank_number,
                              Relay_number=self.EEA_STAPLING_ONE_relay_number)  # B4:R1 - OFF
        self.Switch_OFF_Relay(Bank_number=self.EEA_STAPLING_TWO_bank_number,
                              Relay_number=self.EEA_STAPLING_TWO_relay_number)  # B4:R2 - OFF
        # 5.2.12. Confirm that the device displays the “no staples” error and goes into
        # “surgical site extraction” mode where the only available function is to extend the trocar.
        screen_name = "No_Staples_Error"
        folder_name = "No_Staples_Error"
        file_name = "No_Staples_Error"
        self.handle_screen(videoPath=self.videoPath, screen_name=screen_name, folder_name=folder_name,
                           file_name=file_name, is_static_image=False)
        self.wait(5)

        # 5.2.13. Press and hold the up toggle to fully extend the trocar and remove the anvil and reload (254821).
        # 5.2.14. Confirm that the handle indicates to hold the four rotate keys to reset the adapter (254823).
        # Press and hold up toggle button to enter SSE
        self.Switch_ONN_Relay(Bank_number=self.RETRACT_bank_number,
                              Relay_number=self.RETRACT_relay_number)  # B2:R4 - ON

        screen_name = "SSE"
        folder_name = "SSE"
        file_name = "SSE"
        self.handle_screen(videoPath=self.videoPath, screen_name=screen_name, folder_name=folder_name,
                           file_name=file_name, is_static_image=False)

        self.wait(20)
        self.Switch_OFF_Relay(Bank_number=self.RETRACT_bank_number,
                              Relay_number=self.RETRACT_relay_number)  # B2:R4 - OFF

        # Remove Anvil, red foam and reload.
        self.DisconnectingEEAReload(exit_video=False)

        #########################################################
        ## Remove Load ( Applied during Clamping )
        #########################################################
        self.apply_load_force(0)
        self.wait(10)

        ## 5.2.15. Hold the four rotate keys and observe the countdown (254819).
        # Continue to hold until the adapter is reset.
        self.Switch_ONN_Relay(Bank_number=self.LCW_ROTATION_bank_number,
                              Relay_number=self.LCW_ROTATION_relay_number)  # B2:R1 - ON
        self.Switch_ONN_Relay(Bank_number=self.LCCW_ROTATION_bank_number,
                              Relay_number=self.LCCW_ROTATION_relay_number)  # B2:R2 - ON
        self.Switch_ONN_Relay(Bank_number=self.RCW_ROTATION_bank_number,
                              Relay_number=self.RCW_ROTATION_relay_number)  # B2:R7 - ON
        self.Switch_ONN_Relay(Bank_number=self.RCCW_ROTATION_bank_number,
                              Relay_number=self.RCCW_ROTATION_relay_number)  # B2:R8 - ON
        self.wait(30)
        self.Switch_OFF_Relay(Bank_number=self.LCW_ROTATION_bank_number,
                              Relay_number=self.LCW_ROTATION_relay_number)  # B2:R1 - OFF
        self.Switch_OFF_Relay(Bank_number=self.LCCW_ROTATION_bank_number,
                              Relay_number=self.LCCW_ROTATION_relay_number)  # B2:R2 - OFF
        self.Switch_OFF_Relay(Bank_number=self.RCW_ROTATION_bank_number,
                              Relay_number=self.RCW_ROTATION_relay_number)  # B2:R7 - OFF
        self.Switch_OFF_Relay(Bank_number=self.RCCW_ROTATION_bank_number,
                              Relay_number=self.RCCW_ROTATION_relay_number)  # B2:R8 - OFF

        self.output_on_off(False, self.DcPowerSupplyComPort)

    def EEA_DV_Firing_Knife_Missing_359465(self, logs_to_compare='EEA Firing'):
        fire_success_flag = True

        # Apply Voltage Instead of Applying Load Force
        self.output_on_off(True, self.DcPowerSupplyComPort)
        # turn on 4-1 and 4-2 relays
        self.Switch_ONN_Relay(4, 1)
        self.Switch_ONN_Relay(4, 2)

        self.wait(1)

        # turn off 4-1 and 4-2
        self.Switch_OFF_Relay(4, 1)
        self.Switch_OFF_Relay(4, 2)

        self.applyLoadViaVoltage(5.5, self.DcPowerSupplyComPort)
        self.wait(1)

        self.Switch_ONN_Relay(Bank_number=self.EEA_STAPLING_ONE_bank_number,
                              Relay_number=self.EEA_STAPLING_ONE_relay_number)  # B4:R1 - ON
        self.Switch_ONN_Relay(Bank_number=self.EEA_STAPLING_TWO_bank_number,
                              Relay_number=self.EEA_STAPLING_TWO_relay_number)  # B4:R2 - ON
        self.wait(4)
        # 5.3.11. Press the bottom toggle button once to fire.
        self.Switch_ONN_Relay(Bank_number=self.FIRING_bank_number, Relay_number=self.FIRING_relay_number)  # B2:R5 - ON
        self.wait(0.5)
        self.Switch_OFF_Relay(Bank_number=self.FIRING_bank_number, Relay_number=self.FIRING_relay_number)  # B2:R5 - OFF

        string_to_found = 'GUI_NewState: EEA_STAPLE_26_38'
        self.my_Serthread.waitUntilString(string_to_found, timeout=10)

        self.Switch_OFF_Relay(Bank_number=self.EEA_STAPLING_ONE_bank_number,
                              Relay_number=self.EEA_STAPLING_ONE_relay_number)  # B4:R1 - OFF
        self.Switch_OFF_Relay(Bank_number=self.EEA_STAPLING_TWO_bank_number,
                              Relay_number=self.EEA_STAPLING_TWO_relay_number)  # B4:R2 - OFF


        # turn on 4-5 and 4-6 relays
        self.Switch_ONN_Relay(4, 5)
        self.Switch_ONN_Relay(4, 6)

        self.wait(2)

        # turn off 4-5 and 4-6 relays
        self.Switch_OFF_Relay(4, 5)
        self.Switch_OFF_Relay(4, 6)

        self.applyLoadViaVoltage(9, self.DcPowerSupplyComPort)

        ## Cutting Relays Switched ON
        self.Switch_ONN_Relay(Bank_number=self.EEA_CUTTING_ONE_bank_number,
                              Relay_number=self.EEA_CUTTING_ONE_relay_number)  # B4:R3 - ON
        self.Switch_ONN_Relay(Bank_number=self.EEA_CUTTING_TWO_bank_number,
                              Relay_number=self.EEA_CUTTING_TWO_relay_number)  # B4:R4 - ON
        self.wait(2)
        self.Switch_OFF_Relay(Bank_number=self.EEA_CUTTING_ONE_bank_number,
                              Relay_number=self.EEA_CUTTING_ONE_relay_number)  # B4:R3 - OFF
        self.Switch_OFF_Relay(Bank_number=self.EEA_CUTTING_TWO_bank_number,
                              Relay_number=self.EEA_CUTTING_TWO_relay_number)  # B4:R4 - OFF

        # 5.3.12. Confirm that the device displays the “no knife” error and goes into “surgical site extraction”
        # mode where the only available function is to extend the trocar.
        screen_name = "No_Knife_Error"
        folder_name = "No_Knife_Error"
        file_name = "No_Knife_Error"
        self.handle_screen(videoPath=self.videoPath, screen_name=screen_name, folder_name=folder_name,
                           file_name=file_name, is_static_image=False)
        self.wait(5)

        # 5.3.13. Press the up toggle to extend the trocar just far enough to be able to remove the anvil.
        # DO NOT fully extend the trocar (254821).
        self.Switch_ONN_Relay(Bank_number=self.RETRACT_bank_number,
                              Relay_number=self.RETRACT_relay_number)  # B2:R4 - ON

        screen_name = "SSE"
        folder_name = "SSE"
        file_name = "SSE"
        self.handle_screen(videoPath=self.videoPath, screen_name=screen_name, folder_name=folder_name,
                           file_name=file_name, is_static_image=False)

        self.wait(20)
        self.Switch_OFF_Relay(Bank_number=self.RETRACT_bank_number,
                              Relay_number=self.RETRACT_relay_number)  # B2:R4 - OFF

        # 5.3.14. Remove the anvil and reload.
        self.DisconnectingEEAReload(exit_video=False)

        #########################################################
        ## Remove Load ( Applied during Clamping )
        #########################################################
        self.apply_load_force(0)
        self.wait(10)

        # 5.3.15. Confirm that the handle indicates to hold the four rotate keys
        # to reset the adapter (254823).
        self.Switch_ONN_Relay(Bank_number=self.LCW_ROTATION_bank_number,
                              Relay_number=self.LCW_ROTATION_relay_number)  # B2:R1 - ON
        self.Switch_ONN_Relay(Bank_number=self.LCCW_ROTATION_bank_number,
                              Relay_number=self.LCCW_ROTATION_relay_number)  # B2:R2 - ON
        self.Switch_ONN_Relay(Bank_number=self.RCW_ROTATION_bank_number,
                              Relay_number=self.RCW_ROTATION_relay_number)  # B2:R7 - ON
        self.Switch_ONN_Relay(Bank_number=self.RCCW_ROTATION_bank_number,
                              Relay_number=self.RCCW_ROTATION_relay_number)  # B2:R8 - ON
        self.wait(30)
        self.Switch_OFF_Relay(Bank_number=self.LCW_ROTATION_bank_number,
                              Relay_number=self.LCW_ROTATION_relay_number)  # B2:R1 - OFF
        self.Switch_OFF_Relay(Bank_number=self.LCCW_ROTATION_bank_number,
                              Relay_number=self.LCCW_ROTATION_relay_number)  # B2:R2 - OFF
        self.Switch_OFF_Relay(Bank_number=self.RCW_ROTATION_bank_number,
                              Relay_number=self.RCW_ROTATION_relay_number)  # B2:R7 - OFF
        self.Switch_OFF_Relay(Bank_number=self.RCCW_ROTATION_bank_number,
                              Relay_number=self.RCCW_ROTATION_relay_number)  # B2:R8 - OFF

        self.output_on_off(False, self.DcPowerSupplyComPort)

    def EEA_DV_Firing_Maximum_Cut_Force_359465(self, logs_to_compare='EEA Firing'):
        fire_success_flag = True

        # Apply Voltage Instead of Applying Load Force
        self.output_on_off(True, self.DcPowerSupplyComPort)
        self.applyLoadViaVoltage(4, self.DcPowerSupplyComPort)

        # turn on 4-1 and 4-2 relays
        self.Switch_ONN_Relay(4, 1)
        self.Switch_ONN_Relay(4, 2)

        # self.wait_till_reach_peak_load(15)
        self.wait(1)

        # turn off 4-1 and 4-2
        self.Switch_OFF_Relay(4, 1)
        self.Switch_OFF_Relay(4, 2)

        self.applyLoadViaVoltage(5.5, self.DcPowerSupplyComPort)
        self.wait(1)

        self.Switch_ONN_Relay(Bank_number=self.EEA_STAPLING_ONE_bank_number,
                              Relay_number=self.EEA_STAPLING_ONE_relay_number)  # B4:R1 - ON
        self.Switch_ONN_Relay(Bank_number=self.EEA_STAPLING_TWO_bank_number,
                              Relay_number=self.EEA_STAPLING_TWO_relay_number)  # B4:R2 - ON
        self.wait(4)
        # 5.4.11. Press the bottom toggle button once to fire.
        self.Switch_ONN_Relay(Bank_number=self.FIRING_bank_number, Relay_number=self.FIRING_relay_number)  # B2:R5 - ON
        self.wait(0.5)
        self.Switch_OFF_Relay(Bank_number=self.FIRING_bank_number, Relay_number=self.FIRING_relay_number)  # B2:R5 - OFF

        string_to_found = 'GUI_NewState: EEA_STAPLE_26_38'
        self.my_Serthread.waitUntilString(string_to_found, timeout=10)

        self.Switch_OFF_Relay(Bank_number=self.EEA_STAPLING_ONE_bank_number,
                              Relay_number=self.EEA_STAPLING_ONE_relay_number)  # B4:R1 - OFF
        self.Switch_OFF_Relay(Bank_number=self.EEA_STAPLING_TWO_bank_number,
                              Relay_number=self.EEA_STAPLING_TWO_relay_number)  # B4:R2 - OFF

        self.applyLoadViaVoltage(11, self.DcPowerSupplyComPort)

        self.apply_load_force(0)

        ## Cutting Relays Switched ON
        self.Switch_ONN_Relay(Bank_number=self.EEA_CUTTING_ONE_bank_number,
                              Relay_number=self.EEA_CUTTING_ONE_relay_number)  # B4:R3 - ON
        self.Switch_ONN_Relay(Bank_number=self.EEA_CUTTING_TWO_bank_number,
                              Relay_number=self.EEA_CUTTING_TWO_relay_number)  # B4:R4 - ON
        self.wait(3)
        self.Switch_OFF_Relay(Bank_number=self.EEA_CUTTING_ONE_bank_number,
                              Relay_number=self.EEA_CUTTING_ONE_relay_number)  # B4:R3 - OFF
        self.Switch_OFF_Relay(Bank_number=self.EEA_CUTTING_TWO_bank_number,
                              Relay_number=self.EEA_CUTTING_TWO_relay_number)  # B4:R4 - OFF

        # 5.4.12. Confirm that the device displays the “non-functional cut sequence” error and
        # goes into “surgical site extraction” mode where the only available function is to extend the trocar.
        screen_name = "Non_Functional_Cut_Sequence_Error"
        folder_name = "Non_Functional_Cut_Sequence_Error"
        file_name = "Non_Functional_Cut_Sequence_Error"
        self.handle_screen(videoPath=self.videoPath, screen_name=screen_name, folder_name=folder_name,
                           file_name=file_name, is_static_image=False)
        self.wait(5)

        self.Switch_ONN_Relay(Bank_number=self.EEA_CUTTING_COMPLETE_ONE_bank_number,
                              Relay_number=self.EEA_CUTTING_COMPLETE_ONE_relay_number)  # B4:R5 - ON
        self.Switch_ONN_Relay(Bank_number=self.EEA_CUTTING_COMPLETE_TWO_bank_number,
                              Relay_number=self.EEA_CUTTING_COMPLETE_TWO_relay_number)  # B4:R6 - ON


        # 5.4.13. Extend the trocar to the fully extended position and remove the anvil and reload.
        self.Switch_ONN_Relay(Bank_number=self.RETRACT_bank_number,
                              Relay_number=self.RETRACT_relay_number)  # B2:R4 - ON

        screen_name = "SSE"
        folder_name = "SSE"
        file_name = "SSE"
        self.handle_screen(videoPath=self.videoPath, screen_name=screen_name, folder_name=folder_name,
                           file_name=file_name, is_static_image=False)

        self.wait(20)
        self.Switch_OFF_Relay(Bank_number=self.RETRACT_bank_number,
                              Relay_number=self.RETRACT_relay_number)  # B2:R4 - OFF

        self.DisconnectingEEAReload(exit_video=False)

        #########################################################
        ## Remove Load ( Applied during Clamping )
        #########################################################
        self.apply_load_force(0)
        self.wait(10)

        # 5.4.14. Confirm that the handle indicates to hold the four rotate keys
        # to reset the adapter (254823).
        # 5.4.15. Hold the four rotate keys and observe the countdown (254819).
        # Continue to hold until the adapter resets.
        self.Switch_ONN_Relay(Bank_number=self.LCW_ROTATION_bank_number,
                              Relay_number=self.LCW_ROTATION_relay_number)  # B2:R1 - ON
        self.Switch_ONN_Relay(Bank_number=self.LCCW_ROTATION_bank_number,
                              Relay_number=self.LCCW_ROTATION_relay_number)  # B2:R2 - ON
        self.Switch_ONN_Relay(Bank_number=self.RCW_ROTATION_bank_number,
                              Relay_number=self.RCW_ROTATION_relay_number)  # B2:R7 - ON
        self.Switch_ONN_Relay(Bank_number=self.RCCW_ROTATION_bank_number,
                              Relay_number=self.RCCW_ROTATION_relay_number)  # B2:R8 - ON
        self.wait(30)
        self.Switch_OFF_Relay(Bank_number=self.LCW_ROTATION_bank_number,
                              Relay_number=self.LCW_ROTATION_relay_number)  # B2:R1 - OFF
        self.Switch_OFF_Relay(Bank_number=self.LCCW_ROTATION_bank_number,
                              Relay_number=self.LCCW_ROTATION_relay_number)  # B2:R2 - OFF
        self.Switch_OFF_Relay(Bank_number=self.RCW_ROTATION_bank_number,
                              Relay_number=self.RCW_ROTATION_relay_number)  # B2:R7 - OFF
        self.Switch_OFF_Relay(Bank_number=self.RCCW_ROTATION_bank_number,
                              Relay_number=self.RCCW_ROTATION_relay_number)  # B2:R8 - OFF

        self.output_on_off(False, self.DcPowerSupplyComPort)

    def EEA_DV_firing_460333(self, logs_to_compare='EEA Firing'):
        fire_success_flag = True

        # Apply Voltage Instead of Applying Load Force
        self.output_on_off(True, self.DcPowerSupplyComPort)
        self.applyLoadViaVoltage(5, self.DcPowerSupplyComPort)
        self.my_Serthread.clearQue()
        # self.wait(5)
        # 5.1.19.	Press the down toggle to initiate firing.
        # Prior to staple complete (within a few seconds), detach the adapter from the clamshell.
        self.Switch_ONN_Relay(Bank_number=self.EEA_STAPLING_ONE_bank_number,
                              Relay_number=self.EEA_STAPLING_ONE_relay_number)  # B4:R1 - ON
        self.Switch_ONN_Relay(Bank_number=self.EEA_STAPLING_TWO_bank_number,
                              Relay_number=self.EEA_STAPLING_TWO_relay_number)  # B4:R2 - ON
        self.wait(3)
        self.Switch_ONN_Relay(Bank_number=self.FIRING_bank_number, Relay_number=self.FIRING_relay_number)  # B2:R5 - ON
        self.wait(0.5)
        self.Switch_OFF_Relay(Bank_number=self.FIRING_bank_number, Relay_number=self.FIRING_relay_number)  # B2:R5 - OFF
        self.wait(2)
        self.Switch_OFF_Relay(Bank_number=self.EEA_STAPLING_ONE_bank_number,
                              Relay_number=self.EEA_STAPLING_ONE_relay_number)  # B4:R1 - OFF
        self.Switch_OFF_Relay(Bank_number=self.EEA_STAPLING_TWO_bank_number,
                              Relay_number=self.EEA_STAPLING_TWO_relay_number)  # B4:R2 - OFF

        self.wait(1)
        # Detach the Adapter - Prior to staple complete
        self.removeAdapter_DV()
        self.wait(15)

        # 5.1.20.	Wait a few seconds and then reattach adapter to clamshell.
        # Wait for the timer to complete and confirm that the handle indicates to resume stapling (249786).
        '''249786	The HANDLE shall indicate for USER to resume stapling
        when PEEA_ADAPTER is attached after initiating staple fire and prior to staple complete.'''
        self.Connect_Adapter()
        self.wait(15)

        "Screen 5 - Resume Stapling "
        screen_name = "Resume_Stapling"
        folder_name = "Resume_Stapling"
        file_name = "Resume_Stapling"
        self.handle_screen(videoPath=self.videoPath, screen_name=screen_name, folder_name=folder_name,
                           file_name=file_name, is_static_image=False)

        # 5.1.21 Press the green safety button.
        self.GreenKeyAck_400860()
        self.wait(15)

        # 5.1.22. Press the down toggle to resume stapling.
        self.Switch_ONN_Relay(Bank_number=self.FIRING_bank_number, Relay_number=self.FIRING_relay_number)  # B2:R5 - ON
        self.wait(.5)
        self.Switch_OFF_Relay(Bank_number=self.FIRING_bank_number, Relay_number=self.FIRING_relay_number)  # B2:R5 - OFF

        self.Switch_ONN_Relay(Bank_number=self.EEA_STAPLING_ONE_bank_number,
                              Relay_number=self.EEA_STAPLING_ONE_relay_number)  # B4:R1 - ON
        self.Switch_ONN_Relay(Bank_number=self.EEA_STAPLING_TWO_bank_number,
                              Relay_number=self.EEA_STAPLING_TWO_relay_number)  # B4:R2 - ON
        self.wait(5)
        self.Switch_OFF_Relay(Bank_number=self.EEA_STAPLING_ONE_bank_number,
                              Relay_number=self.EEA_STAPLING_ONE_relay_number)  # B4:R1 - OFF
        self.Switch_OFF_Relay(Bank_number=self.EEA_STAPLING_TWO_bank_number,
                              Relay_number=self.EEA_STAPLING_TWO_relay_number)  # B4:R2 - OFF

        self.applyLoadViaVoltage(9, self.DcPowerSupplyComPort)

        self.Switch_ONN_Relay(Bank_number=self.EEA_CUTTING_ONE_bank_number,
                              Relay_number=self.EEA_CUTTING_ONE_relay_number)  # B4:R3 - ON
        self.Switch_ONN_Relay(Bank_number=self.EEA_CUTTING_TWO_bank_number,
                              Relay_number=self.EEA_CUTTING_TWO_relay_number)  # B4:R4 - ON
        self.wait(5)

        self.Switch_OFF_Relay(Bank_number=self.EEA_CUTTING_ONE_bank_number,
                              Relay_number=self.EEA_CUTTING_ONE_relay_number)  # B4:R3 - OFF
        self.Switch_OFF_Relay(Bank_number=self.EEA_CUTTING_TWO_bank_number,
                              Relay_number=self.EEA_CUTTING_TWO_relay_number)  # B4:R4 - OFF

        # Remove Adapter - Staple complete
        # 5.1.23. After staple completes and within a few seconds after the start of cut,
        # detach the adapter from the clamshell.
        self.removeAdapter_DV()
        self.wait(15)

        # 5.1.24. Wait a few seconds and then reattach adapter to a different handle-clamshell system.
        # 5.1.24. Wait a few seconds and then reattach adapter to a different handle-clamshell system.
        # Wait for the timer to complete and confirm that the handle indicates to resume cutting (249790, 278486).
        '''278486	PEEA_SYSTEM shall allow continuation of the PROCEDURE in the event of attachment to a different HANDLE.
        249790	The HANDLE shall indicate for USER to resume cutting when PEEA_ADAPTER is attached after initiating cut and prior to cut complete.'''
        # self.disconnect_MCP_Port()

        ### Recovery is performing on Different Handle
        Treating_different_handle(self.PowerPackComPort)
        self.wait(2)

        # Restart the Handle
        self.Switch_ONN_Relay(3,5)
        self.Switch_ONN_Relay(3,6)
        self.wait(5)
        self.Switch_OFF_Relay(3,5)
        self.Switch_OFF_Relay(3,6)

        self.wait(7)

        # Removing Clamshell
        # self.removeClamshell()
        self.wait(2)
        self.connectClamshellTest()

        self.wait(3)

        # Connecting Adapter
        self.Connect_Adapter()
        self.wait(15)

        "Screen 6 - Resume Cutting "
        screen_name = "Resume_Cutting"
        folder_name = "Resume_Cutting"
        file_name = "Resume_Cutting"
        self.handle_screen(videoPath=self.videoPath, screen_name=screen_name, folder_name=folder_name,
                           file_name=file_name, is_static_image=False)

        self.apply_load_force(0)

        ###### Added On 13th Nov 24 to apply more force while resuming cut recovery
        ###### Move the linear actuator before cut resume
        self.Switch_ONN_Relay(Bank_number=self.EEA_CUTTING_COMPLETE_ONE_bank_number,
                              Relay_number=self.EEA_CUTTING_COMPLETE_ONE_relay_number)  # B4:R5 - ON
        self.Switch_ONN_Relay(Bank_number=self.EEA_CUTTING_COMPLETE_TWO_bank_number,
                              Relay_number=self.EEA_CUTTING_COMPLETE_TWO_relay_number)  # B4:R6 - ON
        self.wait(2)
        self.Switch_OFF_Relay(Bank_number=self.EEA_CUTTING_COMPLETE_ONE_bank_number,
                              Relay_number=self.EEA_CUTTING_COMPLETE_ONE_relay_number)  # B4:R5 - OFF
        self.Switch_OFF_Relay(Bank_number=self.EEA_CUTTING_COMPLETE_TWO_bank_number,
                              Relay_number=self.EEA_CUTTING_COMPLETE_TWO_relay_number)  # B4:R6 - OFF


        # 5.1.25. Press the green safety button.
        self.GreenKeyAck_400860()
        self.wait(15)

        self.Switch_ONN_Relay(Bank_number=self.EEA_CUTTING_ONE_bank_number,
                              Relay_number=self.EEA_CUTTING_ONE_relay_number)  # B4:R3 - ON
        self.Switch_ONN_Relay(Bank_number=self.EEA_CUTTING_TWO_bank_number,
                              Relay_number=self.EEA_CUTTING_TWO_relay_number)  # B4:R4 - ON

        self.wait(2)
        # 5.1.26. Press the down toggle to resume cutting.
        self.Switch_ONN_Relay(2, 5)
        self.wait(.5)
        self.Switch_OFF_Relay(2, 5)
        self.wait(1)


        self.Switch_OFF_Relay(Bank_number=self.EEA_CUTTING_ONE_bank_number,
                              Relay_number=self.EEA_CUTTING_ONE_relay_number)  # B4:R3 - OFF
        self.Switch_OFF_Relay(Bank_number=self.EEA_CUTTING_TWO_bank_number,
                              Relay_number=self.EEA_CUTTING_TWO_relay_number)  # B4:R4 - OFF
        self.wait(.5)

        self.Switch_ONN_Relay(Bank_number=self.EEA_CUTTING_COMPLETE_ONE_bank_number,
                              Relay_number=self.EEA_CUTTING_COMPLETE_ONE_relay_number)  # B4:R5 - ON
        self.Switch_ONN_Relay(Bank_number=self.EEA_CUTTING_COMPLETE_TWO_bank_number,
                              Relay_number=self.EEA_CUTTING_COMPLETE_TWO_relay_number)  # B4:R6 - ON
        self.wait(30)
        self.compare_logs(logs_to_compare, SuccessFlag=fire_success_flag, is_firing_test=True)
        print(f'STEP : {logs_to_compare} performed!')
        self.Switch_OFF_Relay(Bank_number=self.EEA_CUTTING_COMPLETE_ONE_bank_number,
                              Relay_number=self.EEA_CUTTING_COMPLETE_ONE_relay_number)  # B4:R5 - OFF
        self.Switch_OFF_Relay(Bank_number=self.EEA_CUTTING_COMPLETE_TWO_bank_number,
                              Relay_number=self.EEA_CUTTING_COMPLETE_TWO_relay_number)  # B4:R6 - OFF

        self.output_on_off(False, self.DcPowerSupplyComPort)

    def EEAFiring_RBDV_Recovery_Mode_460333(self, logs_to_compare="EEA Firing"):
        self.output_on_off(True, self.DcPowerSupplyComPort)
        self.applyLoadViaVoltage(4, self.DcPowerSupplyComPort)

        # turn on 4-1 and 4-2 relays
        self.Switch_ONN_Relay(4, 1)
        self.Switch_ONN_Relay(4, 2)

        self.wait(1)

        # turn off 4-1 and 4-2
        self.Switch_OFF_Relay(4, 1)
        self.Switch_OFF_Relay(4, 2)

        self.applyLoadViaVoltage(5.5, self.DcPowerSupplyComPort)
        self.wait(1)

        # turn on 4-1 and 4-2 relays
        self.Switch_ONN_Relay(4, 1)
        self.Switch_ONN_Relay(4, 2)

        self.wait(4)

        # press close key
        self.Switch_ONN_Relay(2, 5)
        time.sleep(0.5)
        self.Switch_OFF_Relay(2, 5)

        string_to_found = 'GUI_NewState: EEA_STAPLE_11_25'
        self.my_Serthread.waitUntilString(string_to_found, timeout=10)
        # turn off 4-1 and 4-2
        self.Switch_OFF_Relay(4, 1)
        self.Switch_OFF_Relay(4, 2)

        self.removeAdapter_DV()
        self.wait(5)

        self.Switch_ONN_Relay(4, 5)
        self.Switch_ONN_Relay(4, 6)

        self.wait(7)

        # turn off 4-5 and 4-6 relays
        self.Switch_OFF_Relay(4, 5)
        self.Switch_OFF_Relay(4, 6)

        # Detach the Adapter - Prior to staple complete
        self.Connect_Adapter()
        self.wait(15)

        # self.GreenKeyAck_400860()
        self.Switch_ONN_Relay(3, 5)
        self.wait(0.5)
        self.Switch_OFF_Relay(3, 5)
        self.wait(15)

        string_to_found = ''
        self.applyLoadViaVoltage(4, self.DcPowerSupplyComPort)

        # turn on 4-1 and 4-2 relays
        self.Switch_ONN_Relay(4, 1)
        self.Switch_ONN_Relay(4, 2)

        self.wait(1)

        # turn off 4-1 and 4-2
        self.Switch_OFF_Relay(4, 1)
        self.Switch_OFF_Relay(4, 2)

        self.applyLoadViaVoltage(5.5, self.DcPowerSupplyComPort)
        self.wait(1)

        # turn on 4-1 and 4-2 relays
        self.Switch_ONN_Relay(4, 1)
        self.Switch_ONN_Relay(4, 2)

        self.wait(4)

        # press close key
        self.Switch_ONN_Relay(2, 5)
        time.sleep(0.5)
        self.Switch_OFF_Relay(2, 5)

        string_to_found = 'GUI_NewState: EEA_STAPLE_26_38'
        # string_to_found = '****  ENTERING OP LSS WRecID STAPLE COMPLETE STATE  ****'
        self.my_Serthread.waitUntilString(string_to_found, timeout=10)
        # turn off 4-1 and 4-2
        self.Switch_OFF_Relay(4, 1)
        self.Switch_OFF_Relay(4, 2)

        # turn on 4-5 and 4-6 relays
        self.Switch_ONN_Relay(4, 5)
        self.Switch_ONN_Relay(4, 6)

        self.wait(2)

        # turn off 4-5 and 4-6 relays
        self.Switch_OFF_Relay(4, 5)
        self.Switch_OFF_Relay(4, 6)

        """"""""""""""""""""""Cut Recovery """""''''''''''''''''''
        string_to_found = 'GUI_NewState: EEA_CUT_70'
        self.my_Serthread.waitUntilString(string_to_found, timeout=10)

        self.removeAdapter_DV()
        self.wait(15)

        ### Recovery is performing on Different Handle
        Treating_different_handle(self.PowerPackComPort)
        self.wait(2)

        # Restart the Handle
        self.Switch_ONN_Relay(3,5)
        self.Switch_ONN_Relay(3,6)
        self.wait(5)
        self.Switch_OFF_Relay(3,5)
        self.Switch_OFF_Relay(3,6)

        self.wait(9)

        # Connect Clamshell
        self.connectClamshellTest()
        self.wait(3)


        self.Connect_Adapter()
        self.wait(15)

        self.Switch_ONN_Relay(3, 5)
        self.wait(0.5)
        self.Switch_OFF_Relay(3, 5)
        self.wait(15)

        self.apply_load_force(0)

        self.applyLoadViaVoltage(9, self.DcPowerSupplyComPort)
        # press close key
        self.Switch_ONN_Relay(2, 5)
        time.sleep(0.5)
        self.Switch_OFF_Relay(2, 5)

        # turn on 4-1 and 4-2 relays
        self.Switch_ONN_Relay(4, 1)
        self.Switch_ONN_Relay(4, 2)

        print(f"finding: GUI_NewState: EEA_CUT_70")
        string_to_found = 'GUI_NewState: EEA_CUT_70'
        self.my_Serthread.waitUntilString(string_to_found, timeout=20)

        self.Switch_OFF_Relay(4, 1)
        self.Switch_OFF_Relay(4, 2)

        self.Switch_ONN_Relay(4, 5)
        self.Switch_ONN_Relay(4, 6)

        self.wait(15)

        # turn off 4-5 and 4-6 relays
        self.Switch_OFF_Relay(4, 5)
        self.Switch_OFF_Relay(4, 6)

    def EEA_Reload_CRC_Failure(self, logs_to_compare='EEA Firing'):
        self.output_on_off(True, self.DcPowerSupplyComPort)
        self.applyLoadViaVoltage(4, self.DcPowerSupplyComPort)

        # turn on 4-1 and 4-2 relays
        self.Switch_ONN_Relay(4, 1)
        self.Switch_ONN_Relay(4, 2)

        self.wait(1)

        # turn off 4-1 and 4-2
        self.Switch_OFF_Relay(4, 1)
        self.Switch_OFF_Relay(4, 2)

        self.applyLoadViaVoltage(5.5, self.DcPowerSupplyComPort)
        self.wait(1)

        # turn on 4-1 and 4-2 relays
        self.Switch_ONN_Relay(4, 1)
        self.Switch_ONN_Relay(4, 2)

        self.wait(4)

        # press close key
        self.Switch_ONN_Relay(2, 5)
        time.sleep(0.5)
        self.Switch_OFF_Relay(2, 5)

        string_to_found = 'GUI_NewState: EEA_STAPLE_11_25'
        self.my_Serthread.waitUntilString(string_to_found, timeout=10)
        # turn off 4-1 and 4-2
        self.Switch_OFF_Relay(4, 1)
        self.Switch_OFF_Relay(4, 2)

        self.removeAdapter_DV()
        self.wait(5)

        self.Switch_ONN_Relay(4, 5)
        self.Switch_ONN_Relay(4, 6)

        self.wait(7)

        # turn off 4-5 and 4-6 relays
        self.Switch_OFF_Relay(4, 5)
        self.Switch_OFF_Relay(4, 6)



        ###################################
        # Making Bad CRC
        ######################################
        # Remove Reload
        self.Switch_OFF_Relay(3, 2)  # B3:R2 - ON
        self.Switch_OFF_Relay(3, 3)  # B3:R3 - ON

        # Reading Reload Onewire
        self.Switch_ONN_Relay(5, 2)  # B5:R2 - ON
        self.Switch_ONN_Relay(5, 6)  # B5:R6 - ON

        reload_1w_eeprom_data = self.read_eeprom_data()

        print("before Reload Onewire EEPROM Data ", reload_1w_eeprom_data)

        reload_1w_eeprom_data[63] = reload_1w_eeprom_data[62]

        print("Reload Onewire EEPROM Data ", reload_1w_eeprom_data)
        # reload_1w_eeprom_data[62] =  reload_1w_eeprom_data[63]

        self.write_eeprom_data(data_bytes=reload_1w_eeprom_data)
        print("Reload Onewire WRITE  EEPROM Data ", reload_1w_eeprom_data)

        self.Switch_OFF_Relay(5, 2)  # B5:R1 - OFF
        self.Switch_OFF_Relay(5, 6)  # B5:R2 - OFF

        ## Reload Connected
        self.Switch_ONN_Relay(3, 2)  # B3:R2 - ON
        self.Switch_ONN_Relay(3, 3)  # B3:R3 - ON
        self.wait(10)

        # Detach the Adapter - Prior to staple complete
        self.Connect_Adapter()
        self.wait(15)

        # self.GreenKeyAck_400860()
        self.Switch_ONN_Relay(3, 5)
        self.wait(0.5)
        self.Switch_OFF_Relay(3, 5)
        self.wait(15)

        string_to_found = ''
        self.applyLoadViaVoltage(4, self.DcPowerSupplyComPort)

        # turn on 4-1 and 4-2 relays
        self.Switch_ONN_Relay(4, 1)
        self.Switch_ONN_Relay(4, 2)

        # self.wait_till_reach_peak_load(15)
        self.wait(1)

        # turn off 4-1 and 4-2
        self.Switch_OFF_Relay(4, 1)
        self.Switch_OFF_Relay(4, 2)

        self.applyLoadViaVoltage(5.5, self.DcPowerSupplyComPort)  # VMK changed to 5.5 from 7
        self.wait(1)

        # turn on 4-1 and 4-2 relays
        self.Switch_ONN_Relay(4, 1)
        self.Switch_ONN_Relay(4, 2)

        self.wait(4)

        # press close key
        self.Switch_ONN_Relay(2, 5)
        time.sleep(0.5)
        self.Switch_OFF_Relay(2, 5)

        string_to_found = 'GUI_NewState: EEA_STAPLE_26_38'
        # string_to_found = '****  ENTERING OP LSS WRecID STAPLE COMPLETE STATE  ****'
        self.my_Serthread.waitUntilString(string_to_found, timeout=10)
        # turn off 4-1 and 4-2
        self.Switch_OFF_Relay(4, 1)
        self.Switch_OFF_Relay(4, 2)

        # turn on 4-5 and 4-6 relays
        self.Switch_ONN_Relay(4, 5)
        self.Switch_ONN_Relay(4, 6)

        # self.wait_till_reach_peak_load(3)
        self.wait(2)

        # turn off 4-5 and 4-6 relays
        self.Switch_OFF_Relay(4, 5)
        self.Switch_OFF_Relay(4, 6)

        """"""""""""""""""""""Cut Recovery """""''''''''''''''''''
        # # turn on 4-5 and 4-6 relays
        # self.Switch_ONN_Relay(4, 5)
        # self.Switch_ONN_Relay(4, 6)
        #
        # # self.wait_till_reach_peak_load(3)
        # self.wait(2)
        #
        # # turn off 4-5 and 4-6 relays
        # self.Switch_OFF_Relay(4, 5)
        # self.Switch_OFF_Relay(4, 6)

        string_to_found = 'GUI_NewState: EEA_CUT_70'
        self.my_Serthread.waitUntilString(string_to_found, timeout=10)

        self.removeAdapter_DV()
        self.wait(10)

        self.Connect_Adapter()
        self.wait(15)

        # self.GreenKeyAck_400860()
        self.Switch_ONN_Relay(3, 5)
        self.wait(0.5)
        self.Switch_OFF_Relay(3, 5)
        self.wait(15)

        self.apply_load_force(0)

        self.applyLoadViaVoltage(9, self.DcPowerSupplyComPort)
        # press close key
        self.Switch_ONN_Relay(2, 5)
        time.sleep(0.5)
        self.Switch_OFF_Relay(2, 5)

        # turn on 4-1 and 4-2 relays
        self.Switch_ONN_Relay(4, 1)
        self.Switch_ONN_Relay(4, 2)

        print(f"finding: GUI_NewState: EEA_CUT_70")
        string_to_found = 'GUI_NewState: EEA_CUT_70'
        self.my_Serthread.waitUntilString(string_to_found, timeout=20)

        self.Switch_OFF_Relay(4, 1)
        self.Switch_OFF_Relay(4, 2)

        self.Switch_ONN_Relay(4, 5)
        self.Switch_ONN_Relay(4, 6)

        # self.wait_till_reach_peak_load(3)
        self.wait(4)

        # turn off 4-5 and 4-6 relays
        self.Switch_OFF_Relay(4, 5)
        self.Switch_OFF_Relay(4, 6)

    def EEA_DV_Firing_450524(self, logs_to_compare='EEA Firing'):
       #  fire_success_flag = True
       #  # Apply Voltage Instead of Applying Load Force
       #  self.output_on_off(True, self.DcPowerSupplyComPort)
       #  self.applyLoadViaVoltage(5, self.DcPowerSupplyComPort)
       #  self.my_Serthread.clearQue()
       #  # self.wait(5)
       #  # 5.1.19.	Press the down toggle to initiate firing.
       #  # Prior to staple complete (within a few seconds), detach the adapter from the clamshell.
       #  self.Switch_ONN_Relay(Bank_number=self.EEA_STAPLING_ONE_bank_number,
       #                        Relay_number=self.EEA_STAPLING_ONE_relay_number)  # B4:R1 - ON
       #  self.Switch_ONN_Relay(Bank_number=self.EEA_STAPLING_TWO_bank_number,
       #                        Relay_number=self.EEA_STAPLING_TWO_relay_number)  # B4:R2 - ON
       #  self.wait(4.5)#3)
       #  self.Switch_ONN_Relay(Bank_number=self.FIRING_bank_number, Relay_number=self.FIRING_relay_number)  # B2:R5 - ON
       #  self.wait(0.5)
       #  self.Switch_OFF_Relay(Bank_number=self.FIRING_bank_number, Relay_number=self.FIRING_relay_number)  # B2:R5 - OFF
       #  self.wait(2)
       #  self.Switch_OFF_Relay(Bank_number=self.EEA_STAPLING_ONE_bank_number,
       #                        Relay_number=self.EEA_STAPLING_ONE_relay_number)  # B4:R1 - OFF
       #  self.Switch_OFF_Relay(Bank_number=self.EEA_STAPLING_TWO_bank_number,
       #                        Relay_number=self.EEA_STAPLING_TWO_relay_number)  # B4:R2 - OFF
       #
       #  self.wait(1)
       #
       #  # Detach the Adapter - Prior to staple complete
       #  self.removeAdapter_DV()
       #  self.wait(5)
       #
       #  # Remove Reload
       #  self.Switch_OFF_Relay(3, 2)  # B3:R2 - ON
       #  self.Switch_OFF_Relay(3, 3)  # B3:R3 - ON
       #
       #
       #  ###################################
       #  # Making Bad CRC
       #  ######################################
       #
       #  # Reading Reload Onewire
       #  self.Switch_ONN_Relay(5, 2)  # B5:R2 - ON
       #  self.Switch_ONN_Relay(5, 6)  # B5:R6 - ON
       #
       # # self.write_eeprom_data(data_bytes=EEA_RELOAD_EEPROM)
       #
       #  reload_1w_eeprom_data = self.read_eeprom_data()
       #
       #  print("before Reload Onewire EEPROM Data ", reload_1w_eeprom_data)
       #
       #  reload_1w_eeprom_data[63]  = reload_1w_eeprom_data[62]
       #
       #  print("Reload Onewire EEPROM Data ", reload_1w_eeprom_data)
       #  # reload_1w_eeprom_data[62] =  reload_1w_eeprom_data[63]
       #
       #  self.write_eeprom_data(data_bytes=reload_1w_eeprom_data)
       #  print("Reload Onewire WRITE  EEPROM Data ", reload_1w_eeprom_data)
       #
       #  self.Switch_OFF_Relay(5, 2)  # B5:R1 - OFF
       #  self.Switch_OFF_Relay(5, 6)  # B5:R2 - OFF
       #
       #  ## Reload Connected
       #  self.Switch_ONN_Relay(3, 2)  # B3:R2 - ON
       #  self.Switch_ONN_Relay(3, 3)  # B3:R3 - ON
       #  self.wait(10)
       #
       #  # 5.1.20.	Wait a few seconds and then reattach adapter to clamshell.
       #  # Wait for the timer to complete and confirm that the handle indicates to resume stapling (249786).
       #  # '''249786	The HANDLE shall indicate for USER to resume stapling
       #  # when PEEA_ADAPTER is attached after initiating staple fire and prior to staple complete.'''
       #  '''249786	The HANDLE shall indicate for USER to resume stapling
       #          when PEEA_ADAPTER is attached after initiating staple fire and prior to staple complete.'''
       #  self.Connect_Adapter()
       #  self.wait(15)
       #
       #  "Screen 5 - Resume Stapling "
       #  screen_name = "Resume_Stapling"
       #  folder_name = "Resume_Stapling"
       #  file_name = "Resume_Stapling"
       #  self.handle_screen(videoPath=self.videoPath, screen_name=screen_name, folder_name=folder_name,
       #                     file_name=file_name, is_static_image=False)
       #
       #  # 5.1.21 Press the green safety button.
       #  self.GreenKeyAck_400860()
       #  self.wait(15)
       #
       #  # 5.1.22. Press the down toggle to resume stapling.
       #  self.Switch_ONN_Relay(Bank_number=self.FIRING_bank_number, Relay_number=self.FIRING_relay_number)  # B2:R5 - ON
       #  self.wait(.5)
       #  self.Switch_OFF_Relay(Bank_number=self.FIRING_bank_number, Relay_number=self.FIRING_relay_number)  # B2:R5 - OFF
       #
       #  self.Switch_ONN_Relay(Bank_number=self.EEA_STAPLING_ONE_bank_number,
       #                        Relay_number=self.EEA_STAPLING_ONE_relay_number)  # B4:R1 - ON
       #  self.Switch_ONN_Relay(Bank_number=self.EEA_STAPLING_TWO_bank_number,
       #                        Relay_number=self.EEA_STAPLING_TWO_relay_number)  # B4:R2 - ON
       #  self.wait(5)
       #  self.Switch_OFF_Relay(Bank_number=self.EEA_STAPLING_ONE_bank_number,
       #                        Relay_number=self.EEA_STAPLING_ONE_relay_number)  # B4:R1 - OFF
       #  self.Switch_OFF_Relay(Bank_number=self.EEA_STAPLING_TWO_bank_number,
       #                        Relay_number=self.EEA_STAPLING_TWO_relay_number)  # B4:R2 - OFF
       #  #
       #  # self.output_on_off(False, self.DcPowerSupplyComPort)
       #  #
       #  # self.wait(1)
       #  # self.output_on_off(True, self.DcPowerSupplyComPort)
       #  self.apply_load_force(0)
       #
       #  self.applyLoadViaVoltage(9, self.DcPowerSupplyComPort)
       #
       #  self.Switch_ONN_Relay(Bank_number=self.EEA_CUTTING_ONE_bank_number,
       #                        Relay_number=self.EEA_CUTTING_ONE_relay_number)  # B4:R3 - ON
       #  self.Switch_ONN_Relay(Bank_number=self.EEA_CUTTING_TWO_bank_number,
       #                        Relay_number=self.EEA_CUTTING_TWO_relay_number)  # B4:R4 - ON
       #  self.wait(5)
       #
       #  self.Switch_OFF_Relay(Bank_number=self.EEA_CUTTING_ONE_bank_number,
       #                        Relay_number=self.EEA_CUTTING_ONE_relay_number)  # B4:R3 - OFF
       #  self.Switch_OFF_Relay(Bank_number=self.EEA_CUTTING_TWO_bank_number,
       #                        Relay_number=self.EEA_CUTTING_TWO_relay_number)  # B4:R4 - OFF
       #
       #  # Remove Adapter - Staple complete
       #  # 5.1.23. After staple completes and within a few seconds after the start of cut,
       #  # detach the adapter from the clamshell.
       #  self.removeAdapter_DV()
       #  self.wait(15)
       #
       #  # 5.1.24. Wait a few seconds and then reattach adapter to a different handle-clamshell system.
       #  # Wait for the timer to complete and confirm that the handle indicates to resume cutting (249790, 278486).
       #  '''278486	PEEA_SYSTEM shall allow continuation of the PROCEDURE in the event of attachment to a different HANDLE.
       #  249790	The HANDLE shall indicate for USER to resume cutting when PEEA_ADAPTER is attached after initiating cut and prior to cut complete.'''
       #  self.Connect_Adapter()
       #  self.wait(15)
       #
       #  "Screen 6 - Resume Cutting "
       #  screen_name = "Resume_Cutting"
       #  folder_name = "Resume_Cutting"
       #  file_name = "Resume_Cutting"
       #  self.handle_screen(videoPath=self.videoPath, screen_name=screen_name, folder_name=folder_name,
       #                     file_name=file_name, is_static_image=False)
       #
       #  ###### Added On 13th Nov 24 to apply more force while resuming cut recovery
       #  ###### Move the linear actuator before cut resume
       #  self.Switch_ONN_Relay(Bank_number=self.EEA_CUTTING_COMPLETE_ONE_bank_number,
       #                        Relay_number=self.EEA_CUTTING_COMPLETE_ONE_relay_number)  # B4:R5 - ON
       #  self.Switch_ONN_Relay(Bank_number=self.EEA_CUTTING_COMPLETE_TWO_bank_number,
       #                        Relay_number=self.EEA_CUTTING_COMPLETE_TWO_relay_number)  # B4:R6 - ON
       #  self.wait(2)
       #  self.Switch_OFF_Relay(Bank_number=self.EEA_CUTTING_COMPLETE_ONE_bank_number,
       #                        Relay_number=self.EEA_CUTTING_COMPLETE_ONE_relay_number)  # B4:R5 - OFF
       #  self.Switch_OFF_Relay(Bank_number=self.EEA_CUTTING_COMPLETE_TWO_bank_number,
       #                        Relay_number=self.EEA_CUTTING_COMPLETE_TWO_relay_number)  # B4:R6 - OFF
       #
       #  # 5.1.25. Press the green safety button.
       #  self.GreenKeyAck_400860()
       #  self.wait(15)
       #
       #  self.Switch_ONN_Relay(Bank_number=self.EEA_CUTTING_ONE_bank_number,
       #                        Relay_number=self.EEA_CUTTING_ONE_relay_number)  # B4:R3 - ON
       #  self.Switch_ONN_Relay(Bank_number=self.EEA_CUTTING_TWO_bank_number,
       #                        Relay_number=self.EEA_CUTTING_TWO_relay_number)  # B4:R4 - ON
       #
       #  # 5.1.26. Press the down toggle to resume cutting.
       #  self.Switch_ONN_Relay(2, 5)
       #  self.wait(.5)
       #  self.Switch_OFF_Relay(2, 5)
       #  self.wait(2)
       #
       #  # self.applyLoadViaVoltage(0, self.DcPowerSupplyComPort)
       #
       #  # self.wait(3)
       #  self.Switch_OFF_Relay(Bank_number=self.EEA_CUTTING_ONE_bank_number,
       #                        Relay_number=self.EEA_CUTTING_ONE_relay_number)  # B4:R3 - OFF
       #  self.Switch_OFF_Relay(Bank_number=self.EEA_CUTTING_TWO_bank_number,
       #                        Relay_number=self.EEA_CUTTING_TWO_relay_number)  # B4:R4 - OFF
       #  self.wait(.5)
       #
       #  self.Switch_ONN_Relay(Bank_number=self.EEA_CUTTING_COMPLETE_ONE_bank_number,
       #                        Relay_number=self.EEA_CUTTING_COMPLETE_ONE_relay_number)  # B4:R5 - ON
       #  self.Switch_ONN_Relay(Bank_number=self.EEA_CUTTING_COMPLETE_TWO_bank_number,
       #                        Relay_number=self.EEA_CUTTING_COMPLETE_TWO_relay_number)  # B4:R6 - ON
       #  self.wait(30)
       #  self.compare_logs(logs_to_compare, SuccessFlag=fire_success_flag, is_firing_test=True)
       #  print(f'STEP : {logs_to_compare} performed!')
       #  self.Switch_OFF_Relay(Bank_number=self.EEA_CUTTING_COMPLETE_ONE_bank_number,
       #                        Relay_number=self.EEA_CUTTING_COMPLETE_ONE_relay_number)  # B4:R5 - OFF
       #  self.Switch_OFF_Relay(Bank_number=self.EEA_CUTTING_COMPLETE_TWO_bank_number,
       #                        Relay_number=self.EEA_CUTTING_COMPLETE_TWO_relay_number)  # B4:R6 - OFF
       #
       #  self.output_on_off(False, self.DcPowerSupplyComPort)
        self.output_on_off(True, self.DcPowerSupplyComPort)
        self.applyLoadViaVoltage(4, self.DcPowerSupplyComPort)

        # turn on 4-1 and 4-2 relays
        self.Switch_ONN_Relay(4, 1)
        self.Switch_ONN_Relay(4, 2)

        self.wait(1)

        # turn off 4-1 and 4-2
        self.Switch_OFF_Relay(4, 1)
        self.Switch_OFF_Relay(4, 2)

        self.applyLoadViaVoltage(5.5, self.DcPowerSupplyComPort)  # VMK changed to 5.5 from 7

        # turn on 4-1 and 4-2 relays
        self.Switch_ONN_Relay(4, 1)
        self.Switch_ONN_Relay(4, 2)

        self.wait(3)

        # press close key
        self.Switch_ONN_Relay(2, 5)
        time.sleep(0.5)
        self.Switch_OFF_Relay(2, 5)

        self.wait(1)

        # turn off 4-1 and 4-2
        self.Switch_OFF_Relay(4, 1)
        self.Switch_OFF_Relay(4, 2)

        # Detach the Adapter - Prior to staple complete
        self.removeAdapter_DV()
        self.wait(15)

        # Remove Reload
        self.Switch_OFF_Relay(3, 2)  # B3:R2 - ON
        self.Switch_OFF_Relay(3, 3)  # B3:R3 - ON


        ###################################
        # Making Bad CRC
        ######################################

        # Reading Reload Onewire
        self.Switch_ONN_Relay(5, 2)  # B5:R2 - ON
        self.Switch_ONN_Relay(5, 6)  # B5:R6 - ON

       # self.write_eeprom_data(data_bytes=EEA_RELOAD_EEPROM)

        reload_1w_eeprom_data = self.read_eeprom_data()

        print("before Reload Onewire EEPROM Data ", reload_1w_eeprom_data)

        reload_1w_eeprom_data[63]  = reload_1w_eeprom_data[62]

        print("Reload Onewire EEPROM Data ", reload_1w_eeprom_data)
        # reload_1w_eeprom_data[62] =  reload_1w_eeprom_data[63]

        self.write_eeprom_data(data_bytes=reload_1w_eeprom_data)
        print("Reload Onewire WRITE  EEPROM Data ", reload_1w_eeprom_data)

        self.Switch_OFF_Relay(5, 2)  # B5:R1 - OFF
        self.Switch_OFF_Relay(5, 6)  # B5:R2 - OFF

        ## Reload Connected
        self.Switch_ONN_Relay(3, 2)  # B3:R2 - ON
        self.Switch_ONN_Relay(3, 3)  # B3:R3 - ON
        self.wait(10)


        self.Connect_Adapter()
        self.wait(15)

        self.GreenKeyAck_400860()
        self.wait(10)


        # turn on 4-1 and 4-2 relays
        self.Switch_ONN_Relay(4, 1)
        self.Switch_ONN_Relay(4, 2)

        # press close key
        self.Switch_ONN_Relay(2, 5)
        time.sleep(0.5)
        self.Switch_OFF_Relay(2, 5)

        self.wait(3)

        # turn off 4-1 and 4-2
        self.Switch_OFF_Relay(4, 1)
        self.Switch_OFF_Relay(4, 2)

        self.Switch_ONN_Relay(4, 5)
        self.Switch_ONN_Relay(4, 6)

        self.wait(1)

        # turn off 4-5 and 4-6 relays
        self.Switch_OFF_Relay(4, 5)
        self.Switch_OFF_Relay(4, 6)

        self.applyLoadViaVoltage(9, self.DcPowerSupplyComPort)

        # turn on 4-1 and 4-2 relays
        self.Switch_ONN_Relay(4, 1)
        self.Switch_ONN_Relay(4, 2)

        self.apply_load_force(0)

        self.wait(1)

        # turn off 4-1 and 4-2
        self.Switch_OFF_Relay(4, 1)
        self.Switch_OFF_Relay(4, 2)

        # Detach the Adapter - Prior to staple complete
        self.removeAdapter_DV()
        self.wait(15)

        self.Connect_Adapter()
        self.wait(15)

        self.GreenKeyAck_400860()
        self.wait(10)

        # press close key
        self.Switch_ONN_Relay(2, 5)
        time.sleep(0.5)
        self.Switch_OFF_Relay(2, 5)

        # turn on 4-1 and 4-2 relays
        self.Switch_ONN_Relay(4, 1)
        self.Switch_ONN_Relay(4, 2)

        self.wait(4)

        # turn off 4-1 and 4-2
        self.Switch_OFF_Relay(4, 1)
        self.Switch_OFF_Relay(4, 2)

        # turn on 4-5 and 4-6 relays
        self.Switch_ONN_Relay(4, 5)
        self.Switch_ONN_Relay(4, 6)

        self.wait(5)

        # turn off 4-5 and 4-6 relays
        self.Switch_OFF_Relay(4, 5)
        self.Switch_OFF_Relay(4, 6)

    def EEA_DV_Firing_SSE_400860(self, logs_to_compare='EEA Firing'):
        fire_success_flag = True
        self.output_on_off(True, self.DcPowerSupplyComPort)
        self.applyLoadViaVoltage(5, self.DcPowerSupplyComPort)

        self.my_Serthread.clearQue()
        self.Switch_ONN_Relay(Bank_number=self.EEA_STAPLING_ONE_bank_number,
                              Relay_number=self.EEA_STAPLING_ONE_relay_number)  # B4:R1 - ON
        self.Switch_ONN_Relay(Bank_number=self.EEA_STAPLING_TWO_bank_number,
                              Relay_number=self.EEA_STAPLING_TWO_relay_number)  # B4:R2 - ON
        self.wait(3)
        self.Switch_ONN_Relay(Bank_number=self.FIRING_bank_number, Relay_number=self.FIRING_relay_number)  # B2:R5 - ON
        self.wait(0.5)
        self.Switch_OFF_Relay(Bank_number=self.FIRING_bank_number, Relay_number=self.FIRING_relay_number)  # B2:R5 - OFF
        self.wait(2)
        self.Switch_OFF_Relay(Bank_number=self.EEA_STAPLING_ONE_bank_number,
                              Relay_number=self.EEA_STAPLING_ONE_relay_number)  # B4:R1 - OFF
        self.Switch_OFF_Relay(Bank_number=self.EEA_STAPLING_TWO_bank_number,
                              Relay_number=self.EEA_STAPLING_TWO_relay_number)  # B4:R2 - OFF

        # Remove Adapter - Prior to staple complete
        self.removeAdapter_DV()
        self.wait(10)

        # Debug Messages for Recovery state - Delete for the final code
        # self.Switch_ONN_Relay(1, 8)  # B1:R8 - OFF
        # self.wait(2)
        # RecoveryID, ErrorCode = GetAdapterEepromRecoveryData(self.FtdiUartComPort)
        # print("Recovery Id data Prior to stapling  :", RecoveryID, ErrorCode)
        # self.Switch_OFF_Relay(1, 8)  # B1:R8 - OFF

        # Re-Attach Adapter - Resume from Stapling Refer Screen 5
        self.Connect_Adapter()
        self.wait(20)

        # Press and hold up toggle button to enter SSE
        self.Switch_ONN_Relay(Bank_number=self.RETRACT_bank_number,
                              Relay_number=self.RETRACT_relay_number)  # B2:R4 - ON

        screen_name = "SSE"
        folder_name = "SSE"
        file_name = "SSE"
        self.handle_screen(videoPath=self.videoPath, screen_name=screen_name, folder_name=folder_name,
                           file_name=file_name, is_static_image=False)

        self.wait(20)
        self.Switch_OFF_Relay(Bank_number=self.RETRACT_bank_number,
                              Relay_number=self.RETRACT_relay_number)  # B2:R4 - OFF

        screen_name = "Handle_Reset"
        folder_name = "Handle_Reset"
        file_name = "Handle_Reset"
        self.handle_screen(videoPath=self.videoPath, screen_name=screen_name, folder_name=folder_name,
                           file_name=file_name, is_static_image=False)

        #########################################################
        ## Remove Load And Revert back to Linear Actuator
        #########################################################
        # Remove Anvil, red foam and reload.
        self.DisconnectingEEAReload(exit_video=False)
        self.wait(2)

        self.output_on_off(True, self.DcPowerSupplyComPort)
        self.Switch_ONN_Relay(4,5)
        self.Switch_ONN_Relay(4,6)
        self.wait(10)
        self.Switch_OFF_Relay(4,5)
        self.Switch_OFF_Relay(4,6)

        self.apply_load_force(0)
        self.output_on_off(False, self.DcPowerSupplyComPort)
        self.wait(5)

        ## Press and hold 4 rotate buttons - to performing SSE
        self.Switch_ONN_Relay(Bank_number=self.LCW_ROTATION_bank_number,
                              Relay_number=self.LCW_ROTATION_relay_number)  # B2:R1 - ON
        self.Switch_ONN_Relay(Bank_number=self.LCCW_ROTATION_bank_number,
                              Relay_number=self.LCCW_ROTATION_relay_number)  # B2:R2 - ON
        self.Switch_ONN_Relay(Bank_number=self.RCW_ROTATION_bank_number,
                              Relay_number=self.RCW_ROTATION_relay_number)  # B2:R7 - ON
        self.Switch_ONN_Relay(Bank_number=self.RCCW_ROTATION_bank_number,
                              Relay_number=self.RCCW_ROTATION_relay_number)  # B2:R8 - ON
        self.wait(30)
        self.Switch_OFF_Relay(Bank_number=self.LCW_ROTATION_bank_number,
                              Relay_number=self.LCW_ROTATION_relay_number)  # B2:R1 - OFF
        self.Switch_OFF_Relay(Bank_number=self.LCCW_ROTATION_bank_number,
                              Relay_number=self.LCCW_ROTATION_relay_number)  # B2:R2 - OFF
        self.Switch_OFF_Relay(Bank_number=self.RCW_ROTATION_bank_number,
                              Relay_number=self.RCW_ROTATION_relay_number)  # B2:R7 - OFF
        self.Switch_OFF_Relay(Bank_number=self.RCCW_ROTATION_bank_number,
                              Relay_number=self.RCCW_ROTATION_relay_number)  # B2:R8 - OFF

        self.output_on_off(False, self.DcPowerSupplyComPort)

    def AlexEEAFiring(self, logs_to_compare='EEA Firing'):
        fire_success_flag = True
        # if relay_switch_over_delay != firing_default_delay:
        #     fire_success_flag = False
        self.apply_load_force(3.25)
        self.my_Serthread.clearQue()
        self.Switch_ONN_Relay(Bank_number=self.EEA_STAPLING_ONE_bank_number,
                              Relay_number=self.EEA_STAPLING_ONE_relay_number)  # B4:R1 - ON
        self.Switch_ONN_Relay(Bank_number=self.EEA_STAPLING_TWO_bank_number,
                              Relay_number=self.EEA_STAPLING_TWO_relay_number)  # B4:R2 - ON
        self.wait(3)
        self.Switch_ONN_Relay(Bank_number=self.FIRING_bank_number, Relay_number=self.FIRING_relay_number)  # B2:R5 - ON
        self.wait(0.5)
        self.Switch_OFF_Relay(Bank_number=self.FIRING_bank_number, Relay_number=self.FIRING_relay_number)  # B2:R5 - OFF
        self.wait(2)

        self.AlexremoveAdapter()
        self.Switch_OFF_Relay(Bank_number=self.EEA_STAPLING_ONE_bank_number,
                              Relay_number=self.EEA_STAPLING_ONE_relay_number)  # B4:R1 - OFF
        self.Switch_OFF_Relay(Bank_number=self.EEA_STAPLING_TWO_bank_number,
                              Relay_number=self.EEA_STAPLING_TWO_relay_number)  # B4:R2 - OFF

        self.wait(15)
        self.Connect_Adapter()
        self.wait(15)
        self.GreenKeyAck()
        self.wait(15)
        self.Switch_ONN_Relay(Bank_number=self.FIRING_bank_number, Relay_number=self.FIRING_relay_number)  # B2:R5 - ON
        self.wait(0.5)
        self.Switch_OFF_Relay(Bank_number=self.FIRING_bank_number, Relay_number=self.FIRING_relay_number)  # B2:R5 - OFF

        self.Switch_ONN_Relay(Bank_number=self.EEA_STAPLING_ONE_bank_number,
                              Relay_number=self.EEA_STAPLING_ONE_relay_number)  # B4:R1 - ON
        self.Switch_ONN_Relay(Bank_number=self.EEA_STAPLING_TWO_bank_number,
                              Relay_number=self.EEA_STAPLING_TWO_relay_number)  # B4:R2 - ON
        self.wait(5)
        self.Switch_OFF_Relay(Bank_number=self.EEA_STAPLING_ONE_bank_number,
                              Relay_number=self.EEA_STAPLING_ONE_relay_number)  # B4:R1 - OFF
        self.Switch_OFF_Relay(Bank_number=self.EEA_STAPLING_TWO_bank_number,
                              Relay_number=self.EEA_STAPLING_TWO_relay_number)  # B4:R2 - OFF
        self.apply_load_force(2)
        self.Switch_ONN_Relay(Bank_number=self.EEA_CUTTING_ONE_bank_number,
                              Relay_number=self.EEA_CUTTING_ONE_relay_number)  # B4:R3 - ON
        self.Switch_ONN_Relay(Bank_number=self.EEA_CUTTING_TWO_bank_number,
                              Relay_number=self.EEA_CUTTING_TWO_relay_number)  # B4:R4 - ON
        self.wait(2)
        self.apply_load_force(0)
        self.wait(15)

        self.Switch_OFF_Relay(Bank_number=self.EEA_CUTTING_ONE_bank_number,
                              Relay_number=self.EEA_CUTTING_ONE_relay_number)  # B4:R3 - OFF
        self.Switch_OFF_Relay(Bank_number=self.EEA_CUTTING_TWO_bank_number,
                              Relay_number=self.EEA_CUTTING_TWO_relay_number)  # B4:R4 - OFF
        self.AlexremoveAdapter()
        self.wait(15)
        self.Connect_Adapter()
        self.wait(15)
        self.GreenKeyAck()
        self.wait(15)

        self.Switch_ONN_Relay(2, 5)
        self.apply_load_force(0)
        self.Switch_ONN_Relay(Bank_number=self.EEA_CUTTING_ONE_bank_number,
                              Relay_number=self.EEA_CUTTING_ONE_relay_number)  # B4:R3 - ON
        self.Switch_ONN_Relay(Bank_number=self.EEA_CUTTING_TWO_bank_number,
                              Relay_number=self.EEA_CUTTING_TWO_relay_number)  # B4:R4 - ON
        self.wait(10)
        self.Switch_OFF_Relay(Bank_number=self.EEA_CUTTING_ONE_bank_number,
                              Relay_number=self.EEA_CUTTING_ONE_relay_number)  # B4:R3 - OFF
        self.Switch_OFF_Relay(Bank_number=self.EEA_CUTTING_TWO_bank_number,
                              Relay_number=self.EEA_CUTTING_TWO_relay_number)  # B4:R4 - OFF
        self.wait(1)
        self.Switch_ONN_Relay(Bank_number=self.EEA_CUTTING_COMPLETE_ONE_bank_number,
                              Relay_number=self.EEA_CUTTING_COMPLETE_ONE_relay_number)  # B4:R5 - ON
        self.Switch_ONN_Relay(Bank_number=self.EEA_CUTTING_COMPLETE_TWO_bank_number,
                              Relay_number=self.EEA_CUTTING_COMPLETE_TWO_relay_number)  # B4:R6 - ON
        self.wait(15)
        self.Switch_OFF_Relay(Bank_number=self.EEA_CUTTING_COMPLETE_ONE_bank_number,
                              Relay_number=self.EEA_CUTTING_COMPLETE_ONE_relay_number)  # B4:R5 - OFF
        self.Switch_OFF_Relay(Bank_number=self.EEA_CUTTING_COMPLETE_TWO_bank_number,
                              Relay_number=self.EEA_CUTTING_COMPLETE_TWO_relay_number)  # B4:R6 - OFF

        # # logger.info(f"Step: {logs_to_compare} Performed")
        print(f'STEP : {logs_to_compare} performed!')

    def TiltOpen_400860(self, logs_to_compare='Tilt Operation of Anvil', fixture_validation_req=False):  ### Remove Open in the funciton name - To Do
        self.my_Serthread.clearQue()
        self.wait(5)
        self.Switch_ONN_Relay(Bank_number=self.RETRACT_bank_number,
                              Relay_number=self.RETRACT_relay_number)  # B2:R4 - ON
        self.wait(5)

        # Remove Adapter - during tilt prompt open
        self.removeAdapter_DV()
        self.wait(15)

        self.Switch_OFF_Relay(Bank_number=self.RETRACT_bank_number,
                              Relay_number=self.RETRACT_relay_number)  # B2:R4 - OFF

        self.wait(5)

        # 5.1.30.	Wait a few seconds and then reattach adapter to clamshell.
        # Wait for the timer to complete and confirm that the device requires an up-toggle press to resume
        # extending the anvil to the tilt open (cleanability) position (250352).
        self.Connect_Adapter()
        self.wait(15)

        self.Switch_ONN_Relay(Bank_number=self.RETRACT_bank_number,
                              Relay_number=self.RETRACT_relay_number)  # B2:R4 - ON
        self.wait(0.5)

        self.Switch_OFF_Relay(Bank_number=self.RETRACT_bank_number,
                              Relay_number=self.RETRACT_relay_number)  # B2:R4 - OFF
        self.wait(10)
        # print("Tilt Completed ")
        self.compare_logs(logs_to_compare, SuccessFlag=True, is_firing_test=True, fixtureValidation=fixture_validation_req)
        if fixture_validation_req:
            pass
        else:
            print(f'STEP : {logs_to_compare} performed!')

    def TiltOpen(self, logs_to_compare='Tilt Operation of Anvil', fixture_validation_req=False):  ### Remove Open in the funciton name - To Do
        self.my_Serthread.clearQue()
        self.wait(5)
        self.Switch_ONN_Relay(Bank_number=self.RETRACT_bank_number,
                              Relay_number=self.RETRACT_relay_number)  # B2:R4 - ON
        self.wait(0.5)
        self.Switch_OFF_Relay(Bank_number=self.RETRACT_bank_number,
                              Relay_number=self.RETRACT_relay_number)  # B2:R4 - OFF
        self.wait(10)
        print("Tilt Completed ")
        self.compare_logs(logs_to_compare, SuccessFlag=True, is_firing_test=True, fixtureValidation=fixture_validation_req)
        if fixture_validation_req:
            pass
        else:
            print(f'STEP : {logs_to_compare} performed!')

    def TiltPromptOpen_original(self, logs_to_compare='Tilt Prompt Open', fixture_validation_req=False):
        self.my_Serthread.clearQue()
        self.Switch_ONN_Relay(Bank_number=self.RETRACT_bank_number,
                              Relay_number=self.RETRACT_relay_number)  # B2:R4 - ON
        self.wait(7)
        self.Switch_OFF_Relay(Bank_number=self.RETRACT_bank_number,
                              Relay_number=self.RETRACT_relay_number)  # B2:R4 - OFF

        print("Tilt Prompt Open Completed")
        self.compare_logs(logs_to_compare, SuccessFlag=True, is_firing_test=True, fixtureValidation=fixture_validation_req)
        if fixture_validation_req:
            pass
        else:
            print(f'STEP : {logs_to_compare} performed!')

        self.handle_fire_count_2, self.status_data_2 = self.read_status_variables()
        status_variables_2 = self.status_data_2['status_variables']
        print('StatusVariable After Firing', status_variables_2)



    def TiltOpenPrompt_400860(self, logs_to_compare='Tilt Prompt Open'):
        self.my_Serthread.clearQue()
        # 5.1.29.	Press and hold the up toggle for 3 seconds until the trocar begins to extend.
        # Within a few seconds, detach the adapter from the clamshell.
        self.Switch_ONN_Relay(Bank_number=self.RETRACT_bank_number,
                              Relay_number=self.RETRACT_relay_number)  # B2:R4 - ON
        self.wait(5)

        # Remove Adapter - during tilt prompt open
        self.removeAdapter_DV()
        self.wait(15)

        self.Switch_OFF_Relay(Bank_number=self.RETRACT_bank_number,
                              Relay_number=self.RETRACT_relay_number)  # B2:R4 - OFF

        self.wait(5)

        # 5.1.30.	Wait a few seconds and then reattach adapter to clamshell.
        # Wait for the timer to complete and confirm that the device requires an up-toggle press to resume
        # extending the anvil to the tilt open (cleanability) position (250352).
        self.Connect_Adapter()
        self.wait(15)

        self.Switch_ONN_Relay(Bank_number=self.RETRACT_bank_number,
                              Relay_number=self.RETRACT_relay_number)  # B2:R4 - ON
        self.wait(5)

        self.Switch_OFF_Relay(Bank_number=self.RETRACT_bank_number,
                              Relay_number=self.RETRACT_relay_number)  # B2:R4 - OFF

        # screen_name = "Tilt_Open_Prompt_Position"
        # folder_name = "Tilt_Open_Prompt_Position"
        # file_name = "Tilt_Open_Prompt_Position"
        # self.handle_screen(videoPath=self.videoPath, screen_name=screen_name, folder_name=folder_name,
        #                    file_name=file_name, is_static_image=True)

        self.compare_logs(logs_to_compare, SuccessFlag=True, is_firing_test=True)
        print(f'STEP : {logs_to_compare} performed!')

    def TiltOpenPrompt_450475(self, logs_to_compare='Tilt Prompt Open'):
        self.my_Serthread.clearQue()
        self.wait(5)
        self.Switch_ONN_Relay(Bank_number=self.RETRACT_bank_number,
                              Relay_number=self.RETRACT_relay_number)  # B2:R4 - ON
        # self.my_Serthread.__log_to_be_found = 'ACK, ACK, ACK - TO WMotHead Opening State'
        # pre_time = time.time()
        # while not self.my_Serthread.is_log_found and (time.time() - pre_time) < 10:
        #     continue
        is_found = self.my_Serthread.waitUntilString('ACK, ACK, ACK - TO WMotHead Opening State')
        self.Switch_OFF_Relay(Bank_number=self.RETRACT_bank_number,
                              Relay_number=self.RETRACT_relay_number)  # B2:R4 - OFF
        if is_found == 'ACK, ACK, ACK - TO WMotHead Opening State':
            print('Wait 3.7 Sec and remove adapter')
            self.wait(3.7)

            self.my_Serthread.log_to_be_found = None
            self.my_Serthread.is_log_found = False
            # self.removeAdapter()

            self.Switch_OFF_ALL_Relays_In_Each_Bank(1)  # Disconnecting Bank 1
            self.Switch_ONN_Relay(1, 5)  # Connecting Clamshell
            previous_time = time.time()
            # From Adapter EEPROM
            print("before error ")
            startPosition, backLash, motorStatus, movement_distance_Byte_No, movement_distance_Bit_No = GetAdapterEepromRecoveryPositionalData(
                self.FtdiUartComPort)
            print("Recovery Position data :", startPosition, backLash, motorStatus, movement_distance_Byte_No,
                  movement_distance_Bit_No)
            # RecoveryReload1WEE = GetAdapterEepromRecoveryReload1WEE(self.FtdiUartComPort)
            # print("Recovery Reload 1W EE :", RecoveryReload1WEE)
            # RecoveryID, ErrorCode = GetAdapterEepromRecoveryData(self.FtdiUartComPort)
            # print("Recovery Id data  :", RecoveryID, ErrorCode)
            # TareCount, procedureCount, FireCount = GetAdapterEepromRecoveryAdapterData(self.FtdiUartComPort)
            # print("Recovery Adapter data :", TareCount, procedureCount, FireCount)
            # post_time = time.time()
            read_time = time.time() - previous_time
            # read_and_write_adapter_eeprom_recovery_position_data(self.FtdiUartComPort)
            self.wait(5.5 - read_time)
            self.my_Serthread.clearQue()
            # self.connect_adapter_test(is_delay_required=False)
            self.Switch_ONN_ALL_Relays_In_Each_Bank(1)
            # self.my_Serthread.log_to_be_found = 'EEA Adapter Values, StartPos(0)'
            # pre_time = time.time()
            # while not self.my_Serthread.is_log_found and (time.time() - pre_time) < 30:
            #     continue

            result_string = self.my_Serthread.waitUntilString('EEA Adapter Values, StartPos(0)')
            # self.my_Serthread.log_to_be_found = None
            # self.my_Serthread.is_log_found = False
            print(simple_colors.yellow(f"result_string : {result_string}"))

            if result_string != 'EEA Adapter Values, StartPos(0)':
                ### press and hold Up key
                self.Switch_ONN_Relay(Bank_number=self.RETRACT_bank_number,
                                      Relay_number=self.RETRACT_relay_number)  # B2:R4 - ON
                print("Pressing Open key - Continue Tilt open ")
                self.wait(6)

                self.Switch_OFF_Relay(Bank_number=self.RETRACT_bank_number,
                                      Relay_number=self.RETRACT_relay_number)  # B2:R4 - OFF
                self.wait(10)
            else:  # Failure Scenario ( string founds )
                self.removeAdapter()

                self.failuerCntr += 1
                print("No of times to Found the String : ", self.failuerCntr)
                # Engaging the Adapter
                # self.Switch_ONN_Relay(1, 8)
                # print("EEA Adapter Engaged to Power Pack Mechanically")

                self.wait(7)
                # self.DisconnectingEEAReload()
                # self.wait(5)

                # From Adapter EEPROM
                startPosition, backLash, motorStatus, movement_distance_Byte_No, movement_distance_Bit_No = GetAdapterEepromRecoveryPositionalData(
                    self.FtdiUartComPort)
                print("Recovery Position data :", startPosition, backLash, motorStatus, movement_distance_Byte_No,
                      movement_distance_Bit_No)
                RecoveryReload1WEE = GetAdapterEepromRecoveryReload1WEE(self.FtdiUartComPort)
                print("Recovery Reload 1W EE :", RecoveryReload1WEE)
                RecoveryID, ErrorCode = GetAdapterEepromRecoveryData(self.FtdiUartComPort)
                print("Recovery Id data  :", RecoveryID, ErrorCode)
                TareCount, procedureCount, FireCount = GetAdapterEepromRecoveryAdapterData(self.FtdiUartComPort)
                print("Recovery Adapter data :", TareCount, procedureCount, FireCount)

                # Remove Reload
                self.Switch_OFF_Relay(3, 2)  # B3:R2 - ON
                self.Switch_OFF_Relay(3, 3)  # B3:R3 - ON

                # From Adapter Onewire EEPROM
                # For capturing Onewire Usage counts from the Adapter via BB, below relays should be ON.
                # To Connect adapter to BB Clutch should be enaged
                #############################################################
                # Relay Numbers Updated - GND Updated 5,8 to 5,5 - 06/03/2025
                #############################################################
                self.Switch_ONN_Relay(5, 5)  # B5:R8 - ON
                self.Switch_ONN_Relay(6, 1)  # B6:R1 - ON

                adapter_1w_eeprom_data = self.read_eeprom_data()
                print("Adapter Onewire EEPROM Data ", adapter_1w_eeprom_data)

                self.Switch_OFF_Relay(6, 1)  # B6:R1 - OFF
                self.Switch_OFF_Relay(5, 5)  # B5:R8 - OFF

                self.my_Serthread.clearQue()
                OLEDRecordingThread.exitFlag = True
                sys.exit()
                # self.connect_adapter_test()
                #
                # ### press and hold Up key
                # self.Switch_ONN_Relay(Bank_number=self.RETRACT_bank_number,
                #                       Relay_number=self.RETRACT_relay_number)  # B2:R4 - ON
                # self.wait(6)
                #
                # self.Switch_OFF_Relay(Bank_number=self.RETRACT_bank_number,
                #                       Relay_number=self.RETRACT_relay_number)  # B2:R4 - OFF

    def Retracting(self, logs_to_compare='Retracting', retract_delay=10):
        self.my_Serthread.clearQue()
        self.Switch_ONN_Relay(Bank_number=self.RETRACT_bank_number, Relay_number=self.RETRACT_relay_number)
        self.wait(1)
        self.Switch_OFF_Relay(Bank_number=self.RETRACT_bank_number, Relay_number=self.RETRACT_relay_number)
        self.wait(retract_delay)
        self.compare_logs(logs_to_compare, SuccessFlag=True, is_firing_test=True)
        # # logger.info(f"Step: {logs_to_compare} Performed")
        print(f'STEP : {logs_to_compare} performed!')

    def Unclamping(self, SuccessFlag=True, is_firing_test=False, logs_to_compare='Clamp Cycle Test Un-Clamping'):
        # logs_to_compare = 'Clamp Cycle Test Un-Clamping'
        self.my_Serthread.clearQue()
        self.Switch_ONN_Relay(Bank_number=self.unclamp_bank_number, Relay_number=self.unclamp_relay_number)
        self.wait(10)
        self.Switch_OFF_Relay(Bank_number=self.unclamp_bank_number, Relay_number=self.unclamp_relay_number)
        self.compare_logs(logs_to_compare, SuccessFlag=SuccessFlag, is_firing_test=is_firing_test,
                          event_name='Reload_Fully_Open', is_event_connecting=True)
        # # # logger.info(f"Step: {logs_to_compare} Performed")
        print(f"Step: {logs_to_compare} Performed")

    def Articulation(self):
        self.Switch_ONN_Relay(2, 3)  # B2:R3 - ON
        self.Switch_OFF_Relay(2, 3)  # B2:R3 - OFF
        self.Switch_ONN_Relay(2, 6)  # B2:R6 - ON
        self.Switch_OFF_Relay(2, 6)  # B2:R6 - OFF

    def right_clockwise_rotation(self, relay_switch_over_delay, SuccessFlag, is_firing_test,
                                 is_emergency_retraction=False):
        logs_to_compare = 'Adapter CW Rotated'
        if is_emergency_retraction:
            logs_to_compare = "Adapter CW Rotated - Emergency Retraction"
        if self.serPP is not None:
            self.my_Serthread.clearQue()
        rotate_success_flag = True
        if relay_switch_over_delay < 0.25 or not SuccessFlag:
            rotate_success_flag = False
        self.wait(0.01)
        before_time = time.time()
        self.Switch_ONN_Relay(Bank_number=self.RCW_ROTATION_bank_number,
                              Relay_number=self.RCW_ROTATION_relay_number)
        self.wait(relay_switch_over_delay - 0.05)  # 50 ms is already being provided while switching ON the relay
        self.Switch_OFF_Relay(Bank_number=self.RCW_ROTATION_bank_number,
                              Relay_number=self.RCW_ROTATION_relay_number)
        after_time = time.time()
        print(f"Elapsed time: {after_time - before_time - 0.05}")
        if self.serPP is not None:
            self.compare_logs(logs_to_compare, rotate_success_flag, is_firing_test=is_firing_test)
        # print(self.Test_Results)
        # # logger.info(f"Step: {logs_to_compare} Performed")
        self.wait(2)

    def left_clockwise_rotation(self, relay_switch_over_delay, SuccessFlag, is_firing_test,
                                is_emergency_retraction=False):
        logs_to_compare = 'Adapter CW Rotated'
        if is_emergency_retraction:
            logs_to_compare = "Adapter CW Rotated - Emergency Retraction"
        if self.serPP is not None:
            self.my_Serthread.clearQue()
        rotate_success_flag = True
        if relay_switch_over_delay < 0.25 or not SuccessFlag:
            rotate_success_flag = False
        self.wait(0.01)
        before_time = time.time()
        self.Switch_ONN_Relay(Bank_number=self.LCW_ROTATION_bank_number,
                              Relay_number=self.LCW_ROTATION_relay_number)
        self.wait(relay_switch_over_delay - 0.05)
        self.Switch_OFF_Relay(Bank_number=self.LCW_ROTATION_bank_number,
                              Relay_number=self.LCW_ROTATION_relay_number)
        after_time = time.time()
        print(f"Elapsed time: {after_time - before_time - 0.05}")
        if self.serPP is not None:
            self.compare_logs(logs_to_compare, rotate_success_flag, is_firing_test=is_firing_test)
        # print(self.Test_Results)
        # # logger.info(f"Step: {logs_to_compare} Performed")
        self.wait(2)

    def right_counter_clockwise_rotation(self, relay_switch_over_delay, SuccessFlag, is_firing_test,
                                         is_emergency_retraction=False):
        logs_to_compare = 'Adapter CCW Rotated'
        if is_emergency_retraction:
            logs_to_compare = "Adapter CCW Rotated - Emergency Retraction"
        if self.serPP is not None:
            self.my_Serthread.clearQue()
        rotate_success_flag = True
        if relay_switch_over_delay < 0.25 or not SuccessFlag:
            rotate_success_flag = False
        self.wait(0.01)
        self.Switch_ONN_Relay(Bank_number=self.RCCW_ROTATION_bank_number,
                              Relay_number=self.RCCW_ROTATION_relay_number)
        self.wait(relay_switch_over_delay - 0.05)
        self.Switch_OFF_Relay(Bank_number=self.RCCW_ROTATION_bank_number,
                              Relay_number=self.RCCW_ROTATION_relay_number)
        if self.serPP is not None:
            self.compare_logs(logs_to_compare, rotate_success_flag, is_firing_test=is_firing_test)
        # print(self.Test_Results)
        # # logger.info(f"Step: {logs_to_compare} Performed")
        self.wait(2)

    def left_counter_clockwise_rotation(self, relay_switch_over_delay, SuccessFlag, is_firing_test,
                                        is_emergency_retraction=False):
        logs_to_compare = 'Adapter CCW Rotated'
        if is_emergency_retraction:
            logs_to_compare = "Adapter CCW Rotated - Emergency Retraction"
        if self.serPP is not None:
            self.my_Serthread.clearQue()
        rotate_success_flag = True
        if relay_switch_over_delay < 0.25 or not SuccessFlag:
            rotate_success_flag = False
        self.wait(0.01)
        self.Switch_ONN_Relay(Bank_number=self.LCCW_ROTATION_bank_number,
                              Relay_number=self.LCCW_ROTATION_relay_number)
        self.wait(relay_switch_over_delay - 0.05)
        self.Switch_OFF_Relay(Bank_number=self.LCCW_ROTATION_bank_number,
                              Relay_number=self.LCCW_ROTATION_relay_number)
        if self.serPP is not None:
            self.compare_logs(logs_to_compare, rotate_success_flag, is_firing_test=is_firing_test)
        # print(self.Test_Results)
        # logger.info(f"Step: {logs_to_compare} Performed")
        self.wait(2)

    # Direction for rotation will be one of "RCW", "LCW", "RCCW", "LCCW". If None all operations will be performed
    # sequentially one after other in RCW, LCW, RCCW, LCCW manner.
    def rotation_with_direction(self, direction=None, relay_switch_over_delay=0, SuccessFlag=True,
                                is_firing_test=False, is_emergency_retraction=False):
        # updating the delay between the switch ON to switch OFF the relay.
        # If it is 0, updating it to default delay to complete the rotation.
        # Else updating it to the specified value.
        # logger.info(f"articulation direction = {direction}, relay_switch_over_delay = {relay_switch_over_delay},"
        #             f"is_firing_test = {is_firing_test}, SuccessFlag= {SuccessFlag}, is_emergency_retraction = "
        #             f"{is_emergency_retraction}")
        if relay_switch_over_delay == 0:
            relay_switch_over_delay = rotate_default_delay
        if direction is None:
            self.right_clockwise_rotation(relay_switch_over_delay, SuccessFlag, is_firing_test, is_emergency_retraction)
            self.right_counter_clockwise_rotation(relay_switch_over_delay, SuccessFlag, is_firing_test,
                                                  is_emergency_retraction)
            self.left_clockwise_rotation(relay_switch_over_delay, SuccessFlag, is_firing_test, is_emergency_retraction)
            self.left_counter_clockwise_rotation(relay_switch_over_delay, SuccessFlag, is_firing_test,
                                                 is_emergency_retraction)
        elif direction.upper() == 'RCW':
            self.right_clockwise_rotation(relay_switch_over_delay, SuccessFlag, is_firing_test, is_emergency_retraction)
        elif direction.upper() == 'LCW':
            self.left_clockwise_rotation(relay_switch_over_delay, SuccessFlag, is_firing_test, is_emergency_retraction)
        elif direction.upper() == 'RCCW':
            self.right_counter_clockwise_rotation(relay_switch_over_delay, SuccessFlag, is_firing_test,
                                                  is_emergency_retraction)
        elif direction.upper() == 'LCCW':
            self.left_counter_clockwise_rotation(relay_switch_over_delay, SuccessFlag, is_firing_test,
                                                 is_emergency_retraction)

    def right_articulation(self, relay_switch_over_delay, SuccessFlag, is_firing_test, is_emergency_retraction=False):
        logs_to_compare = 'Right Articulation'
        if is_emergency_retraction:
            logs_to_compare = "Right Articulation - Emergency Retraction"
        self.my_Serthread.clearQue()
        # articulate_success_flag = True
        # if relay_switch_over_delay < 0.25 or not SuccessFlag:
        #     articulate_success_flag = False
        self.wait(0.01)
        self.Switch_ONN_Relay(Bank_number=self.right_articulation_bank_number,
                              Relay_number=self.right_articulation_relay_number)
        self.wait(relay_switch_over_delay - 0.05)
        self.Switch_OFF_Relay(Bank_number=self.right_articulation_bank_number,
                              Relay_number=self.right_articulation_relay_number)
        self.compare_logs(logs_to_compare, SuccessFlag, is_firing_test=is_firing_test)
        # print(self.Test_Results)
        # logger.info(f"Step: {logs_to_compare} Performed")
        self.wait(2)

    def left_articulation(self, relay_switch_over_delay, SuccessFlag, is_firing_test, is_emergency_retraction=False):
        logs_to_compare = 'Left Articulation'
        if is_emergency_retraction:
            logs_to_compare = "Left Articulation - Emergency Retraction"
        self.my_Serthread.clearQue()
        # articulate_success_flag = True
        # if relay_switch_over_delay < 0.25 or not SuccessFlag:
        #     articulate_success_flag = False

        self.wait(0.01)
        self.Switch_ONN_Relay(Bank_number=self.left_articulation_bank_number,
                              Relay_number=self.left_articulation_relay_number)
        self.wait(relay_switch_over_delay - 0.05)
        self.Switch_OFF_Relay(Bank_number=self.left_articulation_bank_number,
                              Relay_number=self.left_articulation_relay_number)
        self.compare_logs(logs_to_compare, SuccessFlag, is_firing_test=is_firing_test)
        # print(self.Test_Results)
        # logger.info(f"Step: {logs_to_compare} Performed")
        self.wait(2)

    def center_articulation(self, relay_switch_over_delay, SuccessFlag, is_firing_test):
        logs_to_compare = 'Centering Articulation'
        self.my_Serthread.clearQue()
        # articulate_success_flag = True
        # if relay_switch_over_delay != articulate_default_delay or not SuccessFlag:
        #     articulate_success_flag = False
        self.wait(0.01)
        self.Switch_ONN_Relay(Bank_number=self.center_articulation_bank_number,
                              Relay_number=self.center_articulation_relay_number)
        self.wait(relay_switch_over_delay - 0.05)
        self.Switch_OFF_Relay(Bank_number=self.center_articulation_bank_number,
                              Relay_number=self.center_articulation_relay_number)
        self.compare_logs(logs_to_compare, SuccessFlag, is_firing_test=is_firing_test)
        # print(self.Test_Results)
        # logger.info(f"Step: {logs_to_compare} Performed")
        self.wait(2)

    # Direction for articulation will be one of "R", "L", "C". If None, it will perform right, left and center
    # articulations sequentially, one after other
    def articulation_with_direction(self, direction=None, relay_switch_over_delay=0, SuccessFlag=True,
                                    is_firing_test=False):
        # updating the delay between the switch ON to switch OFF the relay.
        # If it is 0, updating it to default delay to complete the articulation.
        # Else updating it to the specified value.
        # logger.info(f"articulation direction = {direction}, relay_switch_over_delay = {relay_switch_over_delay},"
        #             f"is_firing_test = {is_firing_test}, SuccessFlag= {SuccessFlag}")
        if relay_switch_over_delay == 0:
            relay_switch_over_delay = articulate_default_delay
        if direction is None:
            self.right_articulation(relay_switch_over_delay, SuccessFlag, is_firing_test)
            self.center_articulation(relay_switch_over_delay, SuccessFlag, is_firing_test)
            self.left_articulation(relay_switch_over_delay, SuccessFlag, is_firing_test)
            self.center_articulation(relay_switch_over_delay, SuccessFlag, is_firing_test)
        elif direction.upper() == 'R':
            self.right_articulation(relay_switch_over_delay, SuccessFlag, is_firing_test)
        elif direction.upper() == 'L':
            self.left_articulation(relay_switch_over_delay, SuccessFlag, is_firing_test)
        elif direction.upper() == 'C':
            self.center_articulation(relay_switch_over_delay, SuccessFlag, is_firing_test)

    def fetch_parameter(self, data, index):
        result = None
        if type(data) is list:
            if index > len(data):
                result = data[len(data) - 1]
            else:
                result = data[index]
        elif type(data) is int:
            result = data
        elif type(data) is str:
            result = data
        elif type(data) is float:
            result = data

        return result

    def eea_left_articulation(self):
        logs_to_compare = 'Articulation During SP IP'

        self.my_Serthread.clearQue()
        articulate_success_flag = True

        self.wait(0.01)
        self.Switch_ONN_Relay(Bank_number=self.left_articulation_bank_number,
                              Relay_number=self.left_articulation_relay_number)
        self.wait(7)
        self.Switch_OFF_Relay(Bank_number=self.left_articulation_bank_number,
                              Relay_number=self.left_articulation_relay_number)
        self.compare_logs(logs_to_compare, articulate_success_flag)
        # print(self.Test_Results)
        # logger.info(f"Step: {logs_to_compare} Performed")
        self.wait(2)

    def eea_close_key_operation(self):
        logs_to_compare = 'Close Operation During SP IP'

        self.my_Serthread.clearQue()
        articulate_success_flag = True

        self.wait(0.01)
        self.Switch_ONN_Relay(Bank_number=self.FIRING_bank_number,
                              Relay_number=self.FIRING_relay_number)
        self.wait(10)
        self.Switch_OFF_Relay(Bank_number=self.FIRING_bank_number,
                              Relay_number=self.FIRING_relay_number)
        self.compare_logs(logs_to_compare, articulate_success_flag)
        # print(self.Test_Results)
        # logger.info(f"Step: {logs_to_compare} Performed")
        self.wait(2)

    def eea_right_clockwise_rotation(self):
        logs_to_compare = 'Rotation During SP IP'
        if self.serPP is not None:
            self.my_Serthread.clearQue()
        rotate_success_flag = True

        self.wait(0.01)
        self.Switch_ONN_Relay(Bank_number=self.RCW_ROTATION_bank_number,
                              Relay_number=self.RCW_ROTATION_relay_number)
        self.wait(7)
        self.Switch_OFF_Relay(Bank_number=self.RCW_ROTATION_bank_number,
                              Relay_number=self.RCW_ROTATION_relay_number)
        if self.serPP is not None:
            self.compare_logs(logs_to_compare, rotate_success_flag)
        # print(self.Test_Results)
        # # logger.info(f"Step: {logs_to_compare} Performed")
        self.wait(2)

    #  Disconnecting the Adapter During EEA Stapling In Progress
    def IS_12_Firing(self, test_parameters, logs_to_compare=None):
        # Case 1: Firing Recovery
        if 1 == test_parameters["case_id"]:
            if 1 == test_parameters["adapter_removed_1st_eea_stapling"]:
                logs_to_compare = 'Remove Adapter When 1st EEA Stapling In Progress'
            elif 2 == test_parameters["adapter_removed_2nd_eea_stapling"]:
                logs_to_compare = 'Remove Adapter When 2nd EEA Stapling In Progress'

            fire_success_flag = True

            self.apply_load_force(3.25)
            self.my_Serthread.clearQue()
            self.wait(5)
            self.Switch_ONN_Relay(Bank_number=self.EEA_STAPLING_ONE_bank_number,
                                  Relay_number=self.EEA_STAPLING_ONE_relay_number)  # B4:R1 - ON
            self.Switch_ONN_Relay(Bank_number=self.EEA_STAPLING_TWO_bank_number,
                                  Relay_number=self.EEA_STAPLING_TWO_relay_number)  # B4:R2 - ON
            self.wait(3)
            self.Switch_ONN_Relay(Bank_number=self.FIRING_bank_number,
                                  Relay_number=self.FIRING_relay_number)  # B2:R5 - ON
            self.wait(0.5)
            self.Switch_OFF_Relay(Bank_number=self.FIRING_bank_number,
                                  Relay_number=self.FIRING_relay_number)  # B2:R5 - OFF
            self.wait(4)

            # Removing Adapter When 1st EEA Stapling is In-Progress
            if 1 == test_parameters["adapter_removed_1st_eea_stapling"]:
                print("Remove Adapter when 1st EEA Stapling In Progress")
                self.Switch_OFF_Relay(1, 8)  # B1:R8 - Turning Off - Adapter Clutch Disengaged
                self.removeAdapter()
                # Making default so not entering into next time
                test_parameters["adapter_removed_1st_eea_stapling"] = 0
                self.wait(2)

            self.Switch_OFF_Relay(Bank_number=self.EEA_STAPLING_ONE_bank_number,
                                  Relay_number=self.EEA_STAPLING_ONE_relay_number)  # B4:R1 - OFF
            self.Switch_OFF_Relay(Bank_number=self.EEA_STAPLING_TWO_bank_number,
                                  Relay_number=self.EEA_STAPLING_TWO_relay_number)  # B4:R2 - OFF
            self.wait(3)
            self.apply_load_force(0)

            # Remove Adapter when 2nd EEA Stapling In Progress
            if 2 == test_parameters["adapter_removed_2nd_eea_stapling"]:
                print("Remove Adapter when 1st EEA Stapling In Progress")
                self.Switch_OFF_Relay(1, 8)  # B1:R8 - Turning Off - Adapter Clutch Disengaged
                self.removeAdapter()
                # Making default so not entering into next time
                test_parameters["adapter_removed_2nd_eea_stapling"] = 0
                self.wait(2)

            self.wait(5)
            self.compare_logs(logs_to_compare, SuccessFlag=fire_success_flag, is_firing_test=True)
            # # logger.info(f"Step: {logs_to_compare} Performed")
            print(f'STEP : {logs_to_compare} performed!')

        # Case 2: Cutting Recovery
        elif 2 == test_parameters["case_id"]:
            if 3 == test_parameters["adapter_removed_cutting_starts"]:
                logs_to_compare = 'Remove Adapter When Cutting Starts'
            elif 4 == test_parameters["adapter_removed_cut_recovery"]:
                logs_to_compare = 'Remove Adapter When 2nd EEA Stapling In Progress'

            fire_success_flag = True

            self.apply_load_force(3.25)
            self.my_Serthread.clearQue()
            self.wait(5)
            self.Switch_ONN_Relay(Bank_number=self.EEA_STAPLING_ONE_bank_number,
                                  Relay_number=self.EEA_STAPLING_ONE_relay_number)  # B4:R1 - ON
            self.Switch_ONN_Relay(Bank_number=self.EEA_STAPLING_TWO_bank_number,
                                  Relay_number=self.EEA_STAPLING_TWO_relay_number)  # B4:R2 - ON
            self.wait(3)
            self.Switch_ONN_Relay(Bank_number=self.FIRING_bank_number,
                                  Relay_number=self.FIRING_relay_number)  # B2:R5 - ON
            self.wait(0.5)
            self.Switch_OFF_Relay(Bank_number=self.FIRING_bank_number,
                                  Relay_number=self.FIRING_relay_number)  # B2:R5 - OFF
            self.wait(4)
            self.Switch_OFF_Relay(Bank_number=self.EEA_STAPLING_ONE_bank_number,
                                  Relay_number=self.EEA_STAPLING_ONE_relay_number)  # B4:R1 - OFF
            self.Switch_OFF_Relay(Bank_number=self.EEA_STAPLING_TWO_bank_number,
                                  Relay_number=self.EEA_STAPLING_TWO_relay_number)  # B4:R2 - OFF
            self.wait(3)
            self.apply_load_force(0)
            self.Switch_ONN_Relay(Bank_number=self.EEA_CUTTING_ONE_bank_number,
                                  Relay_number=self.EEA_CUTTING_ONE_relay_number)  # B4:R3 - ON
            self.Switch_ONN_Relay(Bank_number=self.EEA_CUTTING_TWO_bank_number,
                                  Relay_number=self.EEA_CUTTING_TWO_relay_number)  # B4:R4 - ON

            # Remove Adapter when Cutting Starts
            if 3 == test_parameters["adapter_removed_cutting_starts"]:
                print("Remove Adapter when Cutting Starts")
                self.Switch_OFF_Relay(1, 8)  # B1:R8 - Turning Off - Adapter Clutch Disengaged
                self.removeAdapter()
                # Making default so not entering into next time
                test_parameters["adapter_removed_cutting_starts"] = 0

            self.wait(5)
            self.Switch_OFF_Relay(Bank_number=self.EEA_CUTTING_ONE_bank_number,
                                  Relay_number=self.EEA_CUTTING_ONE_relay_number)  # B4:R3 - OFF
            self.Switch_OFF_Relay(Bank_number=self.EEA_CUTTING_TWO_bank_number,
                                  Relay_number=self.EEA_CUTTING_TWO_relay_number)  # B4:R4 - OFF

            if 4 == test_parameters["adapter_removed_cut_recovery"]:
                print("Remove Adapter when Cutting Starts")
                self.Switch_OFF_Relay(1, 8)  # B1:R8 - Turning Off - Adapter Clutch Disengaged
                self.removeAdapter()
                # Making default so not entering into next time
                test_parameters["adapter_removed_cutting_starts"] = 0
            self.wait(.5)
            self.Switch_ONN_Relay(Bank_number=self.EEA_CUTTING_COMPLETE_ONE_bank_number,
                                  Relay_number=self.EEA_CUTTING_COMPLETE_ONE_relay_number)  # B4:R5 - ON
            self.Switch_ONN_Relay(Bank_number=self.EEA_CUTTING_COMPLETE_TWO_bank_number,
                                  Relay_number=self.EEA_CUTTING_COMPLETE_TWO_relay_number)  # B4:R6 - ON
            self.wait(30)
            self.compare_logs(logs_to_compare, SuccessFlag=fire_success_flag, is_firing_test=True)
            # # logger.info(f"Step: {logs_to_compare} Performed")
            print(f'STEP : {logs_to_compare} performed!')
            self.Switch_OFF_Relay(Bank_number=self.EEA_CUTTING_COMPLETE_ONE_bank_number,
                                  Relay_number=self.EEA_CUTTING_COMPLETE_ONE_relay_number)  # B4:R5 - OFF
            self.Switch_OFF_Relay(Bank_number=self.EEA_CUTTING_COMPLETE_TWO_bank_number,
                                  Relay_number=self.EEA_CUTTING_COMPLETE_TWO_relay_number)  # B4:R6 - OFF

    def EEA_IS_12_N_Firing(self, test_parameters, reload_parameters, firing_duration=0):
        fire_pass = 0
        # Record System Status variables Before Firing - Reading System Errors and System Warnings
        HandleFireCount1, status_data = self.read_status_variables()

        for procedure_firing in range(reload_parameters["procedure_firings_count"]):
            video_name = reload_parameters["video_name"] + f"_proc_{procedure_firing}"

            reload_length = self.fetch_parameter(data=reload_parameters["reload_length"], index=procedure_firing)
            reload_color = self.fetch_parameter(data=reload_parameters["reload_color"], index=procedure_firing)
            print(simple_colors.blue(f"reload_state = {reload_parameters['reload_state']}"))

            self.connect_reload(firing_count=f"{reload_parameters['firing_count']}_iteration_{procedure_firing + 1}",
                                reload_type=reload_parameters["reload_type"],
                                reload_color=reload_color,
                                reload_length=reload_length,
                                video_name=video_name,
                                reload_state=reload_parameters['reload_state'],
                                ship_cap_status=reload_parameters["ship_cap_presence"]
                                )

            if firing_duration == 0:
                firing_duration = firing_default_delay

            # Clamping on Tissue - Retraction of Trocar Until Clamp GAP is reached
            self.EEAClamping(SuccessFlag=True, is_firing_test=True, logs_to_compare='EEA Clamping on Tissue')

            self.wait(2)
            # Safety Key Acknowledgement
            self.GreenKeyAck(SuccessFlag=True)

            # Firing
            # During Firing Disconnecting the Adapter When 1st EEA and 2nd EEA Stapling is In-Progress
            if 1 == test_parameters["firingValue"] or \
                    2 == test_parameters["firingValue"] or 3 == test_parameters["firingValue"] or \
                    4 == test_parameters["firingValue"]:
                self.IS_12_Firing(test_parameters)

    def adapter_UART_Rx_Tx_OC_before_firing(self, clampingForce, firingForce, reload_parameters, firing_duration=0):
        fire_pass = 0
        firings = reload_parameters["procedure_firings_count"]
        print(simple_colors.blue(f"firing details for the iteration: {self.json_data}"))

        for procedure_firing in range(reload_parameters["procedure_firings_count"]):
            video_name = reload_parameters["video_name"] + f"_proc_{procedure_firing}"

            reload_length = self.fetch_parameter(data=reload_parameters["reload_length"], index=procedure_firing)
            reload_color = self.fetch_parameter(data=reload_parameters["reload_color"], index=procedure_firing)
            cartridge_color = self.fetch_parameter(data=reload_parameters["cartridge_color"], index=procedure_firing)
            print(simple_colors.blue(f"reload_state = {reload_parameters['reload_state']}\ncartridge_state = "
                                     f"{reload_parameters['cartridge_state']}"))

            self.my_Serthread.clearQue()
            self.wait(5)

            self.connect_reload(firing_count=f"{reload_parameters['firing_count']}_iteration_{procedure_firing + 1}",
                                reload_type=reload_parameters["reload_type"],
                                reload_color=reload_color,
                                reload_length=reload_length,
                                video_name=video_name,
                                reload_state=reload_parameters['reload_state'],
                                cartridge_state=reload_parameters['cartridge_state'],
                                cartridge_color=cartridge_color,
                                ship_cap_status=reload_parameters["ship_cap_presence"]
                                )

            self.EEAClamping(SuccessFlag=True, is_firing_test=True, logs_to_compare='EEA Clamping on Tissue',
                             clamp_force=clampingForce, fire_force=firingForce)

            print("Open Circuiting Adapter UART Rx & Tx")
            self.Switch_OFF_Relay(1, 3)
            self.Switch_OFF_Relay(1, 4)
            self.wait(10)
            logs_to_compare = 'EEA Adapter UART Rx & Tx Open Circuit'
            self.compare_logs(logs_to_compare, SuccessFlag=True, is_firing_test=True)
            print(f'STEP : {logs_to_compare} performed!')

            # Restoring Adapter UART Connections
            print("Restoring Adapter UART Rx & Tx")
            self.Switch_ONN_Relay(1, 3)
            self.Switch_ONN_Relay(1, 4)
            self.wait(10)
            logs_to_compare = 'EEA Adapter UART Rx & Tx Open Circuit Restored'
            self.compare_logs(logs_to_compare, SuccessFlag=True, is_firing_test=True)
            print(f'STEP : {logs_to_compare} performed!')

            self.wait(2)
            self.GreenKeyAck(SuccessFlag=True)

            self.apply_load_force(0)
            self.Switch_ONN_Relay(2, 4)
            self.wait(10)
            self.Switch_OFF_Relay(2, 4)

            if reload_parameters["reload_type"] == "EEA":
                self.DisconnectingEEAReload()

            if procedure_firing != reload_parameters["procedure_firings_count"] - 1:
                self.is_firing_test_passed(procedure_firing, reload_parameters["firing_count"], fire_pass)
                fire_pass += 1

        self.is_firing_test_passed(reload_parameters["procedure_firings_count"] - 1, reload_parameters["firing_count"],
                                   fire_pass)

    def adapter_UART_Rx_Tx_OC_after_firing(self, clampingForce, firingForce, reload_parameters, firing_duration=0):
        fire_pass = 0
        firings = reload_parameters["procedure_firings_count"]
        print(simple_colors.blue(f"firing details for the iteration: {self.json_data}"))

        for procedure_firing in range(reload_parameters["procedure_firings_count"]):
            video_name = reload_parameters["video_name"] + f"_proc_{procedure_firing}"

            reload_length = self.fetch_parameter(data=reload_parameters["reload_length"], index=procedure_firing)
            reload_color = self.fetch_parameter(data=reload_parameters["reload_color"], index=procedure_firing)
            cartridge_color = self.fetch_parameter(data=reload_parameters["cartridge_color"], index=procedure_firing)
            print(simple_colors.blue(f"reload_state = {reload_parameters['reload_state']}\ncartridge_state = "
                                     f"{reload_parameters['cartridge_state']}"))

            self.connect_reload(firing_count=f"{reload_parameters['firing_count']}_iteration_{procedure_firing + 1}",
                                reload_type=reload_parameters["reload_type"],
                                reload_color=reload_color,
                                reload_length=reload_length,
                                video_name=video_name,
                                reload_state=reload_parameters['reload_state'],
                                cartridge_state=reload_parameters['cartridge_state'],
                                cartridge_color=cartridge_color,
                                ship_cap_status=reload_parameters["ship_cap_presence"]
                                )

            self.EEAClamping(SuccessFlag=True, is_firing_test=True, logs_to_compare='EEA Clamping on Tissue',
                             clamp_force=clampingForce, fire_force=firingForce)

            self.wait(2)
            self.GreenKeyAck(SuccessFlag=True)

            print("Open Circuiting Adapter UART Rx & Tx After Entering FireMode")
            self.Switch_OFF_Relay(1, 3)
            self.Switch_OFF_Relay(1, 4)
            self.wait(10)

            logs_to_compare = 'EEA Adapter UART Rx & Tx Open Circuit'
            fire_success_flag = True
            self.compare_logs(logs_to_compare, SuccessFlag=fire_success_flag, is_firing_test=True)
            print(f'STEP : {logs_to_compare} performed!')

            logs_to_compare = 'EEA Firing with Adapter UART Rx Tx Open Circuit'

            # self.Adapter_UART_RX_TX_OC_After_Entering_Firingmode(fire_force=firingForce)
            self.EEAFiring(fire_force=firingForce, logs_to_compare='EEA Firing with Adapter UART Rx Tx Open Circuit')

            self.apply_load_force(0)

            self.TiltOpen('Tilt Operation of Anvil with UART Rx & Tx Open Circuit')
            self.TiltPromptOpen_original('SSE with Adapter UART Rx & Tx Open Circuit')

            if reload_parameters["reload_type"] == "EEA":
                self.DisconnectingEEAReload()

            # Restoring Adapter UART Connections
            print("Restoring Adapter UART Rx & Tx")
            self.Switch_ONN_Relay(1, 3)
            self.Switch_ONN_Relay(1, 4)

            logs_to_compare = 'EEA Adapter UART Rx & Tx Open Circuit Restored'
            self.compare_logs(logs_to_compare, SuccessFlag=True, is_firing_test=True)
            print(f'STEP : {logs_to_compare} performed!')

            if procedure_firing != firings - 1:
                is_firing_test_passed = self.is_firing_test_passed(procedure_firing, reload_parameters["firing_count"],
                                                                   fire_pass)
                if is_firing_test_passed:
                    fire_pass += 1
                # adapterConnected = False
        self.is_firing_test_passed(firings - 1, reload_parameters["firing_count"], fire_pass)

    def adapter_sc_before_firing_log_comparision(self, logs_to_compare=None):
        fire_success_flag = True
        self.compare_logs(logs_to_compare, SuccessFlag=fire_success_flag)

    def adapter_1w_SC_before_firing(self, reload_parameters, clampingForce, firingForce, firing_duration=0):
        fire_pass = 0
        firings = reload_parameters["procedure_firings_count"]
        print(simple_colors.blue(f"firing details for the iteration: {self.json_data}"))

        for procedure_firing in range(reload_parameters["procedure_firings_count"]):
            video_name = reload_parameters["video_name"] + f"_proc_{procedure_firing}"

            reload_length = self.fetch_parameter(data=reload_parameters["reload_length"], index=procedure_firing)
            reload_color = self.fetch_parameter(data=reload_parameters["reload_color"], index=procedure_firing)
            cartridge_color = self.fetch_parameter(data=reload_parameters["cartridge_color"], index=procedure_firing)
            print(simple_colors.blue(f"reload_state = {reload_parameters['reload_state']}\ncartridge_state = "
                                     f"{reload_parameters['cartridge_state']}"))

            self.connect_reload(firing_count=f"{reload_parameters['firing_count']}_iteration_{procedure_firing + 1}",
                                reload_type=reload_parameters["reload_type"],
                                reload_color=reload_color,
                                reload_length=reload_length,
                                video_name=video_name,
                                reload_state=reload_parameters['reload_state'],
                                cartridge_state=reload_parameters['cartridge_state'],
                                cartridge_color=cartridge_color,
                                ship_cap_status=reload_parameters["ship_cap_presence"]
                                )

            self.EEAClamping(SuccessFlag=True, is_firing_test=True, logs_to_compare='EEA Clamping on Tissue',
                             clamp_force=clampingForce, fire_force=firingForce)

            print("Short Circuiting Adapter 1Wire")
            self.Switch_ONN_Relay(6, 6)
            self.adapter_sc_before_firing_log_comparision('EEA Adapter 1W Short Circuit Before Entering Fire Mode')

            self.wait(2)
            self.GreenKeyAck(SuccessFlag=True)

            self.EEAFiring(fire_force=firingForce, logs_to_compare='EEA Firing with Adapter 1W Short Circuit')

            self.apply_load_force(0)

            self.TiltOpen()
            self.TiltPromptOpen_original('SSE with Adapter 1W Short Circuit')

            self.wait(5)
            if reload_parameters["reload_type"] == "EEA":
                self.DisconnectingEEAReload()

            if procedure_firing != firings - 1:
                is_firing_test_passed = self.is_firing_test_passed(procedure_firing,
                                                                   reload_parameters["firing_count"],
                                                                   fire_pass)
                if is_firing_test_passed:
                    fire_pass += 1
        self.is_firing_test_passed(firings - 1, reload_parameters["firing_count"], fire_pass)

    def adapter_1w_SC_after_firing(self, clampingForce, firingForce, reload_parameters, firing_duration=0):
        fire_pass = 0
        firings = reload_parameters["procedure_firings_count"]
        print(simple_colors.blue(f"firing details for the iteration: {self.json_data}"))

        for procedure_firing in range(reload_parameters["procedure_firings_count"]):
            video_name = reload_parameters["video_name"] + f"_proc_{procedure_firing}"

            reload_length = self.fetch_parameter(data=reload_parameters["reload_length"], index=procedure_firing)
            reload_color = self.fetch_parameter(data=reload_parameters["reload_color"], index=procedure_firing)
            cartridge_color = self.fetch_parameter(data=reload_parameters["cartridge_color"], index=procedure_firing)
            print(simple_colors.blue(f"reload_state = {reload_parameters['reload_state']}\ncartridge_state = "
                                     f"{reload_parameters['cartridge_state']}"))

            self.connect_reload(firing_count=f"{reload_parameters['firing_count']}_iteration_{procedure_firing + 1}",
                                reload_type=reload_parameters["reload_type"],
                                reload_color=reload_color,
                                reload_length=reload_length,
                                video_name=video_name,
                                reload_state=reload_parameters['reload_state'],
                                cartridge_state=reload_parameters['cartridge_state'],
                                cartridge_color=cartridge_color,
                                ship_cap_status=reload_parameters["ship_cap_presence"]
                                )

            self.EEAClamping(SuccessFlag=True, is_firing_test=True, logs_to_compare='EEA Clamping on Tissue',
                             clamp_force=clampingForce, fire_force=firingForce)

            self.wait(2)
            self.GreenKeyAck(SuccessFlag=True)

            print("Short Circuiting Adapter 1Wire")
            self.Switch_ONN_Relay(6, 6)
            self.wait(15)

            # self.Adapter_1W_SC_After_Entering_Firemode( fire_force=firingForce)
            self.EEAFiring(fire_force=firingForce, logs_to_compare='EEA Firing with Adapter 1W Short Circuit')

            self.apply_load_force(0)

            self.TiltOpen()
            self.TiltPromptOpen_original('SSE with Adapter 1W Short Circuit')

            if reload_parameters["reload_type"] == "EEA":
                self.DisconnectingEEAReload()

            if procedure_firing != firings - 1:
                is_firing_test_passed = self.is_firing_test_passed(procedure_firing,
                                                                   reload_parameters["firing_count"],
                                                                   fire_pass)
                if is_firing_test_passed:
                    fire_pass += 1
                # adapterConnected = False
        self.is_firing_test_passed(firings - 1, reload_parameters["firing_count"], fire_pass)

    def adapter_1w_OC_before_firing(self, clampingForce, firingForce, reload_parameters, firing_duration=0):
        fire_pass = 0
        firings = reload_parameters["procedure_firings_count"]
        print(simple_colors.blue(f"firing details for the iteration: {self.json_data}"))

        for procedure_firing in range(reload_parameters["procedure_firings_count"]):
            video_name = reload_parameters["video_name"] + f"_proc_{procedure_firing}"

            reload_length = self.fetch_parameter(data=reload_parameters["reload_length"], index=procedure_firing)
            reload_color = self.fetch_parameter(data=reload_parameters["reload_color"], index=procedure_firing)
            cartridge_color = self.fetch_parameter(data=reload_parameters["cartridge_color"], index=procedure_firing)
            print(simple_colors.blue(f"reload_state = {reload_parameters['reload_state']}\ncartridge_state = "
                                     f"{reload_parameters['cartridge_state']}"))

            self.connect_reload(firing_count=f"{reload_parameters['firing_count']}_iteration_{procedure_firing + 1}",
                                reload_type=reload_parameters["reload_type"],
                                reload_color=reload_color,
                                reload_length=reload_length,
                                video_name=video_name,
                                reload_state=reload_parameters['reload_state'],
                                cartridge_state=reload_parameters['cartridge_state'],
                                cartridge_color=cartridge_color,
                                ship_cap_status=reload_parameters["ship_cap_presence"]
                                )

            self.EEAClamping(SuccessFlag=True, is_firing_test=True, logs_to_compare='EEA Clamping on Tissue',
                             clamp_force=clampingForce, fire_force=firingForce)

            print('Open Circuiting Adapter 1W')
            self.Switch_OFF_Relay(1, 2)  # B1:R5 - OFF

            self.wait(2)
            self.GreenKeyAck(SuccessFlag=True)

            self.EEAFiring(fire_force=firingForce, logs_to_compare='EEA Firing with Adapter 1W Open Circuit')

            self.apply_load_force(0)

            self.TiltOpen()
            self.TiltPromptOpen_original('SSE with Adapter 1W Open Circuit')

            self.wait(5)
            if reload_parameters["reload_type"] == "EEA":
                self.DisconnectingEEAReload()

            if procedure_firing != firings - 1:
                is_firing_test_passed = self.is_firing_test_passed(procedure_firing,
                                                                   reload_parameters["firing_count"],
                                                                   fire_pass)
                if is_firing_test_passed:
                    fire_pass += 1
        self.is_firing_test_passed(firings - 1, reload_parameters["firing_count"], fire_pass)

    def adapter_1w_OC_after_firing(self, clampingForce, firingForce, reload_parameters, firing_duration=0):
        fire_pass = 0
        firings = reload_parameters["procedure_firings_count"]
        print(simple_colors.blue(f"firing details for the iteration: {self.json_data}"))

        for procedure_firing in range(reload_parameters["procedure_firings_count"]):
            video_name = reload_parameters["video_name"] + f"_proc_{procedure_firing}"

            reload_length = self.fetch_parameter(data=reload_parameters["reload_length"], index=procedure_firing)
            reload_color = self.fetch_parameter(data=reload_parameters["reload_color"], index=procedure_firing)
            cartridge_color = self.fetch_parameter(data=reload_parameters["cartridge_color"], index=procedure_firing)
            print(simple_colors.blue(f"reload_state = {reload_parameters['reload_state']}\ncartridge_state = "
                                     f"{reload_parameters['cartridge_state']}"))

            self.connect_reload(firing_count=f"{reload_parameters['firing_count']}_iteration_{procedure_firing + 1}",
                                reload_type=reload_parameters["reload_type"],
                                reload_color=reload_color,
                                reload_length=reload_length,
                                video_name=video_name,
                                reload_state=reload_parameters['reload_state'],
                                cartridge_state=reload_parameters['cartridge_state'],
                                cartridge_color=cartridge_color,
                                ship_cap_status=reload_parameters["ship_cap_presence"]
                                )

            self.EEAClamping(SuccessFlag=True, is_firing_test=True, logs_to_compare='EEA Clamping on Tissue',
                             clamp_force=clampingForce, fire_force=firingForce)

            self.GreenKeyAck(SuccessFlag=True)

            print('Open Circuiting Adapter 1W')
            self.Switch_OFF_Relay(1, 2)  # B1:R2 - OFF

            # self.Adapter_1W_OC_After_Entering_Firingmode(fire_force=firingForce)
            self.EEAFiring(fire_force = firingForce)

            self.apply_load_force(0)

            self.TiltOpen()
            self.TiltPromptOpen_original('SSE with Adapter 1W Open Circuit')

            # self.wait(3)
            # print("from here ")
            # if reload_parameters["reload_type"] == "EEA":
            #     self.DisconnectingEEAReload()

            if procedure_firing != firings - 1:
                is_firing_test_passed = self.is_firing_test_passed(procedure_firing, reload_parameters["firing_count"],
                                                                   fire_pass)
                if is_firing_test_passed:
                    fire_pass += 1
                # adapterConnected = False
        self.is_firing_test_passed(firings - 1, reload_parameters["firing_count"], fire_pass)


    def clamshell_1w_OC_before_firing(self, clampingForce, firingForce, reload_parameters):
        fire_pass = 0
        firings = reload_parameters["procedure_firings_count"]
        print(simple_colors.blue(f"firing details for the iteration: {self.json_data}"))

        for procedure_firing in range(reload_parameters["procedure_firings_count"]):
            video_name = reload_parameters["video_name"] + f"_proc_{procedure_firing}"

            reload_length = self.fetch_parameter(data=reload_parameters["reload_length"], index=procedure_firing)
            reload_color = self.fetch_parameter(data=reload_parameters["reload_color"], index=procedure_firing)
            cartridge_color = self.fetch_parameter(data=reload_parameters["cartridge_color"], index=procedure_firing)
            print(simple_colors.blue(f"reload_state = {reload_parameters['reload_state']}\ncartridge_state = "
                                     f"{reload_parameters['cartridge_state']}"))

            self.connect_reload(firing_count=f"{reload_parameters['firing_count']}_iteration_{procedure_firing + 1}",
                                reload_type=reload_parameters["reload_type"],
                                reload_color=reload_color,
                                reload_length=reload_length,
                                video_name=video_name,
                                reload_state=reload_parameters['reload_state'],
                                cartridge_state=reload_parameters['cartridge_state'],
                                cartridge_color=cartridge_color,
                                ship_cap_status=reload_parameters["ship_cap_presence"]
                                )

            self.EEAClamping(SuccessFlag=True, is_firing_test=True, logs_to_compare='EEA Clamping on Tissue',
                             clamp_force=clampingForce, fire_force=firingForce)

            print('Open Circuiting Clamshell 1W')
            self.Switch_OFF_Relay(1, 5)  # B1:R5 - OFF

            self.wait(2)
            self.GreenKeyAck(SuccessFlag=True)

            self.EEAFiring(fire_force = firingForce)

            # making Load force zero
            self.apply_load_force(0)

            self.TiltOpen()
            self.TiltPromptOpen_original()

            if reload_parameters["reload_type"] == "EEA":
                self.DisconnectingEEAReload()

            if procedure_firing != firings - 1:
                is_firing_test_passed = self.is_firing_test_passed(procedure_firing, reload_parameters["firing_count"],
                                                                   fire_pass)
                if is_firing_test_passed:
                    fire_pass += 1
                # adapterConnected = False
        self.is_firing_test_passed(firings - 1, reload_parameters["firing_count"], fire_pass)

    def clamshell_1w_OC_after_firing(self, clampingForce, firingForce, reload_parameters):
        fire_pass = 0
        firings = reload_parameters["procedure_firings_count"]
        print(simple_colors.blue(f"firing details for the iteration: {self.json_data}"))


        for procedure_firing in range(reload_parameters["procedure_firings_count"]):
            video_name = reload_parameters["video_name"] + f"_proc_{procedure_firing}"

            reload_length = self.fetch_parameter(data=reload_parameters["reload_length"], index=procedure_firing)
            reload_color = self.fetch_parameter(data=reload_parameters["reload_color"], index=procedure_firing)
            cartridge_color = self.fetch_parameter(data=reload_parameters["cartridge_color"], index=procedure_firing)
            print(simple_colors.blue(f"reload_state = {reload_parameters['reload_state']}\ncartridge_state = "
                                     f"{reload_parameters['cartridge_state']}"))


            self.connect_reload(firing_count = f"{reload_parameters['firing_count']}_iteration_{procedure_firing + 1}",
                                reload_type = reload_parameters["reload_type"],
                                reload_color = reload_color,
                                reload_length = reload_length,
                                video_name = video_name,
                                reload_state = reload_parameters['reload_state'],
                                cartridge_state = reload_parameters['cartridge_state'],
                                cartridge_color = cartridge_color,
                                ship_cap_status = reload_parameters["ship_cap_presence"]
                                )



            self.EEAClamping(SuccessFlag=True, is_firing_test=True, logs_to_compare='EEA Clamping on Tissue',
                             clamp_force = clampingForce, fire_force = firingForce)

            self.wait(2)
            self.GreenKeyAck(SuccessFlag=True)

            print('Open Circuiting Clamshell 1W')
            self.Switch_OFF_Relay(1, 5)  # B1:R5 - OFF

            # self.Shell_1W_OC_After_Entering_Firemode(fire_force = firingForce)
            self.EEAFiring(fire_force=firingForce)

            # making Load force zero
            self.apply_load_force(0)

            self.TiltOpen()
            self.TiltPromptOpen_original()

            if reload_parameters["reload_type"] == "EEA":
                self.DisconnectingEEAReload()

            if procedure_firing != firings - 1:
                is_firing_test_passed = self.is_firing_test_passed(procedure_firing, reload_parameters["firing_count"],
                                                                   fire_pass)
                if is_firing_test_passed:
                    fire_pass += 1
                # adapterConnected = False
        self.is_firing_test_passed(firings - 1, reload_parameters["firing_count"], fire_pass)

    def clamshell_1w_SC_before_firing(self, clampingForce, firingForce, reload_parameters, firing_duration=0):
        fire_pass = 0
        firings = reload_parameters["procedure_firings_count"]
        print(simple_colors.blue(f"firing details for the iteration: {self.json_data}"))

        for procedure_firing in range(reload_parameters["procedure_firings_count"]):
            video_name = reload_parameters["video_name"] + f"_proc_{procedure_firing}"

            reload_length = self.fetch_parameter(data=reload_parameters["reload_length"], index=procedure_firing)
            reload_color = self.fetch_parameter(data=reload_parameters["reload_color"], index=procedure_firing)
            cartridge_color = self.fetch_parameter(data=reload_parameters["cartridge_color"], index=procedure_firing)
            print(simple_colors.blue(f"reload_state = {reload_parameters['reload_state']}\ncartridge_state = "
                                     f"{reload_parameters['cartridge_state']}"))

            self.connect_reload(firing_count=f"{reload_parameters['firing_count']}_iteration_{procedure_firing + 1}",
                                reload_type=reload_parameters["reload_type"],
                                reload_color=reload_color,
                                reload_length=reload_length,
                                video_name=video_name,
                                reload_state=reload_parameters['reload_state'],
                                cartridge_state=reload_parameters['cartridge_state'],
                                cartridge_color=cartridge_color,
                                ship_cap_status=reload_parameters["ship_cap_presence"]
                                )

            self.EEAClamping(SuccessFlag=True, is_firing_test=True, logs_to_compare='EEA Clamping on Tissue',
                             clamp_force=clampingForce, fire_force=firingForce)

            print("Short Circuiting Clamshell 1Wire Before Firing ")
            self.Switch_ONN_Relay(6, 5)

            self.wait(2)
            self.GreenKeyAck(SuccessFlag=True)

            self.EEAFiring(fire_force=firingForce)

            self.apply_load_force(0)

            self.TiltOpen()
            self.TiltPromptOpen_original()

            if reload_parameters["reload_type"] == "EEA":
                self.DisconnectingEEAReload()

            if procedure_firing != firings - 1:
                is_firing_test_passed = self.is_firing_test_passed(procedure_firing, reload_parameters["firing_count"],
                                                                   fire_pass)
                if is_firing_test_passed:
                    fire_pass += 1

        self.is_firing_test_passed(firings - 1, reload_parameters["firing_count"], fire_pass)



    def clamshell_1w_SC_after_firing(self, clampingForce, firingForce, reload_parameters):
        fire_pass = 0
        firings = reload_parameters["procedure_firings_count"]
        print(simple_colors.blue(f"firing details for the iteration: {self.json_data}"))

        for procedure_firing in range(reload_parameters["procedure_firings_count"]):
            video_name = reload_parameters["video_name"] + f"_proc_{procedure_firing}"

            reload_length = self.fetch_parameter(data=reload_parameters["reload_length"], index=procedure_firing)
            reload_color = self.fetch_parameter(data=reload_parameters["reload_color"], index=procedure_firing)
            cartridge_color = self.fetch_parameter(data=reload_parameters["cartridge_color"], index=procedure_firing)
            print(simple_colors.blue(f"reload_state = {reload_parameters['reload_state']}\ncartridge_state = "
                                     f"{reload_parameters['cartridge_state']}"))

            self.connect_reload(firing_count=f"{reload_parameters['firing_count']}_iteration_{procedure_firing + 1}",
                                reload_type=reload_parameters["reload_type"],
                                reload_color=reload_color,
                                reload_length=reload_length,
                                video_name=video_name,
                                reload_state=reload_parameters['reload_state'],
                                cartridge_state=reload_parameters['cartridge_state'],
                                cartridge_color=cartridge_color,
                                ship_cap_status=reload_parameters["ship_cap_presence"]
                                )

            self.EEAClamping(SuccessFlag=True, is_firing_test=True, logs_to_compare='EEA Clamping on Tissue',
                             clamp_force=clampingForce, fire_force=firingForce)

            self.wait(2)
            self.GreenKeyAck(SuccessFlag=True)

            print('Short Circuiting Clamshell 1W After Entering Fire Mode')
            self.Switch_OFF_Relay(6, 5)  # B1:R5 - OFF

            # self.Shell_1W_SC_After_Entering_Firemode(fire_force = firingForce)
            self.EEAFiring(fire_force=firingForce)

            self.apply_load_force(0)

            self.TiltOpen()
            self.TiltPromptOpen_original()

            if reload_parameters["reload_type"] == "EEA":
                self.DisconnectingEEAReload()

            if procedure_firing != firings - 1:
                is_firing_test_passed = self.is_firing_test_passed(procedure_firing, reload_parameters["firing_count"],
                                                                   fire_pass)
                if is_firing_test_passed:
                    fire_pass += 1
                # adapterConnected = False
        self.is_firing_test_passed(firings - 1, reload_parameters["firing_count"], fire_pass)

    def EEA_adapter_reset(self):
        logs_to_compare = 'Adapter reset string'
        SuccessFlag = True
        # Perform rotation operation
        self.Switch_ONN_Relay(2, 1)
        self.Switch_ONN_Relay(2, 2)
        self.Switch_ONN_Relay(2, 7)
        self.Switch_ONN_Relay(2, 8)
        self.wait(5)
        self.compare_logs(logs_to_compare=logs_to_compare, SuccessFlag=SuccessFlag, is_firing_test=False)
        print(f"Step: {logs_to_compare} Performed")

    def checkLockScreenPresent(self):
        logs_to_compare = 'EEA Lock Screen Present'
        SuccessFlag = True
        self.Switch_ONN_Relay(2, 4)
        self.Switch_ONN_Relay(2, 5)
        self.Switch_ONN_Relay(2, 4)
        self.wait(5)
        self.compare_logs(logs_to_compare=logs_to_compare, SuccessFlag=SuccessFlag, is_firing_test=False)
        print(f"Step: {logs_to_compare} Performed")

    def EEA_firing_FV(self, clampingForce, firingForce, reload_parameters, videoName, fixtureValidation):

        reload_length = self.fetch_parameter(data=reload_parameters["reload_length"], index=0)
        reload_color = self.fetch_parameter(data=reload_parameters["reload_color"], index=0)

        # Reload Connected
        self.connect_reload(firing_count=0,
                            reload_type='EEA',
                            reload_color=reload_color,
                            reload_length=reload_length,
                            video_name=videoName,
                            ship_cap_status='Yes',
                            fixture_validation_required=fixtureValidation,
                            record_video=False
                            )

        self.EEAClamping(SuccessFlag=True,
                         is_firing_test=True,
                         logs_to_compare='EEA Clamping on Tissue',
                         clamp_force=clampingForce,
                         fire_force=firingForce,
                         fixture_validation_req=fixtureValidation)

        self.GreenKeyAck(SuccessFlag=True, fixture_validation_req=fixtureValidation)

        self.EEAFiring_Fixture_Validation(fixture_validation_req=fixtureValidation, fire_force=firingForce)

        #making Load force zero
        self.apply_load_force(0, fixture_validation_req=fixtureValidation)

        self.TiltOpen(fixture_validation_req=fixtureValidation)
        self.TiltPromptOpen_original(fixture_validation_req=fixtureValidation)

        # Remove Reload
        self.DisconnectingEEAReload(fixture_validation_required=fixtureValidation)

    def firing_Issue_417349(self, reload_parameters):
        firings = reload_parameters["procedure_firings_count"]

        print(simple_colors.blue(f"firing details for the iteration: {self.json_data}"))

        for procedure_firing in range(firings):
            video_name = reload_parameters["video_name"] + f"_proc_{procedure_firing}"

            reload_length = self.fetch_parameter(data=reload_parameters["reload_length"], index=procedure_firing)
            reload_color = self.fetch_parameter(data=reload_parameters["reload_color"], index=procedure_firing)
            cartridge_color = self.fetch_parameter(data=reload_parameters["cartridge_color"], index=procedure_firing)
            print(simple_colors.blue(f"reload_state = {reload_parameters['reload_state']}\ncartridge_state = "
                                     f"{reload_parameters['cartridge_state']}"))

            self.connect_reload(firing_count=f"{reload_parameters['firing_count']}_iteration_{procedure_firing + 1}",
                                reload_type=reload_parameters["reload_type"],
                                reload_color=reload_color,
                                reload_length=reload_length,
                                video_name=video_name,
                                reload_state=reload_parameters['reload_state'],
                                cartridge_state=reload_parameters['cartridge_state'],
                                cartridge_color=cartridge_color,
                                ship_cap_status=reload_parameters["ship_cap_presence"]
                                )

            self.EEAClamping(SuccessFlag=True, is_firing_test=True, logs_to_compare='EEA Clamping on Tissue')

            # Turn OFF Reload Wire - 3,2 Onewire and 3,3 Ground
            self.Switch_OFF_Relay(3, 2)
            self.Switch_OFF_Relay(3, 3)

            self.Switch_ONN_Relay(2, 4)  # B2:R4 - ON
            self.wait(20)
            self.Switch_OFF_Relay(2, 4)  # B2:R4 - OFF


    def firing_test(self, clampingForce, firingForce, articulationStateinFiring, retractionForce,
                    reload_parameters, firing_duration=0, is_smoke_test=False):
        fire_pass = 0
        # adapterConnected = True
        #  try:
        firings = reload_parameters["procedure_firings_count"]
        #  except:
        # firings = 1

        print(simple_colors.blue(f"firing details for the iteration: {self.json_data}"))

        for procedure_firing in range(firings):

            video_name = reload_parameters["video_name"] + f"_proc_{procedure_firing}"

            reload_length = self.fetch_parameter(data=reload_parameters["reload_length"], index=procedure_firing)
            reload_color = self.fetch_parameter(data=reload_parameters["reload_color"], index=procedure_firing)
            cartridge_color = self.fetch_parameter(data=reload_parameters["cartridge_color"], index=procedure_firing)
            print(simple_colors.blue(f"reload_state = {reload_parameters['reload_state']}\ncartridge_state = "
                                     f"{reload_parameters['cartridge_state']}"))
            # logger.debug(f"reload_parameters = {reload_parameters}")
            self.connect_reload(firing_count=f"{reload_parameters['firing_count']}_iteration_{procedure_firing + 1}",
                                reload_type=reload_parameters["reload_type"],
                                reload_color=reload_color,
                                reload_length=reload_length,
                                video_name=video_name,
                                reload_state=reload_parameters['reload_state'],
                                cartridge_state=reload_parameters['cartridge_state'],
                                cartridge_color=cartridge_color,
                                ship_cap_status=reload_parameters["ship_cap_presence"]
                                )
            self.EEAClamping(SuccessFlag=True, is_firing_test=True, clamp_force=clampingForce,
                             fire_force=firingForce, logs_to_compare='EEA Clamping on Tissue')
            self.wait(1)

            self.GreenKeyAck(SuccessFlag=True)

            # self.apply_load_force(firing_Force)
            self.EEAFiring(fire_force=firingForce)

            # self.apply_load_force(retraction_Force)
            # making Load force zero
            self.apply_load_force(0)

            self.TiltOpen()
            self.TiltPromptOpen_original()

            if reload_parameters["reload_type"] == "EEA":
                self.DisconnectingEEAReload()

            if procedure_firing != firings - 1:
                is_firing_test_passed = self.is_firing_test_passed(procedure_firing, reload_parameters["firing_count"],
                                                                   fire_pass)
                if is_firing_test_passed:
                    fire_pass += 1
        # adapterConnected = False
        self.is_firing_test_passed(firings - 1, reload_parameters["firing_count"], fire_pass)

    def stapling_recovery_test(self, clampingForce, firingForce, articulationStateinFiring, retractionForce,
                    reload_parameters, firing_duration=0, is_smoke_test=False):
        fire_pass = 0
        firings = reload_parameters["procedure_firings_count"]
        print(simple_colors.blue(f"firing details for the iteration: {self.json_data}"))

        for procedure_firing in range(firings):
            video_name = reload_parameters["video_name"] + f"_proc_{procedure_firing}"

            reload_length = self.fetch_parameter(data=reload_parameters["reload_length"], index=procedure_firing)
            reload_color = self.fetch_parameter(data=reload_parameters["reload_color"], index=procedure_firing)
            cartridge_color = self.fetch_parameter(data=reload_parameters["cartridge_color"], index=procedure_firing)
            print(simple_colors.blue(f"reload_state = {reload_parameters['reload_state']}\ncartridge_state = "
                                     f"{reload_parameters['cartridge_state']}"))
            # logger.debug(f"reload_parameters = {reload_parameters}")
            self.connect_reload(firing_count=f"{reload_parameters['firing_count']}_iteration_{procedure_firing + 1}",
                                reload_type=reload_parameters["reload_type"],
                                reload_color=reload_color,
                                reload_length=reload_length,
                                video_name=video_name,
                                reload_state=reload_parameters['reload_state'],
                                cartridge_state=reload_parameters['cartridge_state'],
                                cartridge_color=cartridge_color,
                                ship_cap_status=reload_parameters["ship_cap_presence"]
                                )
            self.EEAClamping(SuccessFlag=True, is_firing_test=True, clamp_force=clampingForce,
                             fire_force=firingForce, logs_to_compare='EEA Clamping on Tissue')

            self.GreenKeyAck(SuccessFlag=True)

            if "Stapling Recovery" == reload_parameters["scenario_title"]:
                self.EEAFiring_Stapling_Recovery()
            elif "Stapling Recovery No Staple Exit State" == reload_parameters["scenario_title"]:
                self.EEAFiring_Stapling_Recovery_No_Staple_Exit_State()
            else:
                pass

            # making Load force zero
            self.apply_load_force(0)

            if not "Stapling Recovery No Staple Exit State" == reload_parameters["scenario_title"]:
                self.TiltOpen()
                self.TiltPromptOpen_original()

            if reload_parameters["reload_type"] == "EEA":
                self.DisconnectingEEAReload()

            if procedure_firing != firings - 1:
                is_firing_test_passed = self.is_firing_test_passed(procedure_firing, reload_parameters["firing_count"],
                                                                   fire_pass)
                if is_firing_test_passed:
                    fire_pass += 1

        self.is_firing_test_passed(firings - 1, reload_parameters["firing_count"], fire_pass)

    def cutting_recovery_test(self, clampingForce, firingForce, articulationStateinFiring, retractionForce,
                    reload_parameters, firing_duration=0, is_smoke_test=False):
        fire_pass = 0
        firings = reload_parameters["procedure_firings_count"]

        print(simple_colors.blue(f"firing details for the iteration: {self.json_data}"))

        for procedure_firing in range(firings):
            video_name = reload_parameters["video_name"] + f"_proc_{procedure_firing}"

            reload_length = self.fetch_parameter(data=reload_parameters["reload_length"], index=procedure_firing)
            reload_color = self.fetch_parameter(data=reload_parameters["reload_color"], index=procedure_firing)
            cartridge_color = self.fetch_parameter(data=reload_parameters["cartridge_color"], index=procedure_firing)
            print(simple_colors.blue(f"reload_state = {reload_parameters['reload_state']}\ncartridge_state = "
                                     f"{reload_parameters['cartridge_state']}"))

            self.connect_reload(firing_count=f"{reload_parameters['firing_count']}_iteration_{procedure_firing + 1}",
                                reload_type=reload_parameters["reload_type"],
                                reload_color=reload_color,
                                reload_length=reload_length,
                                video_name=video_name,
                                reload_state=reload_parameters['reload_state'],
                                cartridge_state=reload_parameters['cartridge_state'],
                                cartridge_color=cartridge_color,
                                ship_cap_status=reload_parameters["ship_cap_presence"]
                                )
            self.EEAClamping(SuccessFlag=True, is_firing_test=True, clamp_force=clampingForce,
                             fire_force=firingForce, logs_to_compare='EEA Clamping on Tissue')

            self.GreenKeyAck(SuccessFlag=True)

            if "Cut Recovery" == reload_parameters["scenario_title"]:
                self.EEAFiring_Cutting_Recovery()
            elif "Cut Recovery Exit State" == reload_parameters["scenario_title"]:
                self.EEAFiring_Cutting_Recovery_Exit_State()
            else:
                pass

            # making Load force zero
            self.apply_load_force(0)

            if not "Cut Recovery Exit State" == reload_parameters["scenario_title"]:
                self.TiltOpen()
                self.TiltPromptOpen_original()

            if reload_parameters["reload_type"] == "EEA":
                self.DisconnectingEEAReload()

            if procedure_firing != firings - 1:
                is_firing_test_passed = self.is_firing_test_passed(procedure_firing, reload_parameters["firing_count"],
                                                                   fire_pass)
                if is_firing_test_passed:
                    fire_pass += 1
        # adapterConnected = False
        self.is_firing_test_passed(firings - 1, reload_parameters["firing_count"], fire_pass)

    def firing_test_450475(self, clampingForce, firingForce, articulationStateinFiring, retractionForce,
                    reload_parameters, firing_duration=0, is_smoke_test=False):
        fire_pass = 0
        # adapterConnected = True
        #  try:
        firings = reload_parameters["procedure_firings_count"]
        #  except:
        # firings = 1

        print(simple_colors.blue(f"firing details for the iteration: {self.json_data}"))

        for procedure_firing in range(firings):
            # if not adapterConnected:
            #     self.removeAdapter()
            #     self.wait(25)
            #     self.connect_adapter_test()
            video_name = reload_parameters["video_name"] + f"_proc_{procedure_firing}"

            reload_length = self.fetch_parameter(data=reload_parameters["reload_length"], index=procedure_firing)
            reload_color = self.fetch_parameter(data=reload_parameters["reload_color"], index=procedure_firing)
            cartridge_color = self.fetch_parameter(data=reload_parameters["cartridge_color"], index=procedure_firing)
            print(simple_colors.blue(f"reload_state = {reload_parameters['reload_state']}\ncartridge_state = "
                                     f"{reload_parameters['cartridge_state']}"))
            # logger.debug(f"reload_parameters = {reload_parameters}")
            self.connect_reload(firing_count=f"{reload_parameters['firing_count']}_iteration_{procedure_firing + 1}",
                                reload_type=reload_parameters["reload_type"],
                                reload_color=reload_color,
                                reload_length=reload_length,
                                video_name=video_name,
                                reload_state=reload_parameters['reload_state'],
                                cartridge_state=reload_parameters['cartridge_state'],
                                cartridge_color=cartridge_color,
                                ship_cap_status=reload_parameters["ship_cap_presence"]
                                )

            self.EEAClamping(SuccessFlag=True, is_firing_test=True, clamp_force=clampingForce,
                             fire_force=firingForce, logs_to_compare='EEA Clamping on Tissue')

            # self.wait(2) # 26th Commented code
            self.GreenKeyAck(SuccessFlag=True)

            # self.apply_load_force(firing_Force)
            self.EEAFiring( fire_force=firingForce)

            # self.apply_load_force(retraction_Force)
            # making Load force zero
            self.apply_load_force(0)

            self.TiltOpen()
            self.TiltOpenPrompt_450475()

            if reload_parameters["reload_type"] == "EEA":
                self.DisconnectingEEAReload()

            if procedure_firing != firings - 1:
                is_firing_test_passed = self.is_firing_test_passed(procedure_firing, reload_parameters["firing_count"],
                                                                   fire_pass)
                if is_firing_test_passed:
                    fire_pass += 1
        # adapterConnected = False
        self.is_firing_test_passed(firings - 1, reload_parameters["firing_count"], fire_pass)

    def increment_1w_counter_failuer_test(self,clampingForce, firingForce, reload_parameters):
        fire_pass = 0
        firings = reload_parameters["procedure_firings_count"]
        print(simple_colors.blue(f"firing details for the iteration: {self.json_data}"))

        for procedure_firing in range(firings):
            video_name = reload_parameters["video_name"]

            reload_length = self.fetch_parameter(data=reload_parameters["reload_length"], index=procedure_firing)
            reload_color = self.fetch_parameter(data=reload_parameters["reload_color"], index=procedure_firing)
            cartridge_color = self.fetch_parameter(data=reload_parameters["cartridge_color"], index=procedure_firing)
            print(simple_colors.blue(f"reload_state = {reload_parameters['reload_state']}\ncartridge_state = "
                                     f"{reload_parameters['cartridge_state']}"))

            self.connect_reload(firing_count=f"{reload_parameters['firing_count']}_iteration_{procedure_firing + 1}",
                                reload_type=reload_parameters["reload_type"],
                                reload_color=reload_color,
                                reload_length=reload_length,
                                video_name=video_name,
                                reload_state=reload_parameters['reload_state'],
                                cartridge_state=reload_parameters['cartridge_state'],
                                cartridge_color=cartridge_color,
                                ship_cap_status=reload_parameters["ship_cap_presence"],
                                videoDisabledFalg=True
                                )

            self.EEAClamping(SuccessFlag=True, is_firing_test=True, clamp_force=clampingForce,
                             fire_force=firingForce, logs_to_compare='EEA Clamping on Tissue')

            self.GreenKeyAck(SuccessFlag=True)

            self.EEAFiring_1w_cntr_failuer(fire_force=firingForce)
            # self.EEAFiring(fire_force=firingForce)

            # making Load force zero
            self.apply_load_force(0)

            self.TiltOpen()
            self.TiltPromptOpen_original("Tilt Prompt Open with Adapter 1W Open Circuit")

            if procedure_firing != firings - 1:
                is_firing_test_passed = self.is_firing_test_passed(procedure_firing, reload_parameters["firing_count"],
                                                                   fire_pass)
                if is_firing_test_passed:
                    fire_pass += 1

            # Remove Adapter along with Reload
            self.DisconnectingEEAReload(exit_video=False)
            self.wait(5)
            self.removeAdapter()
            self.wait(5)

            # Record Power Pack and Adapter usage Counts After Firing
            # Reading Power Pack Usage Counts, output of this stage is
            # Adapter 1-Wire Fire Count and Procedure Count unchanged
            # Adapter EEPROM Fire Count and procedure Count increased by 1
            # Engaging the Adapter - Controlling the stepper motor
            self.Switch_ONN_Relay(1, 8)
            self.wait(7)
            print("EEA Adapter Engaged to Power Pack Mechanically")

            MCPThread.readingPowerPack.exitFlag = True
            # self.serPP.close()
            # self.disconnect_MCP_Port()
            self.wait(2)

            # Reading Power Pack Usage Counts
            HandleFireCount2, HandleProcedureCount2 = GetHandleUseCount(self.PowerPackComPort)
            # print("HandleFireCount2 = , HandleProcedureCount2 = ", HandleFireCount2, HandleProcedureCount2)

            # Reading Adapter EEPROM Usage Counts
            AdapterEeProcedureCount2, AdapterEeFireCount2 = GetAdapterEepromUsageCounts(self.FtdiUartComPort)
            # print("AdapterEeProcedureCount2 = , AdapterEeFireCount2 = ", AdapterEeProcedureCount2, AdapterEeFireCount2)

            # Reading Adapter One-Wire usage Counts - Adapter Black Box connect
            self.Switch_ONN_Relay(5, 5)
            self.Switch_ONN_Relay(6, 1)

            adapter_1w_eeprom_data = self.read_eeprom_data()
            print("Adapter Onewire EEPROM Data ", adapter_1w_eeprom_data)
            print(list(map(hex, adapter_1w_eeprom_data)))

            data = [hex(x)[2:].zfill(2) for x in adapter_1w_eeprom_data]
            fireCnt = data[3:5]
            precCnt = data[7:9]
            AdapterOwFireCount2 = convert_single_list_ele_to_two_byte_decimal(fireCnt)
            AdapterOwProcedureCount2 = convert_single_list_ele_to_two_byte_decimal(precCnt)

            self.Switch_OFF_Relay(6, 1)
            self.Switch_OFF_Relay(5, 5)

            print('After Firing Handle Fire Count:' + str(HandleFireCount2),
                  'Handle Procedure Count:' + str(HandleProcedureCount2))
            print('After Firing Adapter Eeprom Fire Count:' + str(AdapterEeFireCount2),
                  'Adapter Eeprom Procedure Count:' + str(AdapterEeProcedureCount2))
            print('After Firing Adapter Onewire Fire Count:' + str(AdapterOwFireCount2),
                  'Adapter Onewire Procedure Count:' + str(AdapterOwProcedureCount2))

            self.startMCP()

            ## Re-Connecting the adapter
            # Turning ON the Adapter One Wire - Restoring adapter onewire
            self.my_Serthread.clearQue()
            self.wait(5)
            self.connect_adapter_test()  # B1 - ALL ON
            print("Step: EEA Adapter Connected")

            procedure_firing = 1
            reload_length = self.fetch_parameter(data=reload_parameters["reload_length"], index=procedure_firing)
            reload_color = self.fetch_parameter(data=reload_parameters["reload_color"], index=procedure_firing)
            cartridge_color = self.fetch_parameter(data=reload_parameters["cartridge_color"], index=procedure_firing)
            print(simple_colors.blue(f"reload_state = {reload_parameters['reload_state']}\ncartridge_state = "
                                     f"{reload_parameters['cartridge_state']}"))

            # Attaching EEA reload along with ship cap presence check
            self.connect_reload(firing_count=f"{reload_parameters['firing_count']}_iteration_{procedure_firing + 1}",
                                reload_type=reload_parameters["reload_type"],
                                reload_color=reload_color,
                                reload_length=reload_length,
                                video_name=video_name,
                                reload_state=reload_parameters['reload_state'],
                                cartridge_state=reload_parameters['cartridge_state'],
                                cartridge_color=cartridge_color,
                                ship_cap_status=reload_parameters["ship_cap_presence"],
                                videoDisabledFalg = True
                                )

            self.EEAClamping(SuccessFlag=True, is_firing_test=True, clamp_force=clampingForce,
                             fire_force=firingForce, logs_to_compare='EEA Clamping on Tissue')

            self.GreenKeyAck(SuccessFlag=True)

            self.EEAFiring(fire_force=firingForce)

            # making Load force zero
            self.apply_load_force(0)

            self.TiltOpen()
            self.TiltPromptOpen_original()

            if procedure_firing != firings - 1:
                is_firing_test_passed = self.is_firing_test_passed(procedure_firing, reload_parameters["firing_count"],
                                                                   fire_pass)
                if is_firing_test_passed:
                    fire_pass += 1

            # Remove Adapter along with Reload
            self.DisconnectingEEAReload(exit_video=False)
            self.wait(5)
            self.removeAdapter()
            self.wait(7)

            ## STEP 23: Record Power Pack and Adapter usage Counts ( By Engaging the Adapter )
            self.Switch_ONN_Relay(1, 8)
            self.wait(7)
            print("EEA Adapter Engaged to Power Pack Mechanically")

            MCPThread.readingPowerPack.exitFlag = True
            # self.serPP.close()
            self.wait(2)
            # print(serialControlObj.Test_Results)

            # Reading Power Pack Usage Counts
            HandleFireCount3, HandleProcedureCount3 = GetHandleUseCount(self.PowerPackComPort)

            # Reading Adapter EEPROM Usage Counts
            AdapterEeProcedureCount3, AdapterEeFireCount3 = GetAdapterEepromUsageCounts(self.FtdiUartComPort)

            # Reading Adapter One-Wire usage Counts
            self.Switch_ONN_Relay(5, 5)
            self.Switch_ONN_Relay(6, 1)

            adapter_1w_eeprom_data = self.read_eeprom_data()
            print("Adapter Onewire EEPROM Data ", adapter_1w_eeprom_data)
            print(list(map(hex, adapter_1w_eeprom_data)))

            data = [hex(x)[2:].zfill(2) for x in adapter_1w_eeprom_data]
            fireCnt = data[3:5]
            precCnt = data[7:9]
            AdapterOwFireCount3 = convert_single_list_ele_to_two_byte_decimal(fireCnt)
            AdapterOwProcedureCount3 = convert_single_list_ele_to_two_byte_decimal(precCnt)

            self.Switch_OFF_Relay(6, 1)
            self.Switch_OFF_Relay(5, 5)

            print('After Firing2 Handle Fire Count:' + str(HandleFireCount3),
                  'After Firing2 Handle Procedure Count:' + str(HandleProcedureCount3))
            print('After Firing2 Adapter Eeprom Fire Count:' + str(AdapterEeFireCount3),
                  'After Firing2 Adapter Eeprom Procedure Count:' + str(AdapterEeProcedureCount3))
            print('After Firing2 Adapter Onewire Fire Count:' + str(AdapterOwFireCount3),
                  'After Firing2 Adapter Onewire Procedure Count:' + str(AdapterOwProcedureCount3))

            self.Switch_OFF_Relay(1, 8)
            print('Adapter Clutch Disengaged')

        self.is_firing_test_passed(firings - 1, reload_parameters["firing_count"], fire_pass)

    def increment_Eeprom_counter_failuer_test(self, clampingForce, firingForce, reload_parameters):
        fire_pass = 0
        firings = reload_parameters["procedure_firings_count"]
        print(simple_colors.blue(f"firing details for the iteration: {self.json_data}"))

        for procedure_firing in range(firings):
            video_name = reload_parameters["video_name"]

            reload_length = self.fetch_parameter(data=reload_parameters["reload_length"], index=procedure_firing)
            reload_color = self.fetch_parameter(data=reload_parameters["reload_color"], index=procedure_firing)
            cartridge_color = self.fetch_parameter(data=reload_parameters["cartridge_color"], index=procedure_firing)
            print(simple_colors.blue(f"reload_state = {reload_parameters['reload_state']}\ncartridge_state = "
                                     f"{reload_parameters['cartridge_state']}"))

            self.connect_reload(firing_count=f"{reload_parameters['firing_count']}_iteration_{procedure_firing + 1}",
                                reload_type=reload_parameters["reload_type"],
                                reload_color=reload_color,
                                reload_length=reload_length,
                                video_name=video_name,
                                reload_state=reload_parameters['reload_state'],
                                cartridge_state=reload_parameters['cartridge_state'],
                                cartridge_color=cartridge_color,
                                ship_cap_status=reload_parameters["ship_cap_presence"],
                                videoDisabledFalg=True
                                )

            self.EEAClamping(SuccessFlag=True, is_firing_test=True, clamp_force=clampingForce,
                             fire_force=firingForce, logs_to_compare='EEA Clamping on Tissue')

            self.GreenKeyAck(SuccessFlag=True)

            self.EEAFiring_Eeprom_cntr_failuer(fire_force=firingForce)

            # making Load force zero
            self.apply_load_force(0)

            # self.TiltOpen()
            # self.TiltPromptOpen_original("Tilt Prompt Open with Adapter 1W Open Circuit")

            if procedure_firing != firings - 1:
                is_firing_test_passed = self.is_firing_test_passed(procedure_firing, reload_parameters["firing_count"],
                                                                   fire_pass)
                if is_firing_test_passed:
                    fire_pass += 1

            # Remove Adapter along with Reload
            self.DisconnectingEEAReload(exit_video=False)
            self.wait(5)
            self.removeAdapter()
            self.wait(5)

            # Power Pack Fire Count increased by 5
            # Power Pack Procedure Count unchanged
            # Adapter 1-Wire Fire Count increased by 1
            # Adapter EEPROM Fire Count unchanged
            # Adapter 1-Wire Procedure Count increased by 1
            # Adapter EEPROM Procedure Count unchanged
            self.Switch_ONN_Relay(1, 8)
            self.wait(7)
            print("EEA Adapter Engaged to Power Pack Mechanically")

            MCPThread.readingPowerPack.exitFlag = True
            # self.serPP.close()
            self.wait(2)

            # Reading Power Pack Usage Counts
            HandleFireCount2, HandleProcedureCount2 = GetHandleUseCount(self.PowerPackComPort)
            # print("HandleFireCount2 = , HandleProcedureCount2 = ", HandleFireCount2, HandleProcedureCount2)

            # Reading Adapter EEPROM Usage Counts
            AdapterEeProcedureCount2, AdapterEeFireCount2 = GetAdapterEepromUsageCounts(self.FtdiUartComPort)
            # print("AdapterEeProcedureCount2 = , AdapterEeFireCount2 = ", AdapterEeProcedureCount2, AdapterEeFireCount2)
            # self.wait(2)

            # Reading Adapter One-Wire usage Counts
            self.Switch_ONN_Relay(5, 5)
            self.Switch_ONN_Relay(6, 1)

            adapter_1w_eeprom_data = self.read_eeprom_data()
            # print("Adapter Onewire EEPROM Data ", adapter_1w_eeprom_data)
            print(list(map(hex, adapter_1w_eeprom_data)))

            data = [hex(x)[2:].zfill(2) for x in adapter_1w_eeprom_data]
            fireCnt = data[3:5]
            precCnt = data[7:9]
            AdapterOwFireCount2 = convert_single_list_ele_to_two_byte_decimal(fireCnt)
            AdapterOwProcedureCount2 = convert_single_list_ele_to_two_byte_decimal(precCnt)

            self.Switch_OFF_Relay(6, 1)
            self.Switch_OFF_Relay(5, 5)

            print('After Firing Handle Fire Count:' + str(HandleFireCount2),
                  'Handle Procedure Count:' + str(HandleProcedureCount2))
            print('After Firing Adapter Eeprom Fire Count:' + str(AdapterEeFireCount2),
                  'Adapter Eeprom Procedure Count:' + str(AdapterEeProcedureCount2))
            print('After Firing Adapter Onewire Fire Count:' + str(AdapterOwFireCount2),
                  'Adapter Onewire Procedure Count:' + str(AdapterOwProcedureCount2))

            self.startMCP()

            self.Switch_ONN_Relay(3,2)
            self.Switch_ONN_Relay(3,3)
            self.wait(5)

            ## Re-Connecting the adapter
            # Adapter UART Connection - Restoring UART Rx/Tx
            self.connect_adapter_test('UART RESTORED')  # B1 - ALL ON

            self.ExtensionOfTrocar('EEA Trocar Extention with SSE')
            self.DisconnectingEEAReload('Remove EEA Reload with SSE Prompt', exit_video=False)

            ## Holding Rotation Buttons - To Exit SSE Mode
            self.Switch_ONN_Relay(2, 1)  # B2:R7 - ON
            self.Switch_ONN_Relay(2, 2)  # B2:R8 - ON
            self.Switch_ONN_Relay(2, 7)  # B2:R1 - ON
            self.Switch_ONN_Relay(2, 8)  # B2:R2 - ON

            self.wait(5)

            self.Switch_OFF_Relay(2, 7)  # B2:R7 - OFF
            self.Switch_OFF_Relay(2, 8)  # B2:R8 - OFF
            self.Switch_OFF_Relay(2, 1)  # B2:R1 - OFF
            self.Switch_OFF_Relay(2, 2)  # B2:R2 - OFF

            self.wait(25)

            self.removeAdapter()

            self.wait(8)

            ## Re-Connecting the adapter
            self.connect_adapter_test()
            self.wait(5)

            procedure_firing = 1
            reload_length = self.fetch_parameter(data=reload_parameters["reload_length"], index=procedure_firing)
            reload_color = self.fetch_parameter(data=reload_parameters["reload_color"], index=procedure_firing)
            cartridge_color = self.fetch_parameter(data=reload_parameters["cartridge_color"], index=procedure_firing)
            print(simple_colors.blue(f"reload_state = {reload_parameters['reload_state']}\ncartridge_state = "
                                     f"{reload_parameters['cartridge_state']}"))

            # Attaching EEA reload along with ship cap presence check
            self.connect_reload(firing_count=f"{reload_parameters['firing_count']}_iteration_{procedure_firing + 1}",
                                reload_type=reload_parameters["reload_type"],
                                reload_color=reload_color,
                                reload_length=reload_length,
                                video_name=video_name,
                                reload_state=reload_parameters['reload_state'],
                                cartridge_state=reload_parameters['cartridge_state'],
                                cartridge_color=cartridge_color,
                                ship_cap_status=reload_parameters["ship_cap_presence"],
                                videoDisabledFalg=True
                                )

            self.EEAClamping(SuccessFlag=True, is_firing_test=True, clamp_force=clampingForce,
                             fire_force=firingForce, logs_to_compare='EEA Clamping on Tissue')

            self.GreenKeyAck(SuccessFlag=True)

            self.EEAFiring(fire_force=firingForce)

            self.apply_load_force(0)

            self.TiltOpen()
            self.TiltPromptOpen_original()

            if procedure_firing != firings - 1:
                is_firing_test_passed = self.is_firing_test_passed(procedure_firing, reload_parameters["firing_count"],
                                                                   fire_pass)
                if is_firing_test_passed:
                    fire_pass += 1

            # Remove Adapter along with Reload
            self.DisconnectingEEAReload(exit_video=False)
            self.wait(5)
            self.removeAdapter()
            self.wait(5)

            ## STEP 23: Record Power Pack and Adapter usage Counts ( By Engaging the Adapter )
            ## Power Pack Fire Count increased by 5
            # Power Pack Procedure Count unchanged
            # Adapter 1-Wire Fire Count increased by 1
            # Adapter EEPROM Fire Count increased by 2
            # Adapter 1-Wire Procedure Count unchanged
            # Adapter EEPROM Procedure Count increased by 1
            self.Switch_ONN_Relay(1, 8)
            self.wait(7)
            print("EEA Adapter Engaged to Power Pack Mechanically")

            MCPThread.readingPowerPack.exitFlag = True
            # self.serPP.close()
            self.wait(2)

            # Reading Power Pack Usage Counts
            HandleFireCount3, HandleProcedureCount3 = GetHandleUseCount(self.PowerPackComPort)

            # Reading Adapter EEPROM Usage Counts
            AdapterEeProcedureCount3, AdapterEeFireCount3 = GetAdapterEepromUsageCounts(self.FtdiUartComPort)

            # Reading Adapter One-Wire usage Counts
            self.Switch_ONN_Relay(5, 5)
            self.Switch_ONN_Relay(6, 1)

            adapter_1w_eeprom_data = self.read_eeprom_data()
            # print("Adapter Onewire EEPROM Data ", adapter_1w_eeprom_data)
            print(list(map(hex, adapter_1w_eeprom_data)))

            data = [hex(x)[2:].zfill(2) for x in adapter_1w_eeprom_data]
            fireCnt = data[3:5]
            precCnt = data[7:9]
            AdapterOwFireCount3 = convert_single_list_ele_to_two_byte_decimal(fireCnt)
            AdapterOwProcedureCount3 = convert_single_list_ele_to_two_byte_decimal(precCnt)

            self.Switch_OFF_Relay(6, 1)
            self.Switch_OFF_Relay(5, 5)

            print('After Firing2 Handle Fire Count:' + str(HandleFireCount3),
                  'After Firing2 Handle Procedure Count:' + str(HandleProcedureCount3))
            print('After Firing2 Adapter Eeprom Fire Count:' + str(AdapterEeFireCount3),
                  'After Firing2 Adapter Eeprom Procedure Count:' + str(AdapterEeProcedureCount3))
            print('After Firing2 Adapter Onewire Fire Count:' + str(AdapterOwFireCount3),
                  'After Firing2 Adapter Onewire Procedure Count:' + str(AdapterOwProcedureCount3))


            self.Switch_OFF_Relay(1, 8)
            print('Adapter Clutch Disengaged')

        self.is_firing_test_passed(firings - 1, reload_parameters["firing_count"], fire_pass)

    def DV_firing_400860(self, clampingForce, firingForce, articulationStateinFiring, retractionForce,
                  reload_parameters, firing_duration=0, is_smoke_test=False):
        fire_pass = 0

        firings = reload_parameters["procedure_firings_count"]

        print(simple_colors.blue(f"firing details for the iteration: {self.json_data}"))

        for procedure_firing in range(firings):

            video_name = reload_parameters["video_name"] + f"_proc_{procedure_firing}"

            reload_length = self.fetch_parameter(data=reload_parameters["reload_length"], index=procedure_firing)
            reload_color = self.fetch_parameter(data=reload_parameters["reload_color"], index=procedure_firing)
            cartridge_color = self.fetch_parameter(data=reload_parameters["cartridge_color"], index=procedure_firing)
            print(simple_colors.blue(f"reload_state = {reload_parameters['reload_state']}\ncartridge_state = "
                                     f"{reload_parameters['cartridge_state']}"))

            # 5.1.11. and 5.1.12  Attach a reload to the adapter.
            self.connect_reload(firing_count=f"{reload_parameters['firing_count']}_iteration_{procedure_firing + 1}",
                                reload_type=reload_parameters["reload_type"],
                                reload_color=reload_color,
                                reload_length=reload_length,
                                video_name=video_name,
                                reload_state=reload_parameters['reload_state'],
                                cartridge_state=reload_parameters['cartridge_state'],
                                cartridge_color=cartridge_color,
                                ship_cap_status=reload_parameters["ship_cap_presence"],
                                record_video=False,
                                videoDisabledFalg=True)

            # Steps form 5.1.13 to 5.1.15
            # Press the down toggle button until the device displays 100% fully clamped. See Figure 4.
            self.EEAClamping(SuccessFlag=True, is_firing_test=True, clamp_force=clampingForce,
                             fire_force=firingForce, logs_to_compare='EEA Clamping on Tissue', protocol_id = 400860)
            self.wait(1)

            # 5.1.16. Detach PEEA adapter from clamshell.
            self.removeAdapter_DV()
            self.wait(20)

            # 5.1.17. Wait a few seconds and then reattach adapter to clamshell.
            # Wait for the timer to complete and confirm that the handle indicates 100% fully clamped (249784).
            '''249784	In RECOVERY_MODE, the HANDLE shall return to previous indication that PEEA_ADAPTER is fully clamped 
            when PEEA_ADAPTER is attached with ANVIL at indicated CLAMP_GAP and prior to initiating FIRING.'''
            self.Connect_Adapter()
            self.wait(10)

            screen_name = "Fully_Clamped"
            folder_name = "Fully_Clamped"
            file_name = "Fully_Clamped"
            self.handle_screen(videoPath=self.videoPath, screen_name=screen_name, folder_name=folder_name,
                                           file_name=file_name, is_static_image=True)


            # 5.1.18. Press the green safety button.
            self.GreenKeyAck()

            # Firing related steps
            # self.EEA_DV_Firing_400860()
            self.EEA_Multiple_Recovery_Firing()

            self.apply_load_force(0)

            # 5.1.28.	After cutting has completed press the up toggle to extend the anvil to the tilt position.
            # Remove the staple ring and preserve it in a bag labeled with the reload type and firing number for burn-out (400860, 400862).
            self.TiltOpen_400860()
            self.TiltOpenPrompt_400860()

            if reload_parameters["reload_type"] == "EEA":
                self.DisconnectingEEAReload(exit_video=False)

            # removing adapter
            self.removeAdapter_DV()
            self.wait(10)

            # Re-Connect the Adapter
            self.Connect_Adapter()
            self.wait(25)
            print("After one firing reconnecting adapter ")
            self.connect_reload(firing_count=f"{reload_parameters['firing_count']}_iteration_{procedure_firing + 1}",
                                reload_type=reload_parameters["reload_type"],
                                reload_color=reload_color,
                                reload_length=reload_length,
                                video_name=video_name,
                                reload_state=reload_parameters['reload_state'],
                                cartridge_state=reload_parameters['cartridge_state'],
                                cartridge_color=cartridge_color,
                                ship_cap_status=reload_parameters["ship_cap_presence"],
                                record_video=False,
                                videoDisabledFalg=True)

            self.EEAClamping(SuccessFlag=True, is_firing_test=True, logs_to_compare='EEA Clamping on Tissue')

            # Press Green Key
            self.GreenKeyAck()
            print("Brfore SSE FING ")
            self.EEA_DV_Firing_SSE_400860()

            if procedure_firing != firings - 1:
                is_firing_test_passed = self.is_firing_test_passed(procedure_firing, reload_parameters["firing_count"],
                                                                   fire_pass)
                if is_firing_test_passed:
                    fire_pass += 1
        self.is_firing_test_passed(firings - 1, reload_parameters["firing_count"], fire_pass)

    def DV_firing_460333(self, clampingForce, firingForce, articulationStateinFiring, retractionForce,
                  reload_parameters, firing_duration=0, is_smoke_test=False):
        fire_pass = 0

        firings = reload_parameters["procedure_firings_count"]

        print(simple_colors.blue(f"firing details for the iteration: {self.json_data}"))

        for procedure_firing in range(firings):

            video_name = reload_parameters["video_name"] + f"_proc_{procedure_firing}"

            reload_length = self.fetch_parameter(data=reload_parameters["reload_length"], index=procedure_firing)
            reload_color = self.fetch_parameter(data=reload_parameters["reload_color"], index=procedure_firing)
            cartridge_color = self.fetch_parameter(data=reload_parameters["cartridge_color"], index=procedure_firing)
            print(simple_colors.blue(f"reload_state = {reload_parameters['reload_state']}\ncartridge_state = "
                                     f"{reload_parameters['cartridge_state']}"))

            # 5.1.11. and 5.1.12  Attach a reload to the adapter.
            self.connect_reload(firing_count=f"{reload_parameters['firing_count']}_iteration_{procedure_firing + 1}",
                                reload_type=reload_parameters["reload_type"],
                                reload_color=reload_color,
                                reload_length=reload_length,
                                video_name=video_name,
                                reload_state=reload_parameters['reload_state'],
                                cartridge_state=reload_parameters['cartridge_state'],
                                cartridge_color=cartridge_color,
                                ship_cap_status=reload_parameters["ship_cap_presence"],
                                record_video=False)

            # Steps form 5.1.13 to 5.1.15
            # Press the down toggle button until the device displays 100% fully clamped. See Figure 4.
            self.EEAClamping(SuccessFlag=True, is_firing_test=True, clamp_force=clampingForce,
                             fire_force=firingForce, logs_to_compare='EEA Clamping on Tissue')
            self.wait(1)

            # 5.1.16. Detach PEEA adapter from clamshell.
            self.removeAdapter_DV()
            self.wait(20)

            # 5.1.17. Wait a few seconds and then reattach adapter to clamshell.
            # Wait for the timer to complete and confirm that the handle indicates 100% fully clamped (249784).
            '''249784	In RECOVERY_MODE, the HANDLE shall return to previous indication that PEEA_ADAPTER is fully clamped 
            when PEEA_ADAPTER is attached with ANVIL at indicated CLAMP_GAP and prior to initiating FIRING.'''
            self.Connect_Adapter()
            self.wait(10)

            screen_name = "Fully_Clamped"
            folder_name = "Fully_Clamped"
            file_name = "Fully_Clamped"
            self.handle_screen(videoPath=self.videoPath, screen_name=screen_name, folder_name=folder_name,
                                           file_name=file_name, is_static_image=True)


            # 5.1.18. Press the green safety button.
            self.GreenKeyAck()

            # Firing related steps
            # self.EEA_DV_firing_460333()
            self.EEAFiring_RBDV_Recovery_Mode_460333()

            # making Load force zero
            self.apply_load_force(0)

            # 5.1.28.	After cutting has completed press the up toggle to extend the anvil to the tilt position.
            # Remove the staple ring and preserve it in a bag labeled with the reload type and firing number for burn-out (400860, 400862).
            self.TiltOpen_400860()
            self.TiltOpenPrompt_400860()

            if reload_parameters["reload_type"] == "EEA":
                self.DisconnectingEEAReload(exit_video=False)

            # removing adapter
            self.removeAdapter_DV()
            self.wait(10)

            # Re-Connect the Adapter
            self.Connect_Adapter()
            self.wait(25)
            print("After one firing reconnecting adapter ")
            self.connect_reload(firing_count=f"{reload_parameters['firing_count']}_iteration_{procedure_firing + 1}",
                                reload_type=reload_parameters["reload_type"],
                                reload_color=reload_color,
                                reload_length=reload_length,
                                video_name=video_name,
                                reload_state=reload_parameters['reload_state'],
                                cartridge_state=reload_parameters['cartridge_state'],
                                cartridge_color=cartridge_color,
                                ship_cap_status=reload_parameters["ship_cap_presence"],
                                record_video=False)

            self.EEAClamping(SuccessFlag=True, is_firing_test=True, clamp_force = clampingForce, fire_force = firingForce,
                             logs_to_compare='EEA Clamping on Tissue')

            # Press Green Key
            self.GreenKeyAck()
            print("Before SSE FIRING ")
            self.EEA_DV_Firing_SSE_400860()

            if procedure_firing != firings - 1:
                is_firing_test_passed = self.is_firing_test_passed(procedure_firing, reload_parameters["firing_count"],
                                                                   fire_pass)
                if is_firing_test_passed:
                    fire_pass += 1
        self.is_firing_test_passed(firings - 1, reload_parameters["firing_count"], fire_pass)

    def DV_Staple_Missing_359465(self, clampingForce, firingForce,  reload_parameters ):
        fire_pass = 0

        firings = reload_parameters["procedure_firings_count"]

        print(simple_colors.blue(f"firing details for the iteration: {self.json_data}"))

        for procedure_firing in range(firings):

            video_name = reload_parameters["video_name"] + f"_proc_{procedure_firing}"

            reload_length = self.fetch_parameter(data=reload_parameters["reload_length"], index=procedure_firing)
            reload_color = self.fetch_parameter(data=reload_parameters["reload_color"], index=procedure_firing)
            print(simple_colors.blue(f"reload_state = {reload_parameters['reload_state']}"))

            # 5.2.2. Attach a reload with known missing staples to the adapter.
            self.connect_reload(firing_count=f"{reload_parameters['firing_count']}_iteration_{procedure_firing + 1}",
                                reload_type=reload_parameters["reload_type"],
                                reload_color=reload_color,
                                reload_length=reload_length,
                                video_name=video_name,
                                reload_state=reload_parameters['reload_state'],
                                ship_cap_status=reload_parameters["ship_cap_presence"],
                                record_video=False)

            # Steps form 5.2.3 to 5.2.8
            # 5.2.7. Press and hold the down toggle button to retract the trocar until the OLED screen displays “100%”
            # on the OLED screen, indicating 100% clamp on the media.
            # 5.2.8. After reaching 100% clamp, wait for the OLED screen to indicate that the
            # compression has reached steady state. { Image Comparison }
            self.EEAClamping(SuccessFlag=True, is_firing_test=True, clamp_force=clampingForce,
                             fire_force=firingForce, logs_to_compare='EEA Clamping on Tissue')

            # 5.2.9. The handle shall indicate safety key press upon reaching steady state.
            # 5.2.10. Press the green button to enter firing mode.
            self.GreenKeyAck()

            # Firing related steps
            self.EEA_DV_Firing_Staple_Missing_359465()

            if procedure_firing != firings - 1:
                is_firing_test_passed = self.is_firing_test_passed(procedure_firing, reload_parameters["firing_count"],
                                                                   fire_pass)
                if is_firing_test_passed:
                    fire_pass += 1
        self.is_firing_test_passed(firings - 1, reload_parameters["firing_count"], fire_pass)

    def DV_Knife_Missing_359465(self, clampingForce, firingForce,  reload_parameters ):
        fire_pass = 0

        firings = reload_parameters["procedure_firings_count"]

        print(simple_colors.blue(f"firing details for the iteration: {self.json_data}"))

        for procedure_firing in range(firings):

            video_name = reload_parameters["video_name"] + f"_proc_{procedure_firing}"

            reload_length = self.fetch_parameter(data=reload_parameters["reload_length"], index=procedure_firing)
            reload_color = self.fetch_parameter(data=reload_parameters["reload_color"], index=procedure_firing)
            print(simple_colors.blue(f"reload_state = {reload_parameters['reload_state']}"))

            # 5.3.2. Attach a reload with known missing knife to the adapter.
            self.connect_reload(firing_count=f"{reload_parameters['firing_count']}_iteration_{procedure_firing + 1}",
                                reload_type=reload_parameters["reload_type"],
                                reload_color=reload_color,
                                reload_length=reload_length,
                                video_name=video_name,
                                reload_state=reload_parameters['reload_state'],
                                ship_cap_status=reload_parameters["ship_cap_presence"],
                                record_video=False)

            # Steps form 5.3.3 to 5.3.8
            # 5.3.7. Press and hold the down toggle button to retract the trocar until the OLED screen displays “100%”
            # on the OLED screen, indicating 100% clamp on the media.
            # 5.3.8. After reaching 100% clamp, wait for the OLED screen to indicate that the
            # compression has reached steady state. { Image Comparison }
            self.EEAClamping(SuccessFlag=True, is_firing_test=True, clamp_force=clampingForce,
                             fire_force=firingForce, logs_to_compare='EEA Clamping on Tissue')

            # 5.3.9. The handle shall indicate safety key press upon reaching steady state.
            # 5.3.10. Press the green button to enter firing mode.
            self.GreenKeyAck()

            # Firing related steps
            self.EEA_DV_Firing_Knife_Missing_359465()

            if procedure_firing != firings - 1:
                is_firing_test_passed = self.is_firing_test_passed(procedure_firing, reload_parameters["firing_count"],
                                                                   fire_pass)
                if is_firing_test_passed:
                    fire_pass += 1
        self.is_firing_test_passed(firings - 1, reload_parameters["firing_count"], fire_pass)

    def DV_Cut_Max_Force_359465(self, clampingForce, firingForce,  reload_parameters ):
        fire_pass = 0

        firings = reload_parameters["procedure_firings_count"]

        print(simple_colors.blue(f"firing details for the iteration: {self.json_data}"))

        for procedure_firing in range(firings):

            video_name = reload_parameters["video_name"] + f"_proc_{procedure_firing}"

            reload_length = self.fetch_parameter(data=reload_parameters["reload_length"], index=procedure_firing)
            reload_color = self.fetch_parameter(data=reload_parameters["reload_color"], index=procedure_firing)
            print(simple_colors.blue(f"reload_state = {reload_parameters['reload_state']}"))

            # 5.4.2. Attach a reload with the appropriately sized “max cut force plug” inserted inside the reload.
            # Steps from 5.4.3 to 5.4.6
            self.connect_reload(firing_count=f"{reload_parameters['firing_count']}_iteration_{procedure_firing + 1}",
                                reload_type=reload_parameters["reload_type"],
                                reload_color=reload_color,
                                reload_length=reload_length,
                                video_name=video_name,
                                reload_state=reload_parameters['reload_state'],
                                ship_cap_status=reload_parameters["ship_cap_presence"],
                                record_video=False, videoDisabledFalg=True)

            # Steps form 5.4.7 to 5.4.8
            # 5.4.7. Press and hold the down toggle button to retract the trocar until the OLED screen displays “100%”
            # on the OLED screen, indicating 100% clamp on the media.
            # 5.4.8. After reaching 100% clamp, wait for the OLED screen to indicate that the compression has reached steady state.
            self.EEAClamping(SuccessFlag=True, is_firing_test=True, clamp_force=clampingForce,
                             fire_force=firingForce, logs_to_compare='EEA Clamping on Tissue')

            # 5.4.9. The handle shall indicate safety key press upon reaching steady state.
            # 5.4.10. Press the green button to enter firing mode.
            self.GreenKeyAck()

            # Firing related steps
            self.EEA_DV_Firing_Maximum_Cut_Force_359465()

            if procedure_firing != firings - 1:
                is_firing_test_passed = self.is_firing_test_passed(procedure_firing, reload_parameters["firing_count"],
                                                                   fire_pass)
                if is_firing_test_passed:
                    fire_pass += 1
        self.is_firing_test_passed(firings - 1, reload_parameters["firing_count"], fire_pass)

    def DV_firing_450524(self, clampingForce, firingForce, articulationStateinFiring, retractionForce,
                  reload_parameters, firing_duration=0, is_smoke_test=False):
        fire_pass = 0
        # adapterConnected = True
        #  try:
        firings = reload_parameters["procedure_firings_count"]
        #  except:
        # firings = 1

        print(simple_colors.blue(f"firing details for the iteration: {self.json_data}"))

        for procedure_firing in range(firings):

            video_name = reload_parameters["video_name"] + f"_proc_{procedure_firing}"

            reload_length = self.fetch_parameter(data=reload_parameters["reload_length"], index=procedure_firing)
            reload_color = self.fetch_parameter(data=reload_parameters["reload_color"], index=procedure_firing)
            cartridge_color = self.fetch_parameter(data=reload_parameters["cartridge_color"], index=procedure_firing)
            print(simple_colors.blue(f"reload_state = {reload_parameters['reload_state']}\ncartridge_state = "
                                     f"{reload_parameters['cartridge_state']}"))

            # 5.1.11. and 5.1.12  Attach a reload to the adapter.
            self.connect_reload(firing_count=f"{reload_parameters['firing_count']}_iteration_{procedure_firing + 1}",
                                reload_type=reload_parameters["reload_type"],
                                reload_color=reload_color,
                                reload_length=reload_length,
                                video_name=video_name,
                                reload_state=reload_parameters['reload_state'],
                                cartridge_state=reload_parameters['cartridge_state'],
                                cartridge_color=cartridge_color,
                                ship_cap_status=reload_parameters["ship_cap_presence"],
                                record_video=False,
                                videoDisabledFalg=True)

            # Steps form 5.1.13 to 5.1.15
            # Press the down toggle button until the device displays 100% fully clamped. See Figure 4.
            self.EEAClamping(SuccessFlag=True, is_firing_test=True, clamp_force=clampingForce, fire_force=firingForce, logs_to_compare='EEA Clamping on Tissue')
            self.wait(1)

            # # 5.1.16. Detach PEEA adapter from clamshell.
            # self.removeAdapter_DV()
            # self.wait(20)
            #
            # # 5.1.17. Wait a few seconds and then reattach adapter to clamshell.
            # # Wait for the timer to complete and confirm that the handle indicates 100% fully clamped (249784).
            # '''249784	In RECOVERY_MODE, the HANDLE shall return to previous indication that PEEA_ADAPTER is fully clamped
            # when PEEA_ADAPTER is attached with ANVIL at indicated CLAMP_GAP and prior to initiating FIRING.'''
            # self.Connect_Adapter()
            # self.wait(10)
            #
            # screen_name = "Fully_Clamped"
            # folder_name = "Fully_Clamped"
            # file_name = "Fully_Clamped"
            # self.handle_screen(videoPath=self.videoPath, screen_name=screen_name, folder_name=folder_name,
            #                    file_name=file_name, is_static_image=True)


            # 5.1.18. Press the green safety button.
            self.GreenKeyAck()

            # Firing related steps
            self.EEA_DV_Firing_450524()

            self.apply_load_force(0)

            # 5.1.28.	After cutting has completed press the up toggle to extend the anvil to the tilt position.
            # Remove the staple ring and preserve it in a bag labeled with the reload type and firing number for burn-out (400860, 400862).
            self.TiltOpen()
            self.TiltPromptOpen_original()

            if reload_parameters["reload_type"] == "EEA":
                self.DisconnectingEEAReload(exit_video=False)

            if procedure_firing != firings - 1:
                is_firing_test_passed = self.is_firing_test_passed(procedure_firing, reload_parameters["firing_count"],
                                                                   fire_pass)
                if is_firing_test_passed:
                    fire_pass += 1
        self.is_firing_test_passed(firings - 1, reload_parameters["firing_count"], fire_pass)

    def Alex_firing_test(self, clampingForce, firingForce, articulationStateinFiring, retractionForce,
                         reload_parameters, firing_duration=0, is_smoke_test=False):
        fire_pass = 0
        firings = 1
        # reload_parameters["num_of_firings_in_procedure"] if reload_parameters[
        #                                                                   "num_of_firings_in_procedure"] is not None else \
        #     reload_parameters["Num_of_Firings_with_Reload"]

        for procedure_firing in range(firings):
            video_name = reload_parameters["video_name"] + f"_proc_{procedure_firing}"

            reload_length = self.fetch_parameter(data=reload_parameters["reload_length"], index=procedure_firing)
            reload_color = self.fetch_parameter(data=reload_parameters["reload_color"], index=procedure_firing)
            cartridge_color = self.fetch_parameter(data=reload_parameters["cartridge_color"], index=procedure_firing)
            print(simple_colors.blue(f"reload_state = {reload_parameters['reload_state']}\ncartridge_state = "
                                     f"{reload_parameters['cartridge_state']}"))
            # logger.debug(f"reload_parameters = {reload_parameters}")
            self.connect_reload(firing_count=f"{reload_parameters['firing_count']}_iteration_{procedure_firing + 1}",
                                reload_type=reload_parameters["reload_type"],
                                reload_color=reload_color,
                                reload_length=reload_length,
                                video_name=video_name,
                                reload_state=reload_parameters['reload_state'],
                                cartridge_state=reload_parameters['cartridge_state'],
                                cartridge_color=cartridge_color,
                                ship_cap_status=reload_parameters["ship_cap_presence"]
                                )

            if firing_duration == 0:
                firing_duration = firing_default_delay

            self.EEAClamping(SuccessFlag=True, is_firing_test=True, logs_to_compare='EEA Clamping on Tissue')

            self.wait(2)
            self.GreenKeyAck(SuccessFlag=True)

            # self.apply_load_force(firing_Force)
            self.AlexEEAFiring()

            # self.apply_load_force(retraction_Force)
            # self.Retracting()
            self.TiltOpen()
            self.TiltPromptOpen_original()

            if reload_parameters["reload_type"] == "EEA":
                self.DisconnectingEEAReload()

            if procedure_firing != firings - 1:
                is_firing_test_passed = self.is_firing_test_passed(procedure_firing, reload_parameters["firing_count"],
                                                                   fire_pass)
                if is_firing_test_passed:
                    fire_pass += 1

        self.is_firing_test_passed(firings - 1, reload_parameters["firing_count"], fire_pass)

    def is_firing_test_passed(self, procedure_firing, firing_count, fire_pass):
        OLEDRecordingThread.exitFlag = True
        status_variables_1 = {}
        if self.status_data_1 is not None:
            status_variables_1 = self.status_data_1['status_variables']
        temp = 'PASS'

        if len(self.Normal_Firing_Test_Results) == 0:
            self.Normal_Firing_Test_Results = self.Test_Results
            print(f'normal_test_results: {self.Normal_Firing_Test_Results}')

        for item in self.Normal_Firing_Test_Results:
            try:
                if ((str.split(item, ':', 1))[1].strip()) == 'PASS':
                    pass
                elif ((str.split(item, ':', 1))[1].strip()) == 'FAIL':
                    temp = 'FAIL'
                    break
            except Exception as Ex:
                print(f"Exception Occurred! {Ex}")

        if self.status_data_2 is not None:
            status_variables_2 = self.status_data_2['status_variables']

            print('StatusVariable After Firing', status_variables_2)

            if (self.handle_fire_count_2 - self.handle_fire_count_1) == 5 and (
                    status_variables_1 == status_variables_2):
                temp = 'PASS'
                # logger.info("status variables are matched and the fire count incremented by 1.")
                print("status variables are matched and the fire count incremented by 5.")

        if temp == 'PASS':
            fire_pass = fire_pass + 1
        print(f'% of Successful Procedures in firing {firing_count}: ', int(100 * fire_pass / (procedure_firing + 1)))
        # Close MCP port

        self.Test_Results.append(f"Firing={firing_count}_iteration_{procedure_firing + 1}" +
                                 ':' + temp)
        if self.Test_Results != self.Normal_Firing_Test_Results:
            self.Test_Results += self.Normal_Firing_Test_Results
        print(self.Test_Results)
        # logger.info(f"Test Results: {self.Test_Results}")
        if temp == 'PASS':
            return True
        return False

    def Rotation(self):
        self.Switch_ONN_Relay(2, 7)  # B2:R7 - ON
        self.wait(1)
        self.Switch_OFF_Relay(2, 7)  # B2:R7 - OFF

        self.Switch_ONN_Relay(2, 8)  # B2:R8 - ON
        self.wait(1)
        self.Switch_OFF_Relay(2, 8)  # B2:R8 - OFF
        # self.Switch_ONN_Relay(2, 7)  # B2:R7 - ON
        # self.Switch_OFF_Relay(2, 7)  # B2:R7 - OFF

    def Adapter_Rotation_Tests(self, SuccessFlag, my_Serthread):
        # if No parameters are passed to the below method, This will rotate in all the 4 directions.
        self.rotation_with_direction(SuccessFlag=SuccessFlag)

    def Reload_Articulation_Tests(self, SuccessFlag, my_Serthread):

        self.articulation_with_direction(SuccessFlag=SuccessFlag)

    def Reload_Clamp_Cycle_Test(self, SuccessFlag, my_Serthread):
        with nidaqmx.Task() as task:
            task.ao_channels.add_ao_voltage_chan('Dev1/ao0')
            print('1 Channel 1 Sample Write:')
            print(task.write(0.7))
        self.Clamping(SuccessFlag)

        self.Unclamping(SuccessFlag)

    def RemovingSULUReload(self, is_firing_test=True, is_emergency_retraction=False, logs_to_compare='Remove Reload',
                           bypass_compare_logs=False, exit_video_stream=True, delay=5):
        if self.serPP is not None:
            self.my_Serthread.clearQue()
        self.Switch_OFF_Relay(3, 1)  # B3:R1 - OFF
        self.Switch_OFF_Relay(3, 2)  # B3:R2 - OFF
        self.Switch_OFF_Relay(3, 3)  # B3:R3 - ON
        self.Switch_OFF_Relay(5, 8)  # B5:R8 - OFF
        self.wait(delay)
        if not bypass_compare_logs:
            if self.serPP is not None:
                if is_emergency_retraction:
                    logs_to_compare = 'Remove Reload Emergency Retraction'
                self.compare_logs(logs_to_compare=logs_to_compare, SuccessFlag=True, is_firing_test=is_firing_test,
                                  event_name='Reload_Connected', is_event_connecting=False)
        if exit_video_stream:
            OLEDRecordingThread.exitFlag = True
        # self.wait(5)

    def connectUnauthenticatedReload(self, is_firing_test=True):
        if self.serPP is not None:
            self.my_Serthread.clearQue()
        self.Switch_ONN_Relay(6, 4)
        self.Switch_ONN_Relay(3, 1)
        self.wait(5)
        if self.serPP is not None:
            self.compare_logs(logs_to_compare='Unauthenticated SULU Connected', SuccessFlag=True,
                              is_firing_test=is_firing_test)

    def removeUnauthenticatedReload(self, is_firing_test=True):
        if self.serPP is not None:
            self.my_Serthread.clearQue()
        self.Switch_OFF_Relay(3, 1)
        self.Switch_OFF_Relay(6, 4)
        if self.serPP is not None:
            self.compare_logs(logs_to_compare='Remove Reload', SuccessFlag=True,
                              is_firing_test=is_firing_test)
        OLEDRecordingThread.exitFlag = True

    def RecordPowerPackAndAdapterUsageCounts(self, firingCount):
        self.Switch_ONN_Relay(1, 8)
        self.wait(7)
        print("EEA Adapter Engaged to Power Pack Mechanically")

        MCPThread.readingPowerPack.exitFlag = True
        # self.disconnect_MCP_Port()
        self.wait(2)

        # Reading Power Pack Usage Counts
        HandleFireCount, HandleProcedureCount = GetHandleUseCount(self.PowerPackComPort)

        # Reading Adapter EEPROM Usage Counts
        AdapterEeProcedureCount, AdapterEeFireCount = GetAdapterEepromUsageCounts(self.FtdiUartComPort)

        # For capturing Onewire Usage counts from the Adapter via BB, below relays should be ON.
        self.Switch_ONN_Relay(5, 5)  # B5:R8 - ON
        self.Switch_ONN_Relay(6, 1)  # B6:R1 - ON

        # Reading Adapter One-Wire usage Counts
        AdapterOwProcedureCount, AdapterOwFireCount = GetAdapterOnewireUsageCounts(self.BlackBoxComPort)

        self.Switch_OFF_Relay(6, 1)  # B6:R1 - OFF
        self.Switch_OFF_Relay(5, 5)  # B5:R8 - OFF

        if 1 == firingCount:
            print('After Firing Handle Fire Count:' + str(HandleFireCount),
                  'Handle Procedure Count:' + str(HandleProcedureCount))
            print('After Firing Adapter Eeprom Fire Count:' + str(AdapterEeFireCount),
                  'Adapter Eeprom Procedure Count:' + str(AdapterEeProcedureCount))
            print('After Firing Adapter Onewire Fire Count:' + str(AdapterOwFireCount),
                  'Adapter Onewire Procedure Count:' + str(AdapterOwProcedureCount))
        elif 2 == firingCount:
            print('After Firing2 Handle Fire Count:' + str(HandleFireCount),
                  'After Firing2 Handle Procedure Count:' + str(HandleProcedureCount))
            print('After Firing2 Adapter Eeprom Fire Count:' + str(AdapterEeFireCount),
                  'After Firing2 Adapter Eeprom Procedure Count:' + str(AdapterEeProcedureCount))
            print('After Firing2 Adapter Onewire Fire Count:' + str(AdapterOwFireCount),
                  'After Firing2 Adapter Onewire Procedure Count:' + str(AdapterOwProcedureCount))
        elif 0 == firingCount:
            print('Before Firing Handle Fire Count:' + str(HandleFireCount),
                  'Handle Procedure Count:' + str(HandleProcedureCount))
            print('Before Firing Adapter Eeprom Fire Count:' + str(AdapterEeFireCount),
                  'Adapter Eeprom Procedure Count:' + str(AdapterEeProcedureCount))
            print('Before Firing Adapter Onewire Fire Count:' + str(AdapterOwFireCount),
                  'Adapter Onewire Procedure Count:' + str(AdapterOwProcedureCount))
        else:
            print('Adapter Eeprom Fire Count:' + str(AdapterEeFireCount),
                  'Adapter Eeprom Procedure Count:' + str(AdapterEeProcedureCount))
            print('Adapter Onewire Fire Count:' + str(AdapterOwFireCount),
                  'Adapter Onewire Procedure Count:' + str(AdapterOwProcedureCount))

        # Re-Opening the PowerPackComPort
        self.startMCP()

    def ConnectAdapter(self, *args):
        self.Switch_ONN_Relay(1, 8)  # B1:R7 - OFF
        self.wait(5)
        self.Switch_ONN_Relay(1, 1)  # B1:R1 - OFF
        self.Switch_ONN_Relay(1, 2)  # B1:R2 - OFF
        self.Switch_ONN_Relay(1, 3)  # B1:R3 - OFF
        self.Switch_ONN_Relay(1, 4)  # B1:R4 - OFF
        self.Switch_ONN_Relay(1, 7)  # B1:R7 - OFF
        self.Switch_ONN_Relay(1, 6)  # B1:R7 - OFF

    def AlexremoveAdapter(self, logs_to_compare='Remove EEA Adapter'):
        self.my_Serthread.clearQue()
        # self.Switch_OFF_Relay(1, 2)  # B1:R2 - OFF
        # self.Switch_OFF_Relay(1, 3)  # B1:R3 - OFF
        # self.Switch_OFF_Relay(1, 4)  # B1:R4 - OFF
        # self.Switch_OFF_Relay(1, 1)  # B1:R1 - OFF
        # self.Switch_OFF_Relay(1, 7)  # B1:R7 - OFF
        # self.Switch_OFF_Relay(1, 6)  # B1:R7 - OFF
        self.Switch_OFF_ALL_Relays_In_Each_Bank(1)
        self.Switch_ONN_Relay(1, 5)  # B1:R7 - OFF

        # print("Disengaged adapter Stepper motor controlled")
        # self.Switch_OFF_Relay(1, 8)
        print('Adapter Clutch Disengaged')

    def removeAdapter(self, logs_to_compare='Remove EEA Adapter'):
        self.my_Serthread.clearQue()
        self.Switch_OFF_Relay(1, 2)  # B1:R2 - OFF
        self.Switch_OFF_Relay(1, 3)  # B1:R3 - OFF
        self.Switch_OFF_Relay(1, 4)  # B1:R4 - OFF
        self.Switch_OFF_Relay(1, 1)  # B1:R1 - OFF
        self.Switch_OFF_Relay(1, 7)  # B1:R7 - OFF
        self.Switch_OFF_Relay(1, 6)  # B1:R7 - OFF

        #### Delete this part of code once tested ###########
        self.wait(7)
        self.compare_logs(logs_to_compare, SuccessFlag=True)
        self.wait(2)

        self.Switch_OFF_Relay(1, 8)
        ######################################################

        # self.wait(10) ####Issue 450475
        # self.compare_logs(logs_to_compare, SuccessFlag=True)
        # self.wait(2)

        # print("Disengaged adapter Stepper motor controlled")
        # self.Switch_OFF_Relay(1, 8) ####Issue 450475
        # print('Adapter Clutch Disengaged')

    def removeAdapter_DV(self, logs_to_compare='Remove EEA Adapter'):
        self.my_Serthread.clearQue()
        print('Adapter Clutch Disengaged')

        self.Switch_OFF_ALL_Relays_In_Each_Bank(1)
        self.Switch_ONN_Relay(1, 5)  # B1:R5 - ON

    def get_adapter_EOL_data_bytes(self, ItemForEOL):
        ser = serial.Serial(self.BlackBoxComPort, 9600)
        command = None
        for s in range(0, 20):
            ser.write(command_ONEWIRE_READ_ADAPTER)
            s = ser.readline(2)
            packet_size = s[1]
            read_data = ser.read(packet_size - 2)
            # print(read_data, 'read_data')
            read_data = s + read_data

            hex_array = [hex(x)[2:] for x in read_data]
            if (int(hex_array[3], 16) == 73) and (int(hex_array[4], 16) == 3):
                if ItemForEOL == "NoProcedureRem":
                    hex_array[13] = hex_array[15]
                    hex_array[14] = hex_array[16]
                elif ItemForEOL == "ZeroProcLimit":
                    hex_array[15] = 0
                    hex_array[16] = 0
                elif ItemForEOL == "NoFireRem":
                    hex_array[9] = hex_array[11]
                    hex_array[10] = hex_array[12]
                elif ItemForEOL == "ZeroFireLim":
                    hex_array[11] = 0
                    hex_array[12] = 0
                byte_data_from_hex = [int(j, 16) for j in hex_array]
                # Compute CRC for data
                byte_data_temp1 = byte_data_from_hex[6:]
                # Get the data bytes excluding the data CRC and the packet CRC which 4 bytes from the end
                byte_data_temp2 = byte_data_temp1[:-4]

                command = fetch_command([170, 71, 0, 72, 3], byte_data_temp2)
                break

        self.wait(1)
        ser.close()

        return command

    def connect_Adapter_Without_Uart(self):
        self.Switch_ONN_Relay(1, 8)
        self.wait(7)
        self.Switch_ONN_Relay(1, 7)
        self.Switch_ONN_Relay(1, 6)
        self.Switch_ONN_Relay(1, 5)
        self.Switch_ONN_Relay(1, 1)
        self.Switch_ONN_Relay(1, 2)
        logs_to_compare = 'EEA Adapter Connected with UART Rx & Tx Open Circuit'
        self.compare_logs(logs_to_compare, is_firing_test=False, SuccessFlag=True)

        self.wait(5)
        print("Restoring Adapter UART Rx & Tx")
        self.Switch_ONN_Relay(1, 3)
        self.Switch_ONN_Relay(1, 4)
        self.wait(10)
        logs_to_compare = 'EEA Adapter UART Rx & Tx Open Circuit Restored'
        self.compare_logs(logs_to_compare, is_firing_test=False, SuccessFlag=True)

    def connect_adapter_test(self, adapter_type=None, adapter_model=None, successFlag=True, is_procedure_EOL=False,
                             is_firing_EOL=False, is_delay_required=True, fixture_validation=False):
        event_key = ''
        self.my_Serthread.clearQue()
        if adapter_type is None:
            adapter_type = 'GOOD'
        if adapter_model is None:
            adapter_model = 'EEA'
        if adapter_type.upper() == 'EOL':
            event_key = ''
            self.Connect_Adapter()
            if is_procedure_EOL and is_firing_EOL:
                adapter_EOL_data_bytes = self.get_adapter_EOL_data_bytes(ItemForEOL='NoProcedureRem')
                self.configure_adapter_1Wire(adapter_EOL_data_bytes)
            elif is_procedure_EOL:
                adapter_EOL_data_bytes = self.get_adapter_EOL_data_bytes(ItemForEOL='NoProcedureRem')
                self.configure_adapter_1Wire(adapter_EOL_data_bytes)
            else:
                adapter_EOL_data_bytes = self.get_adapter_EOL_data_bytes(ItemForEOL='NoFireRem')
                self.configure_adapter_1Wire(adapter_EOL_data_bytes)
        elif adapter_type.upper() == 'GOOD':
            event_key = 'EEA Adapter Connected'
            self.Connect_Adapter()
        elif adapter_type.upper() == 'UART RESTORED':
            event_key = 'EEA Adapter Connected With Restored Rx & Tx'
            self.Connect_Adapter()
            # self.configure_adapter_1Wire(adapter_usable_byte_data)
        elif adapter_type.upper() == 'SIP IN-PROGRESS':
            event_key = 'EEA Adapter Re-Connected After Stapling In Progress'
            self.Connect_Adapter()
            # self.configure_adapter_1Wire(adapter_usable_byte_data)
        elif adapter_type.upper() == 'AFTER CUT RECOVERY IN-PROGRESS':
            event_key = 'EEA Adapter Re-Connected After Stapling In Progress'
            self.Connect_Adapter()
            # self.configure_adapter_1Wire(adapter_usable_byte_data)
        elif adapter_type.upper() == 'UNSUPPORTED':
            event_key = ''
            self.configure_adapter_1Wire(adapter_unsupported_byte_data)
            self.Connect_Adapter()
        elif adapter_type.upper() == 'UNKNOWN':
            event_key = ''
            self.configure_adapter_1Wire(adapter_unknown_byte_data)
            self.Connect_Adapter()
        elif adapter_type.upper() == 'UNAUTHENTICATED':
            event_key = ''
            self.configure_adapter_1Wire(adapter_unauthenticated_byte_data)
            self.Connect_Unauthenticated_Adapter()

        if is_delay_required:
            self.wait(30)
            if fixture_validation:
                print("EEA Adapter Connected")
            self.compare_logs(logs_to_compare=event_key, SuccessFlag=successFlag, fixtureValidation=fixture_validation)

    def Connect_Adapter(self):
        self.Switch_ONN_Relay(1, 8)  # B1:R7 - OFF
        # self.wait(5)   ### Issue 450475
        self.wait(5)
        self.Switch_ONN_Relay(1, 6)  # B1:R7 - OFF
        self.Switch_ONN_Relay(1, 7)  # B1:R7 - OFF
        self.Switch_ONN_Relay(1, 3)  # B1:R3 - OFF
        self.Switch_ONN_Relay(1, 4)  # B1:R4 - OFF
        self.Switch_ONN_Relay(1, 1)  # B1:R1 - OFF
        self.Switch_ONN_Relay(1, 2)  # B1:R2 - OFF

    def Connect_Unauthenticated_Adapter(self):
        self.Switch_ONN_Relay(1, 8)  # B1:R7 - OFF
        self.wait(5)
        self.Switch_ONN_Relay(1, 6)  # B1:R7 - OFF
        self.Switch_ONN_Relay(1, 7)  # B1:R7 - OFF
        self.Switch_ONN_Relay(1, 3)  # B1:R3 - OFF
        self.Switch_ONN_Relay(1, 4)  # B1:R4 - OFF
        self.Switch_ONN_Relay(1, 1)  # B1:R1 - OFF
        self.Switch_ONN_Relay(6, 3)  # B1:R2 - OFF

    def configure_adapter_1Wire(self, byte_data):
        self.Switch_OFF_Relay(6, 1)
        self.wait(1)

        self.Switch_ONN_Relay(5, 1)  # B5:R1 - ON
        self.Switch_ONN_Relay(5, 5)  # B5:R5 - ON

        self.write_eeprom_data(data_bytes=byte_data)

        self.Switch_OFF_Relay(5, 1)  # B5:R1 - OFF
        self.Switch_OFF_Relay(5, 5)  # B5:R1 - OFF
        self.wait(1)

    def removeClamshell(self, logs_to_compare="Remove Clamshell", fixtureValidation=False):
        self.my_Serthread.clearQue()
        self.send_decimal_bytes(TURN_OFF_ALL_RELAYS_IN_ALL_BANKS[0])
        self.wait(5)
        self.compare_logs(logs_to_compare=logs_to_compare, is_firing_test=False, SuccessFlag=True,
                          event_name='Clampshell_Connected', is_event_connecting=False, fixtureValidation=fixtureValidation)
        self.wait(2)

    def unathenticate_clasmshell(self, events_key, success_flag):
        self.my_Serthread.clearQue()
        self.Switch_OFF_Relay(1, 5)
        self.wait(0.01)
        self.Switch_ONN_Relay(6, 2)
        self.wait(5)
        self.compare_logs(events_key, success_flag)


    def connectClamshellTest(self, clamshell_type=None, success_flag=True, test_step_number=None, fixture_validation=False):
        clsmshell_UNUSED_byte_data = [2, 3, 4, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                                      0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                                      0, 0, 0, 0, 0, 0, 0, 0]
        if clamshell_type is None:
            clamshell_type = 'UNUSED'
        if clamshell_type.upper() == 'USED':
            events_key = 'Used Clamshell Connected'
            self.configure_clamshell(clsmshell_USED_byte_data)
            self.connectClamshell(events_key, success_flag)
        elif clamshell_type.upper() == 'UNUSED':
            events_key = 'Clamshell Connected'
            self.configure_clamshell(clsmshell_UNUSED_byte_data, fixture_validation)
            self.connectClamshell(events_key, success_flag, test_step_number, fixture_validation)
        elif clamshell_type.upper() == 'UNAUTHENTICATED':
            events_key = 'Unauthenticated Clamshell Connected'
            self.unathenticate_clasmshell(events_key, success_flag)
        elif clamshell_type.upper() == 'UNSUPPORTED':
            events_key = ''
            self.configure_clamshell(clsmshell_UNSUPPORTED_byte_data)
            self.connectClamshell(events_key, success_flag)
        elif clamshell_type.upper() == 'UNKNOWN':
            events_key = ''
            self.configure_clamshell(clsmshell_UNKNOWN_byte_data)
            self.connectClamshell(events_key, success_flag, test_step_number)

    def connectClamshell(self, eventKey=None, successFlag=True, test_number=None, fixture_validation=False):
        # self.my_Serthread.clearQue()
        self.Switch_ONN_Relay(1, 5)  # B1:R5 - ON
        self.wait(5)
        if fixture_validation:
            print("Un-used Clamshell Connected")
        self.compare_logs(eventKey, successFlag, event_name='Clampshell_Connected', is_event_connecting=True, fixtureValidation=fixture_validation) #, step_number=test_number)

    def PlacingPowerPackOnCharger(self):
        self.Switch_ONN_Relay(3, 8)
        self.Switch_ONN_Relay(3, 7)
        # self.Switch_ONN_Relay(4, 8)
        # self.Switch_ONN_Relay(5, 7)
        # self.wait(500)  # change this value after code verification to 1.5 hours =5400 seconds
        # self.Switch_OFF_Relay(4, 8)
        # self.Switch_OFF_Relay(5, 7)

    def RotationTest(self, *args):
        delay = 5
        direction = "CW"
        for arg in args:
            if type(arg) is int:
                delay = arg
            elif type(arg) is str and arg.upper() in ["CW", "CCW"]:
                direction = "R" + arg.upper()

        self.rotation_with_direction(relay_switch_over_delay=delay, direction=direction)

    def removingPowerPackFromCharger(self):
        self.Switch_OFF_Relay(3, 7)
        self.Switch_OFF_Relay(3, 8)

    def ForceDecode(self, case):
        switch = {"Low": 1,
                  "Medium": 4.5,
                  "High": 7,
                  "Excessieve": 9,
                  "Load Profile": 5,
                  "65": 3.25,
                  "70": 3.5,
                  "30": 1.5
                  }
        a = switch.get(case)
        return a

    def EEAForceDecode(self, case):
        switch = {"Low": 2,
                  "Medium": 3.5,
                  "High": 5,
                  "Excessieve": 4,
                  "Load Profile": 5,
                  "65": 3.25,
                  "70": 3.5,
                  "30": 1.5
                  }
        a = switch.get(case)
        return a

    def RetractionForceDecode(self, case):
        switch = {"Low": 0.2,
                  "Medium": 1,
                  "High": 2,
                  "Excessieve": 4,
                  "Load Profile": 5,
                  "65": 3.25,
                  "70": 3.5,
                  "30": 1.5
                  }
        b = switch.get(case)
        return b

    def convertListtoLogFile(LogStringsList, LogFileName, fileOpenMode):
        with open(LogFileName, fileOpenMode) as logFile:
            [logFile.write(singleData + "\n") for singleData in LogStringsList]

    # LogFile Name and LogStringsList are mandatory arguments
    # fileOpenMode is a default argument which is 'w' by default, can be overridden by passing 'a' for opening the log file in append mode

    def battery_level_check(self):
        TestBatteryLevelMax = self.json_data['Battery RSOC Max Level']
        TestBatteryLevelMin = self.json_data['Battery RSOC Min Level']
        # clampingForce = self.json_data['Clamping Force']
        # firingForce = self.json_data['Firing Force']
        # articulationStateinFiring = self.json_data['Articulation State for clamping & firing']
        # numberOfFiringsinProcedure = self.json_data['Num of Firings in Procedure']
        # retractionForce = self.json_data['Retraction Force']
        # print(TestBatteryLevelMax, TestBatteryLevelMin, clampingForce, firingForce, articulationStateinFiring,
        #       numberOfFiringsinProcedure)
        # with nidaqmx.Task() as task:
        #     task.ao_channels.add_ao_voltage_chan('Dev1/ao0')
        #     print('1 Channel 1 Sample Write: ')
        #     print(task.write(0.25))

        self.send_decimal_bytes(TURN_OFF_ALL_RELAYS_IN_ALL_BANKS[0])
        self.wait(0.5)
        self.Switch_ONN_Relay(3, 8)

        self.wait(0.5)
        self.Switch_ONN_Relay(3, 7)

        self.wait(60)

        self.send_decimal_bytes(TURN_OFF_ALL_RELAYS_IN_ALL_BANKS[0])
        print("Step: Remove Signia Power Handle from Charger")
        self.wait(40)

        MCPThread.readingPowerPack.exitFlag = True

        if (read_battery_RSOC(25,
                              self.PowerPackComPort) > TestBatteryLevelMax):  # and (read_battery_RSOC(25, PowerPackComPort) > TestBatteryLevelMin):
            self.Switch_ONN_Relay(1, 8)
            self.wait(10)
            print("Adapter Engaged to Power Pack Mechanically")

            # TEST STEP: Attach the EGIA Adapter
            self.Switch_ONN_ALL_Relays_In_Each_Bank(1)  # B1 - ALL ON
            print("Step: Adapter Connected")
            self.wait(20)
            self.ConnectingLegacyReload()
            print("Step: Legacy Reload Connected")
            self.wait(5)
            # NI DAQ Turn on A0 @ 1.5V

            while (read_battery_RSOC(25,
                                     self.PowerPackComPort)) > TestBatteryLevelMax:  # and (read_battery_RSOC(25, PowerPackComPort) > TestBatteryLevelMin):
                self.Switch_ONN_Relay(2, 5)  # B2:R5 - ON -- some operations battery discharge
                self.wait(7)
                self.Switch_OFF_Relay(2, 5)  # B2:R5 - ON
                self.Switch_ONN_Relay(2, 4)  # B2:R5 - ON
                self.wait(7)
                self.Switch_OFF_Relay(2, 4)  # B2:R5 - ON

            self.Switch_OFF_Relay(3, 1)  # B3:R1 - OFF
            self.Switch_OFF_ALL_Relays_In_Each_Bank(1)
            self.wait(10)
        if (read_battery_RSOC(25,
                              self.PowerPackComPort) < TestBatteryLevelMin):  # and (read_battery_RSOC(25, PowerPackComPort) <= TestBatteryLevelMax):
            # print('entered elif loop')
            self.Switch_ONN_Relay(3, 7)  # battery charge
            self.wait(0.5)
            self.Switch_ONN_Relay(3, 8)
            # need to optimize this delay so that handle does not go to sleep or does not result communciation
            self.wait(5)
            while (read_battery_RSOC(25,
                                     self.PowerPackComPort) < TestBatteryLevelMin):  # and (read_battery_RSOC(25, PowerPackComPort) <= TestBatteryLevelMax):
                pass
                # self.wait(0.1)
                # read_battery_RSOC(10, PowerPackComPort)

        # self.wait(20)

    def startup_log(self):
        print("----------Placing Power Pack on Charger for startup Test--------------")
        self.Switch_ONN_Relay(3, 7)
        self.wait(.2)
        self.Switch_ONN_Relay(3, 8)
        self.wait(60)
        # self.wait(10) ### remove this 3rd nov24
        print("----------Removing Power Pack from Charger for startup Test--------------")
        self.Switch_OFF_Relay(3, 7)
        self.wait(.2)
        self.Switch_OFF_Relay(3, 8)

        while True:
            # seriallistData = serial.tools.list_ports.comports()
            # print(seriallistData)
            singiaPowerFound = False
            if any("SigniaPowerHandle" in str(s) for s in serial.tools.list_ports.comports()):
                singiaPowerFound = True
            else:
                print('Signia Com Port Closed')
                singiaPowerFound = False
                break

        # self.wait(4)
        strPort = 'None'
        # self.wait(2)
        while not 'SigniaPowerHandle' in strPort:
            ports = serial.tools.list_ports.comports()
            for port in ports:
                if 'SigniaPowerHandle' in str(port):
                    strPort = str(port)
                    print(strPort, 'Available')
                    break
            # numConnection = len(ports)
            # for i in range(0, numConnection):
            #     port = ports[i]
            #     strPort = str(port)
            #     if 'SigniaPowerHandle' in strPort:
            #         print(ports[i], 'Available')
            #         break
        self.wait(1)

        ################################################################################################################
        # TEST STEP: Remove Signia Power Handle from Charger
        # self.send_decimal_bytes(TURN_OFF_ALL_RELAYS_IN_ALL_BANKS[0])
        # print("Step: Remove Signia Power Handle from Charger")
        # based on the functionality of signals on bank 4, 5 6 this may need to be optimized to check the relay status con control
        # self.wait(7)

        # self.wait(60)
        PPnotReady = True
        while PPnotReady:
            try:
                self.startMCP()
                # self.serPP = serial.Serial(self.PowerPackComPort, 115200, bytesize=8, parity='N', stopbits=1,
                #                            timeout=0.05, xonxoff=0)
                # self.my_Serthread = MCPThread.readingPowerPack(self.serPP, 1000)
                # self.my_Serthread.clearQue()
                # MCPThread.readingPowerPack.exitFlag = False
                # self.my_Serthread.start()
                PPnotReady = False
                # print(sys.argv[0], end=" ")
            except:
                pass

        # self.Test_Results.append("-"*20 + "  " +
        #     str(self.json_data['Scenario Num']) + '#' + str(self.itr + 1) + "@" + self.json_data[
        #         'Test Scenario'] + "  " + "-"*20)  # + str(i+1))
        # logger.info(f"-----------------    Scenario_{self.json_data['Scenario Num']}_"
        # f"{self.json_data['Test Scenario']}    -----------------")
        self.Test_Results.append(f"-----------------    Scenario_{self.json_data['Scenario Num']}_"
                                 f"{self.json_data['Test Scenario']}    -----------------")

        self.Test_Results.append(str(self.json_data['Scenario Num']) + '#' + str(self.itr + 1) + "@" + self.json_data[
            'Test Scenario'])  # + str(i+1))
        self.wait(65)
        # self.wait(10)
        searchFlag = True

        Timestamps, Strings_from_PowerPack, data_path = ReadingQue(self.my_Serthread.readQue, searchFlag)
        print(simple_colors.blue(f"start up logs : \n{Strings_from_PowerPack}"))
        serialControl.convertListtoLogFile(Strings_from_PowerPack, (self.videoPath + '\\StartUpLog.txt'),
                                           fileOpenMode='a')
        serialControl.convertListtoLogFile(Strings_from_PowerPack, 'TotalLog.txt', fileOpenMode='a')
        '''Strings_to_Compare = ['GUI_NewState: WELCOME_SCREEN', 'Piezo: All Good', 'Initialization complete',
                              'SM_NewSystemEventAlert: INIT_COMPLETE', 'systemCheckCompleted complete',
                              'GUI_NewState: PROCEDURES_REMAINING', 'GUI_NewState: REQUEST_CLAMSHELL',
                              'Going to standby', 'Turning off OLED']'''
        Strings_to_Compare = locateStringsToCompareFromEvent('Remove Signia Power Handle from Charger')

        result = Compare('Remove Signia Power Handle from Charger', Strings_to_Compare, Strings_from_PowerPack)

        print(simple_colors.yellow(f"data_path: {data_path}"))
        data_path = "None" if not data_path else data_path
        self.Test_Results.append('Eventlog:' + data_path)
        self.Test_Results.append('Remove Signia Power Handle from Charger:' + result)

    def configure_clamshell(self, byte_data, fixture_validation=False):
        self.Switch_OFF_Relay(1, 5)
        self.wait(1)

        self.Switch_ONN_Relay(5, 5)  # B5:R5 - ON
        self.Switch_ONN_Relay(5, 1)  # B5:R1 - ON

        self.wait(1)
        self.write_eeprom_data(data_bytes=byte_data, fixtureValidationReq=fixture_validation)

        self.Switch_OFF_Relay(5, 1)  # B5:R1 - OFF
        self.Switch_OFF_Relay(5, 5)  # B5:R1 - OFF
        self.wait(1)

    def read_status_variables(self, read_status_data_only=False, fixture_validation_required=False):
        MCPThread.readingPowerPack.exitFlag = True
        handle_fire_count = None
        # self.disconnect_MCP_Port()
        self.wait(2)
        StatusVariables1 = []
        status_retries = 0
        # print(self.Test_Results)
        if not read_status_data_only:
            print(f"time in read_status_variables {time.time() * 1000}")
            handle_fire_count, HandleProcedureCount = GetHandleUseCount(self.PowerPackComPort)
            # logger.info(f"HandleFireCount1: {HandleFireCount1}\nHandleProcedureCount: {HandleProcedureCount}")
            if fixture_validation_required:
                pass
            else:
                print('Before Firing Handle Fire Count:' + str(handle_fire_count),
                  'Handle Procedure Count:' + str(HandleProcedureCount))
            self.wait(2)

        while len(StatusVariables1) == 0 and status_retries < 5:
            StatusVariables1 = ReadStatusVariables(self.PowerPackComPort, fixtureValidationReq=fixture_validation_required)
            if fixture_validation_required:
                pass
            else:
                print(simple_colors.yellow(f"status variables: {StatusVariables1}"))
        # StatusVariables1 = ReadStatusVariables(self.PowerPackComPort)
        # print(simple_colors.yellow(f"status variables: {StatusVariables1}"))
        StatusVariables1 = StatusVariables1[4:]  # truncate the data packet to get the actual data

        status_data = {"handle_moving": StatusVariables1[0], "battery_conneted": StatusVariables1[1],
                       "Adapter_Connected": StatusVariables1[2], "Adapter_Calibrated": StatusVariables1[3],
                       "Clampshell_Connected": StatusVariables1[4], "Reload_Connected": StatusVariables1[5],
                       "Cartidge_Connected": StatusVariables1[6], "Reload_Clampled": StatusVariables1[7],
                       "Reload_Fully_Open": StatusVariables1[8], "Handle_Warning": StatusVariables1[9:13],
                       "Handle_Errors": StatusVariables1[13:17], "Adapter_Warnings": StatusVariables1[17:21],
                       "Adapter_Errors": StatusVariables1[21:25], "SULU_Warnings": StatusVariables1[25:29],
                       "SULU_Errors": StatusVariables1[29:33], "MULU_Warnings": StatusVariables1[33:37],
                       "MULU_Errors": StatusVariables1[37:41], "Battery_Warnings": StatusVariables1[41:45],
                       "Battery_Errors": StatusVariables1[45:49], "Clampshell_Warnings": StatusVariables1[49:53],
                       "Clampshell_Errors": StatusVariables1[53:57], "Wifi_Warnings": StatusVariables1[57:61],
                       "Wifi_Errors": StatusVariables1[61:65]}

        StatusVariables1 = StatusVariables1[9:57]
        StatusVariables1 = (StatusVariables1[4:8] + StatusVariables1[12:16] + StatusVariables1[20:24] +
                            StatusVariables1[28:32] + StatusVariables1[36:40] + StatusVariables1[44:48])
        status_data["status_variables"] = StatusVariables1
        if fixture_validation_required:
            pass
        else:
            print('Status Variables: ', StatusVariables1)

        self.startMCP()
        if read_status_data_only:
            return status_data
        return handle_fire_count, status_data

    def restart_handle(self):
        self.wait(1)
        # self.disconnect_MCP_Port()
        self.Switch_ONN_Relay(3, 5)
        self.Switch_ONN_Relay(3, 6)
        self.wait(10)
        self.Switch_OFF_Relay(3, 5)
        self.Switch_OFF_Relay(3, 6)
        print("restarting the handle. Wait for 60 Sec to restart.")
        strPort = 'None'
        while (not 'SigniaPowerHandle' in strPort):
            ports = serial.tools.list_ports.comports()
            for port in ports:
                if 'SigniaPowerHandle' in str(port):
                    strPort = str(port)
                    print(port, 'Available')
                    break

        self.wait(60)
        PPnotReady = True
        while PPnotReady:
            try:
                self.startMCP()
                # self.serPP = serial.Serial(self.PowerPackComPort, 115200, bytesize=8, parity='N', stopbits=1,
                #                            timeout=0.05, xonxoff=0)
                # self.my_Serthread = MCPThread.readingPowerPack(self.serPP, 1000)
                # self.my_Serthread.clearQue()
                # MCPThread.readingPowerPack.exitFlag = False
                # self.my_Serthread.start()
                PPnotReady = False
                # print(sys.argv[0], end=" ")
            except:
                pass

    def emergency_retraction_test(self):
        self.handle_fire_count_1, self.status_data_1 = self.read_status_variables()
        status_variables_1 = self.status_data_1['status_variables']
        print('StatusVariable After Firing', status_variables_1)

        self.Test_Results.append("Emergency Retraction")
        self.Normal_Firing_Test_Results = []
        logs_to_compare = 'SULU Connected'
        reload_length = 30
        reload_color = "Purple"
        self.connect_sulu_reload(reload_length=reload_length, reload_color=reload_color, event_key=logs_to_compare)
        self.ClampCycleTest()
        self.Clamping(SuccessFlag=True, is_firing_test=True, logs_to_compare='Clamping on Tissue')
        self.GreenKeyAck(SuccessFlag=True)
        self.Firing(firing_default_delay)
        self.restart_handle()
        self.rotation_with_direction(is_firing_test=False, is_emergency_retraction=True)
        self.Clamping(SuccessFlag=True, is_firing_test=False, logs_to_compare="Clamping - Emergency Retraction")
        self.right_articulation(relay_switch_over_delay=articulate_default_delay, SuccessFlag=True,
                                is_firing_test=False, is_emergency_retraction=True)
        self.left_articulation(relay_switch_over_delay=articulate_default_delay, SuccessFlag=True,
                               is_firing_test=False, is_emergency_retraction=True)
        self.right_articulation(relay_switch_over_delay=articulate_default_delay, SuccessFlag=True,
                                is_firing_test=False, is_emergency_retraction=True)

        self.Unclamping(logs_to_compare="Unclamping - Emergency Retraction")
        self.left_articulation(relay_switch_over_delay=3, SuccessFlag=True,
                               is_firing_test=False, is_emergency_retraction=True)
        self.Clamping(SuccessFlag=True, is_firing_test=False, logs_to_compare="Clamping - Emergency Retraction")
        self.GreenKeyAck(SuccessFlag=True, is_firing_test=False, is_emergency_retraction=True)
        self.Unclamping(logs_to_compare="Unclamping - Emergency Retraction")
        self.RemovingSULUReload(is_emergency_retraction=True)
        self.wait(5)

        self.handle_fire_count_2, self.status_data_2 = self.read_status_variables()
        status_variables_2 = self.status_data_2['status_variables']
        print('StatusVariable After Firing', status_variables_2)

    def write_eeprom_data(self, data_bytes, fixtureValidationReq=False):
        if fixtureValidationReq:
            pass
        else:
            print(simple_colors.yellow(f'command_bytes : {data_bytes}'))
        Enable_OW = b'\xAA\x04\x07\x24'
        write_1_wire_command_byte = [0xAA, 0x4C, 0x0A]
        read_1_wire_command_byte = [0xAA, 0x0C, 0x0B]
        # In case of 'NACK' we are retrying to get 'ACK' for at max of 5 times
        try:
            with serial.Serial(port=self.BlackBoxComPort, baudrate=500000, timeout=3) as ser:
                print(f"Gen2ACC port is opened!!!")
                ser.write(Enable_OW)

                for retry in range(5):
                    # ############ READ ###################
                    time.sleep(2)
                    packet_size = 0
                    while packet_size != 12:
                        # ser.write(Enable_OW)
                        # ser.flush()
                        s = ser.read(2)
                        s = list(s)
                        packet_size = s[1]
                        if packet_size != 12:
                            ser.read(packet_size - 2)
                        if fixtureValidationReq:
                            pass
                        else:
                            print(simple_colors.red("One-Wire is not detected!"))
                        self.wait(0.1)

                    read_data = ser.read(packet_size - 2)
                    one_wire_address = list(read_data)[1:-1]
                    if fixtureValidationReq:
                        pass
                    else:
                        print(simple_colors.green(f"one_wire_address: {one_wire_address}"))

                    prefix_command = write_1_wire_command_byte + one_wire_address
                    command_bytes = fetch_command(prefix_list=prefix_command, data_byte=data_bytes, fixtureValidationReq=fixtureValidationReq)

                    ser.write(command_bytes)
                    self.wait(1)

                    read_command = read_1_wire_command_byte + one_wire_address
                    crc_value = calc(read_command)
                    crc_value = int(crc_value, 16)
                    read_command.append(crc_value)

                    if fixtureValidationReq:
                        pass
                    else:
                        print(read_command)
                    read_command = bytes(read_command)

                    ser.flush()
                    ser.flushInput()
                    ser.flushOutput()
                    ser.write(read_command)

                    cmd = 0
                    while cmd != 0x0B:
                        s = ser.read(3)
                        cmd = s[2]
                        length = s[1]
                        read_data = ser.read(length - 3)

                    # print(list(read_data[:64]))
                    command_list = list(command_bytes)[11:75]
                    # print("Command List ", command_list)
                    if list(read_data[:64]) == command_list:
                        if fixtureValidationReq:
                            pass
                        else:
                            print(simple_colors.green(f"one wire is written successfully with the data! \n{data_bytes}"))
                        break
        except serial.SerialException as e:
            print(f"Failed to open port: {e}. \ntraceback: {traceback.format_exc()}")
        # ser.close()
        # serialControl.close_serial_port(ser)

    def read_eeprom_data(self) -> list:
        # print(simple_colors.yellow(f'command_bytes : {data_bytes}'))
        read_data = []
        Enable_OW = b'\xAA\x04\x07\x24'
        # write_1_wire_command_byte = [0xAA, 0x4C, 0x0A]
        read_1_wire_command_byte = [0xAA, 0x0C, 0x0B]
        # In case of 'NACK' we are retrying to get 'ACK' for at max of 5 times
        for retry in range(5):
            try:
                with serial.Serial(self.BlackBoxComPort, 500000) as ser:
                    ser.write(Enable_OW)
                    # ############ READ ###################
                    time.sleep(1)
                    packet_size = 0
                    while packet_size != 12:
                        # ser.flush()
                        # ser.flushInput()
                        # ser.flushOutput()
                        s = ser.read(2)
                        s = list(s)
                        packet_size = s[1]
                        read_data = ser.read(packet_size - 2)
                        print(f'read_data: {list(read_data)}')
                        print(simple_colors.red("One-Wire is not detected!"))
                        self.wait(0.5)

                    # read_data = ser.read(packet_size - 2)
                    one_wire_address = list(read_data)[1:-1]
                    print(simple_colors.green(f"one_wire_address: {one_wire_address}"))

                    # prefix_command = write_1_wire_command_byte + one_wire_address

                    # command_bytes = fetch_command(prefix_list=prefix_command, data_byte=data_bytes)

                    # ser.write(command_bytes)
                    # self.wait(1)

                    read_command = read_1_wire_command_byte + one_wire_address
                    crc_value = calc(read_command)
                    crc_value = int(crc_value, 16)
                    read_command.append(crc_value)
                    print(read_command)
                    read_command = bytes(read_command)

                    # ser.flush()
                    # ser.flushInput()
                    # ser.flushOutput()
                    ser.write(read_command)

                    cmd = 0
                    while cmd != 0x0B:
                        s = ser.read(3)
                        cmd = s[2]
                        length = s[1]
                        read_data = ser.read(length - 3)

                    print(list(read_data[:64]))
                    # command_list = list(command_bytes)[11:75]
                    # if list(read_data[:64]) == command_list:
                    #     print(simple_colors.green(f"one wire is written successfully with the data! \n{data_bytes}"))
                    break
            except serial.SerialException as e:
                print(f"Failed to open port: {e}")


        # serialControl.close_serial_port(ser)
        return list(read_data[:64])

    def startMCP(self):

        self.serPP = serial.Serial(self.PowerPackComPort, 115200, bytesize=8, parity='N', stopbits=1, timeout=0.05,
                                   xonxoff=False)
        MCPThread.readingPowerPack.exitFlag = False
        self.my_Serthread = MCPThread.readingPowerPack(self.serPP, 1000)
        self.my_Serthread.clearQue()
        self.my_Serthread.start()
        self.wait(1)

    ## If it is a 21mm or 25mm reload, press the up-toggle button to remove the TAID
    ## If it is a 28mm, 31mm or 33mm reload, wait for the ship cap to be automatically ejected
    def configure_eea_reload(self, reload_length, reload_color, ship_cap_status, reload_state=None, fix_validation_req=False):
        EEA_RELOAD_EEPROM = [2, 3, 0x1C, 0x31, 0x32, 0x33, 0x34, 0x35, 0x36, 0x37, 0x38, 0x39, 0x31, 0x32, 0x33, 0x34,
                             0x35, 0x36, 4, 4, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                             0, 0, 0x1D, 0x80, 0x78, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1]
        reload_diameter = enumerate([21, 25, 28, 31, 33], 1)
        reload_colors = enumerate(['Purple', 'Black'], 3)
        ship_cap_presence = enumerate(['No', 'Yes'], 4)

        for number, length in reload_diameter:
            if length == reload_length:
                EEA_RELOAD_EEPROM[1] = number  # number will be 1 for 21mm, 2 for 25mm, 3 for 28mm, 4 for 31mm, and 5 for 33mm reload lengths
                break

        for count, possible_color in reload_colors:
            if possible_color == reload_color:
                EEA_RELOAD_EEPROM[19] = count  # count will be 3 for Purple, 4 for Black reload colors
                break

        for presence, possible_check in ship_cap_presence:
            if possible_check == ship_cap_status:
                EEA_RELOAD_EEPROM[18] = presence # presence will be 4 for No, 5 for Yes Ship Cap/TAID Presence checks
                break

        self.Switch_ONN_Relay(5, 2)  # B5:R2 - ON
        self.Switch_ONN_Relay(5, 6)  # B5:R6 - ON

        self.write_eeprom_data(data_bytes=EEA_RELOAD_EEPROM, fixtureValidationReq=fix_validation_req)

        self.Switch_OFF_Relay(5, 2)  # B5:R1 - OFF
        self.Switch_OFF_Relay(5, 6)  # B5:R2 - OFF


    def VerifyRecoveryIDData(self):
        # Engaging the Adapter
        self.Switch_ONN_Relay(1, 8)
        self.wait(7)
        print("EEA Adapter Engaged to Power Pack Mechanically")
        self.DisconnectingEEAReload()
        self.wait(5)

        # From Adapter EEPROM
        RecoveryIDEeprom = GetAdapterEEPROMRecoveryIdData(self.FtdiUartComPort)
        RecoveryStateString = AdapterRecoveryStates(RecoveryIDEeprom)
        print("Recovery ID After Removing Adapter During 1st EEA Stapling In Progress : ", RecoveryStateString)
        self.Test_Results.append(RecoveryStateString + ":" + str(RecoveryIDEeprom))
        print(self.Test_Results)

        # From Adapter Onewire
        # For capturing Onewire Usage counts from the Adapter via BB, below relays should be ON.
        self.Switch_ONN_Relay(5, 5)  # B5:R8 - ON
        self.Switch_ONN_Relay(6, 1)  # B6:R1 - ON

        RecoveryIdHighByte, RecoveryIdLowByte = GetAdapterOnewireRecoveryIdData(self.BlackBoxComPort)

        self.Switch_OFF_Relay(6, 1)  # B6:R1 - OFF
        self.Switch_OFF_Relay(5, 5)  # B5:R8 - OFF

        # RecoveryIdOnewire = int(RecoveryIdLowByte, 16) * 256 + int(RecoveryIdHighByte, 16)

        # Recovery State Verifying in the Adapter onewire and Capturing into the Test Results
        self.Test_Results.append("5th to Last Byte : " + str(RecoveryIdHighByte))
        self.Test_Results.append("4th to Last Byte : " + str(RecoveryIdLowByte))
        print(self.Test_Results)

    def GetRecoveryIDData(self):
        # From Adapter EEPROM
        RecoveryIDEeprom = GetAdapterEEPROMRecoveryIdData(self.FtdiUartComPort)
        RecoveryStateString = AdapterRecoveryStates(RecoveryIDEeprom)
        print(f"Recovery ID From EEPROM, ID : {RecoveryIDEeprom}, State: {RecoveryStateString}")

        # From Adapter Onewire
        # Engaging the Adapter
        self.Switch_ONN_Relay(1, 8)
        self.wait(7)

        # As of Current implementation of onewire device to connect BB, by only one device at a time,
        # before reading adapter onewire data we have to disconnect the reload ( reload and adapter both are connected on the same bus)
        self.DisconnectingEEAReload(exit_video=False)
        self.wait(3)

        # For capturing Onewire Usage counts from the Adapter via BB, below relays should be ON.
        self.Switch_ONN_Relay(5, 5)  # B5:R8 - ON
        self.Switch_ONN_Relay(6, 1)  # B6:R1 - ON

        RecoveryIdHighByte, RecoveryIdLowByte = self.GetAdapterNvmRecoveryID()

        self.Switch_OFF_Relay(6, 1)  # B6:R1 - OFF
        self.Switch_OFF_Relay(5, 5)  # B5:R8 - OFF

        print(f"Recovery ID From Onewire, High Byte: {RecoveryIdHighByte}, Low Byte: {RecoveryIdLowByte}")

        # Connect Reload before, connecting the adapter
        self.Switch_ONN_Relay(3,2)
        self.Switch_ONN_Relay(3,3)


    def test_results_pass_percentage(self, passed_executions):
        try:
            test_scenario = self.json_data['Scenario Num']
            sheet_name = f'Scenario_{test_scenario}'
        except Exception as ex:
            test_scenario = self.json_data['Test Protocol ID']
            sheet_name = test_scenario
            print(ex)
        # saving the results to Excel sheet
        save_results_to_excel(xls_results=self.xls_results, video_path=self.videoPath, sheet_name=sheet_name)

        for item in self.Test_Results:
            temp2 = 'PASS'
            if item[0] != " ":
                try:
                    if ((str.split(item, ':', 1))[1]) == 'PASS':
                        # serialControlObj.Test_Results.append(serialControlObj.Normal_Firing_Test_Results[0] + ':FAIL')
                        pass
                    elif ((str.split(item, ':', 1))[1]) == 'FAIL':
                        temp2 = 'FAIL'
                        print(str((self.Test_Results[0] + ':  Failed')))
                        break
                except:
                    pass
        if temp2 == 'PASS':
            passed_executions[f"{test_scenario}_{self.itr}"] = "PASS"
        print(f'{test_scenario} % of Successful Executions: {100 * (len(passed_executions) / (self.json_data["Num Times to Execute"]))}')

        self.my_Serthread.clearQue()
        self.wait(5)
        MCPThread.readingPowerPack.exitFlag = True
        # self.disconnect_MCP_Port()
        OLEDRecordingThread.exitFlag = True

        # update the test results in the JSON file.
        with open(str((self.videoPath + '\\Detailed_Results.txt')), 'a') as datalog:
            datalog.write('\n'.join(self.Test_Results) + '\n')
        CS = [sys.argv[index + 1] for index, ele in enumerate(sys.argv) if ele == "-c" or ele == "--changeset"]
        TT = [sys.argv[index + 1] for index, ele in enumerate(sys.argv) if ele == "-t" or ele == "--test"]
        INTG = '--integration' in sys.argv
        RP = [sys.argv[index + 1] for index, ele in enumerate(sys.argv) if ele == "-r" or ele == "--root"]
        calculatePassFail(str((self.videoPath + '\\Detailed_Results.txt')), str(RP[0] + '\\Test_Configurator.json'),
                          str((self.videoPath + '\\StartUpLog.txt')), str(TT[0]), str(CS[0]), str(INTG))
        self.PlacingPowerPackOnCharger()
        print('Power Pack Placed on Charger')
        print('------------------- End of Test Scenario --------------')
        self.wait(30)

        self.disconnectSerialConnection()

    def start_capturing_images(self, folder_name, is_static_image: bool = True, file_name='sample'):
        if self.video_thread is not None:
            self.video_thread.set_is_static_image(is_static_image)
            self.video_thread.folder_name = folder_name
            self.video_thread.image_file_name = file_name
            self.video_thread.set_capture_images(True)

    def stop_capturing_images(self):
        if self.video_thread is not None:
            self.video_thread.set_capture_images(False)

    def capture_images(self, folder_name, file_name, is_static_image):
        """
        Capture images using the serial control object.
        """
        if is_static_image:
            wait_time=1
        else:
            wait_time=5

        self.start_capturing_images(folder_name=folder_name, file_name=file_name,
                                                is_static_image=is_static_image)
        self.wait(wait_time)

        self.stop_capturing_images()

    def handle_screen(self, videoPath, screen_name, folder_name, file_name, is_static_image):
        """
        Handle the image capture and processing for a specific screen.
        """
        reference_images_path = 'C:\\Signia-TestAutomation\\Reference_Images'
        specific_reference_path = os.path.join(reference_images_path, folder_name)
        dst_path = os.path.join(videoPath, 'Output', folder_name)
        src_path = os.path.join(videoPath, 'Images', folder_name)

        print(f"Handling screen: {screen_name}")

        # Capture images
        self.capture_images(folder_name, file_name, is_static_image)

        # Process images
        process_images(src_path, specific_reference_path, dst_path, file_name)

    def disconnect_MCP_Port(self):
        # serialControl.flush()
        # serialControl.reset_input_buffer()
        # serialControl.reset_output_buffer()
        serialControl.close_serial_port(self.serPP)

    def EEAFiring_1w_cntr_failuer(self, fire_force, logs_to_compare='EEA Firing'):
        # fire_success_flag = True
        # # Apply Voltage Instead of Applying Load Force
        # self.output_on_off(True, self.DcPowerSupplyComPort)
        # if fire_force == 'Low':
        #     self.applyLoadViaVoltage(5, self.DcPowerSupplyComPort)
        # elif fire_force == 'Medium':
        #     self.applyLoadViaVoltage(5.1, self.DcPowerSupplyComPort)
        # self.my_Serthread.clearQue()
        # self.wait(5)
        # self.Switch_ONN_Relay(Bank_number=self.EEA_STAPLING_ONE_bank_number,
        #                       Relay_number=self.EEA_STAPLING_ONE_relay_number)  # B4:R1 - ON
        # self.Switch_ONN_Relay(Bank_number=self.EEA_STAPLING_TWO_bank_number,
        #                       Relay_number=self.EEA_STAPLING_TWO_relay_number)  # B4:R2 - ON
        # self.wait(4.5)#3)
        # self.Switch_ONN_Relay(Bank_number=self.FIRING_bank_number, Relay_number=self.FIRING_relay_number)  # B2:R5 - ON
        # self.wait(0.5)
        # self.Switch_OFF_Relay(Bank_number=self.FIRING_bank_number, Relay_number=self.FIRING_relay_number)  # B2:R5 - OFF
        # self.wait(4)
        #
        # self.Switch_OFF_Relay(Bank_number=self.EEA_STAPLING_ONE_bank_number,
        #                       Relay_number=self.EEA_STAPLING_ONE_relay_number)  # B4:R1 - OFF
        # self.Switch_OFF_Relay(Bank_number=self.EEA_STAPLING_TWO_bank_number,
        #                       Relay_number=self.EEA_STAPLING_TWO_relay_number)  # B4:R2 - OFF
        #
        # print("Stapling Completed")
        #
        # # self.output_on_off(False, self.DcPowerSupplyComPort)
        # #
        # # self.wait(1)
        # #
        # # self.output_on_off(True, self.DcPowerSupplyComPort)
        # # self.wait(1)
        # self.apply_load_force(0)
        # if fire_force == 'Low':
        #     self.applyLoadViaVoltage(9, self.DcPowerSupplyComPort)
        # elif fire_force == 'Medium':
        #     self.applyLoadViaVoltage(9.1, self.DcPowerSupplyComPort)
        #
        # ## Cutting Relays Switched ON
        # self.Switch_ONN_Relay(Bank_number=self.EEA_CUTTING_ONE_bank_number,
        #                       Relay_number=self.EEA_CUTTING_ONE_relay_number)  # B4:R3 - ON
        # self.Switch_ONN_Relay(Bank_number=self.EEA_CUTTING_TWO_bank_number,
        #                       Relay_number=self.EEA_CUTTING_TWO_relay_number)  # B4:R4 - ON
        #
        # # Disconnecting Adapter Onewire
        # self.Switch_ONN_Relay(1,2)
        #
        # if fire_force == 'Low':
        #     self.wait(5)
        # else:
        #     self.wait(10)
        #
        # self.Switch_OFF_Relay(Bank_number=self.EEA_CUTTING_ONE_bank_number,
        #                       Relay_number=self.EEA_CUTTING_ONE_relay_number)  # B4:R3 - OFF
        # self.Switch_OFF_Relay(Bank_number=self.EEA_CUTTING_TWO_bank_number,
        #                       Relay_number=self.EEA_CUTTING_TWO_relay_number)  # B4:R4 - OFF
        #
        # self.wait(.5)
        # self.Switch_ONN_Relay(Bank_number=self.EEA_CUTTING_COMPLETE_ONE_bank_number,
        #                       Relay_number=self.EEA_CUTTING_COMPLETE_ONE_relay_number)  # B4:R5 - ON
        # self.Switch_ONN_Relay(Bank_number=self.EEA_CUTTING_COMPLETE_TWO_bank_number,
        #                       Relay_number=self.EEA_CUTTING_COMPLETE_TWO_relay_number)  # B4:R6 - ON
        # self.wait(30)
        # self.is_firing_completed = True
        # self.compare_logs(logs_to_compare, SuccessFlag=fire_success_flag, is_firing_test=True)
        #
        # print("Cut Completed")
        #
        # self.output_on_off(False, self.DcPowerSupplyComPort)
        #
        # self.Switch_OFF_Relay(Bank_number=self.EEA_CUTTING_COMPLETE_ONE_bank_number,
        #                       Relay_number=self.EEA_CUTTING_COMPLETE_ONE_relay_number)  # B4:R5 - OFF
        # self.Switch_OFF_Relay(Bank_number=self.EEA_CUTTING_COMPLETE_TWO_bank_number,
        #                       Relay_number=self.EEA_CUTTING_COMPLETE_TWO_relay_number)  # B4:R6 - OFF
        self.output_on_off(True, self.DcPowerSupplyComPort)
        string_to_found = ''
        self.applyLoadViaVoltage(4, self.DcPowerSupplyComPort)

        # turn on 4-1 and 4-2 relays
        self.Switch_ONN_Relay(4, 1)
        self.Switch_ONN_Relay(4, 2)

        self.wait(1)

        # turn off 4-1 and 4-2
        self.Switch_OFF_Relay(4, 1)
        self.Switch_OFF_Relay(4, 2)

        self.applyLoadViaVoltage(5.5, self.DcPowerSupplyComPort)  # VMK changed to 5.5 from 7

        # turn on 4-1 and 4-2 relays
        self.Switch_ONN_Relay(4, 1)
        self.Switch_ONN_Relay(4, 2)

        self.wait(3)

        # press close key
        self.Switch_ONN_Relay(2, 5)
        time.sleep(0.5)
        self.Switch_OFF_Relay(2, 5)
        self.wait(4)

        # turn off 4-1 and 4-2
        self.Switch_OFF_Relay(4, 1)
        self.Switch_OFF_Relay(4, 2)

        # turn on 4-5 and 4-6 relays
        self.Switch_ONN_Relay(4, 5)
        self.Switch_ONN_Relay(4, 6)

        self.wait(1)

        # turn off 4-5 and 4-6 relays
        self.Switch_OFF_Relay(4, 5)
        self.Switch_OFF_Relay(4, 6)

        self.applyLoadViaVoltage(9, self.DcPowerSupplyComPort)  # VMK changed 9 to 6.5V

        self.Switch_ONN_Relay(4, 1)
        self.Switch_ONN_Relay(4, 2)

        self.apply_load_force(0)

        # Disconnecting Adapter Onewire
        self.Switch_ONN_Relay(1,2)

        self.wait(5)

        # turn off 4-1 and 4-2
        self.Switch_OFF_Relay(4, 1)
        self.Switch_OFF_Relay(4, 2)

        # turn on 4-5 and 4-6 relays
        self.Switch_ONN_Relay(4, 5)
        self.Switch_ONN_Relay(4, 6)

        self.wait(10)

        # turn off 4-5 and 4-6 relays
        self.Switch_OFF_Relay(4, 5)
        self.Switch_OFF_Relay(4, 6)

    def EEAFiring_Eeprom_cntr_failuer(self, fire_force, logs_to_compare='EEA Firing'):
        # fire_success_flag = True
        # # Apply Voltage Instead of Applying Load Force
        # self.output_on_off(True, self.DcPowerSupplyComPort)
        # if fire_force == 'Low':
        #     self.applyLoadViaVoltage(5, self.DcPowerSupplyComPort)
        # elif fire_force == 'Medium':
        #     self.applyLoadViaVoltage(5.1, self.DcPowerSupplyComPort)
        # self.my_Serthread.clearQue()
        # self.wait(5)
        # self.Switch_ONN_Relay(Bank_number=self.EEA_STAPLING_ONE_bank_number,
        #                       Relay_number=self.EEA_STAPLING_ONE_relay_number)  # B4:R1 - ON
        # self.Switch_ONN_Relay(Bank_number=self.EEA_STAPLING_TWO_bank_number,
        #                       Relay_number=self.EEA_STAPLING_TWO_relay_number)  # B4:R2 - ON
        # self.wait(4.5)#3)
        # self.Switch_ONN_Relay(Bank_number=self.FIRING_bank_number, Relay_number=self.FIRING_relay_number)  # B2:R5 - ON
        # self.wait(0.5)
        # self.Switch_OFF_Relay(Bank_number=self.FIRING_bank_number, Relay_number=self.FIRING_relay_number)  # B2:R5 - OFF
        # self.wait(4)
        #
        # self.Switch_OFF_Relay(Bank_number=self.EEA_STAPLING_ONE_bank_number,
        #                       Relay_number=self.EEA_STAPLING_ONE_relay_number)  # B4:R1 - OFF
        # self.Switch_OFF_Relay(Bank_number=self.EEA_STAPLING_TWO_bank_number,
        #                       Relay_number=self.EEA_STAPLING_TWO_relay_number)  # B4:R2 - OFF
        #
        # print("Stapling Completed")
        #
        # # self.output_on_off(False, self.DcPowerSupplyComPort)
        # #
        # # self.wait(1)
        # #
        # # self.output_on_off(True, self.DcPowerSupplyComPort)
        # # self.wait(1)
        # self.apply_load_force(0)
        # if fire_force == 'Low':
        #     self.applyLoadViaVoltage(9, self.DcPowerSupplyComPort)
        # elif fire_force == 'Medium':
        #     self.applyLoadViaVoltage(9.1, self.DcPowerSupplyComPort)
        #
        # ## Cutting Relays Switched ON
        # self.Switch_ONN_Relay(Bank_number=self.EEA_CUTTING_ONE_bank_number,
        #                       Relay_number=self.EEA_CUTTING_ONE_relay_number)  # B4:R3 - ON
        # self.Switch_ONN_Relay(Bank_number=self.EEA_CUTTING_TWO_bank_number,
        #                       Relay_number=self.EEA_CUTTING_TWO_relay_number)  # B4:R4 - ON
        #
        #
        # # Disconnecting( Turning OFF) the Adapter Tx or Rx - UART Connection
        # self.Switch_OFF_Relay(1, 3)  # Adapter UART Rx
        # self.Switch_OFF_Relay(1, 4)  # Adapter UART Tx
        #
        # if fire_force == 'Low':
        #     self.wait(5)
        # else:
        #     self.wait(10)
        #
        # self.Switch_OFF_Relay(Bank_number=self.EEA_CUTTING_ONE_bank_number,
        #                       Relay_number=self.EEA_CUTTING_ONE_relay_number)  # B4:R3 - OFF
        # self.Switch_OFF_Relay(Bank_number=self.EEA_CUTTING_TWO_bank_number,
        #                       Relay_number=self.EEA_CUTTING_TWO_relay_number)  # B4:R4 - OFF
        #
        # self.wait(.5)
        # self.Switch_ONN_Relay(Bank_number=self.EEA_CUTTING_COMPLETE_ONE_bank_number,
        #                       Relay_number=self.EEA_CUTTING_COMPLETE_ONE_relay_number)  # B4:R5 - ON
        # self.Switch_ONN_Relay(Bank_number=self.EEA_CUTTING_COMPLETE_TWO_bank_number,
        #                       Relay_number=self.EEA_CUTTING_COMPLETE_TWO_relay_number)  # B4:R6 - ON
        # self.wait(30)
        # self.is_firing_completed = True
        # self.compare_logs(logs_to_compare, SuccessFlag=fire_success_flag, is_firing_test=True)
        #
        # print("Cut Completed")
        #
        # self.output_on_off(False, self.DcPowerSupplyComPort)
        #
        # self.Switch_OFF_Relay(Bank_number=self.EEA_CUTTING_COMPLETE_ONE_bank_number,
        #                       Relay_number=self.EEA_CUTTING_COMPLETE_ONE_relay_number)  # B4:R5 - OFF
        # self.Switch_OFF_Relay(Bank_number=self.EEA_CUTTING_COMPLETE_TWO_bank_number,
        #                       Relay_number=self.EEA_CUTTING_COMPLETE_TWO_relay_number)  # B4:R6 - OFF
        self.output_on_off(True, self.DcPowerSupplyComPort)
        string_to_found = ''
        self.applyLoadViaVoltage(4, self.DcPowerSupplyComPort)

        # turn on 4-1 and 4-2 relays
        self.Switch_ONN_Relay(4, 1)
        self.Switch_ONN_Relay(4, 2)

        self.wait(1)

        # turn off 4-1 and 4-2
        self.Switch_OFF_Relay(4, 1)
        self.Switch_OFF_Relay(4, 2)

        self.applyLoadViaVoltage(5.5, self.DcPowerSupplyComPort)  # VMK changed to 5.5 from 7

        # turn on 4-1 and 4-2 relays
        self.Switch_ONN_Relay(4, 1)
        self.Switch_ONN_Relay(4, 2)

        self.wait(3)

        # press close key
        self.Switch_ONN_Relay(2, 5)
        time.sleep(0.5)
        self.Switch_OFF_Relay(2, 5)
        self.wait(4)

        # turn off 4-1 and 4-2
        self.Switch_OFF_Relay(4, 1)
        self.Switch_OFF_Relay(4, 2)

        # turn on 4-5 and 4-6 relays
        self.Switch_ONN_Relay(4, 5)
        self.Switch_ONN_Relay(4, 6)

        self.wait(1)

        # turn off 4-5 and 4-6 relays
        self.Switch_OFF_Relay(4, 5)
        self.Switch_OFF_Relay(4, 6)

        self.applyLoadViaVoltage(9, self.DcPowerSupplyComPort)  # VMK changed 9 to 6.5V

        self.Switch_ONN_Relay(4, 1)
        self.Switch_ONN_Relay(4, 2)

        self.apply_load_force(0)

        # Disconnecting( Turning OFF) the Adapter Tx or Rx - UART Connection
        self.Switch_OFF_Relay(1, 3)  # Adapter UART Rx
        self.Switch_OFF_Relay(1, 4)  # Adapter UART Tx

        self.wait(5)

        # turn off 4-1 and 4-2
        self.Switch_OFF_Relay(4, 1)
        self.Switch_OFF_Relay(4, 2)

        # turn on 4-5 and 4-6 relays
        self.Switch_ONN_Relay(4, 5)
        self.Switch_ONN_Relay(4, 6)

        self.wait(10)

        # turn off 4-5 and 4-6 relays
        self.Switch_OFF_Relay(4, 5)
        self.Switch_OFF_Relay(4, 6)

    def GetAdapterNvmUsageCounts(self, logs_to_compare='EEA Firing'):
        # Connect Adapter to Black Box
        self.Switch_ONN_Relay(5, 5)
        self.Switch_ONN_Relay(6, 1)

        # Reading Adapter Onewire Usage Counts
        adapter_1w_eeprom_data = self.read_eeprom_data()
        print(list(map(hex, adapter_1w_eeprom_data)))

        data = [hex(x)[2:].zfill(2) for x in adapter_1w_eeprom_data]
        fireCnt = data[3:5]
        procCnt = data[7:9]
        AdapterOwFireCount = convert_single_list_ele_to_two_byte_decimal(fireCnt)
        AdapterOwProcedureCount = convert_single_list_ele_to_two_byte_decimal(procCnt)

        self.Switch_OFF_Relay(6, 1)
        self.Switch_OFF_Relay(5, 5)

        return AdapterOwFireCount, AdapterOwProcedureCount

    def GetAdapterNvmRecoveryID(self):
        # Connect Adapter to Black Box
        self.Switch_ONN_Relay(5, 5)
        self.Switch_ONN_Relay(6, 1)

        # Reading Adapter Onewire Usage Counts
        adapter_1w_eeprom_data = self.read_eeprom_data()
        print(list(map(hex, adapter_1w_eeprom_data)))

        data = [hex(x)[2:].zfill(2) for x in adapter_1w_eeprom_data]
        highByte = data[59]
        LowByte = data[60]

        self.Switch_OFF_Relay(6, 1)
        self.Switch_OFF_Relay(5, 5)

        return highByte, LowByte




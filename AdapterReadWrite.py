import serial
import time
import struct

import simple_colors

from CRC32 import CRC32  # , CRC8
import re
from CRC16 import calc
# from Serial_Relay_Control import serialControl

#################### Addresses are Defined Here ######################
# #define FLASH_SECTOR_SIZE                       (0x400u)
# #define DATA_FLASH_START_ADDR                   (0x1800u)      /*! Timestamps structure goes here */
# #define DATA_FLASH_END_ADDR                     (0x1BFFu)
# #define DATA_FLASH_START_SECTOR                 (DATA_FLASH_START_ADDR / FLASH_SECTOR_SIZE) ## 6 th Sector
# #define DATA_FLASH_END_SECTOR                   ((DATA_FLASH_END_ADDR + 1) / FLASH_SECTOR_SIZE)
# #define ADAPTER_LOT_CHARS                       (16u)
# #define FLASH_ITEM_CHECKSUM_SIZE                (4u)


# define DATA_FLASH_STRAIN_GAUGE_ADDRESS         (DATA_FLASH_START_ADDR + sizeof(AdapterTimeStamps))
# define DATA_FLASH_ADAPTER_PARAM_ADDRESS        (DATA_FLASH_STRAIN_GAUGE_ADDRESS + sizeof(StrainGauge_Flash))
# define DATA_FLASH_LOT_ADDRESS                  (DATA_FLASH_ADAPTER_PARAM_ADDRESS + sizeof(AdapterCalParams_Flash))
# define DATA_FLASH_BOARD_PARAM_ADDRESS          (DATA_FLASH_LOT_ADDRESS+ADAPTER_LOT_CHARS + FLASH_ITEM_CHECKSUM_SIZE)
# define GTIN_ADDRESS_INVALID_CRC                (DATA_FLASH_BOARD_PARAM_ADDRESS + sizeof(AdapterBoard_Flash))
######################################################################
#  Time Stamp Structures are not using
#  Strain Gauge Start Address                   - 180C  (16 bytes)
#  Adapter Calib Params Address                 - 181C  (32 bytes)
#  Adapter Lot Address                          - 183C  (20 bytes)
#  Board Params Address                         - 1850  (20 bytes)
#  GTIN ( Global Trade Item Number ) Address    - 1864  (24 bytes)
#  EEA Data Address                             - 187C  (24 bytes)


# ser = serial.Serial("COM6", 250000, bytesize=8, parity='N', timeout=100, stopbits=1, xonxoff=0)
RecoveryState = ['EEA_REC_INIT', 'EEA_REC_CALIBRATE', 'EEA_REC_PRE_CLAMP', 'EEA_REC_CLAMP_STARTED',
                 'EEA_REC_CLAMPING_COMPLETE', 'EEA_REC_STAPLE_STARTED', 'EEA_REC_STAPLE_COMPLETE',
                 'EEA_REC_CUT_COMPLETE', 'EEA_REC_TILT_COMPLETE',
                 'EEA_REC_TILT-OPEN_STARTED', 'EEA_REC_FIRE_RETRACT', 'EEA_REC_SURGSITE_EXTRACT', 'EEA_REC_LOCKUP',
                 'EEA_REC_ERROR']


def read_packet(PowerPackComPort):
    ser = serial.Serial(PowerPackComPort, 250000, bytesize=8, parity='N', timeout=100, stopbits=1, xonxoff=0)
    data = ser.read(2)
    data = data + ser.read(data[1] - 2)
    # response = ser.readline()
    # print("Response:", response.decode('utf-8'))
    print(data)
    print(list(data))
    data = [hex(x)[2:].zfill(2) for x in data]
    print(data)


def read_and_write_adapter_eeprom_recovery_position_data(FtdiUartPort):
    ser = serial.Serial(FtdiUartPort, 250000, bytesize=8, parity='N', timeout=100, stopbits=1, xonxoff=0)
    ## Sending Boot Exit Command Before reading the Eeprom data from the Adapter
    command_boot_exit = b'\xAA\x05\xE5\x00\x0D'
    ser.write(command_boot_exit)
    time.sleep(.5)
    ser.reset_input_buffer()

    command_read_recovery_data_from_eeprom = b'\xAA\x05\xD8\x01\xF7'
    ser.write(command_read_recovery_data_from_eeprom)

    data = ser.read(2)
    data = data + ser.read(data[1] - 2)
    data = [hex(x)[2:].zfill(2) for x in data]

    # EEA Adapter EEPROM Recovery Position Parameters
    RecoveryPositionData = []
    page_no = data[4]
    start_position = data[5:9]
    backlash = data[9:13]
    motor_status = data[13:17]
    movement_distance_Byte_No = data[17]
    movement_distance_Bit_No = data[18]
    crc_rp = data[19]
    # print(page_no, start_position, backlash,motor_status, movement_distance_Byte_No, movement_distance_Bit_No, crc_rp)

    startPosition = convert_single_list_ele_to_decimal(start_position)
    backLash = convert_single_list_ele_to_decimal(backlash)
    motorStatus = convert_single_list_ele_to_decimal(motor_status)
    for i in [startPosition, backLash, motorStatus, movement_distance_Byte_No, movement_distance_Bit_No]:
        RecoveryPositionData.append(i)

    print("EEA Recovery Position Parameters Are:  ", RecoveryPositionData)

    # Input received from JSON File
    startPos = 0
    backlashValue = 0
    mtrStatus = 1
    moveDisByteNum = int('1c', 16)
    moveDisBitNum = 1

    RecoveryPositionSendData = []
    swappedStartPos = convert_single_byte_to_four_bytes(startPos)
    swappedBacklash = convert_single_byte_to_four_bytes(backlashValue)
    swappedMtrStatus = convert_single_byte_to_four_bytes(mtrStatus)
    moveDisByteNum = hex(moveDisByteNum)
    moveDisByteNum = moveDisByteNum[2:]
    moveDisBitNum = hex(moveDisBitNum)
    moveDisBitNum = moveDisBitNum[2:]
    for i in [swappedStartPos, swappedBacklash, swappedMtrStatus]:
        RecoveryPositionSendData.append(i)
    # print("RecoveryPositionSendData ", RecoveryPositionSendData)

    dataSplitList = []
    for i in range(3):
        dataSplitList.append(re.findall(r".{2}", RecoveryPositionSendData[i]))

    dataForCrcCalculate = []
    dataForCrcCalculate = sum(dataSplitList, [])
    dataForCrcCalculate.append(moveDisByteNum)
    dataForCrcCalculate.append(moveDisBitNum)

    ################################### Packet Framing ###########################################################
    sendDataList = []
    packet_framing = ['AA', '13', 'D6', '01']
    write_data = packet_framing + dataForCrcCalculate
    # print("Packet Without CRC :", write_data)
    sendData = (int(x, 16) for x in write_data)
    sendDataList.extend(sendData)
    packet_crc = calc(sendDataList)
    packet_crc = int(packet_crc, 16)
    sendDataList.append(packet_crc)
    print("EEPROM Write Data  :", sendDataList)
    sendDataToEeprom = bytes(sendDataList)
    # print("bytes data ", sendDataToEeprom)
    ser.write(sendDataToEeprom)

    command_read_recovery_data_from_eeprom = b'\xAA\x05\xD8\x01\xF7'
    ser.write(command_read_recovery_data_from_eeprom)

    data = ser.read(2)
    data = data + ser.read(data[1] - 2)
    data = [hex(x)[2:].zfill(2) for x in data]
    print("data ", data)


def read_and_write_adapter_eeprom_recovery_adapter_data(PowerPackComPort):
    ser = serial.Serial(PowerPackComPort, 250000, bytesize=8, parity='N', timeout=100, stopbits=1, xonxoff=0)
    read_recovery_adapter_data_rom_eeprom = b'\xAA\x05\xD8\x02\x15'
    ser.write(read_recovery_adapter_data_rom_eeprom)

    data = ser.read(2)
    data = data + ser.read(data[1] - 2)
    data = [hex(x)[2:].zfill(2) for x in data]
    # print(data)

    # EEA Adapter EEPROM Recovery Adapter Parameters
    RecoveryAdapterData = []
    page_no = data[4]
    tare_count = data[5:9]
    procedure_count = data[9:13]
    fire_count = data[13:17]
    crc_parameters = data[17]
    # print(page_no, tare_count, procedure_count, fire_count, crc_parameters)
    # Tare Count - converting list to floating point value
    tareCnt = convert_single_list_ele_to_float(tare_count)
    RecoveryAdapterData.append(tareCnt)
    # Procedure and Fire count convert hex list to decimal
    procedureCnt = convert_single_list_ele_to_decimal(procedure_count)
    fireCnt = convert_single_list_ele_to_decimal(fire_count)
    RecoveryAdapterData.append(procedureCnt)
    RecoveryAdapterData.append(fireCnt)
    print("EEA Recovery Adapter Parameters Are: ", RecoveryAdapterData)

    # Input received from JSON File
    tareValue = -14.54
    procedureValue = 6
    fireValue = 25

    RecoveryAdapterSendData = []
    tareHex = convert_single_float_to_hex_value(tareValue)
    tareInt = int(tareHex, 16)
    swapTareCnt = hex(swapEndianess32(tareInt))
    # get rid of 0x
    swapTareCnt = swapTareCnt[2:]
    RecoveryAdapterSendData.append(swapTareCnt)
    swapProcedureCnt = convert_single_byte_to_four_bytes(procedureValue)
    swapFireCnt = convert_single_byte_to_four_bytes(fireValue)
    for i in [swapProcedureCnt, swapFireCnt]:
        RecoveryAdapterSendData.append(i)
    print("RecoveryAdapterSendData : ", RecoveryAdapterSendData)

    dataSplitList = []
    for i in range(3):
        dataSplitList.append(re.findall(r".{2}", RecoveryAdapterSendData[i]))

    dataForCrcCalculate = []
    dataForCrcCalculate = sum(dataSplitList, [])
    # print("dataForCrcCalculate :", dataForCrcCalculate)

    ################################### Packet Framing ###########################################################
    sendDataList = []
    packet_framing = ['AA', '11', 'D6', '02']
    write_data = packet_framing + dataForCrcCalculate
    # print("Packet Without CRC :", write_data)
    sendData = (int(x, 16) for x in write_data)
    sendDataList.extend(sendData)
    packet_crc = calc(sendDataList)
    packet_crc = int(packet_crc, 16)
    sendDataList.append(packet_crc)
    print("EEPROM Write Data  :", sendDataList)
    sendDataToEeprom = bytes(sendDataList)
    # print("bytes data ", sendDataToEeprom)
    ser.write(sendDataToEeprom)

    command_read_recovery_data_from_eeprom = b'\xAA\x05\xD8\x02\x15'
    ser.write(command_read_recovery_data_from_eeprom)

    data = ser.read(2)
    data = data + ser.read(data[1] - 2)
    data = [hex(x)[2:].zfill(2) for x in data]
    print("data ", data)


def read_and_write_adapter_eeprom_recovery_id_data(PowerPackComPort):
    ser = serial.Serial(PowerPackComPort, 250000, bytesize=8, parity='N', timeout=100, stopbits=1, xonxoff=0)
    command_read_recovery_data_from_eeprom = b'\xAA\x05\xD8\x03\x4B'
    ser.write(command_read_recovery_data_from_eeprom)

    data = ser.read(2)
    data = data + ser.read(data[1] - 2)
    data = [hex(x)[2:].zfill(2) for x in data]
    # print("id data : ", data)

    # EEA Adapter EEPROM Recovery ID Parameters
    RecoveryIdData = []
    page_no = data[4]
    recovery_id = data[5:7]
    error_code = data[7:9]
    crc_parameter = data[9]

    # print(page_no, recovery_id, error_code, crc_parameter)
    recoveryID = convert_single_list_ele_to_two_byte_decimal(recovery_id)
    errorCode = convert_single_list_ele_to_two_byte_decimal(error_code)
    RecoveryIdData.append(recoveryID)
    RecoveryIdData.append(errorCode)
    print("EEA Recovery ID Parameters Are: ", RecoveryIdData)

    # Writing to the EEPROM  #
    # Input received from JSON File
    recID = 1
    errID = 0

    RecoveryIDSendData = []
    recID = hex(recID)
    errID = hex(errID)
    recID = recID[2:]
    errID = errID[2:]
    recID = int(recID, 16)
    errID = int(errID, 16)
    swappedRecId = swapEndianess16(recID)
    swappedErrId = swapEndianess16(errID)
    swappedRecId = hex(swappedRecId)
    swappedErrId = hex(swappedErrId)

    for i in [swappedRecId, swappedErrId]:
        RecoveryIDSendData.append(i)
    # print("RecoveryIDSendData ", RecoveryIDSendData)

    len_of_value = 6
    for i in range(2):
        if len(RecoveryIDSendData[i]) != 6:
            no_of_zeros_to_add = len_of_value - len(RecoveryIDSendData[i])
            get_rid_hex = RecoveryIDSendData[i][2:]
            RecoveryIDSendData[i] = str('0' * no_of_zeros_to_add) + get_rid_hex
        else:
            RecoveryIDSendData[i] = RecoveryIDSendData[i][2:]
    # print("after RecoveryIDSendData : ", RecoveryIDSendData)

    dataSplitList = []
    for i in range(2):
        dataSplitList.append(re.findall(r".{2}", RecoveryIDSendData[i]))
    # print("dataSplitList", dataSplitList)

    dataForCrcCalculate = []
    dataForCrcCalculate = sum(dataSplitList, [])
    # print("dataForCrcCalculate ", dataForCrcCalculate)

    ################################### Packet Framing ###########################################################
    sendDataList = []
    packet_framing = ['AA', '09', 'D6', '03']
    write_data = packet_framing + dataForCrcCalculate
    # print("Packet Without CRC :", write_data)
    sendData = (int(x, 16) for x in write_data)
    sendDataList.extend(sendData)
    packet_crc = calc(sendDataList)
    packet_crc = int(packet_crc, 16)
    sendDataList.append(packet_crc)
    print("EEPROM Write Data  :", sendDataList)
    sendDataToEeprom = bytes(sendDataList)
    # print("bytes data ", sendDataToEeprom)
    ser.write(sendDataToEeprom)

    command_read_recovery_data_from_eeprom = b'\xAA\x05\xD8\x03\x4B'
    ser.write(command_read_recovery_data_from_eeprom)

    data = ser.read(2)
    data = data + ser.read(data[1] - 2)
    data = [hex(x)[2:].zfill(2) for x in data]
    print("data ", data)


def read_and_write_adapter_eeprom_recovery_reload_1W_EE_Data(PowerPackComPort):
    ser = serial.Serial(PowerPackComPort, 250000, bytesize=8, parity='N', timeout=100, stopbits=1, xonxoff=0)
    command_read_recovery_data_from_eeprom = b'\xAA\x05\xD8\x04\xC8'
    ser.write(command_read_recovery_data_from_eeprom)

    data = ser.read(2)
    data = data + ser.read(data[1] - 2)
    data = [hex(x)[2:].zfill(2) for x in data]
    # print("Recovery Reload Data first 32 bytes : ", data)

    # EEA Adapter EEPROM Recovery Reload 1Wire Data
    RecoveryReload1Wdata = []
    page_no = data[4]
    reload_1w_data = data[5:13]
    crc_parameter = data[13]
    print(page_no, reload_1w_data, crc_parameter)
    RecoveryReload1Wdata.append(page_no)
    RecoveryReload1Wdata.append(reload_1w_data)
    RecoveryReload1Wdata.append(crc_parameter)

   # serialControl.close_serial_port(ser)
    print("EEA Recovery Reload 1 Wire Parameters Are: ", RecoveryReload1Wdata)


def GetAdapterEepromRecoveryPositionalData(FtdiUartPort):
    ser = serial.Serial(FtdiUartPort, 250000, bytesize=8, parity='N', timeout=100, stopbits=1, xonxoff=0)
    ## Sending Boot Exit Command Before reading the Eeprom data from the Adapter
    command_boot_exit = b'\xAA\x05\xE5\x00\x0D'
    ser.write(command_boot_exit)
    time.sleep(.5)
    ser.reset_input_buffer()

    ## Sending Adapter EEPROM Read Data - Page 1 ( Adapter Recovery States )
    command_read_recovery_data_from_eeprom = b'\xAA\x05\xD8\x01\xF7'
    ser.write(command_read_recovery_data_from_eeprom)
    print("FtdiUartPort", FtdiUartPort)

    data = ser.read(2)
    data = data + ser.read(data[1] - 2)
    data = [hex(x)[2:].zfill(2) for x in data]

    # EEA Adapter EEPROM Recovery Position Parameters
    RecoveryPositionData = []
    page_no = data[4]
    start_position = data[5:9]
    backlash = data[9:13]
    motor_status = data[13:17]
    movement_distance_Byte_No = data[17]
    movement_distance_Bit_No = data[18]
    crc_rp = data[19]

    ser.reset_input_buffer()

    # print(page_no, start_position, backlash,motor_status, movement_distance_Byte_No, movement_distance_Bit_No, crc_rp)

    startPosition = convert_single_list_ele_to_decimal(start_position)
    backLash = convert_single_list_ele_to_decimal(backlash)
    motorStatus = convert_single_list_ele_to_decimal(motor_status)
    for i in [startPosition, backLash, motorStatus, movement_distance_Byte_No, movement_distance_Bit_No]:
        RecoveryPositionData.append(i)

    print("EEA Recovery Position Parameters Are:  ", RecoveryPositionData)

    ser.close()

    return startPosition, backLash, motorStatus, movement_distance_Byte_No, movement_distance_Bit_No


def GetAdapterEepromRecoveryReload1WEE(FtdiUartPort):
    ser = serial.Serial(FtdiUartPort, 250000, bytesize=8, parity='N', timeout=100, stopbits=1, xonxoff=0)
    command_boot_exit = b'\xAA\x05\xE5\x00\x0D'
    ser.write(command_boot_exit)
    time.sleep(.5)
    ser.reset_input_buffer()

    ## Sending Adapter EEPROM Read Data - Page 4 ( Adapter Recovery States )
    command_read_recovery_data_from_eeprom = b'\xAA\x05\xD8\x04\xC8'
    ser.write(command_read_recovery_data_from_eeprom)

    data = ser.read(2)
    data = data + ser.read(data[1] - 2)
    data = [hex(x)[2:].zfill(2) for x in data]
    # print("Recovery Reload Data first 32 bytes : ", data)

    # EEA Adapter EEPROM Recovery Reload 1Wire Data
    page_no = data[4]
    reload_1w_data = data[5:13]
    crc_parameter = data[13]
    # print(page_no, reload_1w_data, crc_parameter)
    ser.close()
    return reload_1w_data


def read_egia_flash_params(PowerPackComPort):
    ser = serial.Serial(PowerPackComPort, 250000, bytesize=8, parity='N', timeout=100, stopbits=1, xonxoff=0)
    sg_params_read_flash_data = b'\xAA\x0A\xC8\x0C\x18\x00\x00\x70\x00\x48'
    ser.write(sg_params_read_flash_data)

    data = ser.read(2)
    data = data + ser.read(data[1] - 2)
    # print(data)
    # print(list(data))
    data = [hex(x)[2:].zfill(2) for x in data]
    # print(data)

    # Strain Gauge Params
    StrainGaugeParams = []
    flash_sg_struct_checksum = data[8:12]
    flash_sg_gain = data[12:16]
    flash_sg_offset = data[16:20]
    flash_sg_second_ord_coefficient = data[20:24]

    # print(flash_sg_struct_checksum, flash_sg_gain, flash_sg_offset, flash_sg_second_ord_coefficient)
    for i in [flash_sg_struct_checksum, flash_sg_gain, flash_sg_offset, flash_sg_second_ord_coefficient]:
        StrainGaugeParams.append(i)
    actual_sg_params = convert_list_to_float(StrainGaugeParams)
    print("EGIA Adapter Flash SG Params Are: ", actual_sg_params)

    # Factory Adapter Cal Params
    AdapterCalibParams = []
    cal_struct_checksum = data[24:28]
    backlash_turns = data[28:32]
    calib_turns = data[32:36]
    clamp_turns = data[36:40]
    art_calib_turns = data[40:44]
    art_max_left_turns = data[44:48]
    art_max_right_turns = data[48:52]
    rotate_max_turns = data[52:56]
    # print(cal_struct_checksum, backlash_turns, calib_turns, clamp_turns,
    #      art_calib_turns, art_max_left_turns, art_max_right_turns, rotate_max_turns)
    for i in [cal_struct_checksum, backlash_turns, calib_turns, clamp_turns,
              art_calib_turns, art_max_left_turns, art_max_right_turns, rotate_max_turns]:
        AdapterCalibParams.append(i)
    actual_calib_params = convert_list_to_float(AdapterCalibParams)
    print("EGIA Adapter Flash Calib Params Are: ", actual_calib_params)

    # Adapter Flash LOT Number
    FlashLotList = []
    lot_struct_checksum = data[56:60]
    lot_number = data[60:76]
    # Reading Only the serial number present portion
    lot_number_EGIA = data[60:70]
    # print("Original Flash Lot Params Are: ", lot_struct_checksum, lot_number)
    lotNumber = convert_single_list_ele_to_ascii(lot_number_EGIA)
    for i in [lot_struct_checksum, lotNumber]:
        FlashLotList.append(i)
    print("EGIA Adapter Flash Lot Params Are: ", FlashLotList)

    # Adapter Board Params
    BoardParamsList = []
    board_struct_checksum = data[76:80]
    tare_drift_high = data[80:84]  # maximum positive drift allowable to tare off
    tare_drift_low = data[84:88]  # maximum drift allowable to tare off
    zb_cnt_ceiling = data[88:92]  # maximum value for zero pound count (ceiling)
    zb_cnt_floor = data[92:96]
    # print(board_struct_checksum, tare_drift_high, tare_drift_low, zb_cnt_ceiling, zb_cnt_floor)
    for i in [board_struct_checksum, tare_drift_high, tare_drift_low, zb_cnt_ceiling, zb_cnt_floor]:
        BoardParamsList.append(i)
    # Converting List of elements to Floating point data
    actual_board_params = convert_list_to_float(BoardParamsList)
    print("EGIA Adapter Board Params Are: ", actual_board_params)

    # Factory GTIN Number
    GTINParamsList = []
    gtin_struct_checksum = data[96:100]
    gtin_number = data[100:120]
    # Reading Only the serial number present portion
    gtin_number_EGIA = data[100:110]
    gtinNumber = convert_single_list_ele_to_ascii(gtin_number_EGIA)
    for i in [gtin_struct_checksum, gtinNumber]:
        GTINParamsList.append(i)
    print("EGIA Adapter GTIN Number Params Are: ", GTINParamsList)

    # Here Receive Input form the JSON File
    sg_gain = 0.10520
    sg_offset = -75.0
    sg_order = 0

    fireRodBacklashTurns = 0.95
    fireRodCalibTurns = 2
    clampTurns = 11
    articCalibTurns = 10
    articMaxleftTurns = 8.5
    articMaxRightTurns = 9.5
    rotateMaxTurns = 0

    lotNum = "C18ABA0135"
    serialNumber = convert_ascii_to_hex(lotNum)
    # Putting dummy data to fulfill the Lot Number size.
    excessNum = ["00", "00", "00", "00", "00", "00"]
    serialNumber = serialNumber + excessNum

    egiaTareDriftHigh = 337
    egiaTareDriftLow = -387
    egiaZeroCeiling = 1709
    egiaZeroFloor = 2

    gtinNum = "1234567890"
    gtinSerialNumber = convert_ascii_to_hex(gtinNum)
    # Putting dummy data to fulfill the GTIN Number size.
    excessNumber = ["00", "00", "00", "00", "00", "00", "00", "00", "00", "00"]
    gtinSerialNumber = gtinSerialNumber + excessNumber

    received_input_data = []
    for i in [sg_gain, sg_offset, sg_order, fireRodBacklashTurns, fireRodCalibTurns, clampTurns,
              articCalibTurns, articMaxleftTurns, articMaxRightTurns, rotateMaxTurns, egiaTareDriftHigh,
              egiaTareDriftLow, egiaZeroCeiling, egiaZeroFloor]:
        received_input_data.append(i)
    # print("received_input_data : ", received_input_data)
    sg_calib_board_data = convert_multiple_float_to_hex_value(received_input_data)
    # print("INPUT_DATA : ", received_input_data)

    received_data_swapped = []
    for i in range(14):
        str_to_int = int(sg_calib_board_data[i], 16)
        swapped_value = swapEndianess32(str_to_int)
        received_data_swapped.append(hex(swapped_value))

    len_of_value = 10
    for i in range(14):
        if len(received_data_swapped[i]) != 10:
            no_of_zeros_to_add = len_of_value - len(received_data_swapped[i])
            get_rig_hex = received_data_swapped[i][2:]
            received_data_swapped[i] = str('0' * no_of_zeros_to_add) + get_rig_hex
        else:
            received_data_swapped[i] = received_data_swapped[i][2:]

    # print("After swapped : ", received_data_swapped)
    ## data to form for the Check sum calculation
    ## Appending Strain Gauge, Adapter Calibration Parameters
    dataForCalChecksum = []
    for i in range(10):
        dataForCalChecksum.append(re.findall(r".{2}", received_data_swapped[i]))

    ## Appending Lot Num here ( received  as hex value )
    dataForCalChecksum.append(serialNumber)

    ## Board Params are started here.
    idx = 10
    for i in range(4):
        dataForCalChecksum.append(re.findall(r".{2}", received_data_swapped[i + idx]))

    ## Appending GTIN Number here ( received as hex value )
    dataForCalChecksum.append(gtinSerialNumber)

    print("data for calculate checksum ", dataForCalChecksum)

    sg_structure_data = []
    calib_structure_data = []
    lot_structure_data = []
    board_structure_data = []
    gtin_structure_data = []
    for i in range(len(dataForCalChecksum)):
        # print("index : , value : ", i, dataForCalChecksum[i])
        if i < 3:
            sg_structure_data.append(dataForCalChecksum[i])
        elif 3 <= i <= 9:
            calib_structure_data.append(dataForCalChecksum[i])
        elif i == 10:
            lot_structure_data.append(dataForCalChecksum[i])
        elif 10 < i <= 14:
            board_structure_data.append(dataForCalChecksum[i])
        elif i > 14:
            gtin_structure_data.append(dataForCalChecksum[i])

    ## CALCULATING SG DATA CHECK SUM
    ## Summing of List of Lists to Single List
    sg_structure_data = sum(sg_structure_data, [])
    ## Using Generator to convert String to Integer List of elements
    sGdataToSend = (int(x, 16) for x in sg_structure_data)
    sg_checksum = CRC32(0xFFFFFFFF, sGdataToSend)
    sg_checksum_value = swapEndianess32(sg_checksum)
    # print("SG CheckSum : ", hex(sg_checksum))
    sg_checksum = hex(sg_checksum_value)[2:]
    sg_checksum_split = re.findall(r".{2}", sg_checksum)
    # print("checksum sg: ", sg_checksum_split)
    # print("dataForCalChecksum ", dataForCalChecksum)
    sgSendList = sg_checksum_split + sg_structure_data
    print("SG Send List ", sgSendList)

    ## CALCULATING CALIB DATA CHECK SUM
    ## Summing of List of Lists to Single List
    calib_structure_data = sum(calib_structure_data, [])
    ## Using Generator to convert String to Integer List of elements
    calibDataToSend = (int(x, 16) for x in calib_structure_data)
    calib_checksum = CRC32(0xFFFFFFFF, calibDataToSend)
    calib_checksum_value = swapEndianess32(calib_checksum)
    # print("Calib CheckSum : ", hex(calib_checksum_value))
    calib_checksum = hex(calib_checksum_value)[2:]
    calib_checksum_split = re.findall(r".{2}", calib_checksum)
    # print("checksum calib : ", calib_checksum_split)
    # print("dataForCalChecksum ", dataForCalChecksum)
    # print("calib_structure_data :", calib_structure_data)
    calibSendList = calib_checksum_split + calib_structure_data
    print("Calib Send  List ", calibSendList)

    ## CALCULATING LOT NUMBER DATA CHECK SUM
    ## Summing of List of Lists to Single List
    lot_structure_data = sum(lot_structure_data, [])
    ## Using Generator to convert String to Integer List of elements
    lotDataToSend = (int(x, 16) for x in lot_structure_data)
    lot_checksum = CRC32(0xFFFFFFFF, lotDataToSend)
    lot_checksum_value = swapEndianess32(lot_checksum)
    # print("Lot Number CheckSum : ", hex(lot_checksum_value))
    lot_checksum = hex(lot_checksum_value)[2:]
    lot_checksum_split = re.findall(r".{2}", lot_checksum)
    # print("checksum lot number : ", lot_checksum_split)
    # print("dataForCalChecksum ", dataForCalChecksum)
    # print("lot_structure_data :", lot_structure_data)
    lotSendList = lot_checksum_split + lot_structure_data
    print("Lot Number Send  List ", lotSendList)

    ## CALCULATING BOARD PARAMS DATA CHECK SUM
    ## Summing of List of Lists to Single List
    board_structure_data = sum(board_structure_data, [])
    ## Using Generator to convert String to Integer List of elements
    boardDataToSend = (int(x, 16) for x in board_structure_data)
    board_checksum = CRC32(0xFFFFFFFF, boardDataToSend)
    board_checksum_value = swapEndianess32(board_checksum)
    # print("Board CheckSum : ", hex(board_checksum_value))
    board_checksum = hex(board_checksum_value)[2:]
    board_checksum_split = re.findall(r".{2}", board_checksum)
    # print("checksum board params : ", board_checksum_split)
    # print("dataForCalChecksum ", dataForCalChecksum)
    # print("board_structure_data :", board_structure_data)
    boardSendList = board_checksum_split + board_structure_data
    print("Board Parameters Send  List ", boardSendList)

    ## CALCULATING GTIN PARAMS DATA CHECK SUM
    ## Summing of List of Lists to Single List
    gtin_structure_data = sum(gtin_structure_data, [])
    ## Using Generator to convert String to Integer List of elements
    gtinDataToSend = (int(x, 16) for x in gtin_structure_data)
    gtin_checksum = CRC32(0xFFFFFFFF, gtinDataToSend)
    gtin_checksum_value = swapEndianess32(gtin_checksum)
    # print("GTIN CheckSum : ", hex(gtin_checksum_value))
    gtin_checksum = hex(gtin_checksum_value)[2:]
    gtin_checksum_split = re.findall(r".{2}", gtin_checksum)
    # print("checksum gtin number : ", gtin_checksum_split)
    # print("dataForCalChecksum ", dataForCalChecksum)
    # print("gtin_structure_data :", gtin_structure_data)
    gtinSendList = gtin_checksum_split + gtin_structure_data
    print("GTIN Parameters Send  List ", gtinSendList)

    ################################### Packet Framing ###########################################################
    sendDataList = []
    packet_framing = ['AA', '78', 'C7', '0C', '18', '00', '00']
    write_data = packet_framing + sgSendList + calibSendList + lotSendList + boardSendList + gtinSendList
    # print("Packet Without CRC :", write_data)
    sendData = (int(x, 16) for x in write_data)
    sendDataList.extend(sendData)
    packet_crc = calc(sendDataList)
    packet_crc = int(packet_crc, 16)
    sendDataList.append(packet_crc)
    # print("flash_write_data :", sendDataList)
    sendDataToFlash = bytes(sendDataList)
    # print("bytes data ", sendDataToFlash)
    ser.write(sendDataToFlash)

    # sg_params_read_flash_data = b'\xAA\x0A\xC8\x0C\x18\x00\x00\x70\x00\x48'
    # ser.write(sg_params_read_flash_data)
    #
    # data = ser.read(2)
    # data = data + ser.read(data[1] - 2)
    # # print(data)
    # # print(list(data))
    # data = [hex(x)[2:].zfill(2) for x in data]
    # print(data)


def read_eea_flash_params(PowerPackComPort):
    ser = serial.Serial(PowerPackComPort, 250000, bytesize=8, parity='N', timeout=100, stopbits=1, xonxoff=0)
    eea_params_read_flash_data = b'\xAA\x0A\xC8\x0C\x18\x00\x00\xA0\x00\x10'
    ser.write(eea_params_read_flash_data)

    data = ser.read(2)
    data = data + ser.read(data[1] - 2)
    # print(data)
    # print(list(data))
    data = [hex(x)[2:].zfill(2) for x in data]
    print(data)

    # Strain Gauge Params
    StrainGaugeParams = []
    flash_sg_struct_checksum = data[8:12]
    flash_sg_gain = data[12:16]
    flash_sg_offset = data[16:20]
    flash_sg_second_ord_coefficient = data[20:24]

    print(flash_sg_struct_checksum, flash_sg_gain, flash_sg_offset, flash_sg_second_ord_coefficient)
    for i in [flash_sg_struct_checksum, flash_sg_gain, flash_sg_offset, flash_sg_second_ord_coefficient]:
        StrainGaugeParams.append(i)
    actual_sg_params = convert_list_to_float(StrainGaugeParams)
    print("EEA Adapter Flash SG Params Are: ", actual_sg_params)

    # Factory Adapter Cal Params
    AdapterCalibParams = []
    cal_struct_checksum = data[24:28]
    staple_x2_coefficient = data[28:32]
    staple_x_coefficient = data[32:36]
    staple_backlash = data[36:40]
    # unused_bytes = data[40:44]
    cut_offset = data[44:48]
    clamp_offset = data[48:52]
    # not_used = data[52:56]
    print(cal_struct_checksum, staple_x2_coefficient, staple_x_coefficient, staple_backlash,
          cut_offset, clamp_offset)
    for i in [cal_struct_checksum, staple_x2_coefficient, staple_x_coefficient, staple_backlash,
              cut_offset, clamp_offset]:
        AdapterCalibParams.append(i)
    actual_calib_params = convert_list_to_float(AdapterCalibParams)
    print("EEA Adapter Flash Calib Params Are: ", actual_calib_params)

    # Adapter Flash LOT Number
    FlashLotList = []
    lot_struct_checksum = data[56:60]
    lot_number = data[60:76]
    # Reading Only the serial number present portion
    lot_number_EEA = data[60:70]
    # print("Original Flash Lot Params Are: ", lot_struct_checksum, lot_number)
    lotNumber = convert_single_list_ele_to_ascii(lot_number_EEA)
    for i in [lot_struct_checksum, lotNumber]:
        FlashLotList.append(i)
    print("EEA Adapter Flash Lot Params Are: ", FlashLotList)

    # Factory GTIN Number
    GTINParamsList = []
    gtin_struct_checksum = data[96:100]
    gtin_number = data[100:120]
    # Reading Only the serial number present portion
    gtin_number_EEA = data[100:114]
    gtinNumber = convert_single_list_ele_to_ascii(gtin_number_EEA)
    for i in [gtin_struct_checksum, gtinNumber]:
        GTINParamsList.append(i)
    print("EEA Adapter GTIN Number Params Are: ", GTINParamsList)

    ## Factory EEA Adapter Flash coefficients Params
    eeaFlashParasList = []
    eea_struct_checksum = data[120:124]
    eea_staple_home = data[124:128]
    eea_cut_home = data[128:132]
    eea_a3_x2 = data[132:136]
    eea_a3_x1 = data[136:140]
    eea_a3_y = data[140:144]
    print(eea_struct_checksum, eea_staple_home, eea_cut_home, eea_a3_x2, eea_a3_x1, eea_a3_y)
    for i in [eea_struct_checksum, eea_staple_home, eea_cut_home, eea_a3_x2, eea_a3_x1, eea_a3_y]:
        eeaFlashParasList.append(i)

    # Converting List of elements to Floating point data
    actual_eea_params = convert_list_to_float(eeaFlashParasList)
    print("EEA Adapter Flash Coefficient Params Are: ", actual_eea_params)

    ## EEA A3 Params Checksum
    eeaFlashParams = []
    eea_a3_checksum = data[144:148]
    eea_a3_staple_x2 = data[148:152]
    eea_a3_staple_x1 = data[152:156]
    eea_a3_staple_y = data[156:160]
    eea_a3_cut_offset = data[160:164]
    eea_a3_x3 = data[164:168]
    print(eea_a3_checksum, eea_a3_staple_x2, eea_a3_staple_x1,
          eea_a3_staple_y, eea_a3_cut_offset, eea_a3_cut_offset, eea_a3_x3)
    for i in [eea_a3_checksum, eea_a3_staple_x2, eea_a3_staple_x1,
              eea_a3_staple_y, eea_a3_cut_offset, eea_a3_cut_offset, eea_a3_x3]:
        eeaFlashParams.append(i)

    # Converting List of elements to Floating point data
    actual_eea_flash_params = convert_list_to_float(eeaFlashParams)
    print("EEA Adapter Extra Params Are: ", actual_eea_flash_params)

    # For EEA Adapters before writing into the flash it needs to be Send the Enable Flash command ( D7 )
    command_enable_flash_commands = b'\xAA\x05\xD7\x00\xB1'
    ser.write(command_enable_flash_commands)

    # Here Receive Input form the JSON File
    sg_gain = 0.16914
    sg_offset = -50.47214
    sg_order = 0

    stapleX2coefficient = -1.12741
    stapleXcoefficient = 0.04963
    stapleBackLash = 0.1446
    eeaUnused = 0
    cutOffset = 11.94
    clampOffset = 2.37829
    notUsed = 0

    lotNum = "C21AFJ0020"
    serialNumber = convert_ascii_to_hex(lotNum)
    # Putting dummy data to fulfill the Lot Number size.
    excessNum = ["00", "00", "00", "00", "00", "00"]
    serialNumber = serialNumber + excessNum

    # In EGIA Adapter case these parameters are used as Bord parameters
    # But in EEA this section is not using, so filling with Dummy Zeros
    unused_dummy_0 = 0
    unused_dummy_1 = 0
    unused_dummy_2 = 0
    unused_dummy_3 = 0

    gtinNum = "10884521703681"
    gtinSerialNumber = convert_ascii_to_hex(gtinNum)
    # Putting dummy data to fulfill the GTIN Number size.
    excessNumber = ["00", "00", "00", "00", "00", "00"]
    gtinSerialNumber = gtinSerialNumber + excessNumber

    stapleHomePos = 19.0890
    cutHomePos = 11.234
    a3X2Coefficient = 0
    a3X1Coefficient = 0
    a3YCoefficient = 0

    a3StapleX2Coefficient = 0
    a3StapleX1Coefficient = 0
    a3StapleYCoefficient = 0
    a3CutOffset = 0
    a3X3Coefficient = 0

    received_input_data = []
    for i in [sg_gain, sg_offset, sg_order, stapleX2coefficient, stapleXcoefficient, stapleBackLash,
              eeaUnused, cutOffset, clampOffset, notUsed, unused_dummy_0, unused_dummy_1, unused_dummy_2,
              unused_dummy_3, stapleHomePos, cutHomePos, a3X2Coefficient, a3X1Coefficient, a3YCoefficient,
              a3StapleX2Coefficient, a3StapleX1Coefficient, a3StapleYCoefficient, a3CutOffset, a3X3Coefficient]:
        received_input_data.append(i)
    # print("received_input_data : ", received_input_data)
    sg_calib_data = convert_multiple_float_to_hex_value(received_input_data)
    print("INPUT_DATA : ", received_input_data)

    received_data_swapped = []
    for i in range(24):
        str_to_int = int(sg_calib_data[i], 16)
        swapped_value = swapEndianess32(str_to_int)
        received_data_swapped.append(hex(swapped_value))

    len_of_value = 10
    for i in range(24):
        if len(received_data_swapped[i]) != 10:
            no_of_zeros_to_add = len_of_value - len(received_data_swapped[i])
            get_rig_hex = received_data_swapped[i][2:]
            received_data_swapped[i] = str('0' * no_of_zeros_to_add) + get_rig_hex
        else:
            received_data_swapped[i] = received_data_swapped[i][2:]

    # print("After swapped : ", received_data_swapped)
    # data to form for the Check sum calculation
    # Appending Strain Gauge, Adapter Calibration Parameters
    dataForCalChecksum = []
    for i in range(10):
        dataForCalChecksum.append(re.findall(r".{2}", received_data_swapped[i]))

    # Appending Lot Num here ( received  as hex value )
    dataForCalChecksum.append(serialNumber)

    # # Board Params are not used in EEA Adapter so sending dummy zero's to calculate the checksum.
    # # In received_data_swapped list ( from index 10 storing dummy zero's )
    idx = 10
    for i in range(4):
        dataForCalChecksum.append(re.findall(r".{2}", received_data_swapped[i + idx]))

    # Appending GTIN Number here ( received as hex value )
    dataForCalChecksum.append(gtinSerialNumber)

    # # EEA Adapter Flash coefficients Params
    # Specific to EEA Parameters - Staple, Cut, Coefficients
    idx = 14
    for i in range(5):
        dataForCalChecksum.append(re.findall(r".{2}", received_data_swapped[i + idx]))

    # EEA Adapter Flash Extra coefficients Parameters
    # Specific to EEA Extra Parameters - A3 Parameters - Staple, Cut, Coefficients
    idx = 19
    for i in range(5):
        dataForCalChecksum.append(re.findall(r".{2}", received_data_swapped[i + idx]))

    print("data for calculate checksum ", dataForCalChecksum)

    sg_structure_data = []
    calib_structure_data = []
    lot_structure_data = []
    board_no_use_eea_structure_data = []
    gtin_structure_data = []
    eea_flash_coefficients_structure_data = []
    eea_flash_extra_a3_structure_data = []
    for i in range(len(dataForCalChecksum)):
        # print("index : , value : ", i, dataForCalChecksum[i])
        if i < 3:
            sg_structure_data.append(dataForCalChecksum[i])
        elif 3 <= i <= 9:
            calib_structure_data.append(dataForCalChecksum[i])
        elif i == 10:
            lot_structure_data.append(dataForCalChecksum[i])
        elif 10 < i <= 14:
            board_no_use_eea_structure_data.append(dataForCalChecksum[i])
        elif i == 15:
            gtin_structure_data.append(dataForCalChecksum[i])
        elif 15 < i <= 20:
            eea_flash_coefficients_structure_data.append(dataForCalChecksum[i])
        elif 20 < i <= 25:
            eea_flash_extra_a3_structure_data.append(dataForCalChecksum[i])

    # CALCULATING SG DATA CHECK SUM
    # Summing of List of Lists to Single List
    sg_structure_data = sum(sg_structure_data, [])
    # Using Generator to convert String to Integer List of elements
    sGdataToSend = (int(x, 16) for x in sg_structure_data)
    sg_checksum = CRC32(0xFFFFFFFF, sGdataToSend)
    sg_checksum_value = swapEndianess32(sg_checksum)
    # print("SG CheckSum : ", hex(sg_checksum))
    sg_checksum = hex(sg_checksum_value)[2:]
    sg_checksum_split = re.findall(r".{2}", sg_checksum)
    # print("checksum sg: ", sg_checksum_split)
    # print("dataForCalChecksum ", dataForCalChecksum)
    sgSendList = sg_checksum_split + sg_structure_data
    print("SG Send List ", sgSendList)

    # CALCULATING CALIB DATA CHECK SUM
    # Summing of List of Lists to Single List
    calib_structure_data = sum(calib_structure_data, [])
    # Using Generator to convert String to Integer List of elements
    calibDataToSend = (int(x, 16) for x in calib_structure_data)
    calib_checksum = CRC32(0xFFFFFFFF, calibDataToSend)
    calib_checksum_value = swapEndianess32(calib_checksum)
    # print("Calib CheckSum : ", hex(calib_checksum_value))
    calib_checksum = hex(calib_checksum_value)[2:]
    calib_checksum_split = re.findall(r".{2}", calib_checksum)
    # print("checksum calib : ", calib_checksum_split)
    # print("dataForCalChecksum ", dataForCalChecksum)
    # print("calib_structure_data :", calib_structure_data)
    calibSendList = calib_checksum_split + calib_structure_data
    print("Calib Send  List ", calibSendList)

    # CALCULATING LOT NUMBER DATA CHECK SUM
    # Summing of List of Lists to Single List
    lot_structure_data = sum(lot_structure_data, [])
    # Using Generator to convert String to Integer List of elements
    lotDataToSend = (int(x, 16) for x in lot_structure_data)
    lot_checksum = CRC32(0xFFFFFFFF, lotDataToSend)
    lot_checksum_value = swapEndianess32(lot_checksum)
    # print("Lot Number CheckSum : ", hex(lot_checksum_value))
    lot_checksum = hex(lot_checksum_value)[2:]
    lot_checksum_split = re.findall(r".{2}", lot_checksum)
    # print("checksum lot number : ", lot_checksum_split)
    # print("dataForCalChecksum ", dataForCalChecksum)
    # print("lot_structure_data :", lot_structure_data)
    lotSendList = lot_checksum_split + lot_structure_data
    print("Lot Number Send  List ", lotSendList)

    # CALCULATING BOARD PARAMS DATA CHECK SUM - NOT USING IN EEA
    # Summing of List of Lists to Single List
    board_no_use_eea_structure_data = sum(board_no_use_eea_structure_data, [])
    # Using Generator to convert String to Integer List of elements
    boardNoUseEeaDataToSend = (int(x, 16) for x in board_no_use_eea_structure_data)
    board_no_use_eea_checksum = CRC32(0xFFFFFFFF, boardNoUseEeaDataToSend)
    board_noUse_eea_checksum_value = swapEndianess32(board_no_use_eea_checksum)
    # print("Board No Use EEA CheckSum : ", hex(board_noUse_eea_checksum_value))
    board_notUsing_eea_checksum = hex(board_noUse_eea_checksum_value)[2:]
    board_notUse_eea_checksum_split = re.findall(r".{2}", board_notUsing_eea_checksum)
    # print("checksum board params ( EEA not using ): ", board_notUse_eea_checksum_split)
    # print("dataForCalChecksum ", dataForCalChecksum)
    # print("board_no_use_eea_structure_data :", board_no_use_eea_structure_data)
    boardSendList = board_notUse_eea_checksum_split + board_no_use_eea_structure_data
    print("Board Parameters No Use EEA Send  List ", boardSendList)

    # CALCULATING GTIN PARAMS DATA CHECK SUM
    # Summing of List of Lists to Single List
    gtin_structure_data = sum(gtin_structure_data, [])
    print("gtin trucutr data ", gtin_structure_data)
    # Using Generator to convert String to Integer List of elements
    gtinDataToSend = (int(x, 16) for x in gtin_structure_data)
    gtin_checksum = CRC32(0xFFFFFFFF, gtinDataToSend)
    gtin_checksum_value = swapEndianess32(gtin_checksum)
    # print("GTIN CheckSum : ", hex(gtin_checksum_value))
    gtin_checksum = hex(gtin_checksum_value)[2:]
    gtin_checksum_split = re.findall(r".{2}", gtin_checksum)
    # print("checksum gtin number : ", gtin_checksum_split)
    # print("dataForCalChecksum ", dataForCalChecksum)
    # print("gtin_structure_data :", gtin_structure_data)
    gtinSendList = gtin_checksum_split + gtin_structure_data
    print("GTIN Parameters Send  List ", gtinSendList)

    # # CALCULATING EEA FLASH COEFFICIENTS DATA CHECK SUM
    # Summing of List of Lists to Single List
    eea_flash_coefficients_structure_data = sum(eea_flash_coefficients_structure_data, [])
    # Using Generator to convert String to Integer List of elements
    eeaCoefficientDataToSend = (int(x, 16) for x in eea_flash_coefficients_structure_data)
    eea_coefficient_checksum = CRC32(0xFFFFFFFF, eeaCoefficientDataToSend)
    eea_coefficient_checksum_value = swapEndianess32(eea_coefficient_checksum)
    # print("EEA Coefficient Checksum : ", hex(eea_coefficient_checksum_value))
    eea_coefficient_checksum = hex(eea_coefficient_checksum_value)[2:]
    eea_coefficient_checksum_split = re.findall(r".{2}", eea_coefficient_checksum)
    # print("checksum eea coefficient : ", eea_coefficient_checksum_split)
    # print("dataForCalChecksum ", dataForCalChecksum)
    # print("eea_flash_coefficients_structure_data :", eea_flash_coefficients_structure_data)
    eeaCoefficientSendList = eea_coefficient_checksum_split + eea_flash_coefficients_structure_data
    print("EEA Flash Coefficient Send  List ", eeaCoefficientSendList)

    # CALCULATING EEA EXTRA COEFFICIENTS A3 DATA CHECK SUM
    # Summing of List of Lists to Single List
    eea_flash_extra_a3_structure_data = sum(eea_flash_extra_a3_structure_data, [])
    # Using Generator to convert String to Integer List of elements
    eeaA3DataToSend = (int(x, 16) for x in eea_flash_extra_a3_structure_data)
    eeaA3_checksum = CRC32(0xFFFFFFFF, eeaA3DataToSend)
    eeaA3_checksum_value = swapEndianess32(eeaA3_checksum)
    # print("EEA A3 Checksum : ", hex(eeaA3_checksum_value))
    eeaA3_checksum = hex(eeaA3_checksum_value)[2:]
    eeaA3_checksum_split = re.findall(r".{2}", eeaA3_checksum)
    # print("checksum eea A3 : ", eeaA3_checksum_split)
    # print("dataForCalChecksum ", dataForCalChecksum)
    # print("eea_flash_extra_a3_structure_data :", eea_flash_extra_a3_structure_data)
    eeaA3SendList = eeaA3_checksum_split + eea_flash_extra_a3_structure_data
    print("EEA A3 Coefficient Send  List ", eeaA3SendList)

    ################################### Packet Framing ###########################################################
    sendDataList = []
    packet_framing = ['AA', 'A8', 'C7', '0C', '18', '00', '00']
    write_data = (packet_framing + sgSendList + calibSendList + lotSendList + boardSendList + gtinSendList +
                  eeaCoefficientSendList + eeaA3SendList)
    print("Packet Without CRC :", write_data)
    sendData = (int(x, 16) for x in write_data)
    sendDataList.extend(sendData)
    packet_crc = calc(sendDataList)
    packet_crc = int(packet_crc, 16)
    sendDataList.append(packet_crc)
    print("flash_write_data :", sendDataList)
    sendDataToFlash = bytes(sendDataList)
    # print("bytes data ", sendDataToFlash)
    ser.write(sendDataToFlash)

    # sg_params_read_flash_data = b'\xAA\x0A\xC8\x0C\x18\x00\x00\xA0\x00\x10'
    # ser.write(sg_params_read_flash_data)
    #
    # data = ser.read(2)
    # data = data + ser.read(data[1] - 2)
    # # print(data)
    # # print(list(data))
    # data = [hex(x)[2:].zfill(2) for x in data]
    # print(data)


def AdapterRecoveryStates(RecoveryIndex):
    return RecoveryState[RecoveryIndex]


def Boot_exit(PowerPackComPort):
    ser = serial.Serial(PowerPackComPort, 250000, bytesize=8, parity='N', timeout=100, stopbits=1, xonxoff=0)
    command_boot_exit = b'\xAA\x05\xE5\x00\x0D'
    ser.write(command_boot_exit)
    time.sleep(.5)


#### This function is used for issue 450475
def GetAdapterEepromRecoveryData(FtdiUartComPort):
    ser = serial.Serial(FtdiUartComPort, 250000, bytesize=8, parity='N', timeout=100, stopbits=1, xonxoff=0)
    ## Sending Boot Exit Command Before reading the Eeprom data from the Adapter
    command_boot_exit = b'\xAA\x05\xE5\x00\x0D'
    ser.write(command_boot_exit)
    time.sleep(.5)
    ser.reset_input_buffer()

    ## Sending Adapter EEPROM Read Data - Page 3 ( Adapter Recovery States )
    command_read_recovery_data_from_eeprom = b'\xAA\x05\xD8\x03\x4B'
    ser.write(command_read_recovery_data_from_eeprom)
    # time.sleep(3)

    data = ser.read(2)
    # print(simple_colors.magenta(f"data : {data}"))
    data = data + ser.read(data[1] - 2)
    data = [hex(x)[2:].zfill(2) for x in data]
    # print("id data : ", data)

    ser.reset_input_buffer()

    recoveryID = 0
    errorCode = 0

    # EEA Adapter EEPROM Recovery ID Parameters
    page_no = data[4]
    recovery_id = data[5:7]
    error_code = data[7:9]
    crc_parameter = data[9]

    # recoveryID and Error Code  - converting list to decimal value
    recoveryID = convert_single_list_ele_to_two_byte_decimal(recovery_id)
    errorCode = convert_single_list_ele_to_two_byte_decimal(error_code)

    print(f"Recovery Parameters : {recoveryID}, {errorCode}")

    ser.close()
    return recoveryID, errorCode


def GetAdapterEepromUsageCounts(FtdiUartComPort):
    ser = serial.Serial(FtdiUartComPort, 250000, bytesize=8, parity='N', timeout=100, stopbits=1, xonxoff=0)
    ## Sending Boot Exit Command Before reading the Eeprom data from the Adapter
    command_boot_exit = b'\xAA\x05\xE5\x00\x0D'
    ser.write(command_boot_exit)
    time.sleep(.5)
    ser.reset_input_buffer()

    ## Sending Adapter EEPROM Read Data - Page 2 ( Adapter Usage Counts )
    read_recovery_adapter_data_rom_eeprom = b'\xAA\x05\xD8\x02\x15'
    ser.write(read_recovery_adapter_data_rom_eeprom)

    data = ser.read(2)
    data = data + ser.read(data[1] - 2)
    data = [hex(x)[2:].zfill(2) for x in data]
    # print(data)

    ser.reset_input_buffer()

    # EEA Adapter EEPROM Recovery Adapter Parameters
    page_no = data[4]
    tare_count = data[5:9]
    procedure_count = data[9:13]
    fire_count = data[13:17]
    crc_parameters = data[17]
    # print(page_no, tare_count, procedure_count, fire_count, crc_parameters)
    # Tare Count - converting list to floating point value
    tareCnt = convert_single_list_ele_to_float(tare_count)
    # Procedure and Fire count convert hex list to decimal
    AdapterEepromProcedureCnt = convert_single_list_ele_to_decimal(procedure_count)
    AdapterEepromFireCnt = convert_single_list_ele_to_decimal(fire_count)

    ser.close()
    return AdapterEepromProcedureCnt, AdapterEepromFireCnt


def GetAdapterEepromRecoveryAdapterData(FtdiUartComPort):
    ser = serial.Serial(FtdiUartComPort, 250000, bytesize=8, parity='N', timeout=100, stopbits=1, xonxoff=0)
    ## Sending Boot Exit Command Before reading the Eeprom data from the Adapter
    command_boot_exit = b'\xAA\x05\xE5\x00\x0D'
    ser.write(command_boot_exit)
    time.sleep(.5)
    ser.reset_input_buffer()

    ## Sending Adapter EEPROM Read Data - Page 2 ( Adapter Usage Counts )
    read_recovery_adapter_data_rom_eeprom = b'\xAA\x05\xD8\x02\x15'
    ser.write(read_recovery_adapter_data_rom_eeprom)

    data = ser.read(2)
    data = data + ser.read(data[1] - 2)
    data = [hex(x)[2:].zfill(2) for x in data]
    # print(data)

    ser.reset_input_buffer()

    # EEA Adapter EEPROM Recovery Adapter Parameters
    page_no = data[4]
    tare_count = data[5:9]
    procedure_count = data[9:13]
    fire_count = data[13:17]
    crc_parameters = data[17]
    print(page_no, tare_count, procedure_count, fire_count, crc_parameters)
    # Tare Count - converting list to floating point value
    tareCnt = convert_single_list_ele_to_float(tare_count)
    # Procedure and Fire count convert hex list to decimal
    AdapterEepromProcedureCnt = convert_single_list_ele_to_decimal(procedure_count)
    AdapterEepromFireCnt = convert_single_list_ele_to_decimal(fire_count)

    ser.close()
    return tareCnt, AdapterEepromProcedureCnt, AdapterEepromFireCnt


def GetAdapterOnewireUsageCounts(BlackBoxComPort):
    print(BlackBoxComPort)
    ser = serial.Serial(BlackBoxComPort, 500000, bytesize=8, parity='N', timeout=100, stopbits=1, xonxoff=0)
    ## Sending PING Command Before reading the Onewire data from the Adapter
    command_PING = b'\xAA\x04\x01\xF9'
    ser.write(command_PING)
    print("hiiiii")
    # time.sleep(.5)

    # for retry in range(5):
    data = ser.read(2)
    print("Reading out ", data )
    data = data + ser.read(data[1] - 2)
    data = [hex(x)[2:].zfill(2) for x in data]
    print("Ping Command : ", data)

    command_ADAPTER_ONE_WIRE_READ_FROM_BB = b'\xAA\x04\x03\x45'
    ser.write(command_ADAPTER_ONE_WIRE_READ_FROM_BB)
    time.sleep(5)

    # readData = ser.read(2)
    # readData = readData + ser.read(readData[1] - 2)
    # readData = [hex(x)[2:].zfill(2) for x in readData]
    # print(" One wie read response ", readData)

    AdapterOnewireFireCount = 0
    AdapterOnewireProcedureCount = 0

    for retry in range(10):
        data = ser.read(2)
        if data[1] != 71:
            ser.read(data[1] - 2)
            print("While retrying  :", data)
            ser.write(command_ADAPTER_ONE_WIRE_READ_FROM_BB)
        else:
            data = data + ser.read(data[1] - 2)
            print(data)
            data = [hex(x)[2:].zfill(2) for x in data]
            print("valid response ", data)
            break

    AdapterOnewireFireCount = (((int(data[10], 16)) * 256) + (int(data[9], 16)))
    AdapterOnewireProcedureCount = (((int(data[14], 16)) * 256) + (int(data[13], 16)))

    return AdapterOnewireFireCount, AdapterOnewireProcedureCount

def read_eeprom_data() -> list:
        # print(simple_colors.yellow(f'command_bytes : {data_bytes}'))
        Enable_OW = b'\xAA\x04\x07\x24'
        # write_1_wire_command_byte = [0xAA, 0x4C, 0x0A]
        read_1_wire_command_byte = [0xAA, 0x0C, 0x0B]
        # In case of 'NACK' we are retrying to get 'ACK' for at max of 5 times
        try:
            with serial.Serial('COM14', 500000) as ser:
                ser.write(Enable_OW)

                for retry in range(5):
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
                        print(f'packet_size: {packet_size}')
                        print(f'read_data: {s}{list(read_data)}')
                        # packet_size = len(list(read_data[1:-1])) / 2
                        print(simple_colors.red("One-Wire is not detected!"))
                        time.sleep(0.5)

                    read_data = ser.read(packet_size - 2)
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

                    print(list(read_data[:64]))
                    # command_list = list(command_bytes)[11:75]
                    # if list(read_data[:64]) == command_list:
                    #     print(simple_colors.green(f"one wire is written successfully with the data! \n{data_bytes}"))
                    #     break
        except serial.SerialException as e:
            print(f"Failed to open port: {e}")


        # serialControl.close_serial_port(ser)
        return list(read_data[:64])


# 0xAA – SIZE – 0x02 – ADDR – DB0 … DBx – CRC

def setAdapterOnewiredata(BlackBoxComPort):
    print(BlackBoxComPort)
    ser = serial.Serial(BlackBoxComPort, 9600, bytesize=8, parity='N', timeout=100, stopbits=1, xonxoff=0)
    ## Sending PING Command Before reading the Onewire data from the Adapter
    command_PING = b'\xAA\x04\x01\xF9'
    ser.write(command_PING)
    time.sleep(.5)
    # ser.reset_input_buffer()
    # print('nothing')

    # for retry in range(5):
    data = ser.read(2)
    data = data + ser.read(data[1] - 2)
    data = [hex(x)[2:].zfill(2) for x in data]
    print("Ping Command : ", data)

    command_ADAPTER_ONE_WIRE_WRITE_FROM_BB = b'\xAA\x04\x02\x45'
    ser.write(command_ADAPTER_ONE_WIRE_WRITE_FROM_BB)
    time.sleep(1)

    readData = ser.read(2)
    readData = readData + ser.read(readData[1] - 2)
    readData = [hex(x)[2:].zfill(2) for x in readData]
    print(" One wie read response ", readData)

    AdapterOnewireFireCount = 0
    AdapterOnewireProcedureCount = 0

    for retry in range(10):
        data = ser.read(2)
        if data[1] != 71:
            ser.read(data[1] - 2)
            print("While retrying  :", data)
            ser.write(command_ADAPTER_ONE_WIRE_WRITE_FROM_BB)
        else:
            data = data + ser.read(data[1] - 2)
            print(data)
            data = [hex(x)[2:].zfill(2) for x in data]
            print("valid response ", data)
            break

    AdapterOnewireFireCount = (((int(data[10], 16)) * 256) + (int(data[9], 16)))
    AdapterOnewireProcedureCount = (((int(data[14], 16)) * 256) + (int(data[13], 16)))

    return AdapterOnewireFireCount, AdapterOnewireProcedureCount


def GetAdapterOnewireRecoveryIdData(BlackBoxComPort):
    ser = serial.Serial(BlackBoxComPort, 9600, bytesize=8, parity='N', timeout=100, stopbits=1, xonxoff=0)
    ## Sending PING Command Before reading the Onewire data from the Onewire EEPROM
    command_PING = b'\xAA\x04\x01\xF9'
    ser.write(command_PING)
    time.sleep(.5)

    data = ser.read(2)
    data = data + ser.read(data[1] - 2)
    data = [hex(x)[2:].zfill(2) for x in data]
    print(data)

    ## Sending Onewire Read Command
    command_ADAPTER_ONE_WIRE_READ_FROM_BB = b'\xAA\x04\x03\x45'
    ser.write(command_ADAPTER_ONE_WIRE_READ_FROM_BB)
    time.sleep(1)

    # readData = ser.read(2)
    # readData = readData + ser.read(readData[1] - 2)
    # readData = [hex(x)[2:].zfill(2) for x in readData]
    # print(" One wire read response ", readData)

    ## Performing five retries until receiving the correct response
    for retry in range(10):
        data = ser.read(2)
        if data[1] != 71:
            ser.read(data[1] - 2)
            print("While retrying  :", data)
            ser.write(command_ADAPTER_ONE_WIRE_READ_FROM_BB)
        else:
            data = data + ser.read(data[1] - 2)
            print(data)
            data = [hex(x)[2:].zfill(2) for x in data]
            print("valid response ", data)
            break
    ## De-serialize the received data for the Recovery ID Data - High Byte, Low Byte
    AdapterRecoveryIdHighByte = int(data[66], 16)
    AdapterRecoveryIdLowByte = int(data[65], 16)

    ## returning the Onewire Adapter Fire and Procedure count
    return AdapterRecoveryIdHighByte, AdapterRecoveryIdLowByte


### Capturing Adapter EEPROM Recovery Data - Returning Adapter Recovery State ID
def GetAdapterEEPROMRecoveryIdData(FtdiComPort):
    ser = serial.Serial(FtdiComPort, 250000, bytesize=8, parity='N', timeout=100, stopbits=1, xonxoff=0)
    ## Sending Boot Exit Command Before reading the Eeprom data from the Adapter
    command_boot_exit = b'\xAA\x05\xE5\x00\x0D'
    ser.write(command_boot_exit)
    time.sleep(.5)
    ser.reset_input_buffer()

    ## Sending Adapter EEPROM Read Data - Page 3 ( Adapter Recovery ID Data )
    command_read_recovery_data_from_eeprom = b'\xAA\x05\xD8\x03\x4B'
    ser.write(command_read_recovery_data_from_eeprom)

    recoveryID = 0

    data = ser.read(2)
    data = data + ser.read(data[1] - 2)
    data = [hex(x)[2:].zfill(2) for x in data]
    # print(data)
    ser.reset_input_buffer()

    # EEA Adapter EEPROM Recovery ID Parameters
    page_no = data[4]
    recovery_id = data[5:7]
    error_code = data[7:9]
    crc_parameter = data[9]

    ## De-serialize the received data for the Recovery ID and Error ID
    recoveryID = convert_single_list_ele_to_two_byte_decimal(recovery_id)
    errorCode = convert_single_list_ele_to_two_byte_decimal(error_code)

    ## returning the Adapter Recovery ID Data
    return recoveryID


def convert_list_to_float(inputList):
    outputList = []
    for i, element in enumerate(inputList):
        singleHexvalue = '0x' + ''.join([format(int(c, 16), '02X') for c in reversed(element)])
        #### Getting Rid of the '0x' Prefix using Slicing
        singleHexvalue = singleHexvalue[2:]
        outputList.append(struct.unpack('!f', bytes.fromhex(singleHexvalue))[0])
    return outputList


def convert_single_list_ele_to_float(s):
    single_hexvalue = '0x' + ''.join([format(int(c, 16), '02X') for c in reversed(s)])
    #### Getting Rid of the '0x' Prefix using Slicing
    # print(singleHexvalue)
    single_hexvalue = single_hexvalue[2:]
    resultf = struct.unpack('!f', bytes.fromhex(single_hexvalue))[0]
    return resultf


def convert_single_list_ele_to_decimal(s):
    single_hex_value = '0x' + ''.join([format(int(c, 16), '02X') for c in reversed(s)])
    #  Getting Rid of the '0x' Prefix using Slicing
    # print("SIngle hex ", single_hex_value)
    single_hex_value = single_hex_value[2:]
    resultd = struct.unpack('!I', bytes.fromhex(single_hex_value))[0]
    return resultd


def convert_single_list_ele_to_ascii(s):
    single_hex_value = '0x' + ''.join([format(int(c, 16), '02X') for c in s])
    # print("single_hex_value", single_hex_value)
    #  Getting Rid of the '0x' Prefix using Slicing
    single_hex_value = single_hex_value[2:]
    # Convert to bytes object.
    bytes_object = bytes.fromhex(single_hex_value)
    # print(bytes_object)
    if bytes_object == b'\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff':
        return
    # Convert to ASCII representation.
    ascii_string = bytes_object.decode("ASCII")
    return ascii_string


def convert_ascii_to_hex(s):
    serialNum = []
    for i in range(len(s)):
        ch = s[i]
        in1 = ord(ch)
        hexNum = hex(in1)
        serialNum.append(hexNum[2:])
    return serialNum


def convert_single_list_ele_to_two_byte_decimal(s):
    single_hex_value = '0x' + ''.join([format(int(c, 16), '02X') for c in reversed(s)])
    #  Getting Rid of the '0x' Prefix using Slicing
    # print(single_hex_value)
    single_hex_value = single_hex_value[2:]
    resultd = struct.unpack('!H', bytes.fromhex(single_hex_value))[0]
    return resultd


def convert_multiple_float_to_hex_value(inputFloat):
    outputHex = []
    for i, element in enumerate(inputFloat):
        outputHex.append(hex(struct.unpack('<I', struct.pack('<f', element))[0]))
    return outputHex


def convert_single_float_to_hex_value(s):
    outputHex = hex(struct.unpack('<I', struct.pack('<f', s))[0])
    return outputHex


def convert_single_byte_to_four_bytes(s):
    return struct.pack('<I', s).hex()


def swapEndianess32(i):
    return struct.unpack("<I", struct.pack(">I", i))[0]


def swapEndianess16(i):
    return struct.unpack("<H", struct.pack(">H", i))[0]
#
#
# # GetAdapterOnewireUsageCounts('COM14')
# adpter_data = read_eeprom_data()
# print(list(map(hex, adpter_data)))
#
# data = [hex(x)[2:].zfill(2) for x in adpter_data]
# print("data ", data)
# read_eeprom_data()
# fireCnt = data[9:11]
# fire1Cnt = data[3:5]
# precCnt = data[7:9]
# AdapterOwFireCount2 = convert_single_list_ele_to_two_byte_decimal(fire1Cnt)
# AdapterOwProcedureCount2 = convert_single_list_ele_to_two_byte_decimal(precCnt)
#
# AdapterEepromProcedureCnt = convert_single_list_ele_to_two_byte_decimal(fireCnt)
# print(AdapterEepromProcedureCnt, AdapterOwFireCount2, AdapterOwProcedureCount2)

# read_and_write_adapter_eeprom_recovery_position_data('COM6')
 #   GetAdapterEepromReco_eeprom_recovery_position_data('COM6')
# GetAdapterEepromRecoveryPositionalData('COM6')
# GetAdapterEepromRecoveryData('COM6')
# GetAdapterEepromRecoveryAdapterData('COM6')

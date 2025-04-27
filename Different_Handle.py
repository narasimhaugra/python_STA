import time

import serial
import serial.tools

oddparity = [0, 1, 1, 0, 1, 0, 0, 1, 1, 0, 0, 1, 0, 1, 1, 0]


def CRC16(crc16In, byte_data):
    # print(f'byte_data: {byte_data}')
    for data in byte_data:
        # data = hex(data)
        # print(data)
        data = (data ^ (crc16In & 0xff))
        crc16In >>= 8

        if (oddparity[data & 0x0f] ^ oddparity[data >> 4]):
            crc16In ^= 0xc001
        data <<= 6
        crc16In ^= data
        data <<= 1
        crc16In ^= data
        # print(crc16In)
        #  crc16In >>= 8
    return (crc16In)


#### CRC 8
def calc(msg):
    check = 0
    for i in msg:
        check = AddToCRC(i, check)
    return hex(check)


def AddToCRC(b, crc):
    if (b < 0):
        b += 256
    for i in range(8):
        odd = ((b ^ crc) & 1) == 1
        crc >>= 1
        b >>= 1
        if (odd):
            crc ^= 0x8C  # this means crc ^= 140
    return crc

def Treating_different_handle(PowerPackComPort):
    for retry in range(5):
        try:
            with serial.Serial(PowerPackComPort, 115200, bytesize=8, parity='N',
                               stopbits=1, timeout=3, xonxoff=False) as serPP:
                command_PING = b'\xAA\x06\x00\x01\x00\x19'
                command_ONEWIRE_GET_CONNECTED = b'\xAA\x06\x00\x45\x00\x2A'
                command_ONEWIRE_GET_ADDRESS = b'\xAA\x07\x00\x46\x00\x2B\x0C'
                command_ONEWIRE_HANDLE_READ = b'\xAA\x07\x00\x49\x00\x2E\xFC'

                command_ONEWIRE_GET_BATTERY_ADDRESS = b'\xAA\x07\x00\x46\x01\xEA\xCC'
                command_ONEWIRE_BATTERY_READ = b'\xAA\x07\x00\x49\x01\xEF\x3C'

                command_ONEWIRE_GET_CLAMSHELL_ADDRESS = b'\xAA\x07\x00\x46\x03\x6B\x0D'
                command_ONEWIRE_CLAMSHELL_READ = b'\xAA\x07\x00\x49\x03\x6E\xFD'


                command_ONEWIRE_CHARGER_READ  = b'\xAA\x07\x00\x49\x06\xAE\xFE'
                # 170 06 00 01 00 25
                # 170 07 00 73 00 46 252
                # 170 07 00 73 01 239 60
                # 170 07 00 73 06 174 254

                serPP.write(command_PING)
                serPP.write(command_ONEWIRE_GET_CONNECTED)
                serPP.write(command_ONEWIRE_GET_ADDRESS)

                print('PING CMD sent', command_PING)
                s = serPP.read(2)
                # print(s, 'Ping S')
                packet_size = s[1]
                read_data = serPP.read(packet_size - 2)
                HandleFireCount = 0
                HandleProcedureCount = 0

                serPP.flush()

                serPP.write(command_PING)
                serPP.write(command_ONEWIRE_GET_CONNECTED)
                serPP.write(command_ONEWIRE_GET_BATTERY_ADDRESS)

                while True:
                    ######################################################################
                    #  BATTERY
                    ######################################################################
                    serPP.write(command_ONEWIRE_BATTERY_READ)
                    s = serPP.readline(2)  ### S[0] - Start Byte, S[1] - Size of the frame
                    packet_size = s[1]
                    read_data = serPP.read(packet_size - 2)
                    # print(read_data, 'read_data')
                    read_data = s + read_data
                    # print(read_data)
                    print("before=======================")
                    print(read_data)
                    if list(read_data)[0] != 0xAA:
                        continue
                    hex_array = list(read_data)
                    print(hex_array)
                    if (hex_array[3] == 73) and (hex_array[4] == 1):
                        hex_array[7] = 1
                        hex_array[8] = 4
                        ## Fire LIMIT
                        hex_array[26] = 0x0F
                        hex_array[27] = 0x27
                        ## Procedure Limit
                        hex_array[30] = 0x0F
                        hex_array[31] = 0x27
                    else:
                        continue
                    byte_data_from_hex = list(hex_array)
                    # Compute CRC for data
                    byte_data_temp1 = byte_data_from_hex[6:]
                    # Get the data bytes excluding the data CRC and the packet CRC which 4 bytes from the end
                    byte_data_temp2 = byte_data_temp1[:-4]
                    print(byte_data_temp2)
                    crc_value = CRC16(0x00, byte_data_temp2)

                    # print(crc_value)
                    crc_value = format(crc_value, '#06X')
                    # print(crc_value)

                    crc_second_byte = crc_value[2:4]
                    crc_first_byte = crc_value[4:]
                    byte_data_temp2.append(int(crc_first_byte, 16))
                    byte_data_temp2.append(int(crc_second_byte, 16))
                    print(byte_data_temp2)
                    # Update the 4th byte to the Write command instead of read command
                    # byte_data_from_hex[3] = 72 ==== WRITE COMMAND
                    # byte_data_final = byte_data_from_hex[:6] + byte_data_temp2
                    # byte_data_final[1] = 71 ==== PAKET SIZE
                    byte_data_final = [170, 71, 0, 72, 1] + byte_data_temp2
                    crc_value = CRC16(0x00, byte_data_final)
                    crc_value = hex(crc_value)
                    l = len(crc_value)
                    if l == 5:
                        crc_value = crc_value[:2] + "0" + crc_value[2:]
                    crc_second_byte = crc_value[2:4]
                    crc_first_byte = crc_value[4:]
                    byte_data_final.append(int(crc_first_byte, 16))
                    byte_data_final.append(int(crc_second_byte, 16))
                    command = bytes(byte_data_final)
                    print("Command : ", command)
                    serPP.write(command)
                    time.sleep(3)
                    print("after =======================")
                    serPP.write(command_ONEWIRE_BATTERY_READ)
                    s = serPP.readline(2)  ### S[0] - Start Byte, S[1] - Size of the frame
                    packet_size = s[1]
                    read_data = serPP.read(packet_size - 2)
                    # print(read_data, 'read_data')
                    read_data = s + read_data
                    # print(read_data)
                    print(read_data)
                    print(list(read_data)[2:])
                    break

                while True:
                    ######################################################################
                    #  HANDLE
                    ######################################################################
                    serPP.write(command_ONEWIRE_HANDLE_READ)
                    s = serPP.readline(2)  ### S[0] - Start Byte, S[1] - Size of the frame
                    packet_size = s[1]
                    read_data = serPP.read(packet_size - 2)
                    # print(read_data, 'read_data')
                    read_data = s + read_data
                    # print(read_data)
                    print("before=======================")
                    print(read_data)
                    if list(read_data)[0] != 0xAA:
                        continue
                    hex_array = list(read_data)
                    print(hex_array)
                    if (hex_array[3] == 73) and (hex_array[4] == 0):
                        hex_array[7] = 2
                        hex_array[8] = 4
                    else:
                        continue
                    byte_data_from_hex = list(hex_array)
                    # Compute CRC for data
                    byte_data_temp1 = byte_data_from_hex[6:]
                    # Get the data bytes excluding the data CRC and the packet CRC which 4 bytes from the end
                    byte_data_temp2 = byte_data_temp1[:-4]
                    print(byte_data_temp2)
                    crc_value = CRC16(0x00, byte_data_temp2)

                    # print(crc_value)
                    crc_value = format(crc_value, '#06X')
                    # print(crc_value)

                    crc_second_byte = crc_value[2:4]
                    crc_first_byte = crc_value[4:]
                    byte_data_temp2.append(int(crc_first_byte, 16))
                    byte_data_temp2.append(int(crc_second_byte, 16))
                    print(byte_data_temp2)
                    # Update the 4th byte to the Write command instead of read command
                    # byte_data_from_hex[3] = 72 ==== WRITE COMMAND
                    # byte_data_final = byte_data_from_hex[:6] + byte_data_temp2
                    # byte_data_final[1] = 71 ==== PAKET SIZE
                    byte_data_final = [170, 71, 0, 72, 0] + byte_data_temp2
                    crc_value = CRC16(0x00, byte_data_final)
                    crc_value = hex(crc_value)
                    l = len(crc_value)
                    if l == 5:
                        crc_value = crc_value[:2] + "0" + crc_value[2:]
                    crc_second_byte = crc_value[2:4]
                    crc_first_byte = crc_value[4:]
                    byte_data_final.append(int(crc_first_byte, 16))
                    byte_data_final.append(int(crc_second_byte, 16))
                    command = bytes(byte_data_final)

                    serPP.write(command)
                    time.sleep(3)
                    print("after =======================")
                    serPP.write(command_ONEWIRE_HANDLE_READ)
                    s = serPP.readline(2)  ### S[0] - Start Byte, S[1] - Size of the frame
                    packet_size = s[1]
                    read_data = serPP.read(packet_size - 2)
                    # print(read_data, 'read_data')
                    read_data = s + read_data
                    # print(read_data)
                    print(read_data)
                    print(list(read_data)[2:])
                    break
        except Exception as ex:
            print(f"Exception Occurred : {ex}")

# Treating_different_handle('COM19')
import serial
from CRC16 import CRC16
from CRC16 import calc


def EndOfLifeSet(component, ItemForEOL):
        serPP = serial.Serial('COM4', 115200, bytesize=8, parity='N', stopbits=1, timeout=3, xonxoff=0)
        command_PING = b'\xAA\x06\x00\x01\x00\x19'
        command_ONEWIRE_GET_CONNECTED = b'\xAA\x06\x00\x45\x00\x2A'

        command_ONEWIRE_GET_ADDRESS_ADAPTER = b'\xAA\x07\x00\x46\x03\x6B\x0D'
        command_ONEWIRE_READ_ADAPTER = b'\xAA\x07\x00\x49\x03\x6E\xFD'

        command_ONEWIRE_GET_ADDRESS_HANDLE = b'\xAA\x07\x00\x46\x00\x2B\x0C'
        command_ONEWIRE_READ_HANDLE = b'\xAA\x07\x00\x49\x00\x2E\xFC'

        command_ONEWIRE_GET_ADDRESS_CLAMSHELL = b'\xAA\x07\x00\x46\x02\xAA\xCD'
        command_ONEWIRE_READ_CLAMSHELL = b'\xAA\x07\x00\x49\x02\xAF\x3D'

        command_ONEWIRE_GET_ADDRESS_RELOAD = b'\xAA\x07\x00\x46\x04\x2A\xCF'
        command_ONEWIRE_READ_RELOAD = b'\xAA\x07\x00\x49\x04\x2F\x3F'

        serPP.write(command_PING)
        serPP.write(command_ONEWIRE_GET_CONNECTED)
        if component == "Adapter":
            for s in range(0, 20):
                    serPP.write(command_ONEWIRE_READ_ADAPTER)
                    s = serPP.readline(2)
                    packet_size = s[1]
                    read_data = serPP.read(packet_size - 2)
                    # print(read_data, 'read_data')
                    read_data = s + read_data
                    hex_array = [hex(x)[2:] for x in read_data]
                    if ((int(hex_array[3], 16) == 73) and (int(hex_array[4], 16) == 3)):
                        if ItemForEOL == "NoProcedureRem":
                            # setting procedure count = procedure limit
                            hex_array[13] = hex_array[15]
                            hex_array[14] = hex_array[16]
                        elif ItemForEOL == "NoFireRem":
                            # setting fire count = fire limit
                            hex_array[9] = hex_array[11]
                            hex_array[10] = hex_array[12]
                        byte_data_from_hex = [int(j,16) for j in hex_array]
                        # Compute CRC for data
                        byte_data_temp1 = byte_data_from_hex[6:]
                        # Get the data bytes excluding the data CRC and the packet CRC which 4 bytes from the end
                        byte_data_temp2 = byte_data_temp1[:-4]
                        crc_value = CRC16(0x00, byte_data_temp2)
                        crc_value = hex(crc_value)
                        l = len(crc_value)
                        crc_second_byte = crc_value[2:(l - 2)]
                        crc_first_byte = crc_value[(l - 2):]
                        byte_data_temp2.append(int(crc_first_byte, 16))
                        byte_data_temp2.append(int(crc_second_byte, 16))
                        # Update the 4th byte to the Write command instead of read command
                        # byte_data_from_hex[3] = 72
                        # byte_data_final = byte_data_from_hex[:6] + byte_data_temp2
                        # byte_data_final[1] = 71
                        byte_data_final= [170, 71, 0, 72, 3] + byte_data_temp2
                        crc_value = CRC16(0x00, byte_data_final)
                        crc_value = hex(crc_value)
                        l = len(crc_value)
                        crc_second_byte = crc_value[2:(l - 2)]
                        crc_first_byte = crc_value[(l - 2):]
                        byte_data_final.append(int(crc_first_byte, 16))
                        byte_data_final.append(int(crc_second_byte, 16))
                        #print(byte_data_final)
                        #print(len(byte_data_final))
                        command = bytes(byte_data_final)
                        #print('final bytes are', command)
                        #swrite data to Adapter
                        serPP.write(command)
                        return 'End of Life set for Handle'
                    break

        elif component == "Handle":
            for s in range(0, 20):
                    serPP.write(command_ONEWIRE_READ_HANDLE)
                    s = serPP.readline(2)
                    packet_size = s[1]
                    read_data = serPP.read(packet_size - 2)
                    # print(read_data, 'read_data')
                    read_data = s + read_data
                    #print(read_data)
                    hex_array = [hex(x)[2:] for x in read_data]
                    print (hex_array)
                    if ((int(hex_array[3], 16) == 73) and (int(hex_array[4], 16) == 0)):
                        if ItemForEOL == "NoProcedureRem":
                            # setting procedure count = procedure limit
                            hex_array[28] = hex_array[30]
                            hex_array[29] = hex_array[31]
                        elif ItemForEOL == "ZeroProcedureLimit":
                            hex_array[30] = hex(0)
                            hex_array[31] = hex(0)
                        elif ItemForEOL == "NoFireRem":
                            # setting fire count = fire limit
                            hex_array[24] = hex_array[26]
                            hex_array[25] = hex_array[27]
                        elif ItemForEOL == "ZeroFireLimit":
                            hex_array[26] = hex(0)
                            hex_array[27] = hex(0)
                        byte_data_from_hex = [int(j,16) for j in hex_array]
                        # Compute CRC for data
                        byte_data_temp1 = byte_data_from_hex[6:]
                        # Get the data bytes excluding the data CRC and the packet CRC which 4 bytes from the end
                        byte_data_temp2 = byte_data_temp1[:-4]
                        crc_value = CRC16(0x00, byte_data_temp2)
                        crc_value = hex(crc_value)
                        l = len(crc_value)
                        crc_second_byte = crc_value[2:(l - 2)]
                        crc_first_byte = crc_value[(l - 2):]
                        byte_data_temp2.append(int(crc_first_byte, 16))
                        byte_data_temp2.append(int(crc_second_byte, 16))
                        # Update the 4th byte to the Write command instead of read command
                        # byte_data_from_hex[3] = 72
                        # byte_data_final = byte_data_from_hex[:6] + byte_data_temp2
                        # byte_data_final[1] = 71
                        byte_data_final = [170, 71, 0, 72, 0] + byte_data_temp2
                        crc_value = CRC16(0x00, byte_data_final)
                        crc_value = hex(crc_value)
                        l = len(crc_value)
                        crc_second_byte = crc_value[2:(l - 2)]
                        crc_first_byte = crc_value[(l - 2):]
                        byte_data_final.append(int(crc_first_byte, 16))
                        byte_data_final.append(int(crc_second_byte, 16))
                        command = bytes(byte_data_final)
                        #print('final bytes are', command)
                        serPP.write(command)
                    break
        elif component == "Clamshell":
            # Get the Clamshell data
            for s in range(0, 20):
                serPP.write(command_ONEWIRE_READ_CLAMSHELL)
                s = serPP.readline(2)
                packet_size = s[1]
                read_data = serPP.read(packet_size - 2)
                read_data = s + read_data
                hex_array = [hex(x)[2:] for x in read_data]
                if ((int(hex_array[3], 16) == 73) and (int(hex_array[4], 16) == 2)):
                        byte_data_from_hex = [int(j, 16) for j in hex_array]
                        # Change the Handle address in the clamshell 1wire by updating just one byte
                        byte_data_from_hex[34] = byte_data_from_hex[34]+1
                        # Compute CRC for data
                        byte_data_temp1 = byte_data_from_hex[6:]
                        # Get the data bytes excluding the data CRC and the packet CRC which 4 bytes from the end
                        byte_data_temp2 = byte_data_temp1[:-4]
                        crc_value = CRC16(0x00, byte_data_temp2)
                        crc_value = hex(crc_value)
                        l = len(crc_value)
                        crc_second_byte = crc_value[2:(l - 2)]
                        crc_first_byte = crc_value[(l - 2):]
                        byte_data_temp2.append(int(crc_first_byte, 16))
                        byte_data_temp2.append(int(crc_second_byte, 16))
                        byte_data_final = [170, 71, 0, 72, 2] + byte_data_temp2
                        #print(byte_data_final)
                        crc_value = CRC16(0x00, byte_data_final)
                        crc_value = hex(crc_value)
                        l = len(crc_value)
                        crc_second_byte = crc_value[2:(l - 2)]
                        crc_first_byte = crc_value[(l - 2):]
                        byte_data_final.append(int(crc_first_byte, 16))
                        byte_data_final.append(int(crc_second_byte, 16))
                        command = bytes(byte_data_final)
                        serPP.write(command)
                        break

        elif component == "MULUReload":
            for s in range(0, 20):
                serPP.write(command_ONEWIRE_READ_RELOAD)
                s = serPP.readline(2)
                packet_size = s[1]
                read_data = serPP.read(packet_size - 2)
                read_data = s + read_data
                hex_array = [hex(x)[2:] for x in read_data]
                if ((int(hex_array[1], 16) == 72) and (int(hex_array[3], 16) == 73) and (int(hex_array[4], 16) == 4) and (int(hex_array[8], 16)==16)):
                    byte_data_from_hex = [int(j, 16) for j in hex_array]
                    # Change the Fire count to Fire limit(12)
                    byte_data_from_hex[24] = 12
                    # Compute CRC for datas
                    byte_data_temp1 = byte_data_from_hex[6:]
                    # Get the data bytes excluding the data CRC and the packet CRC which 4 bytes from the end
                    byte_data_temp2 = byte_data_temp1[:-4]
                    crc_value = CRC16(0x00, byte_data_temp2)
                    crc_value = hex(crc_value)
                    l = len(crc_value)
                    crc_second_byte = crc_value[2:(l - 2)]
                    crc_first_byte = crc_value[(l - 2):]
                    byte_data_temp2.append(int(crc_first_byte, 16))
                    byte_data_temp2.append(int(crc_second_byte, 16))
                    byte_data_final = [170, 71, 0, 72, 4] + byte_data_temp2
                    crc_value = CRC16(0x00, byte_data_final)
                    crc_value = hex(crc_value)
                    l = len(crc_value)
                    crc_second_byte = crc_value[2:(l - 2)]
                    crc_first_byte = crc_value[(l - 2):]
                    byte_data_final.append(int(crc_first_byte, 16))
                    byte_data_final.append(int(crc_second_byte, 16))
                    final_data = [hex(j)[2:] for j in byte_data_final]
                    #print(final_data)
                    command = bytes(byte_data_final)
                    #print(command)
                    serPP.write(command)
                    break

        elif component == "SULUReload":
            for s in range(0, 20):
                serPP.write(command_ONEWIRE_READ_RELOAD)
                s = serPP.readline(2)
                packet_size = s[1]
                read_data = serPP.read(packet_size - 2)
                read_data = s + read_data
                hex_array = [hex(x)[2:] for x in read_data]
                if ((int(hex_array[1], 16) == 72) and (int(hex_array[3], 16) == 73) and (
                        int(hex_array[4], 16) == 4) and (int(hex_array[8], 16) == 12)):
                    byte_data_from_hex = [int(j, 16) for j in hex_array]
                    # Change the Fire count to Fire limit(12)
                    byte_data_from_hex[24] = 1
                    # Compute CRC for datas
                    byte_data_temp1 = byte_data_from_hex[6:]
                    # Get the data bytes excluding the data CRC and the packet CRC which 4 bytes from the end
                    byte_data_temp2 = byte_data_temp1[:-4]
                    crc_value = CRC16(0x00, byte_data_temp2)
                    crc_value = hex(crc_value)
                    l = len(crc_value)
                    crc_second_byte = crc_value[2:(l - 2)]
                    crc_first_byte = crc_value[(l - 2):]
                    byte_data_temp2.append(int(crc_first_byte, 16))
                    byte_data_temp2.append(int(crc_second_byte, 16))
                    byte_data_final = [170, 71, 0, 72, 4] + byte_data_temp2
                    crc_value = CRC16(0x00, byte_data_final)
                    crc_value = hex(crc_value)
                    l = len(crc_value)
                    crc_second_byte = crc_value[2:(l - 2)]
                    crc_first_byte = crc_value[(l - 2):]
                    byte_data_final.append(int(crc_first_byte, 16))
                    byte_data_final.append(int(crc_second_byte, 16))
                    final_data = [hex(j)[2:] for j in byte_data_final]
                    #print(final_data)
                    command = bytes(byte_data_final)
                    # print(command)
                    serPP.write(command)
                    break


def EndOfLifeClear(component):
    serPP = serial.Serial('COM4', 115200, bytesize=8, parity='N', stopbits=1, timeout=3, xonxoff=0)
    command_PING = b'\xAA\x06\x00\x01\x00\x19'
    command_ONEWIRE_GET_CONNECTED = b'\xAA\x06\x00\x45\x00\x2A'

    command_ONEWIRE_GET_ADDRESS_ADAPTER = b'\xAA\x07\x00\x46\x03\x6B\x0D'
    command_ONEWIRE_READ_ADAPTER = b'\xAA\x07\x00\x49\x03\x6E\xFD'

    command_ONEWIRE_GET_ADDRESS_HANDLE = b'\xAA\x07\x00\x46\x00\x2B\x0C'
    command_ONEWIRE_READ_HANDLE = b'\xAA\x07\x00\x49\x00\x2E\xFC'

    command_ONEWIRE_GET_ADDRESS_CLAMSHELL = b'\xAA\x07\x00\x46\x02\xAA\xCD'
    command_ONEWIRE_READ_CLAMSHELL: bytes = b'\xAA\x07\x00\x49\x02\xAF\x3D'

    command_ONEWIRE_GET_ADDRESS_RELOAD = b'\xAA\x07\x00\x46\x04\x2A\xCF'
    command_ONEWIRE_READ_RELOAD = b'\xAA\x07\x00\x49\x04\x2F\x3F'

    serPP.write(command_PING)
    serPP.write(command_ONEWIRE_GET_CONNECTED)
    if component == "Adapter":
        for s in range(0, 20):
            serPP.write(command_ONEWIRE_READ_ADAPTER)
            s = serPP.readline(2)
            packet_size = s[1]
            read_data = serPP.read(packet_size - 2)
            # print(read_data, 'read_data')
            read_data = s + read_data
            hex_array = [hex(x)[2:] for x in read_data]
            if ((int(hex_array[3], 16) == 73) and (int(hex_array[4], 16) == 3)):
                # setting procedure count = 0
                hex_array[13] = hex[0]
                hex_array[14] = hex[0]
                # setting fire count = 0
                hex_array[9] = hex[0]
                hex_array[10] = hex[0]
                byte_data_from_hex = [int(j, 16) for j in hex_array]
                # Compute CRC for data
                byte_data_temp1 = byte_data_from_hex[6:]
                # Get the data bytes excluding the data CRC and the packet CRC which 4 bytes from the end
                byte_data_temp2 = byte_data_temp1[:-4]
                crc_value = CRC16(0x00, byte_data_temp2)
                crc_value = hex(crc_value)
                l = len(crc_value)
                crc_second_byte = crc_value[2:(l - 2)]
                crc_first_byte = crc_value[(l - 2):]
                byte_data_temp2.append(int(crc_first_byte, 16))
                byte_data_temp2.append(int(crc_second_byte, 16))
                # Update the 4th byte to the Write command instead of read command
                # byte_data_from_hex[3] = 72
                # byte_data_final = byte_data_from_hex[:6] + byte_data_temp2
                # byte_data_final[1] = 71
                byte_data_final = [170, 71, 0, 72, 3] + byte_data_temp2
                crc_value = CRC16(0x00, byte_data_final)
                crc_value = hex(crc_value)
                l = len(crc_value)
                crc_second_byte = crc_value[2:(l - 2)]
                crc_first_byte = crc_value[(l - 2):]
                byte_data_final.append(int(crc_first_byte, 16))
                byte_data_final.append(int(crc_second_byte, 16))
                #print(byte_data_final)
                #print(len(byte_data_final))
                command = bytes(byte_data_final)
                #print('final bytes are', command)
                # swrite data to Adapter
                serPP.write(command)
            break

    elif component == "Handle":
        for s in range(0, 20):
            serPP.write(command_ONEWIRE_READ_HANDLE)
            s = serPP.readline(2)
            packet_size = s[1]
            read_data = serPP.read(packet_size - 2)
            read_data = s + read_data
            hex_array = [hex(x)[2:] for x in read_data]
            if ((int(hex_array[3], 16) == 73) and (int(hex_array[4], 16) == 0)):
                # setting procedure count = 0
                hex_array[28] = hex(0)
                hex_array[29] = hex(0)
                # Setting procedure limit to default value
                hex_array[30] = '14'
                hex_array[31] = '0'
                # setting fire count = 0
                hex_array[24] = hex(0)
                hex_array[25] = hex(0)
                # Setting Fire Limit to default value
                hex_array[26] = 'C8'
                hex_array[27] = '0'
                byte_data_from_hex = [int(j, 16) for j in hex_array]
                # Compute CRC for data
                byte_data_temp1 = byte_data_from_hex[6:]
                # Get the data bytes excluding the data CRC and the packet CRC which 4 bytes from the end
                byte_data_temp2 = byte_data_temp1[:-4]
                crc_value = CRC16(0x00, byte_data_temp2)
                crc_value = hex(crc_value)
                l = len(crc_value)
                crc_second_byte = crc_value[2:(l - 2)]
                crc_first_byte = crc_value[(l - 2):]
                byte_data_temp2.append(int(crc_first_byte, 16))
                byte_data_temp2.append(int(crc_second_byte, 16))
                byte_data_final = [170, 71, 0, 72, 0] + byte_data_temp2
                crc_value = CRC16(0x00, byte_data_final)
                crc_value = hex(crc_value)
                l = len(crc_value)
                crc_second_byte = crc_value[2:(l - 2)]
                crc_first_byte = crc_value[(l - 2):]
                byte_data_final.append(int(crc_first_byte, 16))
                byte_data_final.append(int(crc_second_byte, 16))
                command = bytes(byte_data_final)
                #print('final bytes are', command)
                serPP.write(command)
            break
    elif component == "Clamshell":
        # NEED TO UPDATE THIS
        # Get the Clamshell data
        byte_data = [2, 3, 4, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                     0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        crc_value = CRC16(0x00, byte_data)
        crc_value = hex(crc_value)
        l = len(crc_value)
        crc_second_byte = crc_value[2:(l - 2)]
        crc_first_byte = crc_value[(l - 2):]
        byte_data.append(int(crc_first_byte, 16))
        byte_data.append(int(crc_second_byte, 16))
        byte_lst = [170, 69, 2, 1] + byte_data
        # print(byte_lst)
        crc_value = calc(bytes(byte_lst))
        crc_value = int(crc_value, 16)
        byte_lst.append(crc_value)
        command_byte = (byte_lst)
        serialControlObj.Switch_ONN_Relay(5, 1)  # B5:R1 - ON
        serialControlObj.Switch_ONN_Relay(5, 5)  # B5:R1 - ON
        ser = serial.Serial(serialControlObj.BlackBoxComPort, 9600)
        serialControlObj.wait(5)
        ############# READ ###################
        command = bytes(command_byte)
        print('Clamshell ResetByte array', command)
        serPP.write(command)
        serialControlObj.Switch_OFF_Relay(5, 1)  # B5:R1 - OFF
        serialControlObj.Switch_OFF_Relay(5, 5)  # B5:R1 - OFF

    elif component == "MULUReload":
        #print('in the mulureload segement')
        for s in range(0, 20):
            serPP.write(command_ONEWIRE_READ_RELOAD)
            s = serPP.readline(2)
            packet_size = s[1]
            read_data = serPP.read(packet_size - 2)
            read_data = s + read_data
            hex_array = [hex(x)[2:] for x in read_data]
            if ((int(hex_array[1], 16) == 72) and (int(hex_array[3], 16) == 73) and (int(hex_array[4], 16) == 4) and (
                    int(hex_array[8], 16) == 16)):
                byte_data_from_hex = [int(j, 16) for j in hex_array]
                # Change the Fire count to Fire limit(12)
                byte_data_from_hex[24] = 0
                # Compute CRC for datas
                byte_data_temp1 = byte_data_from_hex[6:]
                # Get the data bytes excluding the data CRC and the packet CRC which 4 bytes from the end
                byte_data_temp2 = byte_data_temp1[:-4]
                crc_value = CRC16(0x00, byte_data_temp2)
                crc_value = hex(crc_value)
                l = len(crc_value)
                crc_second_byte = crc_value[2:(l - 2)]
                crc_first_byte = crc_value[(l - 2):]
                byte_data_temp2.append(int(crc_first_byte, 16))
                byte_data_temp2.append(int(crc_second_byte, 16))
                byte_data_final = [170, 71, 0, 72, 4] + byte_data_temp2
                crc_value = CRC16(0x00, byte_data_final)
                crc_value = hex(crc_value)
                l = len(crc_value)
                crc_second_byte = crc_value[2:(l - 2)]
                crc_first_byte = crc_value[(l - 2):]
                byte_data_final.append(int(crc_first_byte, 16))
                byte_data_final.append(int(crc_second_byte, 16))
                final_data = [hex(j)[2:] for j in byte_data_final]
                print(final_data)
                command = bytes(byte_data_final)
                # print(command)
                serPP.write(command)
                break

    elif component == "SULUReload":
        for s in range(0, 20):
            serPP.write(command_ONEWIRE_READ_RELOAD)
            s = serPP.readline(2)
            packet_size = s[1]
            read_data = serPP.read(packet_size - 2)
            read_data = s + read_data
            hex_array = [hex(x)[2:] for x in read_data]
            if ((int(hex_array[1], 16) == 72) and (int(hex_array[3], 16) == 73) and (
                    int(hex_array[4], 16) == 4) and (int(hex_array[8], 16) == 12)):
                byte_data_from_hex = [int(j, 16) for j in hex_array]
                # Change the Fire count to Fire limit(12)
                byte_data_from_hex[24] = 0
                # Compute CRC for datas
                byte_data_temp1 = byte_data_from_hex[6:]
                # Get the data bytes excluding the data CRC and the packet CRC which 4 bytes from the end
                byte_data_temp2 = byte_data_temp1[:-4]
                crc_value = CRC16(0x00, byte_data_temp2)
                crc_value = hex(crc_value)
                l = len(crc_value)
                crc_second_byte = crc_value[2:(l - 2)]
                crc_first_byte = crc_value[(l - 2):]
                byte_data_temp2.append(int(crc_first_byte, 16))
                byte_data_temp2.append(int(crc_second_byte, 16))
                byte_data_final = [170, 71, 0, 72, 4] + byte_data_temp2
                crc_value = CRC16(0x00, byte_data_final)
                crc_value = hex(crc_value)
                l = len(crc_value)
                crc_second_byte = crc_value[2:(l - 2)]
                crc_first_byte = crc_value[(l - 2):]
                byte_data_final.append(int(crc_first_byte, 16))
                byte_data_final.append(int(crc_second_byte, 16))
                final_data = [hex(j)[2:] for j in byte_data_final]
                print(final_data)
                command = bytes(byte_data_final)
                # print(command)
                serPP.write(command)
                break

    # elif component == "SULUReload"

EndOfLifeClear('Handle')
    #elif ItemForEOL == 'NoFiringsRem':

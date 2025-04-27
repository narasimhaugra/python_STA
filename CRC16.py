oddparity = [0, 1, 1, 0, 1, 0, 0, 1, 1, 0, 0, 1, 0, 1, 1, 0]

def CRC16(crc16In, byte_data):
    for data in byte_data:
        # data = hex(data)
        # print(data)
        data = (data ^ (crc16In & 0xff))
        crc16In >>= 8

        if oddparity[data & 0x0f] ^ oddparity[data >> 4]:
            crc16In ^= 0xc001
        data <<= 6
        crc16In ^= data
        data <<= 1
        crc16In ^= data
    #print(crc16In)
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


def fetch_command(prefix_list, data_byte, fixtureValidationReq=False):
    # if the data_bytes length is 62 then calculate and append the data CRC of 2 bytes
    if len(data_byte) == 62:
        crc_value = CRC16(0x00, data_byte)
        # This is to produce 2 bytes of hexadecimal representation of the given number. including '0X', which is prefixing
        # before the hexadecimal representation, the total length is 6. Hence, '#06X' is given. It represents the total
        # length of the hexadecimal.
        crc_value = format(crc_value, '#06X')
        # print('Original CRC: ', crc_value)
        crc_length = len(crc_value)
        crc_second_byte = crc_value[2:(crc_length - 2)]
        crc_first_byte = crc_value[(crc_length - 2):]

        data_byte.append(int(crc_first_byte, 16))
        data_byte.append(int(crc_second_byte, 16))

    byte_lst = prefix_list + data_byte
    # print(byte_lst)
    crc_value = calc(bytes(byte_lst))
    crc_value = int(crc_value, 16)
    byte_lst.append(crc_value)
    if fixtureValidationReq:
        pass
    else:
        print(byte_lst)
    command = bytes(byte_lst)
    return command

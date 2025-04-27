from datetime import datetime as dt

#crc_value: int
now = dt.now()
print('time', now)
current_time = now.strftime("%Y-%m-%d %H:%M:%S")
print(current_time)
# time.sleep(2)
# later = dt.now()
# print('time', now)
# current_time = now.strftime("%Y:%m:%d:%H:%M:%S")
# print(current_time)

# Python's program to calculate time difference between two datetime objects.
#
import datetime

oddparity = [0, 1, 1, 0, 1, 0, 0, 1, 1, 0, 0, 1, 0, 1, 1, 0]

def CRC16(crc16In, byte_data):
    for data in byte_data:
        # data = hex(data)
        # print(data)
        data = (data ^ (crc16In & 0xff)) & 0xff
        crc16In >>= 8

        if (oddparity[data & 0x0f] ^ oddparity[data >> 4]):
            crc16In ^= 0xc001
        data <<= 6
        crc16In ^= data
        data <<= 1
        crc16In ^= data
    #print(crc16In)
    
    return (crc16In)

datetimeFormat = '%Y-%m-%d %H:%M:%S'
date1 = current_time
date2 = '1970-01-01 00:00:00'
diff = datetime.datetime.strptime(date1, datetimeFormat) \
       - datetime.datetime.strptime(date2, datetimeFormat)

print("Difference:", diff)
print("Difference:", diff.total_seconds())
time_diff_IST = diff.total_seconds()
time_diff_UTC = time_diff_IST -19800
print("Time in Sec Since 1970:", time_diff_UTC)
# print("Microseconds:", diff.microseconds)
# print("Seconds:", diff.seconds)
time_diff_UTC_hex = hex(int(time_diff_UTC))[2:]
tv1 = time_diff_UTC_hex[0:2]
tv2 = time_diff_UTC_hex[2:4]
tv3 = time_diff_UTC_hex[4:6]
tv4 = time_diff_UTC_hex[6:8]
print(time_diff_UTC_hex)
print('tv1', tv1)
print('tv2', tv2)
print('tv3', tv3)
print('tv4', tv4)


tv1 = int(tv1, 16)
tv2 = int(tv2, 16)
tv3 = int(tv3, 16)
tv4 = int(tv4, 16)


print('tv1', tv1)
print('tv2', tv2)
print('tv3', tv3)
print('tv4', tv4)

byte_data = [170, 10, 0, 92, tv4, tv3, tv2, tv1]
#byte_data = [170, 10, 0, 92, 120, 11, 110, 96]
# byte_data1 = [0xAA]
# byte_data2 = [0x0A, 0x00]
# byte_data3 = [0x5C]
# byte_data4 = [0xB2, 0xB2, 0x6D, 0x60]


print('byte_date', byte_data)
# hex_array = [hex(x)[2:] for x in byte_data]
#print(hex_array)
#print(command_byte) AA 0A 00 5C 0F 87 6D 60 FA 4D       AA 0A 00 5C CB 86 6D 60 96 BD



crc_value = CRC16(0x00, byte_data)
print('Original CRC1: ', crc_value)
crc_value = hex(crc_value)
print(crc_value)
#

crc_second_byte = crc_value[2:4]
crc_first_byte = crc_value[4:]
print(crc_first_byte)
print(crc_second_byte)

byte_data.append(int(crc_first_byte, 16))
byte_data.append(int(crc_second_byte, 16))
print(byte_data)
SET_RTC = bytearray(byte_data)
# crc_value = CRC16(crc_value, byte_data2)
# #crc_value = hex(crc_value)
# print('Original CRC2: ', crc_value)

# crc_value = CRC16(crc_value, byte_data3)
# #crc_value = hex(crc_value)
# print('Original CRC3: ', crc_value)
#
# crc_value = CRC16(crc_value, byte_data4)
# #crc_value = hex(crc_value)
# print('Final CRC4: ', crc_value)
#
# print('Hex_CRC', hex(crc_value))




# crc_second_byte = crc_value[2:4]
# crc_first_byte = crc_value[4:]
# print('crc_first_byte', crc_first_byte)
# print('crc_second_byte',crc_second_byte)
# byte_data.append(int(crc_first_byte, 16))
# byte_data.append(int(crc_second_byte, 16))
#
# print(byte_data)
# print(bytearray(byte_data))

#AA 0A 00 5C 98 8C 6D 60 A7 FB

import time

import serial

#  ping, enum, set rtc, get rtc, get serial number, get harware version, get parameters, reset
ser = serial.Serial("COM5", 115200, bytesize=8, parity='N', stopbits=1, timeout=None, xonxoff=0)

print("Buffer cleared")
serial.Serial()
ser.flush()
time.sleep(2)

command_PING = b'\xAA\x06\x00\x01\x00\x19'
STATUS_START = b'\xAA\x06\x00\x31\x00\x0D'
STATUS_RATE = b'\xAA\x0A\x00\x2F\xFA\x00\x00\x00\xC5\x19'

ser.write(command_PING)
#print('PING CMD sent', command_PING)
s = ser.read(2)
#print(s, 'Ping S')
packet_size = s[1]
read_data = ser.read(packet_size - 2)
read_data = s + read_data
#print(read_data, 'read_data ping data')


statusListdata = []


ser.flush()

ser.write(STATUS_START)

for s in range (0,10):
    try:
        s = ser.read(2)
        packet_size = s[1]
        read_data = ser.read(packet_size - 2)
        #print(read_data, 'read_data')
        read_data = s+read_data
        hex_array = [hex(x)[2:] for x in read_data]
        #print('Battery_data', hex_array)
        # print(int(hex_array[1], 16), int(hex_array[2], 16))

        if ((int(hex_array[1], 16) == 71) and (int(hex_array[3], 16) == 48)):
            statusListdata = hex_array
            break
        elif ((int(hex_array[1], 16) == 7) and (int(hex_array[3], 16) == 1) and (int(hex_array[5], 16) == 0xD8) and (int(hex_array[6], 16) == 0xFA)):
            s = ser.read(2)

            packet_size = s[1]
            read_data = ser.read(packet_size - 2)
            #print(read_data, 'read_data')
            read_data = s + read_data
            hex_array = [hex(x)[2:] for x in read_data]
            if ((int(hex_array[1], 16) == 71) and (int(hex_array[3], 16) == 48)):
                statusListdata = hex_array

        elif ((int(hex_array[1], 16) == 0x0A) and (int(hex_array[3], 16) == 0x44)):
            s = ser.read(2)

            packet_size = s[1]
            read_data = ser.read(packet_size - 2)
            #print(read_data, 'read_data')
            read_data = s + read_data
            hex_array = [hex(x)[2:] for x in read_data]
            if ((int(hex_array[1], 16) == 71) and (int(hex_array[3], 16) == 48)):
                statusListdata = hex_array
# AA 0A 00 44 FA 00 00 00 C5 19
    except:  statusListdata = 'None'
#     pass
ser.close()
print(statusListdata)

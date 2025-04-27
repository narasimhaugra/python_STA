#AA 0A 00 27 64 00 00 00 0B 30
#AA 07 00 75 01 FE 3C

import serial
import time
from datetime import datetime
import struct
import csv
now = datetime.now()
print('time', now)

#  ping, enum, set rtc, get rtc, get serial number, get harware version, get parameters, reset
ser = serial.Serial("COM5", 115200, bytesize=8, parity='N', stopbits=1, timeout=None, xonxoff=0)


now = datetime.now()
# Serial = "N"
# Serial.stopbits = 1
# Serial.xonxoff = 0
# Serial.timeout = 3
ser.flush()
print("Buffer cleared")
serial.Serial()

command_PING = b'\xAA\x06\x00\x01\x00\x19'
command_ENUM = b'\xAA\x06\x00\x02\x40\x18'
STATUS_START = b'\xAA\x06\x00\x31\x00\x0D'
STATUS_RATE = b'\xAA\x0A\x00\x2F\xFA\x00\x00\x00\xC5\x19'
STREAM_STRAINGAUGE = b'\xAA\x06\x00\x0F\x81\xDD'
STREAMING_RATE = b'\xAA\x0A\x00\x27\x64\x00\x00\x00\x0B\x30'
STRAINGAUGE = b'\xAA\x07\x00\x75\x01\xFE\x3C'

myrows = [0,0]
ser.write(command_PING)
print('PING CMD sent', command_PING)
command = [hex(x)[2:] for x in command_PING]
print('first SET RTC cmd sent in hex ', command)
s = ser.read(2)
s = list(s)
packet_size = s[1]
read_data = ser.read(packet_size - 2)
read_data = list(read_data)
read_data = s + read_data
print("==== READ DATA ====")
print(read_data)
print(bytearray(read_data))


ser.write(STREAMING_RATE)
time.sleep(1)
s = ser.read(2)
s = list(s)
packet_size = s[1]
read_data = ser.read(packet_size - 2)
read_data = list(read_data)
read_data = s + read_data
print("==== READ DATA ====")
print(read_data)
print(bytearray(read_data))
print('s', s)
time.sleep(.5)



# ser.write(STRAINGAUGE)
# s = ser.read(2)
# s = list(s)
# packet_size = s[1]
# read_data = ser.read(packet_size - 2)
# read_data = list(read_data)
# read_data = s + read_data
# print("==== READ DATA ====")
# print(read_data)
# print(bytearray(read_data))
count = 0
mycsvfile = open("Log.csv", 'w')

csvwriter = csv.writer(mycsvfile)
newrows = ["Time", "StrainGauge(lbs)"]
csvwriter.writerow(newrows)

while (True):
    ser.write(STRAINGAUGE)

    time.sleep(.01)
    #ser.flush()
    #time.sleep(.5)

    #time.sleep(.25)
    read_data = []
    s = ser.read(2)
    s = list(s)
    packet_size = s[1]
    read_data = ser.read(packet_size - 2)
    read_data = list(read_data)
    read_data = s + read_data
    # print("==== READ DATA ====")
    # print(read_data)
    ser.flush()
    mystr = ''

    if (len(read_data) >= 3) and read_data[3] == 117 and read_data[1] == 0x0C:

        mystr = mystr + format(read_data[9], '#04x')
        print(mystr)
        mystr = mystr + format(read_data[8], '#04x')
        print(mystr)
        mystr = mystr + format(read_data[7], '#04x')
        print(mystr)
        mystr = mystr + format(read_data[6], '#04x')
        print('mystr', mystr)
        #for i in mystr:
        #    finstr += i
        mystr = mystr.replace('0x', '')
        #finstr = mystr
        print('mystr', mystr)
        #Finalstring = mystr[0].replace('0x', '')+mystr[1].replace('0x', '')+mystr[2].replace('0x', '')+mystr[3].replace('0x', '0')

        #print(Finalstring)
        b = struct.unpack('!f', bytes.fromhex(mystr))[0]
        #b = struct.unpack('!f', bytes.__base__16((finstr)[0]))
        print('Force:', b, 'lbs')

        csvwriter.writerow(myrows)



        dT = datetime.now()
        myrows[0] = dT
        myrows[1] = b
        csvwriter.writerow(myrows)

mycsvfile.close()

ser.close()


# author -Manoj Vadali
# Ver # 1
# Purpose - To make Clamshell used to Unused with help of 1-W master Blackbox
import serial
import time
from CRC16 import CRC16
from CRC16 import calc
#from Gen2_auto_main import wait


oddparity = [0, 1, 1, 0, 1, 0, 0, 1, 1, 0, 0, 1, 0, 1, 1, 0]
clamshell_byte = [2, 3, 4, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
             0, 0, 0,
             0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

sulu_byte = [170, 69, 2, 1, 2, 1, 12, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 91, 84, 98]
mulu_byte = [170, 69, 2, 1, 2, 2, 16, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 12, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 93, 140, 211]
cart_byte = [170, 69, 2, 1, 2, 1, 24, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 4, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 219, 137, 234]
#byte_data= clamshell_byte

byte_data = cart_byte
#[170, 69, 2, 1, 2, 3, 24, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 5, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 219, 137, 234]
#[170, 69, 2, 1, 2, 2, 24, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 6, 90, 62]
crc_value = CRC16(0x00, byte_data)
crc_value = hex(crc_value)
print(crc_value)
# print('Original CRC: ', crc_value)
crc_second_byte = crc_value[2:4]
crc_first_byte = crc_value[4:]
# print(crc_first_byte)
# print(crc_second_byte)
byte_data.append(int(crc_first_byte, 16))
byte_data.append(int(crc_second_byte, 16))
# print(byte_data)
# print(len(byte_data))
######################################
byte_lst = [170, 69, 2, 1] + byte_data
# print(byte_lst)
crc_value = calc(bytes(byte_lst))
crc_value = int(crc_value, 16)
byte_lst.append(crc_value)
command_byte = (byte_lst)
print(command_byte)
ser = serial.Serial("COM9", 9600)
############# READ ###################
command = bytes(command_byte)
#print(sulu_byte, 'before')
#sulu_byte = bytes(sulu_byte)
#mulu_byte = bytes(mulu_byte)
#print(sulu_byte, 'after')
ser.write(command)

#ser.write(sulu_byte)
#ser.write(mulu_byte)
#ser.write(cart_byte)

time.sleep(1)
ser.write(command)
ser.write(command)
#print(command)
s = ser.read(2)
s = list(s)
packet_size = s[1]
read_data = ser.read(packet_size - 2)

print(read_data)
read_data = list(read_data)
print("==== READ DATA ====")
print(read_data[1:-1])
## end

#Reset_Clamshell()
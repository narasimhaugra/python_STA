# author -Manoj Vadali
# Ver # 1
# Purpose - To make Clamshell used to Unused with help of 1-W master Blackbox
import serial
import time
from CRC16 import CRC16
from CRC16 import calc
#from Gen2_auto_main import wait


oddparity = [0, 1, 1, 0, 1, 0, 0, 1, 1, 0, 0, 1, 0, 1, 1, 0]
CLAMSHELL_EEPROM = [2, 3, 4, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
             0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

SULU_EEPROM =  [2, 3, 4, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
             0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

MULU_EEPROM = [2, 3, 4, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
             0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

#CARTRIDGE_EEPROM = [2, 2, 24, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 4, 0, 0, 0, 0, 0, 0,
          #   0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

CARTRIDGE_EEPROM =[2, 2, 24, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0,
 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]


#CARTRIDGE_EEPROM =
# [170, 69, 2, 1, 2, 2, 24, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
# 0, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 103, 216, 87]#
#170, 69, 2, 1, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, ##
#0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 172, 132, 196]

byte_data = CARTRIDGE_EEPROM
#[170, 69, 2, 1, 2, 3, 24, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 5, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 219, 137, 234]
#[170, 69, 2, 1, 2, 2, 24, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 6, 90, 62]
                # crc_value = CRC16(0x00, byte_data)
                # crc_value = hex(crc_value)
                # print(crc_value)
                # # print('Original CRC: ', crc_value)
                # crc_second_byte = crc_value[2:4]
                # crc_first_byte = crc_value[4:]
                # # print(crc_first_byte)
                # # print(crc_second_byte)
                # byte_data.append(int(crc_first_byte, 16))
                # byte_data.append(int(crc_second_byte, 16))
                # print(byte_data)
                # # print(len(byte_data))
                # ######################################
                # byte_lst = [170, 69, 2, 1] + byte_data
                # # print(byte_lst)
                # crc_value = calc(bytes(byte_lst))
                # crc_value = int(crc_value, 16)
                # byte_lst.append(crc_value)
                # command_byte = (byte_lst)
                # print(command_byte)
                # ser = serial.Serial("COM9", 9600)
                # ############# READ ###################
                # command = bytes(command_byte)
                # #print(sulu_byte, 'before')
                # #sulu_byte = bytes(sulu_byte)
                # #mulu_byte = bytes(mulu_byte)
                # #print(sulu_byte, 'after')
                # ser.write(command)
                #
                # #ser.write(sulu_byte)
                # #ser.write(mulu_byte)
                # #ser.write(cart_byte)
                #
                # time.sleep(1)
                # # ser.write(command)
                #
                # #print(command)
                # s = ser.read(2)
                # s = list(s)
                # packet_size = s[1]
                # read_data = ser.read(packet_size - 2)
                #
                # print(read_data)
                # read_data = list(read_data)
                # print("==== READ DATA ====")
                # print(read_data[1:-1])
                # ## end

#Reset_Clamshell()
#
crc_value = CRC16(0x00, CARTRIDGE_EEPROM)
crc_value = hex(crc_value)
print('Original CRC: ', crc_value)
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
print(CARTRIDGE_command_byte)
ser = serial.Serial("COM9", 9600)
############# READ ###################
command = bytes(CARTRIDGE_command_byte)
ser.write(command)
time.sleep(1)
s = ser.read(2)
s = list(s)
packet_size = s[1]
read_data = ser.read(packet_size - 2)

print(read_data)
read_data = list(read_data)
print("==== READ DATA ====")
print(read_data[1:-1])
## end


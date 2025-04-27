import time

import serial

# import pandas as pd
from CRC16 import CRC16


def bytes(integer):
    return divmod(integer, 0x100)

#ser = serial.Serial("COM17", 115200, bytesize=8, parity='N', stopbits=1, timeout=None, xonxoff=0)
#serial.Serial()
#ser.flush()
def read_battery_RSOC(No_of_Strings, PowerPackComPort):

    #ping, enum, set rtc, get rtc, get serial number, get harware version, get parameters, reset
    # mysheet = pd.read_excel('C:\Python\Test_Configurator.xlsx', sheet_name='Initial_Setup')
    # df2 = pd.DataFrame(mysheet)
    # PowerPackComPort = (df2.loc[1])[1]

    battery_rsoc = 0
    print('PowerPackComPort', PowerPackComPort)
    for retry in range(5):
        try:
            with serial.Serial(PowerPackComPort, 115200, bytesize=8, parity='N', stopbits=1,
                                  timeout=0.05, xonxoff=False) as serPP:
                while True:

                    command_PING = b'\xAA\x06\x00\x01\x00\x19'
                    serPP.write(command_PING)

                    time.sleep(0.01)
                    READ_BATTERY_DATA = [170, 7, 0, 104, 13]
                    #print(READ_BATTERY_DATA)
                    crc16In =0
                    crc_value = CRC16(crc16In, READ_BATTERY_DATA)
                    high, low = bytes(crc_value)
                    crc_first_byte = hex(low)
                    crc_second_byte = hex(high)
                    READ_BATTERY_DATA.append(int(crc_first_byte, 16))
                    READ_BATTERY_DATA.append(int(crc_second_byte, 16))
                    #print(READ_BATTERY_DATA)
                    #serPP.write(READ_BATTERY_DATA)
                    for i in range(0, No_of_Strings):
                        serPP.write(READ_BATTERY_DATA)
                        s = serPP.read(2)
                        packet_size = s[1]
                        read_data = serPP.read(packet_size - 2)
                        hex_array = [hex(x)[2:] for x in read_data]
                        #print('Battery_data', hex_array)
                        #print(int(hex_array[1], 16), int(hex_array[2], 16))
                        if (int(hex_array[1], 16) == 104) and (int(hex_array[2], 16) == 13):
                            battery_rsoc = int(hex_array[5], 16)
                            print ('Battery_RSOC is:', battery_rsoc, '%')
                    break
        except Exception as ex:
            print(f"Exception Occurred : {ex}")
    return battery_rsoc


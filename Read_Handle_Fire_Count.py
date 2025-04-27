'''Created by:Manoj Vadali Date: 1-Feb-2022
Ver:1 Function: Reading the fire count from Handle 1W EEPROM '''

import time

import serial


def GetHandleUseCount(PowerPackComPort):
    HandleFireCount = 0
    HandleProcedureCount = 0
    for retry_num in range(5):
        try:
            with serial.Serial(PowerPackComPort, 115200, bytesize=8, parity='N', stopbits=1, timeout=3,
                               xonxoff=False) as serPP:
                time.sleep(1)
                command_PING = b'\xAA\x06\x00\x01\x00\x19'
                command_ONEWIRE_GET_CONNECTED = b'\xAA\x06\x00\x45\x00\x2A'
                command_ONEWIRE_GET_ADDRESS = b'\xAA\x07\x00\x46\x00\x2B\x0C'
                command_ONEWIRE_HANDLE_READ = b'\xAA\x07\x00\x49\x00\x2E\xFC'
                serPP.write(command_PING)
                serPP.write(command_ONEWIRE_GET_CONNECTED)
                serPP.write(command_ONEWIRE_GET_ADDRESS)

                # print('PING CMD sent', command_PING)
                # s = serPP.read(2)
                # # print(s, 'Ping S')
                # packet_size = s[1]
                # read_data = serPP.read(packet_size - 2)

                HandleFireCount = 0
                HandleProcedureCount = 0

                serPP.flush()

                for s in range(0, 20):
                    try:
                        serPP.write(command_ONEWIRE_HANDLE_READ)
                        s = serPP.readline(2)
                        packet_size = s[1]
                        read_data = serPP.read(packet_size - 2)
                        # print(read_data, 'read_data')
                        read_data = s + read_data
                        hex_array = [hex(x)[2:] for x in read_data]
                        # print('Read_data', s, hex_array)
                        # print(int(hex_array[1], 16), int(hex_array[2], 16))
                        time.sleep(.05)
                        if (int(hex_array[1], 16) == 72) and (int(hex_array[3], 16) == 73):
                            HandleFireCount = (((int(hex_array[25], 16))*256) + (int(hex_array[24], 16)))
                            HandleProcedureCount = (((int(hex_array[28], 16)) * 256) + (int(hex_array[27], 16)))
                            #serPP.write(STATUS_STOP)
                            break

                    except Exception as ex:
                        print(f"Exception Occurred:{ex}")
            break
        except Exception as ex:
            print(f"retry count: {retry_num + 1}. exception occurred!!! {ex}")
    # serPP.close()
    return HandleFireCount, HandleProcedureCount

#
# HandleFireCount, HandleProcedureCount = GetHandleUseCount(PowerPackComPort)
# print(HandleFireCount, HandleProcedureCount)
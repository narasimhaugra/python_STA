'''Created by:Manoj Vadali Date: 15-Jan-2022
Ver:1 Function: Reading the status variables '''

import time
import serial
import simple_colors


def ReadStatusVariables(PowerPackComPort, fixtureValidationReq=False):
    for retry_num in range(5):
        try:
            with serial.Serial(PowerPackComPort, 115200, bytesize=8, parity='N', stopbits=1, timeout=3, xonxoff=False) as serPP:

                command_PING = b'\xAA\x06\x00\x01\x00\x19'
                STATUS_START = b'\xAA\x06\x00\x31\x00\x0D'
                STATUS_RATE = b'\xAA\x0A\x00\x2F\xFA\x00\x00\x00\xC5\x19'
                STATUS_STOP = b'\xAA\x06\x00\x32\x40\x0C'
                serPP.write(command_PING)

                serPP.flush()
                serPP.write(STATUS_STOP)
                serPP.write(STATUS_START)

                statusListdata = []

                for s in range(0, 20):
                    try:
                        s = serPP.readline(2)
                        packet_size = s[1]
                        read_data = serPP.read(packet_size - 2)
                        # print(read_data, 'read_data')
                        read_data = s + read_data
                        if fixtureValidationReq:
                            pass
                        else:
                            print(simple_colors.yellow(f'status read_data : {read_data}'))
                        hex_array = [hex(x)[2:] for x in read_data]
                        #print('Read_data', s, hex_array)
                        # print(int(hex_array[1], 16), int(hex_array[2], 16))
                        time.sleep(.05)
                        if (int(hex_array[1], 16) == 71) and (int(hex_array[3], 16) == 48):
                            statusListdata = hex_array
                            serPP.write(STATUS_STOP)
                            break
                    except:
                      #  statusListdata = 'None'
                        serPP.write(STATUS_STOP)
            break

        except serial.SerialException as e:
            print(f"Failed to open port: {e}")

    return statusListdata

            # ser.write(command_PING)
            # print('PING CMD sent', command_PING)
            #
            # ser.write(STATUS_RATE)
            # time.sleep(.25)
            # ser.write(STATUS_START)
            # time.sleep(.25)
            #
            #
            # for i in range(0, 5):
            #     try:
            #         ser.write(STATUS_START)
            #         s = ser.read(2)
            #         packet_size = s[1]
            #         read_data = ser.read(packet_size - 2)
            #         hex_array = [hex(x)[2:] for x in read_data]
            #         #print('Battery_data', hex_array)
            #         #print(int(hex_array[1], 16), int(hex_array[2], 16))
            #         if ((int(hex_array[1], 16) == 71) and (int(hex_array[3], 16) == 48)):
            #             statusListdata = s+read_data
            #             break
            #     except:
            #         statusListdata = 'None'
            #         pass
            # ser.close()

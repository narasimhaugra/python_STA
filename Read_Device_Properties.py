'''Created by:Manoj Vadali Date: 17-Feb-2022
Ver:1 Function: Reading the Device properties to capture in output JSON file for test automation'''

import time
import serial
import datetime


def ReadDeviceProperties(PowerPackComPort):
    serPP = serial.Serial(PowerPackComPort, 115200, bytesize=8, parity='N', stopbits=1, timeout=3, xonxoff=0)
    command_PING = b'\xAA\x06\x00\x01\x00\x19'
    DEVICE_PROPERTIES = b'\xAA\x07\x00\x5F\x00\x20\x9C' #   AA 07 00 5F 00 20 9C
    serPP.write(command_PING)
    # print('PING CMD sent', command_PING)
    # s = serPP.read(2)
    # # print(s, 'Ping S')
    # packet_size = s[1]
    # read_data = serPP.read(packet_size - 2)

    dev_prop = []
    Blob_date = 'None'
    System_Version = 'None'
    PP_Blob_version = 'None'
    PP_Boot_version = 'None'
    Adapter_EGIA_version = 'None'
    Adapter_EEA_version = 'None'
    Adapter_Boot_version = 'None'
    Agile_Part_Number = 'None'

    serPP.flush()
    serPP.write(DEVICE_PROPERTIES)
    #serPP.write(STATUS_START)

    for s in range(0, 20):
        serPP.write(DEVICE_PROPERTIES)
        try:
            s = serPP.readline(2)
            packet_size = s[1]
            read_data = serPP.read(packet_size - 2)
            # print(read_data, 'read_data')
            read_data = s + read_data
            hex_array = [hex(x)[2:] for x in read_data]
            # print('Read_data', s, hex_array)
            # print(int(hex_array[1], 16), int(hex_array[2], 16))
            time.sleep(.05)
            if (int(hex_array[3], 16) == 95):
                hex_array = hex_array[5:-2]
                dev_prop = hex_array
                Blob_date = hex_array[7]+hex_array[6]+hex_array[5]+hex_array[4]

                Blob_date = datetime.datetime.fromtimestamp((int(Blob_date, 16))-19800)
                Blob_date = str(Blob_date) + ' (UTC)'
                print(Blob_date)
                hex_string = ''
                System_Version = hex_array[-20:]
                System_Version = [i for i in System_Version if i != '0']
                #print(System_Version)
                #ln = len(System_Version)
                for i in System_Version:
                    hex_string = hex_string + i
                #return (hex_string)
                print(hex_string)
                #hex_string = System_Version[0]+System_Version[1]+System_Version[2]+System_Version[3]+ System_Version[4]+System_Version[5]+System_Version[6]+System_Version[7]+System_Version[8]+System_Version[9]#+System_Version[10]+System_Version[11]+ System_Version[12]+System_Version[13]+System_Version[14]+System_Version[15]+System_Version[16]+ System_Version[17]+System_Version[18]+System_Version[19]
                bytes_object = bytes.fromhex(hex_string)

                System_Version = str('Rev ' + bytes_object.decode("ASCII"))#.strip('\x00')

                print('System_Version:', System_Version)
#####################################################################

                #print('hex_array', hex_array)
                PP_Blob_version = hex_array[-140:-120]
                #print(PP_Blob_version)
                hex_string = ''
                PP_Blob_version = [i for i in PP_Blob_version if i != '0']
                for i in PP_Blob_version:
                    hex_string = hex_string + i
                #hex_string = PP_Blob_version[0]+PP_Blob_version[1]+PP_Blob_version[2]+PP_Blob_version[3]+ PP_Blob_version[4]+PP_Blob_version[5]+PP_Blob_version[6]+PP_Blob_version[7]+PP_Blob_version[8]+PP_Blob_version[9]+PP_Blob_version[10]+PP_Blob_version[11]+ PP_Blob_version[12]+PP_Blob_version[13]+PP_Blob_version[14]+PP_Blob_version[15]+PP_Blob_version[16]+ PP_Blob_version[17]+PP_Blob_version[18]+PP_Blob_version[19]
                bytes_object = bytes.fromhex(hex_string)

                PP_Blob_version = str('Rev ' + bytes_object.decode("ASCII"))#.strip('\x00')

                print('PP_Blob_version:', PP_Blob_version)
               ###################################################
                PP_Boot_version = hex_array[-120:-100]
                #print(PP_Boot_version)
                hex_string = ''
                PP_Boot_version = [i for i in PP_Boot_version if i != '0']
                for i in PP_Boot_version:
                    hex_string = hex_string + i
                #hex_string = PP_Boot_version[0] + PP_Boot_version[1] + PP_Boot_version[2] + PP_Boot_version[3] + PP_Boot_version[4] #+ PP_Boot_version[5] #+ PP_Boot_version[6] + PP_Boot_version[7] + PP_Boot_version[8] + PP_Boot_version[9] + PP_Boot_version[10] + PP_Boot_version[11] + PP_Boot_version[12] + PP_Boot_version[13] + PP_Boot_version[14] + PP_Boot_version[15] + PP_Boot_version[16] + PP_Boot_version[17] + PP_Boot_version[18] + PP_Boot_version[19]
                #print(hex_string)
                bytes_object = bytes.fromhex(hex_string)

                PP_Boot_version = str('Rev ' + bytes_object.decode("ASCII"))#.strip('\x00')

                print('PP_Boot_version:', PP_Boot_version)

    #####################################################################

                # print('hex_array', hex_array)
                FPGA_version = hex_array[-100:-80]
                # print(PP_Blob_version)
                hex_string = ''
                FPGA_version = [i for i in FPGA_version if i != '0']
                for i in FPGA_version:
                    hex_string = hex_string + i

                #hex_string = FPGA_version[0] + FPGA_version[1] + FPGA_version[2] + FPGA_version[3] + FPGA_version[4] #+ FPGA_version[5] + FPGA_version[6] + FPGA_version[7] + FPGA_version[8] + FPGA_version[9] #+ FPGA_version[10] + FPGA_version[11] + FPGA_version[12] + FPGA_version[13] + FPGA_version[14] + FPGA_version[15] + FPGA_version[16] + FPGA_version[17] + FPGA_version[18] + FPGA_version[19]
                bytes_object = bytes.fromhex(hex_string)

                FPGA_version = str('Rev ' + bytes_object.decode("ASCII"))#.strip('\x00')

                print('FPGA_version:', FPGA_version)

#####################################################################

                # print('hex_array', hex_array)
                Adapter_Boot_version = (hex_array[-80:-60])#.strip('\x00')
                # print(PP_Blob_version)
                hex_string = ''
                Adapter_Boot_version = [i for i in Adapter_Boot_version if i != '0']
                for i in Adapter_Boot_version:
                    hex_string = hex_string + i
                #hex_string = Adapter_Boot_version[0] + Adapter_Boot_version[1] + Adapter_Boot_version[2] + Adapter_Boot_version[3] + Adapter_Boot_version[4] + Adapter_Boot_version[5] + Adapter_Boot_version[6] + Adapter_Boot_version[7] + Adapter_Boot_version [8] + Adapter_Boot_version [9] + Adapter_Boot_version [10] + Adapter_Boot_version [11] + Adapter_Boot_version [12] + Adapter_Boot_version [13] + Adapter_Boot_version [14] + Adapter_Boot_version [15] + Adapter_Boot_version [16] + Adapter_Boot_version[17] + Adapter_Boot_version[18] + Adapter_Boot_version[19]

                bytes_object = bytes.fromhex(hex_string)

                Adapter_Boot_version  = str('Rev ' + bytes_object.decode("ASCII"))#.strip('\x00')

                print('Adapter_Boot_version:', Adapter_Boot_version)
                #
#####################################################################

                # print('hex_array', hex_array)
                Adapter_EGIA_version = hex_array[-60:-40]
                # print(PP_Blob_version)
                hex_string = ''
                Adapter_EGIA_version = [i for i in Adapter_EGIA_version if i != '0']
                for i in Adapter_EGIA_version:
                    hex_string = hex_string + i
                # hex_string = Adapter_EGIA_version[0] + Adapter_EGIA_version[1] + Adapter_EGIA_version[2] + \
                #              Adapter_EGIA_version[3] + Adapter_EGIA_version[4] + Adapter_EGIA_version[5] + \
                #              Adapter_EGIA_version[6] + Adapter_EGIA_version[7] + Adapter_EGIA_version[8] + \
                #              Adapter_EGIA_version[9] + Adapter_EGIA_version[10] + Adapter_EGIA_version[11] + \
                #              Adapter_EGIA_version[12] + Adapter_EGIA_version[13] + Adapter_EGIA_version[14] + \
                #              Adapter_EGIA_version[15] + Adapter_EGIA_version[16] + Adapter_EGIA_version[17] + \
                #              Adapter_EGIA_version[18] + Adapter_EGIA_version[19]
                bytes_object = bytes.fromhex(hex_string)

                Adapter_EGIA_version = str('Rev ' + bytes_object.decode("ASCII"))#.strip('\x00')

                print('Adapter_EGIA_version:', Adapter_EGIA_version)

                #####################################################################

                # print('hex_array', hex_array)
                Adapter_EEA_version = hex_array[-40:-20]
                # print(PP_Blob_version)
                hex_string = ''
                Adapter_EEA_version = [i for i in Adapter_EEA_version if i != '0']
                for i in Adapter_EEA_version:
                    hex_string = hex_string + i

                # hex_string = Adapter_EEA_version[0] + Adapter_EEA_version[1] + Adapter_EEA_version[2] + \
                #              Adapter_EEA_version[3] + Adapter_EEA_version[4] + Adapter_EEA_version[5] + \
                #              Adapter_EEA_version[6] + Adapter_EEA_version[7] + Adapter_EEA_version[8] + \
                #              Adapter_EEA_version[9] + Adapter_EEA_version[10] + Adapter_EEA_version[11] + \
                #              Adapter_EEA_version[12] + Adapter_EEA_version[13] + Adapter_EEA_version[14] + \
                #              Adapter_EEA_version[15] + Adapter_EEA_version[16] + Adapter_EEA_version[17] + \
                #              Adapter_EEA_version[18] + Adapter_EEA_version[19]
                bytes_object = bytes.fromhex(hex_string)

                Adapter_EEA_version = str('Rev ' + bytes_object.decode("ASCII"))#.strip('\x00')

                print('Adapter_EEA_version:', Adapter_EEA_version)
                #####################################################################

                # print('hex_array', hex_array)
                hex_string =''
                Agile_Part_Number = hex_array[-160:-140]
                Agile_Part_Number = [i for i in Agile_Part_Number if i != '0']
                for i in Agile_Part_Number:
                    hex_string = hex_string + i
                # print(PP_Blob_version)

                # hex_string = Agile_Part_Number[0] + Agile_Part_Number[1] + Agile_Part_Number[2] + \
                #              Agile_Part_Number[3] + Agile_Part_Number[4] + Agile_Part_Number[5] + \
                #              Agile_Part_Number[6] + Agile_Part_Number[7] + Agile_Part_Number[8] + \
                #              Agile_Part_Number[9] + Agile_Part_Number[10] + Agile_Part_Number[11] + \
                #              Agile_Part_Number[12] + Agile_Part_Number[13] + Agile_Part_Number[14] + \
                #              Agile_Part_Number[15] + Agile_Part_Number[16] + Agile_Part_Number[17] + \
                #              Agile_Part_Number[18] + Agile_Part_Number[19]
                bytes_object = bytes.fromhex(hex_string)

                Agile_Part_Number = str(bytes_object.decode("ASCII"))#.strip('\x00')

                print('Agile_Part_Number:', Agile_Part_Number)

                #serPP.write(STATUS_STOP)
                break

        except:
            pass
            #  statusListdata = 'None'
            #serPP.write(STATUS_STOP)
    #     pass
    serPP.close()

    # print(statusListdata)
    return (Blob_date, System_Version, PP_Blob_version, PP_Boot_version, Adapter_EGIA_version, Adapter_EEA_version, Adapter_Boot_version, Agile_Part_Number)

#TestDate, BuildDate, BlobVersion, PowerPackVersion, PowerPackBootloaderVersion,
                       #   AdapterEGIAVersion, AdapterEEAVersion, AdapterBootloaderVersion


#print(ReadDeviceProperties('COM8'))
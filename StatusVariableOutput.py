# Author:Varun Pandey
# Date:Jan 14, 2022
# @ Purpose:To decode Status Variable Output based on the input list

'''
Status Variable data #
[170, 71, 0, 48, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 104, 254]

Header data:170, 71, 0, 48
Initial 9 bits status data bit:0, 0, 0, 0, 1, 0, 0, 0, 1,

# warnings and errors data
0, 0, 0, 0, Handle_Warning
0, 0, 0, 0,	Handle_Errors
0, 0, 0, 0, Adapter_Warnings
0, 0, 0, 0, Adapter_Errors
0, 0, 0, 0, Reload_Warnings
0, 0, 0, 0, Reload_Errors
0, 0, 0, 0, MULU_Warnings
0, 0, 0, 0, MULU_Errors
0, 0, 0, 0, Battery_Warnings
0, 0, 0, 0, Battery_Errors
1, 0, 0, 0, Clampshell_Warnings
0, 0, 0, 0, Clampshell_Errors
1, 0, 0, 0, Wifi_Warnings
0, 0, 0, 0,	Wifi_Errors

# CRC data
104, 254

'''

from pprint import pprint

# decode the error data, related with each byte, denoting whether for each error/warning represented by the key
#   is 1 or 0.
#   True  denotes that the error/warning is set
#   False denotes that the error/warning is *not* set
# returns the dict with each key, being set to True or False; based on the inputs
#   Example-
'''
{   
    'Adapter_Calibrated': False,
    'Adapter_Connected': False,
    'Adapter_Errors': False,
    'Adapter_Warnings': False,
    'Battery_Connected': False,
    'Battery_Errors': False,
    'Battery_Warnings': False,
    'CRC_Data': [104, 254],         // for INFORMATION
    'Cartidge_Connected': False,
    'Clampshell_Connected': True,
    'Clampshell_Errors': False,
    'Clampshell_Warnings': True,
    'Handle_Error': False,
    'Handle_Moving': False,
    'Handle_Warning': False,
    'MULU_Errors': False,
    'MULU_Warnings': False,
    'Reload_Clampled': False,
    'Reload_Connected': False,
    'Reload_Errors': False,
    'Reload_Fully_Open': True,
    'Reload_Warnings': False,
    'Wifi_Errors': False,
    'Wifi_Warnings': True,
    'header': [170, 71, 0, 48]     // for INFORMATION
}
'''
def decodeStatusVariable(statusListdata):
    returnStatusDataDict = {}
    # print(statusListdata)
    statusList=[]
    returnStatusDataDict['header'] = statusListdata[:4]
    initial_9_bit_status_list = statusList[4:13]
    # print(initial_9_bit_status_list)

    '''
    Initial 9 bits status data bit:
    0, Handle_Moving        4
    0, Battery_Connected    5
    0, Adapter_Connected    6
    0, Adapter_Calibrated   7
    1, Clampshell_Connected 8
    0, Reload_Connected     9
    0, Cartidge_Connected   10
    0, Reload_Clampled      11
    1, Reload_Fully_Open    12
    
    # warnings and errors data
    0, 0, 0, 0, Handle_Warning    13:17
    0, 0, 0, 0,	Handle_Errors   17:21
    0, 0, 0, 0, Adapter_Warnings    21-25
    0, 0, 0, 0, Adapter_Errors      25-29
    0, 0, 0, 0, Reload_Warnings     29:33
    0, 0, 0, 0, Reload_Errors       33:37
    0, 0, 0, 0, MULU_Warnings       37:41
    0, 0, 0, 0, MULU_Errors         41:45
    0, 0, 0, 0, Battery_Warnings    45:49
    0, 0, 0, 0, Battery_Errors      49:53
    1, 0, 0, 0, Clampshell_Warnings 53:57
    0, 0, 0, 0, Clampshell_Errors`` 57:61
    1, 0, 0, 0, Wifi_Warnings       61:65
    0, 0, 0, 0,	Wifi_Errors         65:69
    
    # CRC data
    104, 254 : CRC_Data  69:70
    '''

    # Set the dict result for the key as True, else False
    # reconstructing the statusListData to int values for type compare
    statusListdata = statusListdata[0:4] + [int(item) for item in statusListdata[4:69] if type(int(item)) == int] + \
                     statusListdata[69:71]
    #statusListdata = [item for item in statusListdata if type(int(item)) == int]
    returnStatusDataDict['Handle_Moving'] = True if statusListdata[4] else False
    returnStatusDataDict['Battery_Connected'] = True if statusListdata[5] else False
    returnStatusDataDict['Adapter_Connected'] = True if statusListdata[6] else False
    returnStatusDataDict['Adapter_Calibrated'] = True if statusListdata[7] else False
    returnStatusDataDict['Clamshell_Connected'] = True if statusListdata[8] else False
    returnStatusDataDict['Reload_Connected'] = True if statusListdata[9] else False
    returnStatusDataDict['Cartidge_Connected'] = True if statusListdata[10] else False
    returnStatusDataDict['Reload_Clampled'] = True if statusListdata[11] else False
    returnStatusDataDict['Reload_Fully_Open'] = True if statusListdata[12] else False

    returnStatusDataDict['Handle_Warning'] = True if any(statusListdata[13:17]) == 1 else False
    returnStatusDataDict['Handle_Error'] = True if any(statusListdata[17:21]) == 1 else False

    returnStatusDataDict['Adapter_Warnings'] = True if any(statusListdata[21:25]) == 1 else False
    returnStatusDataDict['Adapter_Errors'] = True if any(statusListdata[25:29]) == 1 else False

    returnStatusDataDict['Reload_Warnings'] = True if any(statusListdata[29:33]) == 1 else False
    returnStatusDataDict['Reload_Errors'] = True if any(statusListdata[33:37]) == 1 else False

    returnStatusDataDict['MULU_Warnings'] = True if any(statusListdata[37:41]) == 1 else False
    returnStatusDataDict['MULU_Errors'] = True if any(statusListdata[41:45]) == 1 else False

    returnStatusDataDict['Battery_Warnings'] = True if any(statusListdata[45:49]) == 1 else False
    returnStatusDataDict['Battery_Errors'] = True if any(statusListdata[49:53]) == 1 else False

    returnStatusDataDict['Clamshell_Warnings'] = True if any(statusListdata[53:57]) == 1 else False
    returnStatusDataDict['Clamshell_Errors'] = True if any(statusListdata[57:61]) == 1 else False

    returnStatusDataDict['Wifi_Warnings'] = True if any(statusListdata[61:65]) == 1 else False
    returnStatusDataDict['Wifi_Errors'] = True if any(statusListdata[65:69]) == 1 else False

    # CRC Data
    returnStatusDataDict['CRC_Data'] = statusListdata[69:71]

    pprint(returnStatusDataDict, indent=4)

    return returnStatusDataDict

if __name__ == "__main__":
    statusList = [170, 71, 0, 48, 0, 0, 1, 0, 1, 0, 0, 0, 1, 00, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                  0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 104, 254]
    decodeStatusVariable(statusList)
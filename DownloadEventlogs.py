"""  Eventlog Downloading exe calling function. Written by Manoj Vadali 20 March 2022"""

import time, re

from EventLog_Download.gen2_main import ProducerThread
from Serial_Relay_Control import serialControl

import serial
import serial.tools

def identifyDirPathLists(eventLogDirPath_Start, eventLogDirPath_End):
    # \data\data_002551\002600
    # ['003097', '003176']
    eventLogDirPathList = []
    totalNumberOfIterations = abs(int(eventLogDirPath_End) - int(eventLogDirPath_Start)) + 1

    # in case if we mismatch the start and end directories
    lowerDir = eventLogDirPath_Start if eventLogDirPath_Start < eventLogDirPath_End else eventLogDirPath_End
    identifydir = lambda item : (item - (item%50)-49) if not(item%50) else  (item - (item%50) +1)
    for singleIteration in range(totalNumberOfIterations):
        dir_path = identifydir(int(lowerDir) + singleIteration)
        paddedDirPath =  str(dir_path).zfill(6)   # must be total of 6 chars, else pad it up with remaining number of zeros
        fullPath = "\\data\\data_" + paddedDirPath + "\\" + str(int(lowerDir) + singleIteration).zfill(6)
        eventLogDirPathList.append(fullPath)
    # log.logging.debug(eventLogDirPathList)
    return eventLogDirPathList

def DownloadEventlogs(videoPath, PowerPackComPort, NCDComPort):
    portPP = PowerPackComPort.replace('COM', '')
    sampleresultsPath = videoPath + '/Detailed_Results.txt'
    with open(sampleresultsPath) as f:
        lines = f.read().splitlines()

    # Declare the filter function
    def Filter(datalist):
        # Search data based on regular expression in the list
        return [val for val in datalist
                if re.search(r'^Eventlog:Data path:', val)]

    evlog = []
    # Print the filter data
    ln = len(Filter(lines))
    evlog.append(Filter(lines)[0].split('\\')[3])
    evlog.append(Filter(lines)[ln - 1].split('\\')[3])
    print(f"event_logs: {evlog}")
    #print(evlog)
    #print(NCDComPort)
    serialControlObj = serialControl(PowerPackComPort=PowerPackComPort, NCDComPort=NCDComPort)
    serialControlObj.OpenSerialConnection()

    #serialControl.OpenSerialConnection(NCDComPort)
    #serialControl.Switch_ONN_ALL_Relays_In_Each_Bank(1)
    serialControlObj.Switch_OFF_Relay(3, 7)
    serialControlObj.Switch_OFF_Relay(3, 8)
    serialControlObj.Switch_ONN_ALL_Relays_In_Each_Bank(1)
    time.sleep(30)

    dir_path_list = identifyDirPathLists(eventLogDirPath_End=str(int((evlog[1]))),
                                         eventLogDirPath_Start=str(int((evlog[0]))))
    # arg = ['C:\Signia-TestAutomation\SigniaTransferProgram\PYTHON_MCP\dist\signia_transfer_program.exe', portPP,
    #        str(int((evlog[0]))), str(int((evlog[1])))]
    # subprocess.Popen(arg, shell=True)
    thread = ProducerThread(name='Gen2Communications_%s' % portPP, port_num=portPP, log_dest=videoPath,
                            expected_dir_eventlog_download=dir_path_list)
    thread.start()
    # subprocess.run(['python', './EventLog_Download/gen2_main.py', portPP, ])
    time.sleep(30)

    PPnotready = True
    while PPnotready:
        try:
            serPP = serial.Serial(PowerPackComPort, 115200, bytesize=8, parity='N', stopbits=1, timeout=.01, xonxoff=0)
            PPnotready = False
            print('Event Log Download Completed')
            time.sleep(5)
            serialControlObj = serialControl(NCDComPort, PowerPackComPort,videoPath)
            serialControlObj.OpenSerialConnection()
            serialControlObj.Switch_OFF_ALL_Relays_In_Each_Bank(1)
            serialControlObj.Switch_ONN_Relay(3, 7)  # battery charge
            serialControlObj.wait(0.5)
            serialControlObj.Switch_ONN_Relay(3, 8)

        except:
            pass



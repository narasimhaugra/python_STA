# ReadQue function have been refactored by Varun Pandey on Jan 4, 2022


def ReadingQue(qref, searchFlag=False):
    combinedList = []
    LogStrings = []
    TimeStamps = []
    data_path = None

    # print("No of item s allowed in the queue is :", qref.maxsize)
    #
    # print("Return no of items in the queue :", qref.qsize())

    for _ in range(qref.maxsize):
        try:
            combinedList.append(qref.get(block=True, timeout=0.01))
        except:
            continue

    # while not qref.empty():
    #     combinedList.append(qref.get(block=True, timeout=0.01))

    # de-serialize the data and separate them into two different lists data
    # added 'Data path: \\data\\data_001901\\001915' specifically too
    for singleItem in combinedList:
        TimeStamps.append(singleItem[0])
        #LogStrings.append(str(singleItem[1]).strip())  # stripping the unwanted spaces #Commented by Manoj Vadali 18th October
        LogStrings.append(str(singleItem[1]).strip('\x00').strip('\r\n').strip())  # stripping the unwanted spaces # added strip \x00 an \r\n for Gecko as null strings are coming in event log strings on 18th oct 2023
        #LogStrings.append(str(singleItem[1]).strip())
        if searchFlag:
            if 'Data path:'.lower() in str(singleItem[1]).lower():
                data_path = str(singleItem[1]).strip()

    #print('LogStrings', LogStrings)
    #print('TimeStamps', TimeStamps)
    if searchFlag:
        print('Eventlog:', data_path)
        return TimeStamps, LogStrings, data_path
    else:
      return TimeStamps, LogStrings


# Purpose - to deserialize the Queue data into two lists, namely TimeStamps and LogStrings and return the same
def ReadQue(num, qref, searchFlag= False):
    combinedList = []
    LogStrings = []
    TimeStamps = []
    data_path = None
    print("No of item s allowed in the queue is :", qref.maxsize)

    print("Return no of items in the queue :", qref.qsize())
    for _ in range(num):
        try:
            combinedList.append(qref.get(block=True, timeout=0.01))
        except:
            continue

    #print(combinedList)


    # de-serialize the data and separate them into two different lists data
    # added 'Data path: \\data\\data_001901\\001915' specifically too
    for singleItem in combinedList:
        TimeStamps.append(singleItem[0])
        # LogStrings.append(str(singleItem[1]).strip())  # stripping the unwanted spaces
        LogStrings.append(str(singleItem[1]).strip('\x00').strip('\r\n').strip())
        if searchFlag:
            if 'Data path:'.lower() in str(singleItem[1]).lower():
                data_path = str(singleItem[1]).strip()

    #print('LogStrings', LogStrings)
    #print('TimeStamps', TimeStamps)
    if searchFlag:
        print('Eventlog:', data_path)
        return TimeStamps, LogStrings, data_path
    else:
      return TimeStamps, LogStrings


# def ReadQue_OLD (num, qref):
#     x = []
#     for var_String in range(num):
#         try:
#             x.append(qref.get(block=True, timeout=0.01))
#         except:
#             pass
#     #print(x)
#     #my_Serthread.clearQue()
#     #MCPThread.readingPowerPack.exitFlag = True
#     LogStrings = []
#     TimeStamps = []
#     ls = (len(x))
#     print(x)
#
#     if (ls !=0):
#         for i in range (0, ls):
#             LogStrings.append((x)[i][1])
#             TimeStamps.append((x)[i][0])
#
#     print('LogStrings', LogStrings)
#     print('TimeStamps', TimeStamps)
#     return(TimeStamps, LogStrings)
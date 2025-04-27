# ReadQue function have been refactored by Varun Pandey on Jan 4, 2022

# Purpose - to deserialize the Queue data into two lists, namely TimeStamps and LogStrings and return the same
def ReadQue(num, qref):
    combinedList = []
    LogStrings = []
    TimeStamps = []
    for _ in range(num):
        try:
            combinedList.append(qref.get(block=True, timeout=0.01))
        except:
            continue

    #print(combinedList)

    # de-serialize the data and separate them into two different lists data
    for singleItem in combinedList:
        TimeStamps.append(singleItem[0])
        LogStrings.append(str(singleItem[1]).strip())  # stripping the unwanted spaces

    print('LogStrings', LogStrings)
    #print('TimeStamps', TimeStamps)
    return TimeStamps, LogStrings


def ReadQue_OLD (num, qref):
    x = []
    for var_String in range(num):
        try:
            x.append(qref.get(block=True, timeout=0.01))
        except:
            pass
    #print(x)
    #my_Serthread.clearQue()
    #MCPThread.readingPowerPack.exitFlag = True
    LogStrings = []
    TimeStamps = []
    ls = (len(x))
    print(x)

    if (ls !=0):
        for i in range (0, ls):
            LogStrings.append((x)[i][1])
            TimeStamps.append((x)[i][0])

    print('LogStrings', LogStrings)
    print('TimeStamps', TimeStamps)
    return(TimeStamps, LogStrings)
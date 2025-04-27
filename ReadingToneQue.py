'''Written by Manoj Vadali on 31st March. Leveraging the existing code written by Jana and Varun'''
def ReadToneQue(num, qref):
    tonenames = []
    for _ in range(num):
        try:
            tonenames.append(qref.get(block=True, timeout=0.01))
        except:
            continue

        #print('LogStrings', LogStrings)
    #print('TimeStamps', TimeStamps)
        return tonenames
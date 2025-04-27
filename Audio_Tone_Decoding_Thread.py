'''Written by Manoj Vadali on 29th March for decoding Audio Tone signals from Power Pack'''

import queue
import threading
import time
import timeit

import nidaqmx

Fault_Tone = ['700', '550', '700', '550', '700', '550']
All_Good_Tone = ['2100']
Ready_Tone = ['1950', '2100']
Entering_Fire_Mode_Tone = ['1950', '2150']
Exit_Fire_Mode_Tone = ['2150', '1950']
Caution_Tone = ['700']  # Duration 300mSec
Insufficient_Battery_Tone = ['700']  # Duration 1350mSec
Emergency_Retract_Tone = ['700']  # Duration 300mSec
Limit_Reached_Tone = ['700']# Duration 300mSec


class ToneDecoding(threading.Thread):
    exitFlag = False
    def __init__(self, size):
        threading.Thread.__init__(self)
        self.exitFlag = False
        self.size = size
        self.readToneQue = queue.Queue(size)
    def run(self):
        #print(exitFlag)
        while(not ToneDecoding.exitFlag):
            with nidaqmx.Task() as task:
                task.ai_channels.add_ai_voltage_chan("Dev1/ai0")
                data = 0
                while ((-.10 < data) and (data < .10)):
                    data = task.read()
                    # print(data)

            try:
                with nidaqmx.Task() as task:
                    task.ci_channels.add_ci_freq_chan("Dev1/ctr0")
                    tone = []
                    while True:
                        # tone = []
                        start = timeit.default_timer()
                        data = str(50 * round((int(round(task.read(), -1))) / 50))
                        end = timeit.default_timer()
                        deltime = str(int(1000 * (end - start)))
                        # tim = datetime.now()

                        # print(tim, '-:-', int(round(data, -1)))
                        tone.append(deltime + ':' + data)
            except:
                pass

            toneduration = 0
            tonefrequency = 0
            list_of_tone_frequencies = []
            for item in tone:
                # toneduration = toneduration + int(item.split(':')[0])
                tf = str(int(item.split(':')[1]))
                if str(tonefrequency) != tf:
                    tonefrequency = tf
                    list_of_tone_frequencies.append(str(tf))
                    count = len(list_of_tone_frequencies)
                    toneduration = toneduration + int(item.split(':')[0])
                    # if str(tonefrequency) == tf:
                    list_of_tone_frequencies.append((item.split(':')[0]))
                toneduration = toneduration + int(item.split(':')[0])
                list_of_tone_frequencies[count] = int(list_of_tone_frequencies[count]) + int((item.split(':')[0]))

                # tonefrequency.append(str(int(item.split(':')[1])))
            tone_dur = []
            tone_frq = []
            for i in range(0, len(list_of_tone_frequencies)):
                if i % 2:
                    tone_dur.append(list_of_tone_frequencies[i])
                else:
                    tone_frq.append(list_of_tone_frequencies[i])
            print(toneduration)
            # print(tonefrequency)
            print(tone_frq)
            if tone_frq == Caution_Tone:
                print('Caution Tone Played')
                tonename = 'Caution Tone'
                self.readToneQue.put(tonename)
            elif tone_frq == Ready_Tone:
                print('Ready Tone Played')
                tonename = 'Ready Tone'
                self.readToneQue.put(tonename)
            elif tone_frq == All_Good_Tone:
                if toneduration < 120:
                    print('Clamp Confirmation Tone Played')
                    tonename = 'Clamp Confirmation'
                    self.readToneQue.put(tonename)
                else:
                    print('All Good Tone Played')
                    tonename = 'All Good Tone'
                    self.readToneQue.put(tonename)
            elif tone_frq == Entering_Fire_Mode_Tone:
                print('Entering Fire Mode Tone Played')
                tonename = 'Entering Fire Mode'
                self.readToneQue.put(tonename)
            elif tone_frq == Exit_Fire_Mode_Tone:
                print('Exit Fire Mode Tone Played')
                tonename = 'Exit Fire Mode'
                self.readToneQue.put(tonename)
            elif tone_frq == Fault_Tone:
                print('Fault Tone Played')
                tonename = 'Fault Tone'
                self.readToneQue.put(tonename)
    #self.exitFlag = True
    time.sleep(0.001)


    def clearToneQue(self):
        while not self.readToneQue.empty():
            self.readToneQue.get()

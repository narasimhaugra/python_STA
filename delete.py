
from ReadingQue import ReadQue
import Audio_Tone_Decoding_Thread
import time

my_thread = Audio_Tone_Decoding_Thread.ToneDecoding(1000)
my_thread.clearToneQue()
Audio_Tone_Decoding_Thread.ToneDecoding.exitFlag = False
my_thread.start()
ToneNames = ReadQue(20, my_thread.readToneQue)

time.sleep(30)
Audio_Tone_Decoding_Thread.ToneDecoding.exitFlag = True
print('Printing Tones Returend by Thread')

print(ToneNames)

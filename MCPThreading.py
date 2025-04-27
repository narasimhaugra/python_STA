import queue
import threading
import time


class readingPowerPack(threading.Thread):
    def __init__(self, portref, size):
        threading.Thread.__init__(self)
        self.exitFlag = False
        self.portref = portref
        self.size = size
        self.readQue = queue.Queue(size)
    def run(self):
        #print(exitFlag)
        while (not self.exitFlag):
            try:
                self.portref.write(b'\xAA\x06\x00\x01\x00\x19')
                #print("Sent Ping")
                s = self.portref.read(2)
                packet_size = s[1]
                read_data = self.portref.read(packet_size - 2)
                read_data = read_data[2:-3].decode('ascii')
                    # print('rd', read_data)
                data = (read_data.split(":", 1))
                if data[1] != '0':
                    self.readQue.put(data)

                    #self.readQue.put(timestamp)
            except:
                pass
                #self.exitFlag = True
            time.sleep(0.1)

    def clearQue(self):
        while (not self.readQue.empty()):
            self.readQue.get()

    def portClose(self):
        self.portref.close()

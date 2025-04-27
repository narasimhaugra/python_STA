import queue
import threading
import time
import traceback

import simple_colors


class readingPowerPack(threading.Thread):
    exitFlag = False
    def __init__(self, portref, size):
        threading.Thread.__init__(self)
        self.exitFlag = False
        self.portref = portref
        self.size = size
        self.readQue = queue.Queue(size)
        self.log_to_be_found = None
        self.is_log_found = False

    def run(self):
        for retry_num in range(5):
            try:
                with self.portref:
                    while not readingPowerPack.exitFlag:
                        try:
                            self.portref.write(b'\xAA\x06\x00\x01\x00\x19')
                            s = self.portref.read(2)
                            s = list(s)
                            # if len(s) == 0:
                            #     continue
                            packet_size = s[1]
                            read_data = self.portref.read(packet_size - 2)
                            # if len(list(read_data)) == 0:
                            #     continue
                            if self.log_to_be_found is not None and not self.is_log_found:
                                if packet_size >= (len(self.log_to_be_found) + 16):
                                    # print(" s + read_data : ", read_data)
                                    print(f"(s + read_data).decode('ascii') : {(read_data[3:-3]).decode('ascii')}")
                                    if read_data[3:-3].decode('ascii').find(self.log_to_be_found) != -1:
                                        self.is_log_found = True
                                        print(simple_colors.magenta(f'read_data[12:-3] : {(s + read_data)[13:-3]}'
                                                                    f'\n{bytes(self.log_to_be_found.encode("ascii"))}'))
                            if read_data[3] != 0xd8:
                                if read_data[4] != 0xfa:
                                    if read_data[2] != 0x09:
                                        read_data = read_data[2:-3].decode('ascii')
                                        data = (read_data.split(":", 1))
                                        if data[1] != '0':
                                            self.readQue.put(data)

                            if read_data[3] == 0xd8:
                                if read_data[4] == 0xfa:
                                    if read_data[2] == 0x09:
                                        s = self.portref.read(2)
                                        s = list(s)
                                        # if len(s) == 0:
                                        #     continue
                                        packet_size = s[1]
                                        read_data = self.portref.read(packet_size - 2)
                                        read_data = read_data[2:-3].decode('ascii')
                                        data = (read_data.split(":", 1))
                                        # print(f'read_data: {read_data}')
                                        if len(data) > 2 and data[1] != '0':
                                            self.readQue.put(data)
                                        else:
                                            continue
                            print("Read data from MCP Thread :", read_data)
                        except Exception as e:
                            # print(f'Exception Occurred!!! {e}. \ntraceback: {traceback.format_exc()}')
                            continue
                break
            except Exception as ex:
                print(f"retry count: {retry_num + 1}. exception occurred!!! {ex}. \ntraceback: {traceback.format_exc()}")
                continue

    time.sleep(0.001)

    def clearQue(self):
        while not self.readQue.empty():
            self.readQue.get()

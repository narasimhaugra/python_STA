#Updated by Manoj Vadali for re-arch adding sending authetntication bytes over serial port 19-July 23

import serial
import threading
import queue
import time
import simple_colors
class readingPowerPack(threading.Thread):
    exitFlag = False
    def __init__(self, portref = None, size = 0):

        self.exitFlag = False
        self.portref = portref
        self.size = size
        self.readQue = queue.Queue(size)
        self.__log_to_be_found = None
        threading.Thread.__init__(self)
        self.__stringFoundCondition = threading.Event()


    def run(self):
        #print(exitFlag)


        self.portref.write(b'\xAA\x06\x00\x01\x00\x19')

        ## added for rearch ####
        #self.portref.write(b'\xAA\x06\x00\x7F\x80\x39')#AUTHENTICATE_DEVICE
        #self.portref.write(b'\xAA\x16\x00\x7F\x40\xC4\xD1\x68\x0E\x5B\xCE\x82\x25\x64\x37\xEA\x54\x06\x36\x1A\xAB\x5D')# AUTHENTICATE_DEVICE
        ## added for rearch ####
        for retry_num in range(5):
            print(f"entering MCP thread.......{time.time() * 1000}")
            with self.portref:
                while not readingPowerPack.exitFlag:
                    try:
                        self.portref.write(b'\xAA\x06\x00\x01\x00\x19')
                        #print("Sent Ping")
                        s = self.portref.read(3)
                        #print(f"s: {s}")
                        packet_size = s[1] | (s[2] << 8)

                        if packet_size > 255:
                            print("Warning.........1")

                        #print(f"packet_size: {packet_size}")
                        read_data = self.portref.read(packet_size - 3)
                        #b= ((hex(read_data[3])))
                        #print (b)
                        if packet_size > 7 :
                            print(f"(s + read_data).decode('ascii') : {(read_data[3:-3]).decode('ascii')}")
                        if self.__log_to_be_found is not None:
                            # print(" packet size : ", packet_size)
                            if packet_size >= (len(self.__log_to_be_found) + 16):
                                print(" s + read_data : ", read_data)
                                print(f"(s + read_data).decode('ascii') : {(read_data[3:-3]).decode('ascii')}")
                                if read_data[3:-3].decode('ascii').find(self.__log_to_be_found) != -1:
                                    self.__stringFoundCondition .set()
                                    print(simple_colors.magenta(f'read_data[12:-3] : {(s + read_data)[13:-3]}'
                                                                f'\n{bytes(self.__log_to_be_found.encode("ascii"))}'))

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
                                    s = self.portref.read(3)
                                    packet_size = s[1] | (s[2] << 8)
                                    read_data = self.portref.read(packet_size - 3)
                                    read_data = read_data[2:-3].decode('ascii')
                                    data = (read_data.split(":", 1))
                                    if data[1] != '0':
                                        self.readQue.put(data)

                #self.readQue.put(timestamp)
                    except:
                        continue
                print(f"Exiting MCP thread.......{time.time() * 1000}")
            break
    #self.exitFlag = True
    time.sleep(0.001)

    def clearQue(self):
        while not self.readQue.empty():
            self.readQue.get()

    def waitUntilString(self, string=None, timeout=5) -> str:
        """
        Blocks until expected string is received.
        Default timeout is 5 seconds.
        Returns new "string" if change, "" if timeout.
        """""
        print(f"searching foe the string: {string}")
        self.__stringFoundCondition.clear()
        self.__log_to_be_found = string
        result = string if self.__stringFoundCondition.wait(timeout) else ""
        self.__log_to_be_found = None
        return result

    def MultipleStringsRead(self, strings=None, timeout=5) -> str:
        """
        Blocks until any of the expected strings is received.
        Default timeout is 5 seconds.
        Returns the matched string if found, "" if timeout.
        """
        self.__stringFoundCondition.clear()

        # Check if the input is a list or just a single string
        if isinstance(strings, str):
            strings = [strings]  # Convert single string to a list for uniform processing

        self.__log_to_be_found = strings
        result = ""

        if self.__stringFoundCondition.wait(timeout):
            for expected_string in strings:
                if expected_string in self.__log_to_be_found:
                    result = expected_string
                    break

        self.__log_to_be_found = None
        return result

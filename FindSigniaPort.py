import serial.tools.list_ports


def get_ports():
    ports = serial.tools.list_ports.comports()

    return ports


def findSignia(portsFound):
    commPort = 'None'
    numConnection = len(portsFound)

    for i in range(0, numConnection):
        port = foundPorts[i]
        strPort = str(port)

        if 'SigniaPowerHandle' in strPort:
            splitPort = strPort.split(' ')
            commPort = (splitPort[0])

    return commPort


foundPorts = get_ports()
connectPort = findSignia(foundPorts)

if connectPort != 'None':
    ser = serial.Serial(connectPort, baudrate=115200, timeout=1)
    print('Connected to ' + connectPort)

else:
    print('Connection Issue!')

print('DONE')
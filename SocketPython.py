import socket
#169.254.1.105


c = socket.socket()
c.close()
c.connect(('169.254.1.105',2000))
command_PING = b'\xAA\x06\x00\x01\x00\x19'
c.send(command_PING)
print(c.recv(1024).decode())
print(c.recv(1024))
c.close()
while True:
    c.send(command_PING)
    print(c.recv(1024))

import serial

#
# TURN_ADC_COMMAND_CHANNEL_WISE = [
#
#     [170,2,254,151,65 ],]
## Read 8 bit ADC  Input Channels -  command ID - 254,  Channel ID (1-8) - 150-157
## Read 10 bit ADC  Input Channels - command ID - 254,  Channel ID (1-8) - 158-165


# Open serial connection
ser = serial.Serial('COM12', 115200, bytesize=8, parity='N', stopbits=1, timeout=0.05,
                                   xonxoff=False)

channel_1_command = [170,2,254,150,64], # Read the Analog Input Channel 1 and Return a 8-Bit Value ( 170 1 0 171 )

def send_serial_bytes(command_bytes):
    command_bytes = bytearray(command_bytes)
    ser.write(command_bytes)

# # Channel 1 ADC command (replace with your desired channel)
# channel = 1
# command = f"AD8_READ_CHANNEL_{channel}"

# write(command.encode())
# Transmit command
for i in channel_1_command:
    send_serial_bytes(i)

# Receive response
decimal_bytes = bytearray()
decimal_bytes.extend(ser.readline())
# response = ser.readline()
print(decimal_bytes)

# Close serial connection
ser.close()


#### Make a function of Green Key status via status and frequency
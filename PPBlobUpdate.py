#!/usr/bin/env python
"""@package PPBlobUpdate
This module updates the Signia Handle Blob. It uses the serial commands as mentioned in the R0055200.
The order of commands are
    SERIALCMD_BLOB_DATA_SETUP
    SERIALCMD_BLOB_DATA_PACKET
    SERIALCMD_BLOB_DATA_VALIDATE
    Then to force the update, send below
    SERIALCMD_ERASE_HANDLE_TIMESTAMP
    SERIALCMD_ERASE_HANDLE_BL_TIMESTAMP
    SERIALCMD_ERASE_JED_TIMESTAMP
    Finally send below command to reset the handle
    SERIALCMD_RESET_DEVICE
"""
import os
import shutil
import subprocess
import time

import serial


def BlobUpload(PowerPackComPort, NCDComPort, BLOB_PATH, ARCHIVE_PATH, OUTPUT_PATH):
    # serialControlObj.

    def createFolder(directory):
        try:
            if not os.path.exists(directory):
                os.makedirs(directory)
        except OSError:
            print('Error: Creating directory. ' + directory)

    # Owned
    __copyright__ = "Copyright 2021, Covidien - Surgical Innovations. All Rights Reserved."
    __author__ = "Ginto Kurian" "Updated by ManojVadali" "Copying blob from remote server and creatig folder structure triggered by Jenkins/arguments"
    __version__ = "0.0.4"

    # Change this as per your computer
    SIGNIA_USB_SERIAL_COM_PORT = PowerPackComPort
    # print("PowerPackComPort", PowerPackComPort)

    # Note: Path as per your computer
    MCP_FILE_PATH = "C:\\Signia-TestAutomation\\Master Control Panel\\MasterControlPanel.exe"

    BLOB_FILE_NAME = (os.path.basename(BLOB_PATH))
    blob_path = BLOB_PATH.replace(BLOB_FILE_NAME, '')
    blob_path = blob_path[:-1]
    # print("blob path ", blob_path)

    # SplitDrive function returns tuple value which is drive [0] and path [1]
    dstpath = os.path.splitdrive(blob_path)[1]
    # print("dstpath ", dstpath)
    #
    #blob_path = os.path.splitdrive(blob_path)[1]
    #dst = "C:" + blob_path
    dst = "C:" + dstpath
    createFolder(dst)
    #dst = dst.replace('/\\', '/')
    #    BLOB_FILE_PATH = ARCHIVE_PATH +":/" + BLOB_PATH
    BLOB_FILE_PATH = BLOB_PATH

    # print('blob file path', BLOB_FILE_PATH)

    #src = "Z:\\" + JOB_NAME + "/" + CHANGESET
    src = BLOB_FILE_PATH

    #createFolder(dst)

    #createFolder(OUTPUT_PATH)
    # print(f'source :{src}, destination :{dst}')
    #Copying Blob File to Local Machine
    shutil.copy(src=src, dst=dst)

    # Change the below Blob files as per the need
    # Note: Path as per your computer

    RAW_BLOB_FILE_PATH = "C:\\Signia-Legacy\\Raw_Blobs\\BlobFile"
    BLOB_FILE_PATH = dst + "/" + BLOB_FILE_NAME
    #print("BLOB_FILE_PATH:", BLOB_FILE_PATH)
    SERIALCMD_GET_RTC = 66
    SERIALCMD_BLOB_DATA_SETUP = 82
    SERIALCMD_BLOB_DATA_PACKET = 83
    SERIALCMD_BLOB_DATA_VALIDATE = 84
    SERIALCMD_ERASE_HANDLE_TIMESTAMP = 89
    SERIALCMD_ERASE_HANDLE_BL_TIMESTAMP = 90
    SERIALCMD_ERASE_JED_TIMESTAMP = 91
    SERIALCMD_GET_SERIALNUM = 116
    SERIALCMD_RESET_DEVICE = 122

    MAX_BLOB_PACKET_LIMIT = 960

    oddparity = [0, 1, 1, 0, 1, 0, 0, 1, 1, 0, 0, 1, 0, 1, 1, 0]

    def fnReadAndPrintReply(waitForRead):
        s = pSerialHandle.read(2)
        s = list(s)
        packetSize = s[1]
        readData = pSerialHandle.read(packetSize - 2)
        readData = list(readData)
        readData = s + readData
        if waitForRead:
            time.sleep(0.1)
            print("READ DATA:", readData)
            print("READ Byte:", bytearray(readData))
        return readData

    def fnCreateFrame(cmd_id=0x01, parm=None):
        sz = 0
        if type(parm) is list:
            xmit_str = [0xAA, sz, 0x00, cmd_id] + parm
            sz = len(xmit_str) + 2
            xmit_str[1] = sz
        elif type(parm) is int:
            xmit_str = [0xAA, sz, 0x00, cmd_id, parm]
            sz = len(xmit_str) + 2
            xmit_str[1] = sz
        else:
            xmit_str = [0xAA, 0x06, 0x00, cmd_id]

        crc = CRC16(0, xmit_str)

        hi_byte = crc >> 8
        lo_byte = 0xff & crc

        xmit_str.append(lo_byte)
        xmit_str.append(hi_byte)
        return xmit_str

    def CRC16(crc16In=0, frame=[0xAA, 0x06, 0x00, 0x01]):
        for ch in frame:
            data = (ch ^ (crc16In & 0xff)) & 0xff
            crc16In >>= 8
            if oddparity[data & 0x0f] ^ oddparity[data >> 4]:
                crc16In ^= 0xc001
            data <<= 6
            crc16In ^= data
            data <<= 1
            crc16In ^= data
        return crc16In

    def fnSendCmdAndGetReply(cmdIn):
        cmdFrame = fnCreateFrame(cmdIn, None)
        pSerialHandle.write(cmdFrame)
        # print('SER CMD sent: ', cmdIn)
        fnReadAndPrintReply(False)

    def fnCreateRawBlob(pBlobFilePath, pRawBlobFilePath):
        # This function uses MCP command line option (PARSEBLOBFILE) to parse the .gen2Blob to RawBlobfile

        # Make the command
        SystemCommand = MCP_FILE_PATH + " PARSEBLOBFILE, " + pBlobFilePath + ", " + pRawBlobFilePath

        # print(BatSystemCommand)

        # print("Calling MCP to Parse ", pBlobFilePath, " Blob file to ", pRawBlobFilePath)
        subprocess.call(SystemCommand)
        time.sleep(15)

    def fnUpdateRawBlob(pRawBlobFileName):
        with open(pRawBlobFileName, 'rb') as fpHandle:
            print("Uploading '", pRawBlobFileName, "' Raw Blob! Please Wait...!")
            BlobArrList = list(fpHandle.read())
            fpHandle.close()
            # print([hex(x) for x in bytes(BlobArrList)])

            # BlobArrList contains all the bytes from the Blobfile.

            # Get the iteration count
            iterationCount = int(len(BlobArrList) / MAX_BLOB_PACKET_LIMIT)
            iterationExtra = int(len(BlobArrList) % MAX_BLOB_PACKET_LIMIT)

            # print(iterationCount, iterationExtra)

            if 0 != iterationExtra:
                # Append the list with 0xff
                for iCount in range(MAX_BLOB_PACKET_LIMIT - iterationExtra):
                    BlobArrList.append(0xff)  # pad with 0xff

            # Get the iteration count Again
            iterationCount = int(len(BlobArrList) / MAX_BLOB_PACKET_LIMIT)
            iterationExtra = int(len(BlobArrList) % MAX_BLOB_PACKET_LIMIT)

            #print(iterationCount, iterationExtra)
            initime = time.time()
            # print('Using Multiple SER CMDs : ', SERIALCMD_BLOB_DATA_PACKET)
            for iCount in range(iterationCount):
                #print(iCount, iterationCount)
                CurrLocation = (iCount * MAX_BLOB_PACKET_LIMIT)
                NextLocation = ((iCount + 1) * MAX_BLOB_PACKET_LIMIT)

                CurrLocAddr = [0x00, 0x00, 0x00, 0x00]
                CurrLocAddr[0] = ((CurrLocation & 0x000000ff) >> 0)
                CurrLocAddr[1] = ((CurrLocation & 0x0000ff00) >> 8)
                CurrLocAddr[2] = ((CurrLocation & 0x00ff0000) >> 16)
                CurrLocAddr[3] = ((CurrLocation & 0xff000000) >> 32)
                # print([hex(x) for x in CurrLocAddr])

                # Get the current blob packet using the location details.
                CurrBlobPacket = BlobArrList[CurrLocation:NextLocation]
                # print([hex(x) for x in CurrBlobPacket])

                # 1 byte 0xAA + 2 Byte Size + 1 byte Command ID + 4 bytes location + MAX_BLOB_PACKET_LIMIT Data Bytes +  2 byte CRC = 970 = 0x03CA
                BlobPacketFrame = [0xAA, 0x00, 0x00, SERIALCMD_BLOB_DATA_PACKET] + CurrLocAddr + CurrBlobPacket
                BlobPacketLen = len(BlobPacketFrame) + 2
                BlobPacketFrame[1] = ((BlobPacketLen & 0x00ff) >> 0)  # copy the length low byte
                BlobPacketFrame[2] = ((BlobPacketLen & 0xff00) >> 8)  # copy the length high byte

                CurrCRC = [0x00, 0x00]
                crcValue = CRC16(0, BlobPacketFrame)
                CurrCRC[0] = ((crcValue & 0x00ff) >> 0)
                CurrCRC[1] = ((crcValue & 0xff00) >> 8)
                BlobPacketFrame.append(CurrCRC[0])  # copy the CRC low byte
                BlobPacketFrame.append(CurrCRC[1])  # copy the CRC high byte

               # print("Before writing ... ", BlobPacketFrame)

                # print([hex(x) for x in BlobPacketFrame])
                pSerialHandle.write(BlobPacketFrame)
                # print('CMD Frame sent:', BlobPacketFrame)
                fnReadAndPrintReply(False)
            exittime= time.time()
            print("Blob Upload Complete")
            timediff = exittime-initime
            # print("init, exit, diff ", initime, exittime, timediff)

    def fnResetHandle():
        ResetChallengeData = [200, 5, 173, 96, 210, 13, 66, 12, 127, 42]
        cmdFrame = fnCreateFrame(SERIALCMD_RESET_DEVICE, ResetChallengeData)
        pSerialHandle.write(cmdFrame)
        # print('SER CMD sent: ', SERIALCMD_RESET_DEVICE)
        fnReadAndPrintReply(False)

    # --------------------- main -----------------------
    #
    # now = datetime.now()
    # print('DATE & TIME: ', now)

    # Create the Raw Blob file
    fnCreateRawBlob(BLOB_FILE_PATH, RAW_BLOB_FILE_PATH)

    if os.path.exists(RAW_BLOB_FILE_PATH):
        #  Open the Serial Port.
        pSerialHandle = serial.Serial(PowerPackComPort, 115200, bytesize=8, parity='N', stopbits=1, timeout=None,
                                      xonxoff=0)
        serial.Serial()
        pSerialHandle.flush()

        # print("Serial", SIGNIA_USB_SERIAL_COM_PORT, "Port Opened")

        # Get the handle Serial Number
        # fnSendCmdAndGetReply(SERIALCMD_GET_SERIALNUM)

        # Start the update by sending the SERIALCMD_BLOB_DATA_SETUP command; this erases the existing BlobFile in the SD card.
        fnSendCmdAndGetReply(SERIALCMD_BLOB_DATA_SETUP)

        fnUpdateRawBlob(RAW_BLOB_FILE_PATH)

        # Send the Blob Validate Command
        fnSendCmdAndGetReply(SERIALCMD_BLOB_DATA_VALIDATE)

        # Send the following commands to force the Handle, Bootloader and FPGA update
        fnSendCmdAndGetReply(SERIALCMD_ERASE_HANDLE_TIMESTAMP)
        fnSendCmdAndGetReply(SERIALCMD_ERASE_HANDLE_BL_TIMESTAMP)
        fnSendCmdAndGetReply(SERIALCMD_ERASE_JED_TIMESTAMP)

        # Reset the Handle to complete the update.
        fnResetHandle()

        #  Flush and then Close the Serial Port.
        pSerialHandle.flush()
        pSerialHandle.close()

       # print("Serial", SIGNIA_USB_SERIAL_COM_PORT, "Port Closed")
        print("Update Complete, Resetting the Handle! Please Wait...!")

        os.remove(RAW_BLOB_FILE_PATH)
    else:
        print("Update Failed, The " + RAW_BLOB_FILE_PATH + " does not exist")
    #return(result_path)
    return ()

#https://wiki.python.org/moin/UdpCommunication
#https://v1993.github.io/cemuhook-protocol/

import socket
from tkinter import EventType
import keyboard
import binascii
import numpy as np

def bytes_to_int(n):
    o = 0
    for i in n:
        o = (o << 8) + int(i)
    return o

def bytes_to_int_rev(n):
    o = 0
    for i in reversed(n):
        o = (o << 8) + int(i)
    return o

def int_to_byte_array(n, num):
    return [int(digit) for digit in np.binary_repr(n,width=num)]

def split_int_32(n):
    return [n >> 24 & 0xff, n >> 16 & 0xff, n >> 8 & 0xff, n & 0xff]

def split_int_16(n):
    return [n >> 8 & 0xff, n & 0xff]

def split_int_48_rev(n):
    return [n & 0xff, n >> 8 & 0xff, n >> 16 & 0xff, n >> 24 & 0xff, n >> 32 & 0xff, n >> 40 & 0xff]

def split_int_32_rev(n):
    return [n & 0xff, n >> 8 & 0xff, n >> 16 & 0xff, n >> 24 & 0xff]

def split_int_16_rev(n):
    return [n & 0xff, n >> 8 & 0xff]


class CEMUMessage:
    def __init__(self, data):
        CRCTestPacket = [data[i:i + 1] for i in range(0, len(data), 1)]
        #print(CRCTestPacket)
        CRCTestPacket[8] = b'\x00'
        CRCTestPacket[9] = b'\x00'
        CRCTestPacket[10] = b'\x00'
        CRCTestPacket[11] = b'\x00'
        #print(CRCTestPacket)
        CRCTestPacketCombined = b''
        for i in CRCTestPacket:
            CRCTestPacketCombined += i
        self.intendedCRC32 = binascii.crc32(CRCTestPacketCombined)

        self.bytes = data#[data[i:i + 1] for i in range(0, len(data), 1)]
        self.owner =self.bytes[0:4].decode('UTF-8')
        self.protocol = bytes_to_int_rev(self.bytes[4:6]) & 0xffff
        self.length = bytes_to_int_rev(self.bytes[6:8]) & 0xffff
        self.CRC32 = bytes_to_int_rev(self.bytes[8:12]) & 0xffffffff
        self.senderID = bytes_to_int_rev(self.bytes[12:16]) & 0xffffffff
        self.eventType = bytes_to_int_rev(self.bytes[16:20]) & 0xffffffff
        self.type = 0 # 0 is Blank, 1 is protocol info, 2 is info about connected controllers, 3 is actual controller data
        if(self.eventType == 1048576):
            self.type = 1
        elif(self.eventType == 1048577):
            self.type = 2
        elif(self.eventType == 1048578):
            self.type = 3
        self.data = self.bytes[20:32]

        # self.controllerID, self.controllerType,
        # if(self.eventType == 2 || self.eventType = 3):
            



    def print(self):
        print("---------")
        print("Owner: %s" % self.owner)
        print("Protocol: %s" % self.protocol)
        print("Length: %s" % self.length)
        print("Intended CRC32: %s" % self.intendedCRC32)
        print("Recieved CRC32: %s" % self.CRC32)
        print("Sender ID: %s" % self.senderID)
        print("Event Type: 0x%x" % self.eventType)
        print("Data: ",end="")
        if(self.type == 2):
            if(self.owner == "DSUS"):
                print()
                print("- ID: #%i" % (int.from_bytes(self.data[0:1], "big") + 1), )
                print("- Connected?: %i" % int.from_bytes(self.data[1:2], "big"))
                print("- Model: %i" % int.from_bytes(self.data[2:3], "big"))
                print("- Connection: %i" % int.from_bytes(self.data[3:4], "big"))
                print("- MAC: 0x%x" % int.from_bytes(self.data[4:10], "big"))
                print("- Battery: 0x%x" % int.from_bytes(self.data[10:11], "big"))
            elif(self.owner == "DSUC"):
                print()
                num = int.from_bytes(self.data[0:4], "big")
                print("- # of Controller: %i" % num)
                print("- Controllers: ", end="")
                for i in self.data[4:4+num]:
                    print(i, end="")
                    print(", ", end="")
                print()

        else:
            print(self.data)
        print("---------")

    @staticmethod
    def construct(id, eventType, data):
        message = bytearray()
        message += b'DSUS'
        message += b'\xe9' + b'\x03'
        message += bytearray(split_int_16_rev(len(data) + 4))
        message += b'\x00\x00\x00\x00' #CRC32 PLACEHOLDER
        message += bytearray(split_int_32_rev(id))
        message += bytearray(split_int_32_rev(eventType))
        message += data
        crc = split_int_32_rev(binascii.crc32(message))
        for i in range(4):
            message[8 + i] = crc[0 + i]
        #print(returnMsg)
        return CEMUMessage(message)

    def constructResponse(id, eventType, controllerID, connectStatus, controllerType, connectType, MAC, battery, data = b'\0'):
        packet = bytearray([controllerID, connectStatus, controllerType, connectType])
        packet += bytearray(split_int_48_rev(MAC))
        packet += bytearray([battery])
        packet += data
        return CEMUMessage.construct(id, eventType, packet)

UDP_IP = "127.0.0.1"
UDP_PORT = 26761

sock = socket.socket(socket.AF_INET, # Internet
                     socket.SOCK_DGRAM) # UDP
sock.bind((UDP_IP, UDP_PORT))

while True:
    data, addr = sock.recvfrom(128) # buffer size is 1024 bytes
    #bytes = [data[i:i + 1] for i in range(0, len(data), 1)]
    rxMsg = CEMUMessage(data)
    rxMsg.print()

    txMsg = CEMUMessage.construct(28592813,0x100001,b'\x00\x01\x02\x02\x00\x00\x00\x00\x00\x00\x04\x00')
    txMsg.print()
    atxMsg = CEMUMessage.constructResponse(28592813,0x100001,0,1,2,2,0,3)
    atxMsg.print()

    try:  # used try so that if user pressed other than the given key error will not be shown
        if keyboard.is_pressed('home'):  # if key 'q' is pressed
            print('Quit!')
            exit()
    except:
        continue
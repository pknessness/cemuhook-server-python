#https://wiki.python.org/moin/UdpCommunication
#https://v1993.github.io/cemuhook-protocol/

import socket
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


class CEMUMessage:
    def __init__(self, data):
        CRCTestPacket = [data[i:i + 1] for i in range(0, len(data), 1)]
        print(CRCTestPacket)
        CRCTestPacket[8] = b'\x00'
        CRCTestPacket[9] = b'\x00'
        CRCTestPacket[10] = b'\x00'
        CRCTestPacket[11] = b'\x00'
        print(CRCTestPacket)
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
        print(self.data)
        print("---------")

    @staticmethod
    def construct(id, eventType, data):
        message = b''
        message += b'DSUS'
        message += b'\xe9' + b'\x03'
        lenBytes = bytearray(int_to_byte_array(len(data) + 4,16))
        print(lenBytes)
        for i in reversed(lenBytes):
            message += bytes(i) #THIS MIGHT NOT WORK????
        #message += b'\x00\x00\x00\x00' #CRC32 PLACEHOLDER
        #message += reversed(int_to_byte_array(id), 32)
        #message += reversed(int_to_byte_array(eventType), 32)
        #message += data
        print(message)
        #returnMsg = CEMUMessage(message)
        #print(returnMsg)
        exit()
        return 

UDP_IP = "127.0.0.1"
UDP_PORT = 26761

sock = socket.socket(socket.AF_INET, # Internet
                     socket.SOCK_DGRAM) # UDP
sock.bind((UDP_IP, UDP_PORT))

while True:
    data, addr = sock.recvfrom(128) # buffer size is 1024 bytes
    #bytes = [data[i:i + 1] for i in range(0, len(data), 1)]
    rxMsg = CEMUMessage(data)
    #rxMsg.print()

    txMsg = CEMUMessage.construct(28592813,0x100001,b'\x00\x01\x02\x02\x00\x00\x00\x00\x00\x00\x04\x00')
    txMsg.print()

    try:  # used try so that if user pressed other than the given key error will not be shown
        if keyboard.is_pressed('home'):  # if key 'q' is pressed
            print('Quit!')
            exit()
    except:
        continue
#https://wiki.python.org/moin/UdpCommunication
#https://v1993.github.io/cemuhook-protocol/

import socket
import keyboard

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


class CEMUMessage:
    def __init__(self, data):
        self.bytes = data#[data[i:i + 1] for i in range(0, len(data), 1)]
        self.owner =self.bytes[0:4].decode('UTF-8')
        self.protocol = bytes_to_int_rev(self.bytes[4:6]) & 0xffff
        self.length = bytes_to_int_rev(self.bytes[6:8]) & 0xffff
        self.CRC32 = bytes_to_int_rev(self.bytes[8:12]) & 0xffffffff
        self.senderID = bytes_to_int_rev(self.bytes[12:16]) & 0xffffffff
        self.eventType = bytes_to_int_rev(self.bytes[16:20]) & 0xffffffff

    def print(self):
        print("---------")
        print("Owner: %s" % self.owner)
        print("Protocol: %s" % self.protocol)
        print("Length: %s" % self.length)
        print("CRC32: %s" % self.CRC32)
        print("Sender ID: %s" % self.senderID)
        print("Event Type: %x" % self.eventType)
        print("---------")

UDP_IP = "127.0.0.1"
UDP_PORT = 26761

sock = socket.socket(socket.AF_INET, # Internet
                     socket.SOCK_DGRAM) # UDP
sock.bind((UDP_IP, UDP_PORT))

while True:
    data, addr = sock.recvfrom(128) # buffer size is 1024 bytes
    #bytes = [data[i:i + 1] for i in range(0, len(data), 1)]
    msg = CEMUMessage(data)
    msg.print()

    try:  # used try so that if user pressed other than the given key error will not be shown
        if keyboard.is_pressed('home'):  # if key 'q' is pressed
            print('Quit!')
            exit()
    except:
        continue
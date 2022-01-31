import sys
sys.path.append('../')

from libs.tinycc import TinyCC
import serial
import time


a = 1
b = 2
c = 3
d = 4
e = 5
print(type(a))
print(type(b))
print(type(c))
print(type(d))
print(type(e))
print(a.to_bytes(1, 'little'))
print(b.to_bytes(1, 'little'))
print(c.to_bytes(1, 'little'))
print(d.to_bytes(1, 'little'))
print(e.to_bytes(1, 'little'))

"""
ser = serial.Serial()

ser.baudrate = "9600"
ser.port = "COM14"
ser.open()
ser.write(b'\x02\x00\x01\xf2\x0b')

while True:
        bytesToRead = ser.inWaiting()
        if bytesToRead == 0:
            continue
        else:
            raw = ser.read(bytesToRead)
            print("RAW: {}".format(raw))




def readCcFrame
"""


def lettura_pacchetto(serial=None):

    pacchetto = []

    destination = serial.read(1)
    pacchetto.append(destination)
    #print("Destination: {}".format(destination))

    data_len = serial.read(1)
    pacchetto.append(data_len)
    #print("Data Len: {} ({})".format(data_len, ord(data_len)))

    source = serial.read(1)
    pacchetto.append(source)
    #print("Source: {}".format(source))

    header = serial.read(1)
    pacchetto.append(header)
    #print("Header: {}".format(header))

    if ord(data_len) > 0:
        data = serial.read(ord(data_len))
        pacchetto.append(data)


    checksum = serial.read(1)
    pacchetto.append(checksum)

    return pacchetto
    #return serial.read(1)


def lettura_raw(serial=None):


    destination = serial.read(1)

    return destination
    #return serial.read(1)



try:
    ser = serial.Serial()
    tc = TinyCC(ser)

    ser.baudrate = "9600"
    ser.port = "COM6"
    ser.open()

    while True:
        p = lettura_raw(ser)
        print("Pacchetto: {}".format(p))
        #bytesToRead = ser.inWaiting()
        #if bytesToRead == 0:
            #print("Nessuno messaggio")
        #    continue
        #print("Raw: {}".format(raw_response))
        #print("i    {} {}".format(raw_response, len(raw_response)))
        #raw_response = ser.read(bytesToRead)
        #print(raw_response)
        #response = tc.analyze_ret(response=raw_response, sent_len=len(raw_response))
        #print("Response: {}".format(response))
        #time.sleep(.2)

except Exception as e:
    print(e)

#"""
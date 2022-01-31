import sys
import time
from struct import pack, unpack

from libs.console import *


class TinyCC:
    def __init__(self, ser):


        self.lock = False

        # The time a send_command should wait before triyng to gain the lock.
        self.lock_wait_time = .1

        # Time that TinyCC waits for the CCTalk to answer
        self.response_timeout = .3

        try:
            self.serial = ser

        except Exception as e:
            exit(1)
        pass

    def send_command(self, command, args, dest, src, is_slow=False):

        while self.lock:
            #print "{} LOCKED-Should stop..".format(addr)
            self.lock_wait_time = .1

        try:
            #print "{} GOT CONTROL B) ".format(addr)
            self.lock = True
            byte_message, int_message = self.create_msg(command, args, to_slave_addr=dest, from_host_addr=src)
            #debug("SENDING-{}".format(int_message))
            print("Sent byte   -{}".format(byte_message))
            print("Int message -{}".format(int_message))
            byte_sent = self.serial.write(byte_message)
            #print("Bytes sent-{}".format(byte_sent))
            # Wait for a response
            time.sleep(2)
            raw_response = self.serial.read_all()


            print("RAW: {}".format(raw_response))

            if raw_response == b'':
                print("La risposta è vuota")
                return byte_sent, []
#print("Raw Response-{}".format(raw_response))
            response = self.analyze_ret(raw_response, len(raw_response))
            print("Response-{}".format(response))
            self.lock = False
        except Exception as e:
            self.lock = False
            print(sys.exc_info())
            exception("Cannot send message via serial, releasing the lock")
            return False

        return byte_sent, response

    def create_msg(self, code, data=None, to_slave_addr=2, from_host_addr=1):


        # Check if data is not empty to create data_len field.
        if not data:
            data_len = 0
        else:
            data_len = len(data)


        data_sequence = [to_slave_addr, data_len, from_host_addr, code] + data
        packet_sum = 0

        for i in data_sequence:
            packet_sum += i

        end_byte = self.get_checksum(packet_sum)

        packet = data_sequence + [end_byte]



        return self.pack_message(packet), packet

        #return packet, packet

    def analyze_ret(self, response, sent_len):

        #print("Analizzo la risposta")
        #print("Respose len-{}".format(sent_len))
        response_len = len(response)

        # Unpacking response from byte to hex
        out_byte = unpack('={0}c'.format(int(response_len)), response)
        #print("Out bytes -{}".format(out_byte))
        # Mapping hex to int
        out_int = list(map(ord, out_byte))
        #print("Out int -{}".format(out_int))
        #resp = out_int[sent_len:]
        #print("Resp -{}".format(resp))
        return self.split_response(out_int)

    @staticmethod
    def pack_message(packet):
        #print(packet)
        sent_len = len(packet)
        #byte_msg = list(map(to_bytes(1, 'big'), packet))
        byte_msg = []


        for p in packet:
            #print("Packet-{} {}".format(type(p), p))
            bp = p.to_bytes(1, 'little')
            byte_msg.append(bp)
            #print("BP Packet-{} {}".format(type(bp), bp))



        #print( "{} {}".format(sent_len, byte_msg))
        message = pack('={0}c'.format(int(sent_len)), *byte_msg)


        return message

    @staticmethod
    def split_response(response):
        print(response)
        res = {}
        #debug("RESPONSE DATA  -{}".format(response))
        res['sender'] = response[0]
        res['n_args'] = response[1]
        res['receiver'] = response[2]
        res['header'] = response[3]
        res['data'] = response[4:(4 + res['n_args'])]
        res['sum'] = response[-1:]
        #debug("SPLIT RESP. DATA-{}".format(res))
        return res


    @staticmethod
    def byte_to_string(byte):
        return ''.join(map(chr, byte))

    @staticmethod
    def get_checksum(packet_sum):
        checksum = 256 - (packet_sum % 256)
        return checksum



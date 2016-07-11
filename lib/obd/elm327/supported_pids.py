import time

from lib.obd import serial_communicator
from lib.obd.elm327.pid import Pid

class SuportedPids():
    try_count = 3

    def __init__(self, communicator, debug=False):
        self.serial = communicator

    def read(self, mode, ids=[0x0, 0x20, 0x40, 0x60, 0x80]):
        supported = {}

        data_rate = self.current_settings['data_rate']

        for origin in ids:
            response = self.serial.query(self.to_s(mode, origin), data_rate)

            count = 0
            while response[0].startswith("7F"):
                if count > self.try_count:
                    response = ['NO DATA']
                    break
                response = self.serial.query(self.to_s(mode, origin), data_rate)
                count += 1

            result = self.parse(response, mode, origin)

            supported.update(result)

        for origin in ids:
            if origin in supported:
                del supported[origin]

        return supported

    def validate(self, response, mode, id):
        response_mode = int(self.bytes(response)[0]) - 40
        response_id = self.bytes(response)[1]

        identifier = "%02d %s" % (response_mode, response_id)

        return identifier == self.to_s(mode, id)

    def parse(self, response, mode, origin):
        result = {}

        if not response or response[0] == 'NO DATA' or not self.validate(response[0], mode, origin):
            return result

        info = "".join(self.bytes(response[0])[2:])

        binary_rep = ""

        for byte in info:
            binary_rep += bin(int(byte, 16))[2:].zfill(4)

        counter = origin + 1
        for bit in binary_rep:
            result[counter] = bit == "1"
            counter += 1

        return result

    def to_s(self, mode, value):
        return ("%02d %s" % (mode, self.dec_to_hex(value))).upper()

    def dec_to_hex(self, value):
        return "{0:#0{1}x}".format(int(value), 4)[2:]

    def bytes(self, response_line):
        return response_line.strip().split(" ")
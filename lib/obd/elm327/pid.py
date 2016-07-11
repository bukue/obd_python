import time

from lib.obd import serial_communicator
from lib.ui import config

class Pid():
    def __init__(self, communicator, debug=False):
        self.serial = communicator
        self.read_config()

    def read(self, mode, id):
        self.mode = mode
        self.id = id

        data_rate = self.current_settings['data_rate']
        self.response = self.serial.query(self.to_s(), data_rate)

        accum = data_rate
        while self.response and (self.response[0].startswith("7F") or self.response[0] in ['STOPPED']):
            if accum > data_rate*10:
                self.response = ['NO DATA']
                break
            self.response = self.serial.query(self.to_s(), accum)
            accum += data_rate

        if self.response:
            return self.parse()
        else:
            return None

    def to_s(self):
        return ("%02d %s" % (self.mode, self.dec_to_hex(self.id))).upper()

    def validate(self):
        mode = int(self.bytes()[0]) - 40
        id = self.bytes()[1]

        identifier = "%02d %s" % (mode, id)

        return identifier == self.to_s()

    def bytes(self):
        return self.response[0].strip().split(" ")

    def parse(self):
        if not self.response or self.response[0] == 'NO DATA':
            return None

        if not self.validate():
            return False

        value = self.value()

        return str(value)

    def dec_to_hex(self, number):
        return "{0:#0{1}x}".format(number,4)[2:]

    def value(self):
        return int("".join(self.bytes()[2:]), 16)

    def read_config(self):
        self.current_settings = config.Config().read()


from lib.obd import serial_communicator
from lib.ui import config

class Ecu():
    mode = '01'
    id = '00'

    def __init__(self, communicator, debug=False):
        self.serial = communicator
        self.read_config()

    def read(self):
        self.serial.headers(True)

        data_rate = self.current_settings['data_rate']

        query = "%s %s" % (self.mode, self.id)
        self.response = self.serial.query(query, data_rate)

        self.serial.headers(False)

        return self.parse()

    def parse(self):
        if not self.validate():
            return False

        hex_result = []

        for line in self.response:
            bytes = line.strip().split(" ")

            owner = bytes[2]

            if index == 1:
                bytes = [byte for byte in bytes if byte != "00" ]

                hex_result += bytes

        ascii_vin = [bytearray.fromhex(byte).decode() for byte in hex_result]

        return "".join(ascii_vin)

    def read_config(self):
        self.current_settings = config.Config().read()
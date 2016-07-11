from lib.obd import serial_communicator
from lib.ui import config

class Vin():
    mode = '09'
    id = '02'

    def __init__(self, communicator, debug=False, protocol=None):
        self.serial = communicator
        self.protocol = protocol

        self.read_config()

    def read(self):
        self.serial.headers(0)

        data_rate = self.current_settings['data_rate']

        query = "%s %s" % (self.mode, self.id)
        self.response = self.serial.query(query, data_rate)

        return self.parse()

    def is_can(self):
        return self.protocol.startswith("ISO 15765-4")

    def response_validation_string(self):
        return "49 %s" % self.id

    def validate(self):
        if self.is_can():
            response_validation = " ".join(self.response[1].strip().split(" ")[1:3])

            if response_validation != self.response_validation_string():
                return False

            for index in range(1,4):
                line = self.response[index]

                bytes = line.strip().split(" ")

                if bytes[0] != ("%d:" % (index-1)):
                    return False
        else:
            for index in range(1,6):
                line = self.response[index-1]

                if not line.startswith(self.response_validation_string()):
                    return False

                bytes = line.strip().split(" ")[2:]

                if bytes[0] != "%02d" % index:
                    return False

        return True

    def parse(self):
        if not self.response or self.response[0] == 'NO DATA':
            return None

        if not self.validate():
            return False

        hex_vin = []

        if self.is_can():
            for index in range(1,4):
                line = self.response[index]

                bytes = line.strip().split(" ")

                if index == 1:
                    bytes = bytes[4:]
                else:
                    bytes = bytes[1:]

                hex_vin += bytes
        else:
            for index in range(1,6):
                line = self.response[index-1]

                bytes = line.strip().split(" ")[3:]

                if index == 1:
                    bytes = [byte for byte in bytes if byte != "00" ]

                hex_vin += bytes

        ascii_vin = [bytearray.fromhex(byte).decode() for byte in hex_vin]

        return "".join(ascii_vin)

    def read_config(self):
        self.current_settings = config.Config().read()

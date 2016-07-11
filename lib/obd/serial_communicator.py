import serial
import calendar
import time
import logging

from PyQt4.QtCore import QObject, pyqtSignal


class SerialCommunicator(QObject):
    def __init__(self, port, bps=9600, timeout=0.125, debug=False, data_rate=0.0):
        super(SerialCommunicator, self).__init__()

        self.debugging = debug
        self.data_rate = data_rate

        self.connected_to_hardware = False

        logging.basicConfig(
            filename = self.log_path(),
            level = logging.DEBUG,
            format = '%(asctime)s %(message)s',
            datefmt='%m/%d/%Y %I:%M:%S %p'
        )

        try:
            self.connection = serial.Serial(port, bps, timeout=timeout)
        except Exception as inst:
            self.debug(inst)
            raise

    def log_folder(self):
        return "logs/"

    def connect(self, max_tries = 10):
        if self.connection.isOpen():
            self.connection.close()

        self.connection.open()

    def disconnect(self):
        if self.connection.isOpen():
            self.connection.close()

    def write(self, command):
        if type(command) is int:
            formatted_command = "%d\r\n" % command
        else:
            formatted_command = "%s\r\n" % command

        return self.connection.write(formatted_command.encode())

    def read(self):
        return self.connection.readline()[:-2].decode("utf-8")

    def query(self, command, wait_time=0.0):
        self.write(command)
        self.connection.flush()
        time.sleep(wait_time)
        result = self.read()

        return result

    def debug(self, message, level=0):
        message_for_log = "(%d) %s %s" % (level, "*"*level, message)

        if self.debugging:
            print(message_for_log)

        logging.debug(message_for_log)

    def get_hex(self, level, value):
        return "%s%s" % ('{0:02x}'.format(level), '{0:02x}'.format(value))

    def log_path(self):
        return "%s/%d.log" % (self.log_folder(), calendar.timegm(time.gmtime()))

    def is_alive(self):
        if self.is_reading():
            return 0

        if self.connect():
            return 1
        else:
            return -1
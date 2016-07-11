from lib.obd import serial_communicator
from my_collections import pids

from lib.obd.elm327.vin import Vin
from lib.obd.elm327.pid import Pid
from lib.obd.elm327.monitor import Monitor
from lib.obd.elm327.calid import Calid
from lib.obd.elm327.supported_pids import SuportedPids

import time
from random import randint

from PyQt4.QtCore import QObject, pyqtSignal

from lib.ui import config

class Elm327(serial_communicator.SerialCommunicator):

    connected = pyqtSignal()

    all_pids = pids.PIDs().by_id()
    counter = -1

    protocol_map = {
            "Auto": 0,
            "J1850 PWM" : 1,
            "SAE J1850 PWM" : 1,
            "J1850 VPW" : 2,
            "SAE J1850 VPW" : 2,
            "ISO 9141-2" : 3,
            "ISO 14230-4 (KWP 5BAUD)" : 4,
            "ISO 14230-4 (KWP FAST)" : 5,
            "ISO 15765-4 (CAN 11/500)" : 6,
            "ISO 15765-4 (CAN 29/500)" : 7,
            "ISO 15765-4 (CAN 11/250)" : 8,
            "ISO 15765-4 (CAN 29/250)" : 9
        }

    def __init__(self):
        self.read_config()

    def initialize(self, port, bps=38400, timeout=0.125, debug=False, data_rate=0.0):
        data_rate = self.current_settings['data_rate']
        super(Elm327, self).__init__(port, bps, timeout, debug, data_rate)

        self.echo(False)

    def query(self, command, wait_time=0.0):
        if wait_time == 0:
            wait_time = self.data_rate

        result = super(Elm327, self).query(command, wait_time).strip().split('\r')

        return [x for x in result if x]

    def query_protocol(self):
        self.headers(False)

        try:
            result = self.query("AT DP")[0]

            if result.startswith("AUTO"):
                protocol = self.query("AT DP")[0].split(',')[1]
            else:
                protocol = self.query("AT DP")[0]
        except:
            protocol = "ERROR"

        return protocol.strip()

    def connect(self, max_tries = 10):
        super().connect(max_tries)

        count = 0
        while not self.connected_to_hardware:
            response = self.info()[0]

            self.debug("attempting communication %s." % response, 3)

            if response == "ELM327 v1.5":
                self.debug("Succesfully established communication with car.", 3)
                self.connected_to_hardware = True
            elif count > max_tries:
                self.debug("Could not establish communication with car.", 3)
                self.connected_to_hardware = False
                break

        return self.connected_to_hardware

    def reset(self):
        return self.query("ATZ")

    def info(self):
        return self.query("ATI")

    def echo(self, status):
        status_string = "E%d" %(1 if status else 0)
        return self.query("AT%s" % status_string)

    def headers(self, status):
        status_string = "H%d" %(1 if status else 0)
        return self.query("AT%s" % status_string)

    def protocol(self, name, sleep=15):
        self.query("AT SP %d" % self.protocol_map[name])

        self.query("01 00")

        self.debug("Finding car protocol.", 3)

        time.sleep(sleep)

        self.protocol_name = self.query_protocol()

        self.debug("Protocol found: %s" % self.protocol_name, 3)

        self.emit_connected()

    def emit_connected(self):
        self.connected.emit()

    def status(self):
        return (self.counter/len(self.all_pids))*100.0

    def is_reading(self):
        return False if self.counter < 0 else True

    def get_all_pids(self, rate, mode):
        pids_dict = {}

        self.counter = 0

        self.read_config()

        if self.connect():
            if self.current_settings["fast"]:
                supported_values = {pid:supported for (pid,supported) in SuportedPids(self).read(mode).items() if supported}
            else:
                supported_values = {pid:True for (pid,data) in pids.PIDs().by_id().items()}

            self.headers(False)

            values = {}
            while supported_values:
                pid, supported = supported_values.popitem()

                if pid == 0x1:
                    pid_value = Monitor(self).read()
                else:
                    pid_value = Pid(self).read(mode, pid)

                if pid_value:
                    values[pid] = pid_value
                elif self.current_settings["fast"]:
                    supported_values[pid] = supported

            for pid, value in values.items():
                pid_name = self.all_pids[pid]
                pids_dict[pid] ={
                    'name': pid_name,
                    'value': value
                }

            self.debug("Connection with car has ended", 3)

        self.counter = -1

        self.debug(pids_dict)

        return pids_dict

    def get_vin(self):
        return Vin(self, False, self.protocol_name).read()

    def get_calid(self):
        return Calid(self, False, self.protocol_name).read()

    def status(self):
        return 50

    def is_reading(self):
        return True

    def read_config(self):
        self.current_settings = config.Config().read()


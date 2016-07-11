from lib.obd import serial_communicator
from my_collections import pids


class Adapter(serial_communicator.SerialCommunicator):
    all_pids = pids.PIDs().by_name()
    counter = -1

    def connect(self, max_tries = 10):
        super

        count = 0
        while True:
            response = self.query(0,1)

            self.debug("attempting communication %s." % response, 3)

            if response == "READY":
                self.debug("Succesfully established communication with car.", 3)
                return True
            elif count > max_tries:
                self.debug("Could not establish communication with car.", 3)
                return False

    def get_all_pids(self, rate):
        pids_dict = {}

        self.counter = 0

        if self.connect():
            for pid_name, data in self.all_pids.items():
                self.counter += 1

                pid_id = data["id"]
                pid_value = self.query(pid_id, rate)

                pids_dict[pid_id] = {
                    'name': pid_name,
                    'value': pid_value
                }

                self.debug("%s (%s): %s" % (pid_name, pid_id, pid_value), 0)

            self.debug("Connection with car has ended", 3)

        self.counter = -1

        self.debug(pids_dict)

        return pids_dict

    def status(self):
        return (self.counter/len(self.all_pids))*100.0

    def is_reading(self):
        return False if self.counter < 0 else True
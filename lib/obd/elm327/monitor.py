from lib.obd import serial_communicator
from lib.obd.elm327.pid import Pid

class Monitor(Pid):
    def read(self, mode=0x1, id=0x1):
        return super(Monitor, self).read(mode, id)

    def value(self):
        return "".join(self.bytes()[2:])
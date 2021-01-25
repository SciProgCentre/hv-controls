import sys, pylibftdi as ftdi
from typing import Optional, Callable, List


class FTDIDevice:
    def __init__(self, device: ftdi.Device):
        self.device = device
        self.name = device.name
        # OPS = 0x03
        # device.ftdi_fn.ftdi_set_bitmode(OPS, 2)  # TODO(Select correct bit mode)

    def open(self):
        self.device.open()

    def close(self):
        self.device.close()

    def write(self, code : int, data: List[int]=None):
        temp = bytes([code, data]) if data is not None else bytes(code)
        self.device.write(temp)

    def read(self, nbytes) -> List[int]:
        s = self.device.read(nbytes)
        return [ord(c) for c in s] if type(s) is str else list(s)

    @staticmethod
    def find_all_device(key: Optional[Callable] = None):
        devices = []
        dev_list = filter(key, ftdi.Driver().list_devices())
        for dev in dev_list:
            temp = ftdi.Device(dev[2], lazy_open=True)
            temp.name = dev[2]
            devices.append(temp)
        return devices

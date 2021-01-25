import sys, ftd2xx
from typing import Optional, Callable, List


class FTD2XXDevice:
    """
    Полезные ссылки для реализации этого класса
https://iosoft.blog/2018/12/02/ftdi-python-part-1/
https://iosoft.blog/2018/12/05/ftdi-python-part-2/
https://iosoft.blog/2018/12/05/ftdi-python-part-3/
    """
    def __init__(self, device):
        self.device = device
        # OPS = 0x03
        # set_bitmode(OPS, 2)  # TODO(Select correct bit mode)

    def open(self):
        pass

    def close(self):
        pass

    def write(self, code : int, data: List[int]=None):
        pass

    def read(self, nbytes) -> List[int]:
        pass

    @staticmethod
    def find_all_device(key: Optional[Callable] = None):
        devices = []
        return devices

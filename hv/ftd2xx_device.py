import sys, ftd2xx
from typing import Optional, Callable, List


class FTD2XXDevice:
    """
    """
    def __init__(self, device):
        self.device = device

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

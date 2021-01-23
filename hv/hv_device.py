import abc

import usb.core
import os, sys
import pathlib

ROOT_PATH = pathlib.Path(__file__).parent.absolute()
#
# BACKEND = None
#
# if sys.platform.startswith("win32"):
#     import usb.backend.libusb1
#     path = pathlib.Path(ROOT_PATH, "..",
#                         "libusb-1.0.24", "MinGW64", "dll",
#                         "libusb-1.0.dll")
#     BACKEND = usb.backend.libusb1.get_backend(find_library=lambda x: path)
#     print(BACKEND)


class DeviceInfoFormatter(abc.ABC):
    @abc.abstractmethod
    def format(self, device) -> str:
        pass


class TextFormatter(DeviceInfoFormatter):

    def format(self, device) -> str:
        text = ""
        text += "Device class: {}".format(device.bDeviceClass)
        return text


class HVDevice:

    def __init__(self, device):
        self.device = device

    def set_value(self, value):
        pass

    def update_value(self):
        pass

    def reset_value(self):
        pass

    def get_IU(self):
        pass

    @staticmethod
    def find_usb_devices():
        devices = usb.core.find(find_all=True)
        return [HVDevice(dev) for dev in devices]

    def device_info(self, formatter = TextFormatter()):
        return formatter.format(self.device)

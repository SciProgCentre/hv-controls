import abc
from dataclasses import dataclass
from typing import List

import usb.core
import os, sys
import pathlib
import random

ROOT_PATH = pathlib.Path(__file__).parent.absolute()
DEVICE_PATH = pathlib.Path(ROOT_PATH, "device_data")

"""
Этот флаг определяет какой драйвер мы будет использовать FTD2XX или FTDI
Они оба кросплатформенные, однако вероятнее FTD2XX лучше использовать на windows,а FTDI на *nix
Полезные ссылки:
https://iosoft.blog/2018/12/02/ftdi-python-part-1/
https://iosoft.blog/2018/12/05/ftdi-python-part-2/
https://iosoft.blog/2018/12/05/ftdi-python-part-3/
"""
# FTD2XX = False
# if FTD2XX:
#     from ftd2xx_device import FTD2XXDevice as Device
# else:
#     from ftdi_device import FTDIDevice as Device

class DeviceInfoFormatter(abc.ABC):
    @abc.abstractmethod
    def format(self, device) -> str:
        pass


class TextFormatter(DeviceInfoFormatter):

    def format(self, device) -> str:
        text = ""
        text += "Device class: {}".format(device.bDeviceClass)
        return text


@dataclass
class DeviceData:
    name: str
    current_coeff: float
    voltage_coeff: float

class HVDevice:

    MANUFACTUTER = "Mantigora" # See Unit1.pas

    SET_CODE = 0x01
    UPDATE_CODE = 0x02
    RESET_CODE = 0x03
    RESERVE_CODE = 0x04
    GET_CODE = 0x05

    def __init__(self, device, data: DeviceData = None):
        self.device = device
        self.data = data

    def open(self):
        self.device.open()

    def close(self):
        self.device.close()

    def set_value(self, value):
        pass

    def update_value(self):
        pass

    def reset_value(self):
        pass

    def get_IU(self):
        return (random.random(), random.random())

    def device_info(self, formatter = TextFormatter()):
        return formatter.format(self.device)

    @staticmethod
    def find_all_devices() -> List["HVDevice"]:
        return []

    @staticmethod
    def find_new_devices(old) -> List["HVDevice"]:
        pass

    @staticmethod
    def load_device_data(name):

        def loaf_coeff(file, name):
            coeff = None
            with open(pathlib.Path(DEVICE_PATH, file)) as fin:
                for line in fin.readlines():
                    line = line.split(" ")
                    if line[0] == name:
                        coeff = float(line[1])
            return coeff

        voltage_coef = loaf_coeff("voltage.txt", name)
        current_coef = loaf_coeff("current.txt", name)
        return DeviceData(name, current_coef, voltage_coef)

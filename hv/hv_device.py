import abc
import math
from dataclasses import dataclass
from enum import Enum
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
FTD2XX = False
if FTD2XX:
    from hv.ftd2xx_device import FTD2XXDevice as Device
else:
    from hv.ftdi_device import FTDIDevice as Device


class DeviceInfoFormatter(abc.ABC):
    @abc.abstractmethod
    def format(self, device) -> str:
        pass


class TextFormatter(DeviceInfoFormatter):

    def format(self, device) -> str:
        return str(device.device) + "\n" + str(device.data)


@dataclass
class DeviceData:
    name: str
    codemax_ADC: int
    codemax_DAC: int
    voltage_max: float
    voltage_min: float
    voltage_step: float
    current_step: float
    polarity: str
    sensor_resistance: float
    feedback_resistanse: float
    current_min: float
    current_max: float
    current_units: str


class HVDevice:
    MANUFACTUTER = "Mantigora"  # See Unit1.pas

    SET_CODE = 0x01
    UPDATE_CODE = 0x02
    RESET_CODE = 0x03
    RESERVE_CODE = 0x04
    GET_CODE = 0x05

    def __init__(self, device, data: DeviceData = None):
        self.device = device
        self.data = data
        if data.current_units == "micro":
            self.units_label = "μA"
        else:
            self.units_label = "mA"

    def open(self):
        self.device.open()

    def close(self):
        self.device.close()

    def set_value(self, value):
        value = round(value * self.data.codemax / self.data.voltage_max)
        first_byte = value - math.trunc(value / 256) * 256
        second_byte = math.trunc(value / 256)
        self.device.write(HVDevice.SET_CODE, [first_byte, second_byte])

    def update_value(self):
        self.device.write(HVDevice.UPDATE_CODE)

    def reset_value(self):
        self.device.write(HVDevice.RESET_CODE)

    def get_IU(self):
        """
        Return Current (microA or milliA) and Voltage (V)
        """
        self.device.write(HVDevice.GET_CODE)
        temp = self.device.read(5)
        if temp is None or len(temp) < 5:
            print("Can not get data from device, data_array={}".format(str(temp)))
            return 0, 0
        if temp[4] != 13:
            print("Bad read: ", temp)
            return 0, 0
        U = (temp[2] * 256 + temp[3]) * self.data.voltage_max / self.data.voltage_max
        if self.data.polarity == "N": U = -U
        MAGIC_CONST = 4096 / 65535  # See Unit1.pas
        I = (temp[0] * 256 + temp[1]) * MAGIC_CONST * self.data.sensor_resistance
        k = 1
        if self.data.current_units == "мА": k = 0.001
        I = k * I
        # Subtract feedback resistance current
        I = I - abs(U * k / self.data.feedback_resistanse)
        return I, U

    def device_info(self, formatter=TextFormatter()):
        return formatter.format(self)

    @staticmethod
    def find_all_devices() -> List["HVDevice"]:
        devices = Device.find_all_device(lambda x: x == HVDevice.MANUFACTUTER)
        devices = [HVDevice(dev, HVDevice.load_device_data(dev.name)) for dev in devices]
        return devices  # + [create_test_device()]

    @staticmethod
    def find_new_devices(old) -> List["HVDevice"]:
        devices = Device.find_new_device(old, lambda x: x == HVDevice.MANUFACTUTER)
        devices = [HVDevice(dev, HVDevice.load_device_data(dev.name)) for dev in devices]
        return devices

    @staticmethod
    def load_device_data(name):
        with open(pathlib.Path(DEVICE_PATH, "device_table.csv")) as fin:
            fin.readline()
            for line in fin.readlines():
                line = line.split(",")
                if line[0] == name:
                    return DeviceData(name=name,
                                      codemax_ADC=int(line[1]),
                                      codemax_DAC=int(line[2]),
                                      voltage_max=float(line[3]),
                                      voltage_min=float(line[4]),
                                      voltage_step=float(line[5]),
                                      current_step=float(line[6]),
                                      polarity=line[7],
                                      sensor_resistance=float(line[8]),
                                      feedback_resistanse=float(line[9]),
                                      current_max=float(line[10]),
                                      current_min=float(line[11]),
                                      current_units=line[12].strip()
                                      )
        return None


def create_test_device():
    from hv.ftdi_device import FTDIDevice
    dev = FTDIDevice('Mantigora', 'HT6000P', '00001010')
    dev.open = lambda: None
    dev.close = lambda: None
    dev = HVDevice(dev, HVDevice.load_device_data(dev.name))
    dev.get_IU = lambda: (random.random(), random.random())
    dev.set_value = lambda x: print(x)
    dev.update_value = lambda: print("update")
    dev.reset_value = lambda: print("reset")
    return dev

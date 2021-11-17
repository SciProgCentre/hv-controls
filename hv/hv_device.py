import abc
import math
import time
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
    from hv.ftdi_device import PyFTDIDevice as Device


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
                                      current_min=float(line[10]),
                                      current_max=float(line[11]),
                                      current_units=line[12].strip()
                                      )
        return None

    def resolve_current_label(self):
        if self.current_units == "micro":
            return "μA"
        elif self.current_units == "milli":
            return "mA"
        else:
            return "μA"

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
        self.units_label = data.resolve_current_label()

    def __str__(self):
        return str(self.device)

    def open(self):
        self.device.open()

    def close(self):
        self.device.close()

    def set_value(self, voltage, current):
        voltage = round(voltage * self.data.codemax_DAC / self.data.voltage_max)
        first_byte_U = voltage - math.trunc(voltage / 256) * 256
        second_byte_U = math.trunc(voltage / 256)

        current = round(current * self.data.codemax_DAC / self.data.current_max)
        first_byte_I = current - math.trunc(voltage / 256) * 256
        second_byte_I = math.trunc(current / 256)
        self.device.write(HVDevice.SET_CODE, [first_byte_U, second_byte_U,
                                              first_byte_I, second_byte_I
                                              ])

    def update_value(self):
        self.device.write(HVDevice.UPDATE_CODE)

    def reset_value(self):
        self.device.write(HVDevice.RESET_CODE)
        time.sleep(1)

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
        ADC_mean_count = 16
        U = (temp[2] * 256 + temp[3]) * self.data.voltage_max / self.data.codemax_ADC / ADC_mean_count
        if self.data.polarity == "N": U = -U
        I = (temp[0] * 256 + temp[1]) * self.data.current_max / self.data.codemax_DAC
        if self.data.current_units == "micro":
            I = I - abs(U/ self.data.feedback_resistanse)
        elif self.data.current_units == "milli":
            I =I/1000
        return I, U

    @staticmethod
    def find_all_devices() -> List["HVDevice"]:
        devices = Device.find_all_device(lambda x: x == HVDevice.MANUFACTUTER)
        devices = [HVDevice(dev, DeviceData.load_device_data(dev.name)) for dev in devices]
        return devices  # + [create_test_device()]

    @staticmethod
    def find_new_devices(old) -> List["HVDevice"]:
        devices = Device.find_new_device(old, lambda x: x == HVDevice.MANUFACTUTER)
        devices = [HVDevice(dev, DeviceData.load_device_data(dev.name)) for dev in devices]
        return devices




def create_test_device():
    from hv.ftdi_device import PyFTDIDevice
    dev = PyFTDIDevice("TEST", "HT-60-30-P")
    dev.open = lambda: print("open")
    dev.close = lambda: print("close")
    dev = HVDevice(dev, DeviceData.load_device_data(dev.name))
    dev.get_IU = lambda: (random.random(), random.random())
    dev.set_value = lambda x,y: print(x,y)
    dev.update_value = lambda: print("update")
    dev.reset_value = lambda: print("reset")
    return dev

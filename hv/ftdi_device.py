import time
from typing import Optional, Callable, List

from pyftdi import ftdi
from pyftdi.usbtools import UsbTools
import pyftdi.serialext
import serial
from serial import EIGHTBITS, PARITY_NONE, STOPBITS_ONE
import logging

logger = logging.root

class FTDIDevice:

    BAUDRATE = 38400
    URLS = "ftdi"

    def __init__(self, url, name):
        self.port = None
        self.name = name
        self.url = url

    def __str__(self):
        return "{}: {}".format(self.name,self.url)

    def open(self):
        self.port = pyftdi.serialext.serial_for_url(self.url, bytesize=EIGHTBITS, parity=PARITY_NONE, stopbits=STOPBITS_ONE, baudrate = 38400)
        self.port.open()
        logger.info("Open serial port for {}".format(self))

    def close(self):
        self.port.close()
        self.port = None
        logger.info("Close serial port for {}".format(self))

    def write(self, code : int, data: List[int]=None):
        logger.debug("Write method get code : {}, data : {}".format(code, data))
        temp = bytes([code]+ data) if data is not None else bytes([code])
        logger.debug("Write {}".format(temp))
        self.port.write(temp)

    def read(self, nbytes) -> List[int]:
        time.sleep(0.5)
        s = self.port.read(nbytes)
        logger.debug("Read {}".format(s))
        result = [ord(c) for c in s] if type(s) is str else list(s)
        logger.debug("Convert read to {}".format(result))
        return result

    @staticmethod
    def find_all_device(key: Optional[Callable] = None):
        devspec = ftdi.Ftdi.list_devices()
        urls = UsbTools.build_dev_strings(FTDIDevice.URLS, ftdi.Ftdi.VENDOR_IDS, ftdi.Ftdi.PRODUCT_IDS, devspec)
        devices = []
        for url, name in urls:
            dev = FTDIDevice(url, name[1:-1])
            devices.append(dev)
        return devices

    @staticmethod
    def find_new_device(exist_dev: List["HVDevice"], key: Optional[Callable] = None):
        devices = []
        dev_list = filter(lambda x: key(x[0]), ftdi.Driver().list_devices())
        for dev in dev_list:
            for exist in exist_dev:
                device: FTDIDevice = exist.device
                if (dev[2] != device.device_id):
                    devices.append(FTDIDevice(*dev))
        return devices
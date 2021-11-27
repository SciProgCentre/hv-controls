import time
from typing import Optional, Callable, List

from pyftdi import ftdi
from pyftdi.usbtools import UsbTools
import pyftdi.serialext
from serial import EIGHTBITS, PARITY_NONE, STOPBITS_ONE
import logging

logger = logging.root


class PyFTDIDevice:

    BAUDRATE = 38400
    URLS = "ftdi"

    def __init__(self, url, name):
        self.port = None
        self.name = name
        self.url = url

    def __str__(self):
        return "{}:{}".format(self.name, self.url)

    def open(self):
        self.port = pyftdi.serialext.serial_for_url(self.url, bytesize=EIGHTBITS, parity=PARITY_NONE,
                                                    stopbits=STOPBITS_ONE,
                                                    baudrate=38400, do_not_open=True,
                                                    timeout=0.2)
        self.port.open()
        logger.info("Open serial port for {}".format(self))

    def close(self):
        self.port.close()
        logger.info("Close serial port for {}".format(self))

    def write(self, code : int, data: List[int]=None):
        temp = bytes([code] + data) if data is not None else bytes([code])
        self.port.write(temp)
        logger.debug("Write method get code : {}, data : {}".format(code, data))
        logger.debug("Write {}".format(temp))


    def read(self, nbytes) -> List[int]:
        s = self.port.read(nbytes)
        logger.debug("Read {}".format(s))
        result = [ord(c) for c in s] if type(s) is str else list(s)
        logger.debug("Convert read to {}".format(result))
        return result

    @staticmethod
    def open_urls(urls):
        devices = []
        for url, name in urls:
            dev = PyFTDIDevice(url, name[1:-1])
            devices.append(dev)
        return devices

    @staticmethod
    def get_urls(key: Optional[Callable] = None):
        devspec = ftdi.Ftdi.list_devices()
        urls = UsbTools.build_dev_strings(PyFTDIDevice.URLS, ftdi.Ftdi.VENDOR_IDS, ftdi.Ftdi.PRODUCT_IDS, devspec)
        urls = filter(key, urls)
        return urls

    @staticmethod
    def find_all_device(key: Optional[Callable] = None):
        return PyFTDIDevice.open_urls(PyFTDIDevice.get_urls(key))

    @staticmethod
    def find_new_device(exist_dev: List["HVDevice"], key: Optional[Callable] = None):
        new_urls = []
        for url, name in PyFTDIDevice.get_urls(key):
            for exist in exist_dev:
                if url == exist.device.url:
                    break
            else:
                new_urls.append(url)
        return PyFTDIDevice.open_urls(new_urls)
import time

from pyftdi import ftdi
from pyftdi.usbtools import UsbTools
import pyftdi.serialext
from serial import EIGHTBITS, PARITY_NONE, STOPBITS_ONE

devspec = ftdi.Ftdi.list_devices()
urls = UsbTools.build_dev_strings('ftdi', ftdi.Ftdi.VENDOR_IDS, ftdi.Ftdi.PRODUCT_IDS, devspec)
print(*urls, sep="\n")
url = urls[0]
port = pyftdi.serialext.serial_for_url(url[0], bytesize=EIGHTBITS, parity=PARITY_NONE, stopbits=STOPBITS_ONE, baudrate = 38400, timeout=0.2)

port.open()
port.write(bytes([3]))
time.sleep(2)
port.write(bytes([5]))
# port.write(bytes([1,10,10,10,10]))
# port.write(bytes([2]))
print(list(port.read(5)))
port.write(bytes([5]))
print(list(port.read(5)))
port.close()

if __name__ == '__main__':
    pass


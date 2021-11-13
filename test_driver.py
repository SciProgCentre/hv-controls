from pyftdi import ftdi
from pyftdi.usbtools import UsbTools
import pyftdi.serialext

devspec = ftdi.Ftdi.list_devices()
urls = UsbTools.build_dev_strings('ftdi', ftdi.Ftdi.VENDOR_IDS, ftdi.Ftdi.PRODUCT_IDS, devspec)
print(*urls, sep="\n")
url = urls[0]
port = pyftdi.serialext.serial_for_url(url[0], baudrate = 38400)

port.write(bytes([5]))
print(list(port.read(5)))


if __name__ == '__main__':
    pass


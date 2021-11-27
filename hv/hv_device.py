import logging
import math
import pathlib
import time
from dataclasses import dataclass
from typing import List

ROOT_PATH = pathlib.Path(__file__).parent.absolute()
DEVICE_PATH = pathlib.Path(ROOT_PATH, "device_data")

"""
Сейчас подключение к девайсу происходит через PyFTDI  и протестированно на Linux.
Для корректной работы программы под Windows возможно потребуется реализация подключение через FTD2XX.
"""
FTD2XX = False
if FTD2XX:
    from hv.ftd2xx_device import FTD2XXDevice as Device
else:
    from hv.ftdi_device import PyFTDIDevice as Device


@dataclass
class DeviceCoefficient:
    max_voltage: int
    voltage_coef: float
    current_coef_6w: float
    current_coef_15w: float
    current_coef_60w: float

    @staticmethod
    def load_data(voltage):
        with open(DEVICE_PATH / "data_from_protocol.csv") as fin:
            fin.readline()
            for line in fin.readlines():
                line = line.split(",")
                if int(line[0]) == voltage:
                    return DeviceCoefficient(*tuple(map(float, line)))


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

    def resolve_current_label(self):
        if self.current_units == "micro":
            return "μA"
        elif self.current_units == "milli":
            return "mA"
        else:
            return "μA"

    def resolve_current_step(self):
        if self.current_units == "micro":
            return self.current_step
        elif self.current_units == "milli":
            return self.current_step / 1000
        else:
            return self.current_step

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
        self.init_coefficient()
        self.is_open = False

    def init_coefficient(self):
        coeff = DeviceCoefficient.load_data(int(self.data.voltage_max / 1000))
        self.voltage_coeff = coeff.voltage_coef
        name: str = self.device.name
        if name[:3] == "HT-":
            power = int(name[3:5])  # Source power in Watt
            if power == 6:
                self.current_coef = coeff.current_coef_6w
            elif power == 15:
                self.current_coef = coeff.current_coef_15w
            elif power == 60:
                self.current_coef = coeff.current_coef_60w
            else:
                self.current_coef = None
        else:
            self.current_coef = None

    def __str__(self):
        return str(self.device)

    def open(self):
        try:
            self.device.open()
            self.is_open = True
        except Exception as e:
            logging.root.error(str(e))

    def close(self):
        self.device.close()

    def _write(self, code, data=None):
        try:
            self.device.write(code, data)
        except Exception as e:
            self.is_open = False
            logging.root.warning(str(e))

    def set_value(self, voltage, current):
        coeff = self.data.codemax_DAC / self.data.voltage_max
        if not math.isclose(coeff, self.voltage_coeff, abs_tol=1e-2):
            logging.root.warning("Voltage coefficients not consistent {}, {}".format(coeff, self.voltage_coeff))
        voltage = round(voltage * coeff)
        first_byte_U = voltage - math.trunc(voltage / 256) * 256
        second_byte_U = math.trunc(voltage / 256)

        coeff = self.data.codemax_DAC / self.data.current_max
        if self.current_coef is not None:
            if not math.isclose(coeff, self.current_coef, abs_tol=1e-2):
                logging.root.warning("Current coefficients not consistent {}, {}".format(coeff, self.current_coef))
        current = round(current * coeff)
        first_byte_I = current - math.trunc(current / 256) * 256
        second_byte_I = math.trunc(current / 256)

        self._write(HVDevice.SET_CODE, [first_byte_U, second_byte_U,
                                        first_byte_I, second_byte_I])

    def update_value(self):
        self._write(HVDevice.UPDATE_CODE)

    def reset_value(self):
        self._write(HVDevice.RESET_CODE)

    def get_IU(self):
        """
        Return Current (microA or milliA) and Voltage (V)
        """
        self._write(HVDevice.GET_CODE)
        temp = self.device.read(5)
        if temp is None or len(temp) < 5:
            print("Can not get data from device, data_array={}".format(str(temp)))
            return 0, 0
        if temp[4] != 13:
            print("Bad read: ", temp)
            return 0, 0
        ADC_mean_count = 16
        U = (temp[2] * 256 + temp[3]) * self.data.voltage_max / self.data.codemax_ADC / ADC_mean_count
        if self.data.polarity == "N":
            U = -U
        I = (temp[0] * 256 + temp[1]) * self.data.current_max / self.data.codemax_DAC
        if self.data.current_units == "micro":
            I = I - abs(U / self.data.feedback_resistanse)
        elif self.data.current_units == "milli":
            I = I / 1000
        return I, U

    @staticmethod
    def find_all_devices() -> List["HVDevice"]:
        devices = Device.find_all_device(lambda x: True)
        devices = [HVDevice(dev, DeviceData.load_device_data(dev.name)) for dev in devices]
        return devices  # + [create_test_device()]

    @staticmethod
    def find_new_devices(old) -> List["HVDevice"]:
        devices = Device.find_new_device(old, lambda x: True)
        devices = [HVDevice(dev, DeviceData.load_device_data(dev.name)) for dev in devices]
        return devices


def create_test_device():

    class FakeDevice:
        name = "HT-60-30-P"
        data = [0xFF, 0xFF, 0xFF, 0xFF]

        def __str__(self):
            return self.name + "-TEST"

        def open(self):
            print("open")
            logging.root.info("Open device {}".format(self))

        def close(self):
            print("close")
            logging.root.info("Close device {}".format(self))

        def write(self, code,data=None):
            print("Code:", code, "Data:", data)
            logging.root.debug("Write method get code : {}, data : {}".format(code, data))
            if code == 1:
                self.data = data
            elif code == 2:
                pass
                # raise Exception
            elif code == 3:
                self.data = [0,0,0,0]

        def read(self, n):
            print("Read:", n)
            return self.data[2:] + self.data[0:2] + [13]
    dev = FakeDevice()
    dev = HVDevice(dev, DeviceData.load_device_data(dev.name))
    return dev

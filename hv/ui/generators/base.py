import math

from PyQt5.QtCore import QObject, pyqtSignal
from PyQt5.QtWidgets import QWidget

from hv.hv_device import HVDevice

class Generator(QObject):
    NAME = ""
    abort_signal = pyqtSignal()

    MIN_PERIOD = 1.0
    MAX_PERIOD = MIN_PERIOD*1_000
    MIN_TICK = 0.5

    def __init__(self, device: HVDevice):
        super(Generator, self).__init__()
        self.device = device
        self.voltage_accuracy = self.device.data.voltage_step

    def start(self):
        pass

    def stop(self):
        pass

    def setup(self, voltage=0.0, current=0.0):
        if math.isclose(voltage, 0.0, abs_tol=self.voltage_accuracy):
            self.device.reset_value()
        else:
            self.device.set_value(voltage, current)
            self.device.update_value()


class GeneratorWidget(QWidget):


    def __init__(self,parent, generator: Generator):
        super(GeneratorWidget, self).__init__(parent)
        self.generator = generator

    def start(self):
        self.setDisabled(True)
        self.generator.start()

    def stop(self):
        self.generator.stop()
        self.setDisabled(False)

    def export_settings(self) -> dict:
        return None